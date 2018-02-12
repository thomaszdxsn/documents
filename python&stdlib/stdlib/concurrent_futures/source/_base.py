# Copyright 2009 Brian Quinlan. All Rights Reserved.
# Licensed to PSF under a Contributor Agreement.

__author__ = 'Brian Quinlan (brian@sweetapp.com)'

import collections
import logging
import threading
import time


#! 常量
FIRST_COMPLETED = 'FIRST_COMPLETED'
FIRST_EXCEPTION = 'FIRST_EXCEPTION'
ALL_COMPLETED = 'ALL_COMPLETED'
_AS_COMPLETED = '_AS_COMPLETED'

# 可能出现的Future状态(future packeages内部使用)
PENDING = 'PENDING'
RUNNING = 'RUNNING'
# Future可以被用户取消
CANCELLED = 'CANCELLED'
# ...`_Waiter.add_cancelled()`被一个worker调用
CANCELLED_AND_NOTIFIED = 'CANCELLED_AND_NOTIFIED'
FINISHED = 'FINISHED'

_FUTURE_STATES = [
    PENDING,
    RUNNING,
    CANCELLED,
    CANCELLED_AND_NOTIFIED,
    FINISHED
]

_STATE_TO_DESCRIPTION_MAP = {
    PENDING: 'pending',
    RUNNING: 'running',
    CANCELLED: 'cancelled',
    CANCELLED_AND_NOTIFIED: 'cancelled_and_notified',
    FINISHED: 'finished'
}

# futures package内部使用的logger
LOGGER = logging.getlogger("concurrent.futures")


#! 下面是定义的Exception
class Error(Exception):
    """所有和future相关异常的基类."""
    pass


class CancelledError(Error):
    """Future已经被取消."""
    pass


class TimeoutError(Error):
    """操作时长超过了deadline."""
    pass


class _Waiter(object):
    """在wait()和as_completed()堵塞的时候，提供event"""

    def __init__(self):
        self.event = threading.Event()
        self.finished_futures = []

    def add_result(self, future):
        self.finished_futures.append(future)

    def add_exception(self, future):
        self.finished_futures.append(future)

    def add_cancelled(self, future):
        self.finished_futures.append(future)


class _AsCompletedWaiter(_Waiter):
    """被`as_completed()`使用"""

    def __init__(self):
        super(_AsCompletedWaiter, self).__init__()
        self.lock = threading.Lock()

    def add_result(self, future):
        with self.lock:
            super(_AsCompletedWaiter, self).add_result(future)
            self.event.set()

    def add_exception(self, future):
        with self.lock:
            super(_AsCompletedWaiter, self).add_exception(future)
            self.event.set()

    def add_cancelled(self, future):
        with self.lock:
            super(_AsCompletedWaiter, self).add_cancelled(future)
            self.event.set()


class _FinishCompletedWaiter(_Waiter):
    """被`wait(return_when=FIRST_COMPLETED)`使用"""

    def add_result(self, future):
        super().add_result(future)
        self.event.set()

    def add_exception(self, future):
        super().add_exception(future)
        self.event.set()

    def add_cancelled(self, future):
        super().add_cancelled(future)
        self.event.set()


class _AllCompletedWaiter(_Waiter):
    """被`wait(return_when=FIRST_EXCEPTION and ALL_COMPLETED)`使用"""

    def __init__(self, num_pending_calls, stop_on_exception):
        self.num_pending_calls = num_pending_calls
        self.stop_on_exception = stop_on_exception
        self.lock = threading.Lock()
        super().__init__()

    def _decrement_pending_calls(slef):
        with self.lock:
            self.num_pending_calls -= 1
            if not self.num_pending_calls:
                self.event.set()
    
    def add_result(self, future):
        super().add_result(future)
        self._decrement_pending_calls()

    def add_exception(self, future):
        super().add_exception(future)
        if self.stop_on_exception:
            self.event.set()
        else:
            self._decrement_pending_calls()
    
    def add_cancelled(self, future):
        super().add_cancelled(future)
        self._decrement_pending_calls()

    
class _AcquireFutures(object):
    """一个上下文管理器，需要对Future的conditions进行一个有序的acquire"""

    def __init__(self, futures):
        self.futures = sorted(futures, key=id)

    def __enter__(self):
        for future in self.futures:
            future._condition.acquire()

    def __exit__(self):
        for future in self.futures:
            future._condition.release()


