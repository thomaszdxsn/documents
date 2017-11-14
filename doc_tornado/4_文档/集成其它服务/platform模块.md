## tornado.platform.asyncio -- 桥接asyncio和tornado

桥接`asyncio`模块和Tornado的IOLoop．


这个模块集成了Tornado和asyncio模块．可以让两个库运行在同一个事件循环中．

多数应用应该使用`asyncio`的`AsyncIOMainLoop`模块来运行Tornado．如果需要在多线程中运行事件循环，可以使用`AsyncIOLoop`来创建多个循环．

> 注意
>
>> Tornado要求`add_reader`家族方法，所以和Windows上面的`ProactorEventLoop`不兼容．请使用`SelectorEventLoop`来替代．

- `tornado.platform.asyncio.AsyncIOMainLoop`

    `AsyncIOMainLoop`创建一个符合当前`asyncio`事件循环的`IOLoop`．

    ```python
    from tornado.platform.asyncio import AsyncIOMainLoop
    import asyncio

    AsyncIOMainLoop().install()
    asyncio.get_event_loop().run_forever()
    ```

- `tornado.platform.asyncio.AsyncIOLoop`

    `AsyncIOLoop`是一个运行在asyncio事件循环上面的`IOLoop`．这个类使用通常的Tornado语义来创建一个新的`IOLoop`；这些类不需要关键`asyncio`的默认事件循环．推荐用法:

    ```python
    from tornado.ioloop import IOLoop
    IOLoop.configure("tornado.platform.asyncio.AsyncIOLoop")
    IOLoop.current().start()
    ```

- `tornado.platform.asyncio.to_tornado.future`

    将一个`asyncio.Future`转换成一个`tornado.concurrent.Future`．

- `tornado.platform.asyncio.to_asyncio_future`

    将一个Tornado可yield对象，转换为asyncio的Future．

    