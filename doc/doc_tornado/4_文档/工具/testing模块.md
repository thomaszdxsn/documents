## tornado.testing 异步代码的单元测试

用于自动化测试的类：

- `AsyncTestCase`和`AsyncHTTPTestCase`：unittest的子类。`TestCase`被重写，支持了异步代码的测试(基于IOLoop)。
- `ExpectLog`和`LogTrapTestCase`: 让测试日志少点废话.
- `main()`: 一个简单的测试runner(封装了`unittest.main()`)，支持Tornado的autoreload模块，在代码改动时运行测试。

### 异步test-cases

- `tornado.testing.AsyncTestCase(methodName='runTest')`
    
    `TestCase`的子类，用于以`IOLoop`为基础代码的测试。

    unittest框架是同步的，所以测试只有在测试方法返回的时候才会结束，这意味着异步代码不能使用通常的方式来进行测试。想要测试的函数通常可以使用和`tornado.gen`模块相同`yield`模式语法，应该将你的测试方法使用`@tornado.testing.gen_test`替代`@gen.coroutine`来装饰。这个类同样提供了`stop()`和`wait()`方法，用于支持更多人工控制风格的测试。这个测试方法本身必须调用`self.wait()`，异步回调应该调用`self.stop()`来发出结束型号。

    默认情况下，每个测试都会构建一个新的IOLoop，可以通过`self.io_loop`来获取。这个`IOLooop`可以用来构建HTTP客户端／服务器，等等。如果测试代码需要使用一个全局的IOLoop，子类必须重写`get_new_ioloop`来返回它。

    IOLoop的`start`, `stop`不应该直接调用。应该使用`self.stop`, `self.wait`来替代。参数传入`self.stop`，最后将会由`self.wait`返回。在一个测试中可以有多个`wati/stop`循环。

    例子：

    ```python
    # 这个测试使用异步风格
    class MyTestCase(AsyncTestCase):
        @tornado.testing.gen_test
        def test_http_fetch(self):
            client = AsyncHTTPClient(self.io_loop)
            response = yield client.fetch("http://www.tornadoweb.org")
            self.assertIn("FriendFeed", response.body)
        
    
    # 这个测试使用self.stop及self.wait之间传递的参数
    class MyTestCase2(AsyncTestCase):
        def test_http_fetch(self):
            client = AsyncHTTPClient(self.io_loop)
            client.fetch("http://www.tornadoweb.org/", self.stop) response = self.wait()
            # 对response的测试代码
            self.assertIn("FriendFeed", response.body)

    
    # 这个测试使用显式的callback风格
    class MyTestCase3(AsyncTestCase):
        def test_http_fetch(self):
            client = AsyncHTTPClient(self.io_loop)
            client.fetch("http://www.tornadoweb.org/", self.handle_fetch)
            self.wait()

        def handle_fetch(self, response):
            # 在这里写response的测试代码
            # (这里的错误和异常，将会让测试结束，并让self.wait抛出异常)
            # 这里抛出的异常会使用StackException黑魔法，将它传播到
            # test_http_fetch()中的self.wait()
            self.assertIn("FriendFeed", response.body)
            self.stop() 
    ```

    - `get_new_loop()`

        为这个测试创建一个新的`IOLoop`。如果测试需要一个特定的IOLoop，可以重写这个方法(通常使用单例`IOLoop.instance()`)

    - `stop(_arg=None, **kwargs)`

        将`IOLoop`停止，提起一个pending(或future), 让`wait()`方法可以返回。

        传入到`stop()`的关键字参数，或者单个位置参数将会被保存，并由`wait()`返回。

    - `wait(condition=None, timeout=None)`

        运行IOLoop，直到调用了`stop()`，或者传入的timeout超时。

        在超时的情况中，将会抛出一个异常。默认的超时是5秒；可以通过timeout参数或者全局环境变量`ASYNC_TEST_TIMEOUT`来覆盖这个值。

        如果`condition`为None，IOLoop将会在`stop()`之后重启，直到`condition()`返回True为止。

    