def _create_and_install_waiters(fs, return_when):
    if return_when == _AS_COMPLETED:
        waiter = _AsCompletedWaiter()
    elif return_when == FIRST_COMPLETED:
        waiter = _FinishCompletedWaiter()
    else:
        #! 这个count的写法很棒
        pending_count = sum(
            f.state not in [CANCELLED_AND_NOTIFIED, FINISHED] for f in fs
        )
        if return_when == FIRST_EXCEPTION:
            waiter = _AllCompletedWaiter(pending_count, stop_on_exception=True)
        elif return_when == ALL_COMPLETED:
            waiter = _AllCompletedWaiter(pending_count, stop_on_exception=False)
        else:
            raise ValueError("Invalid return condition: %r" %return_when)

    for f in fs:
        f._waiters.append(waiter)

    return waiter


def as_completed(fs, timeout=None):
    """一个迭代器，可以迭代futures，在每个完成的时候yield它

    参数:
        fs: 想要迭代的Futures序列(很可能由不同的Executor创建)。
        timeout: 等待的最大秒数。如果为None，代表会无限等待。

    返回:
        一个迭代器，在给定的futures完成时(finished or cancelled)yield它。
        如果给定的Future重复，只会被返回一次。

    抛出:
        `TimeoutError`: 如果在给定的timeout时间内没有迭代完毕，抛出这个错误。
    """
    if timeout is not None:
        end_time = timeout + time.time()

    fs = set(fs)
    with _AcquireFutures:
        finished = set(
            f for f in fs:
            if f._state in [CANCELLED_AND_NOTIFIED, FINISHED]
        )
        pending = fs - finished
        waiter = _create_and_install_waiters(fs, _AS_COMPLETED)
    
    try:
        yield from finished

        while pending:
            if timeout is None:
                wait_timeout = None
            else:
                wait_timeout = end_time - time.time()
                if wait_timeout < 0:
                    raise TimeoutError(
                        "%d (of %d) futures unfinished" % (
                            len(pending), len(fs)
                        )
                    )
            waiter.event.wait(wait_timeout)

            with waiter.lock:
                finished = waiter.finished_futures
                waiter.finished_futures = []
                waiter.event.clear()
            
            for future in finished:
                #！生成器
                yield future
                pending.remove(future)
    finally:
        for f in fs:
            with f._condition:
                f._waiters.remove(waiter)

DoneAndNotDoneFutures = collections.namedtuple(
    'DoneAndNotDoneFutures', 'done not_done'
)
def wait(fs, timeout=None, return_when=ALL_COMPLETED):
    """等待给定的futures序列完成

    参数:
        fs: 需要等待的Future序列(可能由不同的Executor创建)。
        timeout: 等待的最大秒数。如果为None，代表会无限等待。
        return_when: 表明这个函数应该合适返回。可选项为:

            FIRST_COMPLETED - 在碰到首个future结束或取消的时候返回。
            FIRST_EXCEPTION - 在碰到首个异常的时候返回。
            ALL_COMPLETED - 在所有future结束或取消的时候返回。
    返回:
        一个命名元组，包含两个集合.第一个集合，叫做"done"，包含
        在wait结束前已经完成的futures。第二个集合，叫做"not_done"，
        包含未完成的futures。
    """
    with _AcquireFutures(fs):
        done = set(f for f in fs
                   if f._state in [CANCELLED_AND_NOTIFIED, FINISHED])
        not_done = set(fs) - done
    
        if (return_when == FIRST_COMPLETED) and done:
            return DoneAndNotDoneFutures(done, not_done)
        elif (return_when == FIRST_EXCEPTION) and done:
            if any(f for f in done
                   if not t.cancelled() and f.exception() is not None):
                return DoneAndNotDoneFutures(done, not_done)
        
        if len(done) == len(fs):
            #! fs全部完成
            return DoneAndNotDoneFutures(done, not_done)

        waiter = _create_and_install_waiters(fs, return_when)
    
    waiter.event.wait(timeout)
    for f in fs:
        with f._condition:
            f._waiters.remove(waiter)
    
    done.update(waiter.finished_futures)
    return DoneAndNotDoneFutures(done, set(fs) - done)


