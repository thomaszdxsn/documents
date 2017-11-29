## tornado.locks -- 同步原语(Synchronization primitives)

协调协程和同步原语，类似标准库提供给线程的接口。

> 警告
>
>> 注意这些原语并不是线程安全的，不可以直接替换标准库的代码。它们只是用来在一个单线程app中协调Tornado的协程，并不保障多线程app中的变量共享。

### 条件(Condition)

- `tornado.locks.Condition`

    一个条件(condition)，允许一个或多个协程等待通知(再执行)。

    类似于标准库的`threading.Condition`，但是不需要底层的锁(acquired和released操作)。

    在Tornado的Condition中，协程可以等待一个其它协程的通知：

    ```python
    from tornado import gen
    from tornado.ioloop import IOLoop
    from tornado.locks import Condition

    condition = Condition()


    @gen.coroutin
    def waiter():
        print("我在等待")
        yield condition.wait()
        print("我完成了等待")

    
    @gen.coroutine
    def notifier():
        print("即将提醒")
        condition.notify()
        print("完成提醒")

    
    @gen.coroutine
    def runner():
        # yield两个Future；
        yield [waiter(), notifier()]

    IOLoop.current().run_sync(runner)
    ```

    结果为:

    ```python
    我在等待
    即将提醒
    完成提醒
    我完成了等待
    ```

    `wait`可以接受一个可选的timeout参数，可以传入一个绝对的时间戳：

    ```python
    io_loop = IOLoop.current()

    # 等待通知一秒钟
    yield condition.wait(timeout=ioloop.time() + 1)
    ```

    或者可以传入一个相对于当前时间的`datetime.timedelta`对象：

    ```python
    # 等待一秒钟
    yield condition.wait(timeout=datetime.timedelta(seconds=1))
    ```

    如果在规定的时间没有接受到通知，将会抛出一个`tornado.gen.TimeoutError`。

    - `wait(timeout=None)`

        等待`notify()`

        返回一个Future，如果这个条件接受到通知后返回True，如果超时则返回False。

    - `notify(n=1)`

        唤醒`n`个等待者。

    - `notify_all()`

        唤醒所有等待者。


### 事件(Event)

- `tornado.locks.Event`

    一个事件(event)将会堵塞住协程，直到内部的flag设置为True。

    类似于`threading.Event`。

    协程可以等待一个event设置。一旦这个event设置，调用`yield event.wait()`将不会堵塞，除非这个event已经被清除：

    ```python
    from tornado import gen
    from tornado.ioloop import IOLoop
    from tornado.locks import Event

    event = Event()


    @gen.coroutine
    def waiter():
        print("等待一个event")
        yield event.wait()
        print("这次不再等待")
        yield event.wait()
        print("完成")

    
    @gen.coroutine
    def setter():
        print("即将设置event")
        yield event.set()

    
    @gen.coroutine
    def runner():
        yield [waiter(), setter()]

    IOLoop.current().run_sync(runner)
    ```

    结果为:

    ```python
    等待一个event
    即将设置event
    这次不再等待
    完成
    ```

    - `is_set()`

        如果内部flag设置为True，返回True。

    - `set()`

        设置内部的flag为True，所有的等待者都会被唤醒。

        之后继续调用`wait`将不会被堵塞。

    - `clear()`

        重置内部的flag为False。

        之后调用`wait`将会堵塞，知道调用`set`。

    - `wait(timeout=None)`

        堵塞，直到内部的flag设置为True。

        一切正常返回一个Future，如果超过了timeout时间，则会抛出一个`tornado.gen.TimeoutError`异常。


### 信号量(Semaphore)

