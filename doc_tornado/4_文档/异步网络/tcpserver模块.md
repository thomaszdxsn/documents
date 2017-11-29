## tornado.tcpserver -- 以IOStream为基础的TCP服务器

一个非堵塞的，单线程的TCP服务器。

- `tornado.tcpserver.TCPServer(io_loop=None, ssl_options=None, max_buffer_size=None, read_chunk_size=None)`

    一个非堵塞的，单线程的TCP服务器。

    想要使用`TCPServer`，继承这个类并重写`handle_stream`方法。下面是一个简单的echo服务器例子：

    ```python
    from tornado.tcpserver import TCPServer
    from tornado.iostream import StreamClosedError
    from tornado import gen


    class EchoServer(TCPServer)
        @gen.coroutine
        def handle_stream(self, stream, address):
            while True:
                try:
                    data = yield stream.read_until(b"\n")
                    yield steam.write(data)
                except StreamClosedError:
                    break
    ```

    想要让这个服务器伺服SSL流量，可以为`ssl.SSLContext`对象传入`ssl_options`关键字参数。为了适配老版本Python的`ssl_options`，可以为`ssl.wrap_socket`方法传入一个字典参数：

    ```python
    ssl_ctx = ssl.create_default_context(ssl.Purpose.CLIETN_AUTH)
    ssl_ctx.load_cert_chain(os.path.join(data_dir, "mydomain.crt"),
                            os.path.join(data_dir, "mydomain.key"))
    TCPServer(ssl_options=ssl_ctx)
    ```

    `TCPServer`可以通过以下三种模式来初始化：

    1. `listen`：简单的单进程

        ```python
        server = TCPServer()
        server.listen(8888)
        IOLoop.current().start()
        ```

    2. `bind_start`: 简单的多进程

        ```python
        server = TCPServer()
        server.bind(8888)
        server.start(0)
        IOLoop.current().start()
        ```

        当使用这个接口时，`IOLoop`不会传入到`TCPServer`构造器中。`start`将会使用默认的singleton`IOLoop`来开启服务器。

    3. `add_sockets`: 搞起多进程

        ```python
        sockets = bind_sockets(8888)
        tornado.process.fork_processes(0)
        server = TCPServer()
        server.add_sockets(sockets)
        IOLoop.current().start()
        ```

        `add_sockets`接口更加复杂，它可以通过`tornado.process.fork_processes()`来时fork更加弹性，`add_sockets`也可以设置单进程模式。

    **方法**

    - `listen(port, address='')`

        开始在给定的端口上面接收连接。

        如果想要监听多个端口，可以调用这个方法多次。`listen`可以立即生效，没必要再去调用`TCPServer.start`。但是，之后一定要启动`IOLoop`.

    - `add_sockets(sockets)`

        让这个服务器在给定的sockets上面接受连接。

        `sockets`参数是一个socket对象列表，比如`bind_sockets`和`add_sockets`返回的对象。一般讲这个方法和`tornado.process.fork_processes`合并使用来更细腻的控制多进程服务器的初始化。

    - `bind(port, address=None, family=<AddressFamily.AF_UNSPEC: 0>, backlog=128, reuse_port=False)`

        将server绑定给定的端口和给定的地址。

        想要启动这个服务器，需要调用`.start()`。如果你想在单个进程运行这个服务器，那么你只需要调用`.listen()`就可以了。

        `address`可以是一个IP地址或者域名。如果它是一个域名，服务器将会监听所有关联这个域名的IP地址。`address`可以为空或者`None`可以监听所有可获取的接口。`family`参数可以是`socket.AF_INET`或者`socket.AF_INET6`来限制IPv4或者IPv6地址，如果不设置这个参数，将会使用这两种IP地址格式。

        `backlog`参数和`socket.listen()`的意义一样。`reuse_port()`参数和`bind_sockets()`的意义一样。

        如果想要监听多个端口，那么可以调用多次这个端口。

    - `start(num_processes=1)`

        在`IOLoop`中启动这个服务器。

        默认情况下，我们将会在这个进程下面运行这个服务器，不会fork其它的子进程。

        如果`num_proceeses=None`或者`num_processes=0`，我们将会监测当前机器有多少个核心，并且fork这个数量的进程。如果`num_proceeses`的值大于1，那么fork这个指定数量的子进程。

        由于我们使用的是进程而不是线程，所有在服务器代码间没有共享的内存。

        注意多进程并不适用于autoreload模式。当使用多进程时，在调用`TCPServer.start(n)`之前不会创建任何IOLoop或者引用。

    - `stop()`

        停止监听新的连接。

        在服务器停止后，当前进行中的请求仍然会继续执行。

    - `handle_stream(stream, address)`

        重写这个方法，处理一个即将到达的连接新的`IOStream`。

        这个方法可以定义为协程；如果在异步过程中出现任何异常，都会被记录到日志中。这个协程中等待接收即将到达的连接时不会堵塞。

        如果这个TCPServer配置了`SSL`，`handle_stream`将会在SSL握手之前被调用。如果你需要验证客户端的证书或者NPN/ALPN，需要使用`SSLOStream.wait_for_handshake`。

        