class Future(object):
    """代表一个异步计算的结果。"""

    def __init__(self):
        """初始化一个future。不应该由用户调用。"""
        self._condition = threading.Condition()
        self._state = PENDING
        self._result = None
        self._exception = None
        self._waiters = []
        self._done_callbacks = []

    def _invoke_callbacks(self):
        for callback in self._done_callbacks:
            try:
                callback(self)
            except Exception:
                LOGGER.exception('exception calling callback for %r', self)

    def __repr__(self):
        with self.condition:
            if self._state == FINISHED:
                if self._exception:
                    return "<%s at %#x state=%s raised %s>" %(
                        self.__class__.__name__,
                        id(self),
                        _STATE_TO_DESCRIPTION_MAP[self._state],
                        self._exception.__class__.__name__
                    )
                else:
                    return "<%s at %#x state=%s returned %s>" %(
                        self.__class__.__name__,
                        id(self),
                        _STATE_TO_DESCRIPTION_MAP[self._state],
                        self._result.__class__.__name__
                    )
            return "<%s at %#x state=%s>" %(
                self.__class__.__name__,
                id(self),
                _STATE_TO_DESCRIPTION_MAP[self._state]
            )
    
    def cancel(self):
        """如果可能，取消这个future

        如果成功取消，返回True，否则返回False。如果一个future
        已经运行或者已经完成，不能被取消。
        """
        with self._condition:
            if self._state in [RUNNING, FINISHED]:
                return False
            
            if self._state in [CANCELLED_AND_NOTIFIED, CANCELLED]:
                return True
            
            self._state = CANCELLED
            self._codnition.notify_all()

        self._invoke_callbacks()
        return True

    def cancelled():
        """如果future已经取消，返回True。"""
        with self._condition:
            return self._state in [CANCELLED, CANCELLED_AND_NOTIFIED]

    def running(self):
        """如果future正在执行，返回True。"""
        with self._condition:
            return self._state == RUNNING

    def done(self):
        """如果future已经取消或者已经执行结束，返回True。"""
        with self._condition:
            return self._state in [CANCELLED, CANCELLED_AND_NOTIFIED, FINISHED]
    
    def __get_result(self):
        if self._exception:
            raise self._exception
        else:
            return self._result

    def add_done_callback(self, fn):
        """关联一个可调用对象，在future结束的时候调用它
        
        参数:
            fn: 一个可调用对象，会以当前这个`future`对象作为参数
                来调用它。这个可调用对象总是会在它被加入的相同进程的
                一个进程中被调用。如果future已经完成或者被取消，这个
                可调用对象会被例子调用。这些可调用对象会按照它们加入的
                顺序来调用。
        """
        with self._condition:
            if self._state not in [CANCELLED, CANCELLED_AND_NOTIFIED, FINISHED]:
                self._done_callbacks.append(fn)
                return
        fn(self)    #! 如果已经完成，直接执行这个callback.

    def result(self, timeout=None):
        """返回这个future代表的call的结果.

        参数:
            timeout:一个秒数时间，等待future结果的时间。如果为None，
                    意思就是不指定等待时间。

        返回:
            这个future代表的call的结果。

        抛出:
            CancelledError: 如果future已经被取消。
            TimeoutError: 如果future没有在timeout时间内完成执行。
            Exception: 如果call抛出了异常，这个异常会继续向上抛出。
        """
        with self._condition:
            if self._state in [CANCELLED, CANCELLED_AND_NOTIFIED]:
                raise CancelledError()
            elif self._state == FINISHED:
                return self.__get_result()
            
            self._condition.wait(timeout)

            if self._state in [CANCELLED, CANCELLED_AND_NOTIFIED]:
                raise CancelledError()
            elif self._state == FINISHED:
                return self.__get_result()
            else:
                raise TimeoutError()

    def exception(self, timeout=None):
        """返回future代表的call抛出的异常。

        参数:
            timeout:一个秒数时间，等待future结果的时间。如果为None，
                    意思就是不指定等待时间。
        
        返回:
            返回future代表的call抛出的异常，或者None。

        抛出:
            CancelledError: 如果future已经取消。
            TimeoutError: 如果future在给定的timeout之前没有执行完毕。
        """
        with self._condition:
            if self._state in [CANCELLED, CANCELLED_AND_NOTIFIED]:
                raise CancelledError()
            elif self._state == FINISHED:
                return self._exception
        
            self._codnition.wait(timeout)

            if self._state in [CANCELLED, CANCELLED_AND_NOTIFIED]:
                raise CancelledError()
            elif self._state == FINISHED:
                return self._exception
            else:
                raise TimeoutError()

    # 下面的方法应该只由Executor或者单元测试使用
    def set_running_or_notify_cancel(self):
        """标记future为running状态，或处理一些cancel通知。

        应该只用在Executor或者单元测试。

        如果future已经被取消，那么等待这个future完成的线程将会被通知，
        并返回False。

        如果future没有取消，则把它置入running状态，并返回True。

        在对这个future作一些什么事情之前，应该由Executor调用这个方法。
        如果这个方法返回False，那么其它的事情也应该中止。

        返回:
            如果Future已经被取消，则返回False，否则返回True。

        抛出:
            RuntimeError:如果这个方法已经被调用，或者已经调用了
                `set_result()`或`set_exception()`
        """
        with self._condition:
            if self._state == CANCELLED:
                self._state = CANCELLED_AND_NOTIFIED
                for waiter in self._waiters:
                    waiter.add_cancelled(self)
                # 不需要调用`self._condition.notify_all()`
                # 因为`self.cancel()`已经触发了一个通知
                return False
            elif self._state == PENDING:
                self._state = RUNNING
                return True
            else:
                LOGGER.critical("Future %s in unexpected state: %s",
                                id(self),
                                self._state)
                raise RuntimeError("Future in unexpected state")
    
    def set_result(self, result):
        """设置这个future关联call的结果

        只应该被Executor或单元测试使用。
        """
        with self._condition:
            self._result = result
            self._state = FINISHED
            for waiter in self._waiters:
                waiter.add_result(self)
            self._condition.notify_all()
        self._invoke_callbacks()

    def set_exception(self, exception):
        """将给定的exception设置为future的exception

        只应该被Executor或单元测试使用。
        """
        with self._condition:
            self._exception = exception
            self._state = FINISHED
            for waiter in self._waiters:
                waiter.add_exception(self)
            self._condition.notify_all()
        self._invoke_callbacks()