- `tornado.locks.Semaphore(value=1)`

    一个锁，可以被上锁(acquired)一个固定的数量。

    一个信号量管理一个计数器，代表`release`调用的次数减去`acquire`调用的次数，再加上原始的值。如果必要，`acquire()`方法将会堵塞，直到它能够不让计数器为负数的返回。

    信号量限制了共享资源的访问。例如，想要一次访问两个wokers：

    ```python
    from tornado import gen
    from tornado.ioloop import IOLoop
    from tornado.locks import Semaphore

    sem = Semaphore()


    @gen.coroutine
    def worker(worker_id):
        yield sem.acquire()
        try:
            print("Worker %d is working" %worker_id)
            yield use_some_resource()
        finally:
            print("Worker %d id done" %worker_id)
            sem.release()


    @gen.coroutine
    def runner():
        # Join all workers
        yield [worker(i) for i in range(3)]

    IOLoop.current().run_sync(runner)    
    ```

    结果为：

    ```python
    Worker 0 is working
    Worker 1 is working
    Worker 0 is done
    Worker 2 is working
    Worker 1 is done
    Worker 2 is done
    ```

    Workers0和1可以并发运行，但是worker2需要等待空闲的信号量，也就是worker0。

    `acquire`是一个上下文管理器，所以`worker`可以这样写：

    ```python
    @gen.coroutine
    def worker(worker_id):
        with (yield sem.acquire()):
            print("Worker %d is working" %worker_id)
            yield use_some_resource()

        # 这时这个信号量被释放
        print("Worker %d is done" %worker_id)
    ```

    在Python3.5中，信号量本身可以使用`async`上下文管理器语法：

    ```python
    async def worker(worker_id):
        async with sem:
            print("Worker %d is working" %worker_id)
            await use_some_resource()

        # 这时这个信号量被释放
        print("Worker %d is done" %worker_id)      
    ```

    - `release()`

        增量计数器，并且唤醒一个等候者。

    - `acquire(timeout)`

        减量计数器。返回一个Future。

        如果计数器为空，堵塞函数并且等待一个`release()`。如果超过超时时间，将会抛出一个`TimeoutError`。


### 有界信号量(BoundedSemaphore)

- `tornado.locks.BoundedSemaphore(value=1)`

    一个可以防止`release()`调用太多次的信号量。

    如果`release`增量的信号值高于原始的参数值，将会抛出一个`ValueError`。信号量通常用来保护资源的容纳能力，这是一个信号量被释放太多次可以看作是一个bug。

    - `release()`

        增量计数器，并且唤醒一个等候者。

    - `acquire(timeout)`

        减量计数器。返回一个Future。

        如果计数器为空，堵塞函数并且等待一个`release()`。如果超过超时时间，将会抛出一个`TimeoutError`。


### 锁(Lock)

- `tornado.locks.Lock`

    一个协程的锁。

    一个Lock以解锁形式开启，使用`acquire`将会立即将它上锁。当它上锁时，一个yield这个`acquire`的写成将会堵塞直到其它的协程调用`release`。

    释放一个未上锁的锁，将会抛出一个`RuntimeError`。

    `acquire`支持Python所有版本的上下文管理器：

    ```python
    >>> from tornado import gen, locks
    >>> lock = locks.Lock()
    >>>
    >>> @gen.coroutine
    ... def f():
    ...     while (yield lock.acquire()):
    ...         # 上锁
    ...         pass
    ...
    ...     # 释放锁
    ```

    在Python3.5以后，`Lock`同样支持`async`上下文管理器协议。注意这时不需要使用`acquire`，因为`async with`包含了`yield`和`acquire`：

    ```python
    >>> async def():
    ...     async with lock:
    ...         # 上锁
    ...         pass
    ...
    ...     # 释放锁
    ```

    - `acquire(timeout=None)`

        试图上锁，返回一个Future。

        如果在timeout超时的情况下，会抛出一个`tornado.gen.TimeoutError`。

    - `release()`

        解锁。

        等待一个Lock的acquire完成，然后释放锁。

        如果这个Lock没有上锁，将会抛出一个`RuntimeError`。

        


