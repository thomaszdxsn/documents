## tornado.tcpclient - IOStream连接工厂

一个非堵塞的TCP连接工厂。

- `tornado.tcpclient.TCPClient(resolver=None, io_loop=None)`

    一个非堵塞的TCP连接工厂。

    - `connect(host, port, af=<AddressFamily.AF_UNSPEC:0>, ssl_options=None, max_buffer_size=None, source_ip=None, source_port=None)`

        连接给定的host和port。

        异步性的返回一个`IOStream`(如果`ssl_options`不为`None`则返回`SSLIOStream`)

        使用`source_ip`关键字参数，它可以设定连接建立的源IP地址。如果用户需要解析和使用一个特殊的接口可以使用这个参数。

        同样的，我们可以让用户设定一个源短空，通过关键字参数`source_port`来实现。

        