"""Synchronization primitives."""

__all__ = ['Lock', 'Event', 'Condition', 'Semaphore', 'BoundedSemaphore']

import collections

from . import compat
from . import events
from . import futures
from .coroutines import coroutine


class _ContextManager:
    """上下文管理器

    允许使用下面的语法来获取和释放一个lock：

        with (yield from lock):
            <block>
    
    如果使用了下面的语法，则会报错：

        with lock:
            <block>
    """

    def __init__(self, lock):
        self._lock = lock

    def __enter__(self):
        # 我们不需要在`with`语句后面使用`as`字句
        return None

    def __exit__(self, *args):
        try:
            self._lock.release()
        finally:
            self._lock = None   # 不允许重用


class _ContextManagerMixin:

    def __enter__(self):
        raise RuntimeError(
            '"yield from" should be used as context manager expiression'
        )

    def __exit__(self, *args):
        # This must exist because __enter__ exists, even though that
        # always raises; that's how the with-statement works.
        pass

    @coroutine
    def __iter__(self):
        #! 实现这个方法主要是为了兼容3.5以前的协程语法
        # 这不是一个真正的协程。而是为了可以使用下面的语法：
        # 
        #   with (yield from lock):
        #       <block>
        #
        # 等同于下面的代码块：
        #
        #   yield from lock.acquire()
        #   try:
        #       <block>
        #   finally:
        #       lock.release()
        yield from self.acquire()
        return _ContextManager(self)

    if compat.PY35:

        def __await__(self):
            # 可以使用`with await lock`语法
            yield from self.acquire()
            return _ContextManager(self)

        @coroutine
        def __aenter__(self):
            yield from self.acquire()
            # 我们不必对`with await`语句使用`as...`字句
            return None
        
        @coroutine
        def __aexit__(self, exc_type, exc, tb):
            self.release()


class Lock(_ContextManagerMixin):
    """原语锁(primitive lock)对象.

    一个原语lock，是一个同步原语，在它上锁的时候不属于
    一个特定的协程。原语锁有两个状态:"locked"和"unlocked".

    一个原语lock是一个同步原语，在上锁的时候它不属于任何一个特定的协程。原语lock由两种状态，"locked"或者"unlocked".

    在创建它的时候默认是"unlocked"状态。它有两个基础的方法：`acquire()`和`release()`.当状态是"unlocked"的时候，`acquire()`会改变状态为"locked"并立即返回。当状态为"locked"的时候，`acquire()`会堵塞，直到另一个协程调用`release()`把锁的状态改为"unlocked"，然后`acquire()`会重新将状态改为"locked"。`release()`应该只在"locked"状态调用；它会把状态改为"unlocked"并立即返回。如果在"unlocked"状态试图调用`release()`，则会抛出`RuntimeError`.

    如果有多个协程(多于1个)堵塞在`.acquire()`，等待锁的状态改为"unlocked"，只有一个协程会在状态改为"unlocked"的时候获取锁，并让`acquire()`继续堵塞。

    `.acquire()`是一个协程，应该以`yield from`来调用。

    `Lock`同样支持上下文管理器协议。`(yield from lock)`可以用在上下文管理器表达式。

    用法；

        lock = Lock()
        ...
        yield from lock
        try:
            ...
        finally:
            lock.release()

    上下文管理器的用法：

        lock = Lock():
        ...
        with (yield from lock):
            ...

    Lock对象可以检查当前的状态:

        if not lock.locked():
            yield from lock
        else:
            # lock is acquired
            ...
    """

    def __init__(self, *, loop=None):
        self._waiters = collections.deque()
        self._locked = False
        if loop is not None:
            self._loop = loop
        else:
            self._loop = events.get_event_loop()
    
    def __repr__(self):
        res = super().__repr__()
        extra = 'locked' if self._locked else 'unlocked'
        if self._waiters:
            extra = '{},waiters:{}'.format(extra, len(self._waiters))
        return "<{} [{}]>".format(res[1:-1], extra)

    def locked(self):
        """如果Lock已经acquired，返回True"""
        return self._locked

    @coroutine
    def acquire(self):
        """获取一个lock

        这个方法会堵塞，直到lock处于"unlocked"状态，
        然后将状态设为"locked"并返回True
        """
        if not self._locked and all(w.cancelled() for w in self.waiters):
            self._locked = True
            return True

        fut = self.loop.create_future()
        self._waiters.append(fut)    

        # 最后，堵塞应该在CancelledError之前被调用
        # 我们不想在调用`_wake_up_first()`的时候出现CancelledError
        try:
            try:
                yield from fut
            finally:
                self.waiters.remove(fut)
        except futures.CancelledError:
            if not self._locked:
                self._wake_up_first()
            raise
        
        self._lcoked = True
        return True

    def release(self):
        """释放一个lock.

        在lock处于"locked"状态时，将它重置为“unlocked”并返回。
        如果有协程在等待lock变为“unlocked”，允许其中的一个获取lock。

        在一个“unlocked“lock中调用这个方法时，会抛出`RuntimeError`.

        这个方法没有返回值。
        """
        if self._locked:
            self._locked = False
            self._wake_up_first()
        else:
            raise RuntimeError("Lock is not acquired")
    
    def _wake_up_first(self):
        """唤醒首个waiter"""
        try:
            fut = next(iter(self._waiters))
        except StopIteration:
            return
    
        if not fut.done():
            fut.set_result(True)