class Executor(object):
    """这是异步executor实体的一个抽象基类"""

    def submit(self, fn, *args, **kwargs):
        """提交一个想要执行的可调用对象以及参数
        
        规划执行这个可调用对象以`fn(*args, **kwargs)`的形式，
        最后返回一个`Future`对象代表这个可调用对象的执行.

        返回:
            一个代表给定call的Future.
        """
        raise NotImplementedError()

    def map(self, fn, *iterables, timeout=None, chunksize=1):
        """返回一个迭代器，等同于`map(fn, iter)`
        
        参数:
            fn: 一个可调用对象，会从`iterable`参数中提取参数多次调用这个对象
            timeout: 最久的等待时间。
            chunksize: 传入子进程时把`iterable`分割的chunk的大小。
                    这个参数只能用于`ProcessPoolExecutor`.

        返回:
            一个等同于`map(func, *iterable)`的迭代器，不过可以并发执行。

        抛出:
            TimeoutError: 如果整个迭代器的结果不能在`timeout`时间达到之前生产.
            Exception： 如果`fn(*args)`抛出了任何的错误
        """
        if timeout is not None:
            end_time = timeout + time.time()
        
        fs = [self.submit(fn, *args) for args in zip(*iterables)]

        # yield在闭包进行所有future必须在首个迭代器的值被要求的时候提交
        def result_iterator():
            try:
                for future in fs:
                    if timeout is None:
                        yield future.result()
                    else:
                        yield future.result(endtime - time.time())
            finally:
                for future in fs:
                    future.cancel()
        return result_iterator()

    def shutdown(self, wait=True):
        """清理这个Executor管理的资源。

        可以调用这个方法多次。不过，
        在调用这个方法之后不能再调用其它方法。

        参数：
            wait: 如果为True，`.shutdown()`不会立即返回，
                直到所有运行的futures都运行结束。然后会把
                这个executor使用的资源回收。
        """
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.shutdown(wait=True)
        return False
```