- `tornado.testing.AsyncHTTPTestCase(methodName='runTest')`

    将会启动一个HTTP Server的test-case。

    子类必须重写`get_app()`，这个方法必须返回一个用于测试的`tornado.web.Application`(或者其它HTTPServer callback)。测试一般使用提供的`self.http_client`来从这个服务器获取URL。

    使用“Hello World”的demo作为例子：

    ```python
    import hello


    class TestHelloApp(AsyncHTTPTestCase):
        def get_app(self):
            return hello.make_app()

        def test_homepage(self):
            response = self.fetch('/')
            self.assertEqual(response.code, 200)
            self.assertEqual(response.bdoy, 'Hello, world')
    ```

    `self.fetch()`的调用等同于：

    ```python
    self.http_client.fetch(self.get_url('/'), self.stop)
    response = self.wait()
    ```

    这个例子解释了如何使用将AsyncTestCase转换为异步操作，如`http_client.fetch()`，转换成同步操作。如果你需要在测试中做一些其它的异步操作，你可能需要自己调用`wait()`和`stop()`。

    - `get_app()`

        应该在子类中继承，返回一个`tornado.web.Application`或者其它`HTTPServer`可调用对象。

    - `fetch(path, **kwargs)`

        使用同步语法来异步获取url的方便方法。

        给定的path将会追加到当前服务器的host和port后面。任何额外的kwargs将会直接传入到`AsyncHTTPClient.fetch`(比如`method="POST", body="..."`)

    - `get_httpserver_options()`

        可以在子类中重写，返回用于server的参数。

    - `get_http_port()`

        返回server使用的端口。

        每个测试使用一个新的端口。

    - `get_url(path)`

        返回测试服务器给定path的绝对路径url。


- `tornado.testing.AsyncHTTPTestCase(methodName='runTest')`

    一个开启HTTPS服务器的test-case。

    接口大致和`AsyncHTTPTestCase`一样。

    - `get_ssl_options()`

        可以在子类中重写，来选择一个SSL。

        默认包含一个自签名(self-signed)的测试证书。


- `tornado.testing.gen_test(func=None, timeout=None)`

    测试中`@gen.coroutine`的等价物，用于测试方法。

    `@gen.coroutine`不能用于测试，因为`IOLoop`当前并没有运行。`@gen_test`应该用于`AsyncTestCase`子类的方法。

    例子：

    ```python
    class MyTest(AsyncHTTPTestCase):
        @gen_test
        def test_something(self):
            response = yield gen.Task(self.fetch('/'))
    ```

    默认情况下，`@gen.test`的超时时间是5秒，但是可以通过关键字参数`timeout`和环境变量`ASYNC_TEST_TIMEOUT`来重写：

    ```python
    class MyTest(AsyncHTTPTestCase):
        @gen_test(timeout=10)
        def test_something_slow(self):
            response = yield gen.Task(self.fetch('/'))
    ```


### 控制输出日志

- `tornado.testing.ExPectLog(logger, regex, required=True)`

    上下文管理器，用来捕获和阻止意料中的日志输出。

    想让测试的错误条件少罗嗦点就很有用，这个方法仍然会让未意料的日志实体可见。另外这个方法不是线程安全的。

    如果日志中有任何stack回溯信息，需要把`logged_stack`设置为True。

    用法：

    ```python
    with ExpectLog("tornado.application", "Uncaught expection"):
        error_response = self.fetch('/some_page")
    ```

    参数：

    - `logger`: 想要观察的纪录器(logger)对象(或者记录器的名称)。如果传入空字符串，将会观察根logger。

    - `regex`: 想要观察的正则表达式。任何匹配这个正则表达式的logger实体都会被阻止。

    - `required`: 如果为True，如果with代码块结束还没有阻止任何日志，则抛出一个异常。


- `tornado.testing.LogTrapTestCase(methodName='runTest')`

    如果测试通过，捕获并丢弃所有日志输出的一个test-case。

    一些库即使测试通过仍然会输出一大堆日志，所以这个类可以最小化输出的啰嗦程度。只需简单地继承这个类，也可以将它组合`AsyncTestCase`来多重继承。

    这个类假定只配置了一个log handler，即`StreamHandler`。并不兼容于其它日志缓冲机制。


### Test Runner

- `tornado.testing.main(**kwargs)`

    一个简单的测试runner。

    这个test runner本质上等同于标准库的`unittest.main`，但是支持一些额外的tornado风格option解析及日志格式。但是在使用类似`AsyncTestCase`时并不一定要使用这个`main()`函数；这些test-case是自满足的，可以用于任何test-runner。

    最简单地运行一个test的方式即通过命令行：

    `python -m tornado.testing tornado.test.stack_context_test`

    一个包含众多测试的项目，可能需要定义一个脚本，比如`tornado/test/runtests.py`。这个脚本需要定义一个方法`all()`,它会定义一个`test-suite`，然后调用`main()`。注意即使定义了这个test脚本，仍然可以通过命令行来运行单个测试：

    ```python
    # 运行所有的测试
    python -m tornado.test.runtests

    # 运行单个测试
    python -m tornado.test.runtests tornado.test.stack_context_test
    ```

### 助手函数

- `tornado.testing.bind_unused_port(reuse_port=False)`

    将本机一个可获取的port和一个server socket绑定。

    返回一个元组(socket, port)

- `tornado.testing.get_unused_port()`

    返回一个(但愿)未使用的port。

    这个函数并不保证返回的端口是可用的。

- `tornado.testing.get_async_test_timeout()`

    获取异步测试的全局timeout设置。

    返回一个浮点数，即超时的秒数。




    