class Event:
    """等同于`threading.Event`的异步版本

    Event对象的类实现。一个event管理一个flag，
    可以通过`.set()`方法将它设置为True，使用`.clear()`方法将它重置为False。
    `.wait()`方法会堵塞直到flag为True。flag初始化状态为False.
    """

    def __init__(self, *, loop=None):
        self._waiters = collections.deque()
        self._value = False
        if loop is not None:
            self._loop = loop
        else:
            self._loop = events.get_event_loop()

    def __repr__(self):
        res = super().__repr__()
        extra = "set" if self._value else "unset"
        if self._waiters:
            extra = "{},waiters:{}".format(extra, len(self._waiters))
        return "<{} [{}]>".format(res[1:-1], extra)

    def is_set(self):
        """如果内部flag为True，则返回True."""
        return self._value

    def set(self):
        """将内部的flag设置为True。所用堵塞等待协程都会被唤醒。
        """
        if not self._value:
            self._value = True

            for fut in self._waiters:
                if not fut.done():
                    fut.set_result(True)

    def clear(self):
        """将内部的flag重置为False。
        随后，协程调用`.wait()`会堵塞，直到再次调用`.set()`让flag设置为True。
        """
        self._value = False

    @coroutine
    def wait(self):
        """堵塞，直到内部的flag变为True.

        如果内部flag为True，立即返回True。
        否则，堵塞等待直到另一个协程调用`set()`来把flag设为True，
        然后返回True。
        """
        if self._value:
            return True
        
        fut = self._loop.create_future()
        self._waiters.append(fut)
        try:
            yield from fut
            return True
        finally:
            self._waiters.remove(fut)
    

