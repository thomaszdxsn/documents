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


## tornado.platform.caresresolver -- 使用C-ares的异步DNS解析

这个模块使用（c-ares)库实现了DNS解析(封装了`pycares`)

- `python.platform.caresresolver.CaresResolver`

    根据c-ares库建立的域名解析器．

    这是一个非堵塞和非线程的解析器．它可能生成的结果和系统解析器不一样，但是当线程不可用时，可以使用这个它做非堵塞的解析方法．

    如果域名的`family`是`AF_UNSPEC`，c-ares将会失败，所以只推荐使用`AF_INET`(即IPv4)．这是`tornado.simple_httpclient`的默认行为，但是其它库可能仍然使用`AF_UNSPEC`．


## tornado.platform.twisted -- 桥接twisted和tornado

桥接Twisted reactor 和 Tornado IOLoop．

这个模块让你可以运行Twisted和Tornado代码写的应用．可以有两种使用方式，取决与你想使用哪个框架的事件循环．

### 在Tornado上面运行Twisted

- `tornado.platform.twisted.TornadoReactor(io_loop=None)`

    建立在Tornado IOLoop上面的Twisted Reactor。

    `TornadoReactor`在Tornado IOLoop的基础上实现了Twisted Reactor的接口。想要使用它，是需要在应用的开始调用`install`。

    ```python
    import tornado.platform.twisted
    tornado.platform.twisted.install()
    from twisted.iternet import reactor
    ```

    当应用准备启动时，使用`IOLoop.current().start()`来代替`reactor.run()`

    可以通过调用`tornado.platform.twisted.TornadoReactor(io_loop)`来创建一个非全局的reactor。但是，如果`IOLoop`和`reactor`存活时间过短(比如用于单元测试)，需要一些额外的清理工作。

    一般推荐这样清理(在关闭IOLoop之前):

    ```python
    reactor.fireSystemEvent("shutdown")
    reactor.disconnectAll()
    ```

- `tornado.platform.twisted.install(io_loop=None)`

    安装这个包当作默认的Twisted reactor。

    `install()`必须在非常早的起始阶段调用，在import其它关联twisted模块之前调用。但是相反的，因为它会初始化IOLoop,所以不能在`fork_processes`或者多进程`start`之前调用。所以多进程模式很难结合使用TornadoReactor，推荐使用外部进程管理器，如`supervisord`。

###　在Ｔwisted上面使用Tornado

- `tornaod.platform.twisted.TwistedIOLoop`

    实现运行于Twisted的IOLoop．

    `TwistedLoop`基于Twisted　reactor实现了Tornado IOLoop接口．

    例子：

    ```python
    from tornado.platform.twisted import TwistedIOLoop
    from twsited.internet import reactor
    TwistedIOLoop().install()
    # 编写你的Tornado代码，就像平常使用＂IOLoop.instance＂一样
    reactor.run()
    ```

    默认使用全局Twisted reactor．想要早同个进程创建多个`TwistedIOLoops`，你需要在每次创建时传入不同的reactor.

    不兼容信号`tornado.process.Subprocess.set_exit_callback`，因为`SIGCHLD`处理器在Ｔｗｉｓｔｅｄ和Ｔｏｒｎａｄｏ　中相冲突．

### Twisted DNS解析器

基于Twisted的异步DNS解析器

这是一个非堵塞，非线程的DNS解析器．只有在线程不可用时推荐使用它，因为它相比标准的`getaddrinfo`有若干限制．特别是，它的结果只有一个，非host和family的结果将会被忽略．如果family为`socket.AF_UNSPEC`的话，将会失败．