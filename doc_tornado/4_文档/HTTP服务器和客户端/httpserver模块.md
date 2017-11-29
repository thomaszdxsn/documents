## tornado.httpserver -- 非堵塞HTTP服务器

一个非堵塞，单线程HTTP服务器。

一般的应用都只有一点代码直接与`HTTPServer`类交互，包括启动服务器。

### HTTP服务器

- `tornado.httpserver.HTTPServer(*args, **kwargs)`

    一个非堵塞，单线程HTTP服务器。

    这个服务器定义为`HTTPServerConnectionDelegate`的子类。或者说，处于向后兼容的原因，将会有一个接收`HTTPServerRequest`请求作为参数的callback。delegate通常是指`tornado.web.Application`。

    `HTTPServer`默认支持`keep-alive`连接(HTTP/1.1这是默认值，对于HTTP/1.0需要客户端请求带上头部`Connection: keep-alive`)。

    如果在构造器传入`xheaders=True`，我们支持`X-Real-Ip/X-Forwarded-For`和`X-Scheme/X-Forwarded-Proto`头部，它会将所有请求的远端IP和URI协议覆盖。如果Tornado运行在一个反向代理或者负载均衡器后面时，这个头部会非常有用。

    默认情况下，当解析`X-Forwarded-For`头部时，Tornado将会选择列表中最后(即最近)的一个地址当作远端IP地址。想要在链条中选择下一个服务器，一个**信赖的**下游(downstream)host列表可以传入`trusted_downstream`参数。当解析`X-Forwarded-For`头部时将会跳过这些host。

    想要让这个服务器伺服SSL流量，将一个`ssl.SSlContext`参数以`ssl_options`关键字参数的形式传入。为了兼容旧版本的Python,`ssl_options`也可以传入关键字参数字典(`ssl.wrap_socket`方法)：

    ```python
    ssl_ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ssl_ctx.load_cert_chain(os.path.join(data_dir, "mydomain.crt"),
                            os.path.join(data_dir, "mydomain.key"))
    HTTPServer(application, ssl_options=ssl_ctx)
    ```

    HTTPServer的初始化有3种模式(初始化方法定义在`tornado.tcpsever.TCPServer`中):

    1. `listen`: 简单的单进程

        ```python
        server = HTTPServer(app)
        server.listen(8888)
        IOLoop.current().start()
        ```

        在多数情况下，`tornado.web.Application.listen()`可以用来避免显式创建`HTTPServer`。

    2. `bind/start`：简单的多进程

        ```python
        server = HTTPServer(app)
        server.bind(8888)
        server.start(0)         # 岔(fork)出多个子进程
        IOLoop.current().start()
        ```

        当使用这个接口时，`IOLoop`不要传入到`HTTPServer`构造器中。单个IOLoop的`start()`方法会总是启动这个服务器。

    3. `add_sockets`: 高级多进程

        ```python
        sockets = tornado.netutil.bind_sockets(8888)
        tornado.process.fork_processes(0)
        server = HTTPServer(app)
        server.add_sockets(sockets)
        IOLoop.current().start()
        ```

        `add_sockets()`接口会更加复杂，但是它可以使用`tornado.process. fork_processes()`来更加灵活的fork。如果你像让监听的sockets有些地方不同于`tornado.netutil.bind_sockets()`，`add_sockets()`也可以用于单进程服务器。

    