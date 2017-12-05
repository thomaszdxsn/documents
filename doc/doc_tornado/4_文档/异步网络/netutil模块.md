## tornado.netutil -- 其它网络实用工具

其它混杂的网络工具代码。

- `tornado.netutil.bind_sockets(port, address=None, family=<AddressFamily.AF_UNSPEC: 0>, backlog=128, flags=None, reuse_port=False)`

    通过给定的port和address创建一个sockets监听。

    返回一个socket对象列表(如果给定了多个IP／端口对则返回多个对象，IP可以使用IPv4和IPv6)

    `address`可以是IP地址或者主机名。如果是一个主机名，将会监听所有绑定这个主机名的IP。`address`可以设置一个空字符串或者`None`，用来监听所有的可获取接口。
    
    可以通过设置`family`参数为`socket.AF_NET`或者`socket.AF_INET6`来限制IPv4或者IPv6，否则两者都将被使用。

    `backlog`和`socket.listen()`相同。

    `flag`是`getaddrinfo`的一个常量，比如`socket.AI_PASSIVE`或者`socket.NUMERICHOST`.

    `reuse_port`可以为列表中的每个socket对象设置`SO_REUSEPORT`。如果你的操作系统不支持这个设置，将会抛出一个`ValueError`.

- `tornado.netutil.bind_unix_socket(file, mode=384, backlog=128)`

    创建一个监听中的unix socket。

    如果给定名称的socket已经存在，将会把它删除。如果有其它文件使用了这个名词，将会抛出一个异常。

    返回一个socket对象(和`bind_sockets`不一样，这个函数不能返回多个值)。

- `tornado.netutil.add_accept_handler(sock, callback, io_loop=None)`

    增加一个新的`IOLoop`事件handler，可以在sock上面接受新的连接。

    当一个连接接收时，将会运行`callback(connection, address)`(connection是一个socket对象，address是连接另一端的地址)。注意这个函数的签名和`IOLoop`handler中的`callback(fd, events)`的区别。

- `tornado.netutil.is_valid_ip(ip)`

    如果给定的`ip`是一个合法的IP地址，返回True。

    支持IPv4和IPv6.

- `tornado.netutil.Resolver`

    配置异步DNS解析接口。

    默认情况下，会使用一个堵塞形式的接口实现(它只会简单的调用`socket.getaddrinfo`).一个替代选择时选择使用类方法`Resolver.configure`：

    `Resolver.configure("tornado.netutil.ThreadResolver')`

    Tornado中的DNS解析接口包含：

    - `tornado.netutil.BlockingResolver`
    - `tornado.netutil.ThreadedResolver`
    - `tornado.netutil.OverrideResolver`
    - `tornado.platform.twisted.TwistedResolver`
    - `tornado.platform.caresresolver.CaresResolver`

    - `resolve(host, port, family=<AddressFamily.AF_UNSPEC:0>, callback=None)`

        解析一个地址。

        `host`参数是一个字符串，可以是一个主机名称，或者单纯是一个IP地址。

        返回一个`Future`，如果是IPv4，它的结果为一个`(family, address)`2维元组列表。如果是IPv6，将会包含其它的字段。如果传入一个`callback`，在结束后将会把结果作为参数传递给callback运行。

        异常: `IOError` - 如果地址不能被解析则抛出。

    - `close()`

        关闭这个`Resolver`，释放它使用的资源。

- `tornado.netutil.ExecutorResolver`

    使用`concurrent.futures.Executor`实现的`Resolver`。

    如果你需要对executor记性额外的控制，使用这个类来替代`ThreadResolver`。

    当Resolver对象关闭时，这个executor也会关闭，除非设置了`close_resolver=False`；如果你想在其它地方继续使用这个executor，那么需要传入这个参数。

- `tornado.netutil.BlockingResolver`

    默认的`Resolver`的接口实现，使用`socket.getaddrinfo`

    在解析过程中，IOLoop将会被堵塞，直到下次IOLoop迭代前这个callback都不会被调用。

- `tornado.netutil.ThreadResolver`

    多线程的非堵塞`Resolver`实现。

    要求安装了`concurrent.futures`包。

    线程池的代销可以配置：

    `Resolver.configure('tornado.netutil.ThreadResolver', num_threads=10)`

- `tornado.netutil.OverrideResolver`

    将一个Resolver和覆盖(override)映射封装在一起。

    可以用来创建一个本地的DNS(测试用途)，而不需要修改系统级别的配置。

    映射可以包含host字符串，或者`(host, port)`元组对。

- `tornado.netutil.ssl_options_to_context(ssl_options)`

    尝试将一个`ssl_options`字典转换为一个`SSLContext`对象。

    `ssl_options`字典将会以关键字参数形式传入到`ssl.wrap_socket`。在Python2.7.9+,会传入到`ssl.SSLContext`.

- `tornado.netutil.ssl_wrap_socket(socket, ssl_options, server_hostname=None, **kwargs)`

    返回一个封装了给定socket的`ssl.SSLSocket`对象。

    


    