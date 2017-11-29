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

    实现这个接口来处理一个HTTP Request或者Response。

    - `headers_received(start_line, headers)`

        在HTTP头部接受并解析后调用这个方法。

        参数：

        - `start_line`: 根据这是一个客户端还是服务器消息来决定传入到这个参数的是一个`RequestStartLine`还是`ResponseStartLine`。

        - `headers`: 一个`HTTPHeaders`实例。

        一些`HTTPConnect`方法只有在`headers_received`运行期间被调用。

        可以返回一个`Future`；如果它在运行那么知道它完成以后都不能读取body。

    - `data_received(chunk)`

        在一部分(chunk)数据被接收后调用这个方法。

        可以返回一个`Future`.

    - `finish()`

        在最后一部分(chunk)被接收后调用。

    - `on_connection_close()`

        在请求被关闭而请求未关闭时调用。

        如果`headers_received()`被调用，那么`finish`或者`on_connection_close`中的一个将会被调用，但两者不会一起调用。


- `tornado.utils.HTTPCollection`

    Web APP使用这个这个接口来写它的response。

    - `write_headers(start_line, headers, chunk=None, callback=None)`

        写一个HTTP头部块。

        参数：

        - `start_line`: 一个`RequestStartLine`或者`ResponseStartLine`。
        - `headers`: 一个`HTTPHeaders`头部。
        - `chunk`: 首(可选)部分数据。
        - `callback`: 在写入动作完成后使用的一个callback。

    `start_line`的`version`字段被忽略。

    如果没有给定回调，返回一个`Future`。

    - `write(chunk, callback=None)`

        写一部分(chunk)body数据.

        在写入动作完成后，callback将会被调用。如果没有给定callback，将会返回Future。

    - `finish()`

        指明最后一部分(chunk)数据已经写完。


- `tornado.httputil.url_concat(url, args)`

    联结URL和参数，不管URL是否存在query参数。

    `args`可以是一个字典，或者一个键值对元组列表，后者可以允许对一个键存在多个值。

    ```python
    >>> url_concat("http://example.com/foo", dict(c="d"))
    'http://example.com/foo?c=d'
    >>> url_concat("http://example.com/foo?a=b", dict(c="d"))
    'http://example.com/foo?a=b&c=d'
    >>> url_concat("http://example.com/foo?a=b", [("c", "d"), ("c", "d2")])
    'http://example.com/foo?a=b&c=d&c=d2'
    ```

- `tornado.httputil.HTTPFile`

    代表一个通过`form`上传的文件。

    出于向后兼容的原因，以下属性也可以通过字典键的方式访问：

    - `filename`
    - `body`
    - `content_type`

- `tornado.httputil.parse_body_arguments(content_type, body, arguments, files, headers=None)`

    解析一个form的请求内容。

    支持`application/x-www-form-urlencodeed`以及`multipart/form-data`。`content_type`参数需要是一个字符串，`body`需要是一个byte字符串。给定`arguments`和`files`参数都是字典，它们通过被解析的内容来更新。


- `tornado.httputil.parse_multipart_form_data(boundary, data, arguments, files)`

    解析一个`multipart/form-data`内容体。

    `boundary`和`data`参数都是byte字符串。给定`arguments`和`files`参数都是字典，它们通过被解析的内容来更新。

- `tornado.httputil.format_timestamp(ts)`

    使用HTTP格式来格式化一个时间戳。

    参数可以是`time.time()`返回的数字时间戳，`time.gmtime()`返回的时间元组，或者一个`datetime.datetime`对象.

    ```python
    >>> format_timestamp(1359312200)
    'Sun, 27 Jan 2013 18:43:20 GMT'
    ```

- `tornado.httputil.RequestStartLine`

    - `__init__(method, path, version)`

        创建一个新的RequestStartLine实例。

        参数：

        - `method`： 字段0的别称
        - `path`: 字段1的别称
        - `version`: 字段2的别称

- `tornado.httputil.ResponseStartLine`

    - `__init__(code, reason, version)`

        创建一个新的RequestStartLine实例。

        参数：

        - `code`： 字段0的别称
        - `reason`: 字段1的别称
        - `version`: 字段2的别称

- `tornado.httputil.parse_response_start_line(line)`

    对一个HTTP 1.x响应行，返回一个`(version, code, version)`元组。

    对象是一个`collections.namedtuple`.

    ```python
    >>> parse_response_start_line("HTTP/1.1 200 OK")
    ResponseStartLine(version='HTTP/1.1', code=200, reason='OK')
    ```

- `tornado.httputil.split_host_and_port(netloc)`

    根据`netloc`返回一个`(host, port)`元组。

    如果没有port，将会对它赋值为None。

- `tornado.httputil.parse_cookie(cookie)`

    将一个HTTP的`Cookie`头部解析为一个字典，或者一个键值对列表。

    这个函数试图模仿浏览器的cookie解析行为；它没有严格的遵从关于Cookie的RFC规范(因为浏览器也这样)。

    这个解析算法和Django1.9.10使用的一样。




