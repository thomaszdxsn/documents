## tornado.iostream -- 非堵塞sockets方便的封装

工具类，对非堵塞的文件及socket中进行读写操作。

内容：

- `BaseIOStream`: 读／写的通用接口
- `IOStream`: 使用非堵塞socket实现`BaseIOStream`
- `SSLIOStream`: SSL版本的`IOStream`
- `PipeIOStream`: 以管道为基础的`IOStream`实现

### 基类

- `tornado.iostream.BaseIOStream(io_loop=None, max_buffer_size=None, read_chunk_size=None, max_write_buffer_size=None)`

    一个工具类，对非堵塞的文件及socket中进行读写操作。

    我们支持一个非堵塞的`write()`方法以及`read_*()`家族方法。所有的方法都可以接受一个可选的callback参数，如果没有传入callback参数的话，它们就会返回一个`Future`对象。当操作完成后，`callback`将会运行，或者`Future`将会被读取。当i/o流结束后，所有单独的`Future`都会解析为`StreamClosedError`；使用callback需要注意这个接口：`BaseIOStream.set_close_callback`。

    当一个stream因为抛出错误而关闭，这个`IOStream`的`.error`属性将会包含这个异常对象。

    继承这个类，必须实现`fileno`, `close_fd`, `write_to_fd`, `read_from_fd`，以及一个可选的方法`get_fd_error`。

    `BaseIOStream`的构造器：

    **参数**

    - `io_loop`: 使用的`IOLoop`对象；默认为`IOLoop.current`
    - `max_buffer_size`: (读取)数据的内存缓冲区最大值；默认为100MB。
    - `read_chunk_size`: 在底层传输时，一次性读取的数据总量；默认为64KB。
    - `max_write_buffer_size`: (写出)数据的内存缓冲区最大值；默认无限制。

### 主要接口

- `BaseIOStream.write(data, callback=None)`

    将给定到这个stream的数据异步写入。

    如果给定了`callback`，我们在将所有缓冲的数据写入到stream以后调用这个callback。

    如果没有给定`callback`，这个方法会返回一个`Future`，并等待数据写入完成后解析它。

    `data`参数的类型必须是`byte`或者`memoryview`。

- `BaseIOStream.read_bytes(num_bytes, callback=None, streamning_callback=None, partial=False)`

    异步读取一个`num_bytes`数量的bytes。

    如果给定了一个`streaming_callback`，在一个数据chunk可获取时即调用这个callback，最后的结果应该为空。否则，结果就是读取的总数据。如果`callback`给定，它会把这个data作为参数来运行，如果没有给定，返回一个`Future`。

    如果`partial=True`，我们返回任意数量(但不能超过`num_bytes`)的bytes都会调用`callback`。

- `BaseIOStream.read_until(delimiter, callback=None, max_bytes=None)`

    异步读取，直到我们找到给定的分隔符。

    结果包含读取的数据及分隔符。如果给定一个callback，它会通过一个data参数来调用；否则返回一个`Future`。

    如果`max_bytes`不是`None`，那么如果读取的数据超过了`max_bytes`仍然没有找到分隔符，连接仍然会关闭。

- `BaseIOStream.read_until_regex(regex, callback=None, max_bytes=None)`

    异步读取，直到匹配给定的正则表达式。

    结果包含读取的数据及匹配部分。如果给定一个callback，它会通过一个data参数来调用；否则返回一个`Future`。

    如果`max_bytes`不是`None`，那么如果读取的数据超过了`max_bytes`仍然没有找到匹配，连接仍然会关闭。

- `BaseIOStream.read_until_close(callback=None, streaming_callback=None)`

    从socket异步读取所有数据，直到它关闭。

    如果给定了一个`streaming_callback`，在一个数据chunk可获取时即调用这个callback，最后的结果应该为空。否则，结果就是读取的总数据。如果`callback`给定，它会把这个data作为参数来运行，如果没有给定，返回一个`Future`。

    注意，如果使用了`streaming_callback`，那么只要socket的数据可以获取就会立即被读取；没有方法可以取消这次读取；如果需要控制流程或者取消，应该使用`read_bytes(partial=True)`方法。

- `BaseIOStream.close(exc_info=False)`

    关闭这个stream。

    如果`exc_info=True`，将来自于`sys.exc_info`的当前异常信息赋值为`.errro`属性。

- `BaseIOStream.set_close_callback(callback)`

    在stream关闭后调用给定的callback。

- `BaseIOStream.closed()`

    如果stream已经关闭，返回True。

- `BaseIOStream.reading()`

    如果我们正从stream中读取数据，返回True。

- `BaseIOStream.writing()`

    如果我们正往stream中写入数据，返回True。

- `BaseIOStream.set_nodelay(value)`

    对这个stream设置不延时(no-delay)标志。

    默认情况下，写入TCP流中的数据一般会延时等待更多的数据一起发送，可以有效节省带宽(根据**Nagle**算法)。不延时标志意思就是让写入尽快进行，即使可能会消耗额外的带宽。

    这个标志(flag)目前只支持在以TCP协议为基础的`IOStream`上面设置。

### 用于继承的方法

- `BaseIOStream.fileno()`

    返回这个stream的文件描述符。

