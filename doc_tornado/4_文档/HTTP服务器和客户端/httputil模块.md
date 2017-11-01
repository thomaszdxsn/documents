## tornado.httputil -- 操作HTTP头部和URL

包含HTTP客户端和服务器使用的工具代码。

这个模块同样定义了一个`HTTPServerRequest`类，它还有一个大家都属性的引用，即`tornado.web.RequestHandler.request`。

- `tornado.httputil.HTTPHeaders(*args, **kwargs)`

    一个字典，它的所有键都是`Http-Header-Case`。

    通过一对新方法`add()`和`get_list()`来为一个键支持多个值。常规的字典接口一个键只会返回一个值，多个值需要用逗号来拼接。

    ```python
    >>> h = HTTPHeaders({"content-type": "text/html"})
    >>> list(h.keys())
    ['Content-Type']
    >>> h['Content-Type']
    'text/html'
    ```

    ```python
    >>> h.add("Set-Cookie", "A=B")
    >>> h.add("Set-Cookie", "C=D")
    >>> h['set-cookie']
    'A=B, C=D'
    >>> h.get_list("set-cookie')
    ['A=B', 'C=D']
    ```

    ```python
    >>> for (k, v) in sorted(h.get_all()):
    ...     print("%s: %s" %(k, v))
    ...     
    Content-Type: text/html
    Set-Cookie: A=B
    Set-Cookie: C=D
    ```

    - `add(name, value)`

        对给定的键增加一个新的value。

    - `get_list(name)`

        通过给定的头部名称返回所有值，以列表形式返回。

    - `get_all()`

        返回所有(name, value)键值对的一个可迭代对象。

        如果一个头部名称具有多个值，将会以这个同样的名称返回多个键值对。

    - `parse_line(line)`

        通过一个头部行(字符串)更新这个字典。

        ```python
        >>> h = HTTPHeaders()
        >>> h.parse_line('Content-Type: text/html')
        >>> h.get('content-type')
        'text/html'
        ```

    - 类方法`parse(headers)`

        将一个HTTP头部文本解析，并返回一个字典(HTTPHeaders对象)。

        ```python
        >>> h = HTTPHeaders.parse("Content-Type: text/html\r\nContent-Length: 42\r\n")
        >>> sorted(h.items())
        [('Content-Length', '42'), ('Content-Type', 'text/html')]
        ```

- `tornado.httputil.HTTPServerRequest(method=None, uri=None, version='HTTP/1.0', headers=None, body=None, host=None, files=None, connection=None, start_line=None, server_connection=None)`

    一个HTTP请求。

    所有属性类型都是`str`，除非有特别提及。

    - `method`

        HTTP请求方法。比如"GET", "POST"

    - `uri`

        请求的URI

    - `path`

        URI的path部分

    - `query`

        URI的query部分

    - `version`

        请求指定的HTTP版本，比如"HTTP/1.1"

    - `headers`

        用于请求头部的一个类字典对象`HTTPHeaders`。它的键是不区分大小写的，另外为重复的头部增加了额外的方法来使用。

    - `body`

        请求body，如果有值，类型就是byte。

    - `remote_ip`

        客户端IP地址的字符串形式。如果设置了`HTTPServer.xheaders`，我们将会接受负载均衡器通过`X-Real-Ip`或者`X-Forwarded-For`提供的真实IP。

    - `protocol`

        这个请求使用的协议，"http"和"https"二选一。如果设定了`HTTPServer.xheaders`，将会使用负载均衡器提供的`X-Scheme`头部作为协议。

    - `host`

        请求的host名称，通常从头部`Host`中获取。

    - `arguments`

        GET/POST的参数都可以在property`arguments`中获取，它将映射参数名称为一个值列表(用来支持单参数名多个值)。name的类型是`str`，参数为`byte`。注意这里和`RequestHandler.get_argument()`不同，后者的参数总是以unicode字符串形式返回。

    - `query_arguments`

        和`arguments`相同的格式，但是只包含从`query string`提取的参数。

    - `body_arguments`

        和`arguments`相同的格式，但是只包含从`request body`提取的参数。

    - `files`

        上传的文件可以通过property`files`获取，它会映射文件名和一个`HTTPFile`列表。

    - `connection`

        一个HTTP请求绑定一个HTTP连接，它可以通过`.connection`属性来访问。由于在HTTP/1.1中连接一直保持开启，在一个连接中可以连续处理多个请求。

    - `cookies`

        一个`Cookie.Morsel`对象的字典。

    - `write(chunk, callback=None)`

        将给定的数据段(chunk)写入到response流(stream)中。

        在v4.0以后弃用：使用`request.connection`和`HTTPConnection`方法来写入response。

    - `finish()`

        在一个开启的连接中结束这个HTTP请求。

        在v4.0以后弃用：使用`request.connection`和`HTTPConnection`方法来写入response。

    - `full_url`

        重构这个请求的完整URL。

    - `request_time`

        返回这个请求执行的总时间。

    - `get_ssl_certificate(binary_form=False)`

        如果存在，返回客户端的SSL证书。

        要使用客户端证书，HTTPServer的`ssl.SSLContext.verify_mode`字段必须设置:

        ```python
        ssl_ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        ssl_ctx.load_cert_chain("foo.crt", "foo.key")
        ssl_ctx.load_verify_locations("cacerts.pem")
        ssl_ctx.verify_mode = ssl.CERT_REQUIRED
        server = HTTPServer(app, ssl_options=ssl_ctx)
        ```

        默认情况下，返回的值是一个字典(如果没有客户端证书，就返回None)。如果`binary_form=True`，将会返回证书的DER编码形式。

- 异常`tornado.httputil.HTTPInputError`

    碰到来自远端资源的恶意request或者response，将会抛出这个异常。

- 异常`tornado.httputil.HTTPOutputError`

    HTTP输出发生错误时抛出的异常。

- `tornado.httputil.HTTPServerConnectionDelegate`

    实现这个接口，让`HTTPServer`处理请求。

    - `start_request(server_conn, request_conn)`

        在一个新的请求发起时，这个方法会被服务器调用。

        参数：

        - `server_conn`: 一个不透明的对象，代表一个长(tcp级别)连接。
        - `request_conn`: 一个`HTTPConnection`对象，用于单个request/response的交换。

        这个方法应该返回一个`HTTPMessageDelegate`。

    - `on_close(server_conn)`

        在一个连接关闭后，调用这个方法。

        参数：

        - `server_conn`: 之前传入到`start_request`中的服务器连接。


- `tornado.httputil.HTTPMessageDelegate`

    pass
        

