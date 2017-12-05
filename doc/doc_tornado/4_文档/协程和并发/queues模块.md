## tornado.queues -- 协程队列

协程使用的异步队列。

> 警告
>
>> 不想标准库的`queue`模块，这里定义的类不是线程安全的。想要使用其它线程的队列，在使用任意队列的方法时，请使用`IOLoop.add_callback`来把控制转移到当前的`IOLoop`线程。

### 类

#### Queue

- `tornado.queues.Queue(maxsize=0)`

    协调生产者和消费者协程。

    如果`maxsize=0`，这个队列的大小是无限的。

    ```python
    from tornado import gen
    from tornado.ioloop import IOLoop
    from tornado.queues import Queue

    q = Queue(maxsize=2)


    @gen.coroutine
    def consumer():
        while True:
            item = yield q.get()
            try:
                print("Doing work on %s" %itme)
                yield gen.sleep(.01)
            finally:
                q.task_done()


    @gen.coroutine
    def producer():
        for item in range(5):
            yield q.put(item)
            print("Put %s" %item)

    
    @gen.coroutine
    def main():
        # Start consumer without waiting (since it never finishes).
        IOLoop.current().spawn_callback(consumer)
        yield producer()
        yield q.join()
        print("Done")

    IOLoop.current().run_sync(main)
    ```

    结果为：

    ```python
    Put 0
    Put 1
    Doing work on 0
    Put 2
    Doing work on 1
    Put 3
    Doing work on 2
    Put 4
    Doing work on 3
    Doing work on 4
    Done
    ```

    在Python3.5以后，`Queue`实现了`async`迭代器协议，所以`consumer()`可以重写成以下这样：

    ```python
    async def consumer():
        async for item in q:
            try:
                print("Doing work on %s" %item)
                yield gen.sleep(.01)
            finally:
                q.task_done()
    ```

    - `maxsize`: 这个队列中允许的最大item数量
    - `qsize()`: 队列中当前存在的item数量。
    - `put(item, timeout=None)`

        将一个itme放到队列中，可能需要等待，直到队列中有空间可以使用。

        返回一个`Future`，如果超出了timeout的超时时间，将会抛出一个`tornado.gen.TimeoutError`。

    - `put_nowait(item)`

        将一个item**非堵塞的**置入队列中。

        如果队列已满，将会抛出`QueueFull`.

    - `get(timeout=None)`

        从队列中移除并返回一个item。

        返回一个`Future`，它将会在item可获取时才会被完成，或者在超时之后抛出`tornado.gen.TimeoutError`。

    - `get_nowait()`

        **非堵塞的**从队列中移除并返回一个item。

        如果队列为空，将会抛出一个`QueueEmpty`。

    - `task_done()`

        代表之前出列的任务已经完成。

        在队列的消费者中使用。每个`get`取出一个任务后，都会调用`task_donw()`来告诉队列，任务的处理已经结束。

        如果一个`join`是堵塞的，所有的item被处理后它会被重新使用。每个`put`都对应一个`task_done`。

        如果调用这个方法的次数多于`put`的次数，将会抛出一个`ValueError`。

    - `join(timeout=None)`

        堵塞，直到队列中的所有item都被处理过。

        返回一个Future，如果超过timeout时间，将会抛出一个`tornado.gen.TimeoutError`。


#### PriorityQueue

- `tornado.queues.PriorityQueue(maxsize=0)`

    一个`Queue`以优先级顺序取出entires，低优先级的entries会先取出。

    entries类似于元组`(priority number, data)`

    ```python
    from tornado.queues import PriorityQueue

    q = PriorityQueue()
    q.put((1, "medium-priority item"))
    q.put((0, "high-priority item"))
    q.put((10, "low-priority item"))

    print(q.get_nowait())
    print(q.get_nowait())
    print(q.get_nowait())
    ```

    结果为：

    ```python
    (0, 'high-priority item')
    (1, 'medium-priority item')
    (10, 'low-priority item')
    ```

#### LifoQueue

- `tornado.queues.LifoQueue(maxsize=0)`

    一个`Queue`，最近放入的item将会优先取出(即`栈结构`)。

    ```python
    from tornado.queue import LifoQueue

    q = LifoQueue()
    q.put(3)
    q.put(2)
    q.put(1)

    print(q.get_nowait())
    print(q.get_nowait())
    print(q.get_nowait())
    ```

    结果为:

    ```python
    1
    2
    3
    ```

### 异常

#### QueueEmpty

- `tornado.queues.QueueEmpty`

    在队列中没有item时，调用`Queue.get_nowait()`，将会抛出这个异常。

#### QueueFull

- `tornado.queues.QueueFull`

    在队列中满了的时候，调用`Queue.put_nowait()`，将会抛出这个异常。