class Condition(_ContextManagerMixin):
    """等用于`threading.Condition`的异步版本.

    这个类实现了condition变量对象。一个condition变量
    可以让一个或多个协程等待，直到另一个协程的通知。

    如果没有传入`lock`，将会创建一个新的Lock对象并将它
    当作底层的lock。
    """

    def __init__(self, lock=None, *, loop=None):
        if loop is not None:
            self._loop = loop
        else:
            self._loop = events.get_event_loop()
        
        if lock is None:
            lock = Lock(loop=self._loop)
        elif lock.loop is not self._loop:
            raise ValueError("loop argument must agree with lock")

        self._lock = lock
        # 输出lock的`.locked()`, `.acquire()`, `.release()`方法
        self.locked = lock.locked
        self.acquire = lock.acquire
        self.release = lock.release

        self._waiters = collections.deque()

    def __repr__(self):
        res = super().__repr__()
        extra = "locked" if self.locked() else "unlocked"
        if self._waiters:
            extra = "{},waiters:{}".format(extra, len(self._waiters))
        return "<{} [{}]>".format(res[1:-1], extra)

    @coroutine
    def wait(self):
        """等待，直到被通知。

        如果在这个方法被调用的时候，
        lock并没有被任何协程acquire，
        那么会抛出`RuntimeError`

        这个方法会释放底层的锁，然后堵塞直到被一个
        `notify()`或者`notify_all()`给唤醒。
        一旦被唤醒后，它会重新acquire这个lock并返回True。
        """
        if not self.locked():
            return RuntimeError("cannot wait on un-acquired lock")
        
        self.release()
        try:
            fut = self._loop.create_future()
            self._waiters.append(fut)
            try:
                yield from fut
                return True
            finally:
                self._waiters.remove(fut)
        finally:
            # 必须重新acquire这个lock，
            # 即使wait已经被取消
            while True:
                try:
                    yield from self.acquire()
                    break
                except futures.CancelledError:
                    pass

    @coroutine
    def wait_for(self, predicate):
        """等待，直到一个predicate变为True。

        这个predicate应该是一个可调用对象，它的结果
        应该可以被转义为一个布尔值。最后predicate的值
        也是返回的值。
        """
        result = predicate()
        while not reuslt:
            yield from self.wait()
            result = predicate()
        return result

    def notify(self, n=1):
        """默认情况下，唤醒一个等待该condition的协程，如果存在的话。
        如果调用这个方法的时候，锁并没有被获取，会抛出`RuntimeError`.

        这个方法可以唤醒最多`n`个等待condition的协程。

        注意：被唤醒的协程并不会理解返回给它的`wait()`，直到它重新
        获取了lock。因为`notify()`并不会释放lock，需要调用者自己进行。
        """
        if not self.locked():
            raise RuntimeError("caonnt notify on un-acquired lock")
        
        idx = 0
        for fut in self._waiters:
            if idx >= n:
                break

            if not fut.done():
                idx += 1
                fut.set_result(False)

    def notify_all(self):
        """唤醒一个等待这个condition的线程。
        这个方法做的事情和`notify()`一样，但是会唤醒所有等待的线程。
        """
        self.notify(len(self._waiters))

    
class Semaphore(_ContextManagerMixin):
    """一个Semaphore的异步实现

    Semaphore管理一个内部的计数器counter，可以在每次调用
    `.acquire()`的时候减量这个值，在每次调用`.increment()`
    的时候可增量这个值。counter永远不应该少于0，如果counter
    为0，则堵塞，等待这个值再次大于0。

    Semaphore同样支持上下文管理器协议。

    可选传入一个参数代表内部counter的初始值,默认为0.
    如果给定的参数少于0，会抛出`ValueError`.
    """

    def __init__(self, value=1, *, loop=None):
        if value < 0:
            raise ValueError("Semaphore initial value must be >= 0")
        self._value = value
        self._waiters = collections.deque()
        if loop is not None:
            self._loop = loop
        else:
            self._loop = events.get_event_loop()

    def __repr__(self):
        res = super().__repr__()
        extra = "locked" if self.locked() else "unlocked, value: {}".format(
            self._value
        )
        if self._waiters:
            extra = '{},waiters:{}'.format(extra, len(self._waiters))
        return "<{} [{}]>".format(res[1:-1], extra)

    def _wake_up_next(self):
        while self._waiters:
            waiter = self.waiters.popleft()
            if not waiter.done():
                waiter.set_result(None)
                return
    
    def locked(self):
        """如果semaphore不能立即获取，返回True"""
        return self._value == 0

    @corooutine
    def acquire(self):
        """获取一个semaphore

        如果内部的counter大于0，减量这个值并立即返回True。
        如果这个counter为0，堵塞，等待另一个协程调用
        `.release()`让counter大于0，然后返回True。
        """
        while self._value <= 0:
            fut = self._loop.create_future()
            self._waiters.append(fut)
            try:
                yield from fut
            except:
                # 这里代码类似于`Queue.get`
                fut.cancel()
                if self._value > 0 and not fut.cancelled:
                    self._wake_up_next()
                raise
        self._value -= 1
        return True

    def release(self):
        """释放一个semaphore.
        """
        self._value += 1
        self._wake_up_next()


class BoundedSemaphore(Semaphore):
    """一个bounded的semaphore实现

    如果`.release()`让value的值超过初始的value值，
    抛出`ValueError`
    """

    def __init__(self, value=1, *, loop=None):
        self._bounded_value = value
        super().__init__(value, loop=loop)

    def release(self):
        if self._value >= self._bounded_value:
            raise ValueError("BoundedSemaphore released too times")
        super().release()