- `BaseIOStream.close_fd()`

    关闭这个stream底层的文件。

    `close_fd()`方法在`BaseIOStream`内部调用，不应该使用在其它地方；其它的情况应该调用`close()`。

- `BaseIOStream.write_to_fd(data)`

    尝试将`data`写入到底层文件。

    返回写入的bytes总数。

- `BaseIOStream.read_from_fd()`

    尝试从底层文件读取。

    如果没有读取到任何东西(socket返回`EWOULDBLOCK`或者类似的常量)，返回None。否则返回(读取的)数据。一般一次性应该不会读取超过`self.read_chunk_size`数量的数据。

- `BaseIOStream.get_fd_error()`

    在底层文件存在任何错误，都会返回相关信息。

    这个方法在`IOLoop`的信息系统调用，应该会返回一个异常对象。

### 实现

- `tornado.iostream.IOStream(socket, *args, **kwargs)`

    以socket为基础的`IOStream`实现。

    这个类支持`BaseIOStream`的读／写方法，外加一个`connect()`方法。

    `socket`参数可以是一个已连接或未连接的socket对象。对于服务器端的操作，socket的结果通过调用`socket.accept()`来获取。客户端通过`socket.socket`创建socket，可以在传入`IOStream`或者使用`IOStream.connect()`之前就连接起来。

    一个使用这个类实现的简单的HTTP客户端：

    ```python
    import tornado.ioloop
    import tornado.iostream
    import socket


    def send_request(stream):
        stream.write(b"GET / HTTP/1.0\r\nHost: friendfeed.com\r\n\r\n")
        stream.read_until(b"\r\n\r\n", on_headers)

    
    def on_headers(data):
        headers = []
        for line in data.split(b\"\r\n"):
            parts = line.split(b":")
            if len(parts) == 2:
                headers[parts[0].strip()] = parts[1].strip()
        stream.read_bytes(int(headers[b"Content-Length"]), on_body)

    def on_body(data):
        print(data)
        stream.close()
        tornado.ioloop.IOLoop.current().stop()

    if __name__ = '__main__':
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        stream = tornado.iostream.IOStream(s)
        stream.connect(("friendfeed.com", 80), send_request)
        tornado.ioloop.IOLoop.current().start()
    ```

    - `connect(address, callback=None, server_hostname=None)`

        非堵塞的连接到一个远程地址的socket。

        在传入构造器的socket之前没有连接的情况下，才调用这个方法。`address`参数的格式和`socket.connect`一样，也就是`(ip, port)`元组。这里可以接受hostname，但是它会同步解析并且堵塞IOLoop。如果你需要使用hostname，那么推荐使用`TCPClient`，这个类有一个异步DNS解析器，可以处理IPv4和IPv6。

        如果给定了`callback`参数，它会在连接完成以后无参数的调用;如果没有给定这个参数，最后会返回一个`Future`对象。

        在SSL模式下，`server_hostname`将会进行证书确认(除非禁用`ssl_options`)以及SNI。

        注意，在连接待定状态下仍然可以调用`IOStream.write()`，只要连接准备好这个调用会立即将数据写入。

    - `start_tls(server_side, ssl_options=None, server_hostname=None)`

        将一个`IOStream`转换为一个`SSLIOStream`。


- `tornado.iostream.SSLIOStream(*args, **kwargs)`

    一个工具类，可以对一个SSL socket进行非堵塞读写操作。

    如果传入到这个构造器的socket已经连接，它应该这样被封装起来：

    ```python
    ssl.wrap_socket(sock, do_handshake_on_connection=False, **kwargs)
    ```

    在构建`SSLIOStrem`之前。未连接的socket将会被封装。

    `ssl_options`关键字参数可以是一个`ssl.SSLContext`对象或者一个用于`ssl.wrap_socket`的关键字参数字典。

    - `wait_for_handshake(callback=None)`

        等待初始SSL握手完成。

        如果给定一个callback，它会以无参数形式来调用；否则返回一个`Future`。

        一旦握手完成，可以通过访问`self.socket`获取peer证书以及NPN/ALPN的选择。

        这个方法，应该在服务器端使用`IOStream.start_tls`之后调用。

- `tornado.iostream.PipeIOStream(fd, *args, **kwargs)`

    一个Pipe为基础的`IOStream`实现。

    这个类的构造器接受一个整数型文件描述符(比如通过`os.pipe`返回的整数)，但不能接受文件对象。`Pipe`是单向的，所以一个`PipeIOStream`一次只可以进行读或者写，而不能同时进行。

### 异常

- `tornado.iostream.StreamBufferFullError`

    当缓冲区满了以后，`IOStream`的方法抛出的异常

- `tornado.iostream.StreamClosedError(real_error=None)`

    当一个stream关闭后，`IOStream`的方法抛出的异常。

    但是如果你在一个callback中看到这个错误，其实是正常情况(因为是callback)。

    `real_error`属性包含引起stream关闭的底层错误(如果存在)。

- `tornado.iostream.UnsatisfiableReadError`

    在读取不能被满足的情况下抛出的异常。

    在`read_until`, `read_until_regex`携带`max_bytes`参数的情况下抛出的异常。

