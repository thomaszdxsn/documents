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

        pass