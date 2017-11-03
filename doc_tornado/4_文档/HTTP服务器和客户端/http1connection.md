## tornado.http1connection - HTTP/1.x client/server 实现

HTTP/1.x的客户端和服务器实现。

- `tornado.http1connection.HTTP1ConnectionParameters(no_keep_alive=False, chunk_size=None, max_header_size=None, header_timeout=None, max_body_size=None, body_timeout=None, decompress=False)`

    `HTTP1Connection`和`HTTP1ServerConnection`的参数：

    参数：

    - `no_keep_alive`(布尔值): 如果为True，在一个请求后总是会关闭连接。

    - `chunk_size`(整数): 一次为内存读入多少数据。

    - `max_header_size`(整数): HTTP头部数据的最大值。

    - `header_timeout`(浮点数): 所有头部等待的最长时间(秒数)。

    - `max_body_size`(整数): body数据的最大值。

    - `body_timeout`(浮点数): 在body读取时等待的最长时间(秒数)

    - `decompress`(布尔值): 如果为True，将`Content-Encoding: gzip`解码。


- `tornado.http1connection.HTTP1Conntion(stream, is_client, params=None, context=None)`

    实现HTTP/1.x协议。

    这个类可以用于客户端，或者通过`HTTP1ServerConnection`用于服务器。

    参数：

    - `stream`: 一个`IOStream`
    - `is_client`(布尔值): 代表客户端或者服务器。
    - `params`: 一个`HTTP1ConnectionParameter`实例或者`None`。
    - `context`: 一个不透明的app定义的对象，可以通过`connection.context`来访问。

    方法：

    - `read_response(delegate)`

        读取单个HTTP Response。

        通常客户端模型写一个request的用法是使用`write_headers`, `write`以及`finish`，然后调用`read_response`。

        参数:

        - `delegate`: 一个`HTTPMessageDelegate`

    - `set_close_callback(callback)`

        设置一个在连接关闭后调用的callback。

        在Tornado4.0以后被弃用：使用`HTTPMessageDelegate.on_connection_close()`方法.

    - `detach()`

        控制底层的流。

        返回一个底层的`IOStream`对象，并且停止所有进一步的HTTP处理。应该只在`HTTPMessageDelegate.headers_received`运行期间调用。

    - `set_body_timeout(timeout)`

        对单个请求设置body超时。

        通过`HTTP1ConnectionParameters`来覆盖这个值。

    - `set_max_body_size(max_body_size)`

        对单个请求设置body大小的限制。

        通过`HTTP1ConnectionParameters`来覆盖这个值。

    - `write_headers(start_line, headers, chunk=None, callback=None)`

        实现`HTTPConnection.write_headers`。

    - `write(chunk, callback=None)`

        实现`HTTPCollection.write`。

        处于向后兼容的原因，可以跳过调用`write_headers`而直接使用`write()`以及一些预先定义的头部块。

    - `finish()`

        实现`HTTPConnection.finish()`

- `tornado.http1connection.HTTP1ServerConnection(stream, params=None, connect=None)`

    一个HTTP/1.x服务器。

    参数：

    - `stream`: 一个`IOStream`。

    - `params`: 一个`HTTP1ConnectionParamters`或者`None`。

    - `context`: - `context`: 一个不透明的app定义的对象，可以通过`connection.context`来访问。

    方法：

    - `close()`

        关闭连接。

        返回一个`Future`，在伺服的loop退出后完成关闭。

    - `start_serving(delegate)`

        通过这个连接来开始伺服请求。

        参数:

        - `delegate`: 一个`HTTPServerConnectionDelegate`对象