## tornado.httpclient -- 异步HTTP客户端

堵塞和非堵塞HTTP客户端接口。

这个模块为两种客户端实现定义了相同的接口，`simple_httpclient`和`curl_httpclient`。应用可以直接通过类来实例化，或者通过`AsyncHTTPClient.configure`方法来配置。

默认的实现是`simple_httpclient`，它适用于大多数用户的需求。然而，一些应用可能会处于以下原因选择使用`curl_httpclient`：

- `curl_httpclient`: 具有一些`simple_httpclient`没有的特性，包括支持HTTP代理和使用特殊的网络接口。

- `curl_httpclient`更加兼容于网站但并不那么服从HTTP规格。

- `curl_httpclient`更加快。

- `curl_httpclient`在Tornado2.0以前是默认的httpclient。

注意如果你在使用`curl_httpclient`，强烈推荐你使用最近版本的`libcurl`和`pycurl`。当前支持的最低`libcurl`版本为7.22.0，支持的最低`pycurl`版本为7.18.2。并且强烈推荐你的`libcurl`和异步DNS解析器一起安装(线程或者c-area)，否则你可能会碰到版本问题以及请求超时。

想要使用`curl_httpclient`，在初始阶段调用`AsyncHTTPClient.configure()`：

`AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")`

### HTTP客户端接口

- `tornado.httpclient.HTTPClient(async_client_class=None, **kwargs)`

    一个堵塞的HTTP客户端。

    这个接口提供与测试和方便的用途；大多数运行在IOLoop中的应用应该使用`AsyncHTTPClient`来替代它。典型的用法为：

    ```python
    http_client = httpclient.HTTPClient()
    try:
        response = http_client.fetch("http://www.google.com/")
        print(response.body)
    except httpclient.HTTPError as e:
        # 在response状态码为非200时抛出；response可以通过e.response获取
        print("Error: " + str(e))
    except Except as e:
        # 也可能发送其它的错误，比如IOError
        print("Error: " + str(e))
    http_client.close()
    ```

    - `close()`

        关闭这个HTTP连接，释放使用的资源。

    - `fetch(request, **kwargs)`

        执行一个请求，返回一个`HTTPResponse`。

        `request`参数可以是一个URL字符串或者一个`HTTPRequest`对象。如果是一个字符串，我们将使用额外的关键字参数`**kwargs`构造一个`HTTPRequest`对象。

        如果在fetch中出现一个错误，除非设置了`raise_error`关键字参数，否则都会抛出`HTTPError`。

- `tornado.httpclient.AsyncHTTPClient`

    一个非堵塞的HTTP客户端。

    使用案例：

    ```python
    def handle_response(response):
        if response.error:
            print("Error: {}".format(response.error))
        else:
            print(response.body)
    
    http_client = AsyncHTTPClient()
    http_client.fetch("http://www.google.com/", handle_response)
    ```

    这个类的构造器在几个方面有点“魔术”：它确实创建了一个特定子类实现的实例，实例在一种`pseudo-singleton`(伪单例)中被复用。关键字参数`force_instance=True`可以用来取消这个单例行为。除非设置了`force_instance=True`，除了`io_loop`以外的参数都不会传入到`AsyncHTTPClient`构造器中。子类实现的参数可以通过静态方法`configure()`来设置。

    所有的`AsyncHTTPClient`实现都支持一个`defaults`关键字参数，它可以用来设置`HTTPRequest`属性的默认值。例如：

    ```python
    AsyncHTTPClient.configure(
        None, defaults=dict(user_agent='MyUserAgent')
    )
    # 或者使用force_instance
    client = AsyncHTTPClient(force_instance=True, defaults=dict(user_agent="MyUserAgent"))
    ```

    - `close()`

        摧毁这个HTTP客户端，解放它使用的文件描述符。

        这个方法在**平常使用中并不需要**，因为通常`AsyncHTTPClient`都是需要重用的。`close()`只有在`IOLoop`关闭时，或者使用`force_instance=True`参数的时候才需要调用。

        在调用`close()`以后，不能继续调用`AsyncHTTPClient`的其它方法了。

    - `fetch(request, callback=None, raise_error=None, **kwargs)`

        执行一个请求，异步返回一个`HTTPResponse`.

        `request`参数要么是一个URL字符串，要么是一个`HTTPRequest`对象。如果是一个字符串，我们使用`kwargs`来构造一个`HTTPRequest`。

        这个方法将会返回一个`Future`，它的结果是一个`HTTPResponse`。默认情况下，如果这个请求返回一个非200的响应码这个`Future`将会抛出一个`HTTPError`。另外，如果`raise_erro=False`，那么无论响应码是什么都不会抛出错误而总是返回。

        如果给定一个`callback`，它会使用`HTTPResponse`来调用。在callback接口中，`HTTPError`并不会自动抛出。你需要自己检查response的`.error`属性或者调用它的`rethorw()`方法。

    - 类方法`configure(impl, **kwargs)`

        配置一个`AsyncHTTPClient`子类以供使用。

        `AsyncHTTPClient()`事实上会创建一个子类的实例。这个方法可以通过一个类对象或者一个完全(`python path风格`)的类名来调用(或者传入`None`，来使用默认的`SimpleAsyncHTTPClient`)。

        如果给定了额外的参数，它们将会传入到每个子类的构造器中以供实例的创建使用。关键字参数`max_clients`决定每个IOLoop并行`fetch()`操作的最大数量。其它的参数根据子类实现来决定。

        例子：

        `AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")`

#### 请求对象

- `tornado.httpclient.HTTPRequest(url, method='GET', headers=None, body=None, auth_usrename=None, auth_password=None, auth_mode=None, connnect_timeout=None, request_timeout=None, if_modified_since=None, follow_redirects=None, max_redirects=None, user_agent=None, user_gzip=None, network_interface=None, stream_callback=None, header_callback=None, prepare_curl_callback=None, proxy_host=None, proxy_port=None, proxy_usrename=None, proxy_password=None, proxy_auth_mode=None, allow_nonstandard_methods=None, validate_cert=None, ca_certs=None, allow_ipv6=None, client_key=None, client_cert=None, body_producer=None, expect_100_continue=None, decompress_response=None, ssl_options=None)`

    HTTP客户端请求(request)对象。
    
    除了`url`，其它所有参数都是可选的。

    参数：

    - `url`(字符串): 要获取的URL
    - `method`(字符串)：HTTP方法，比如“GET”或者“POST”
    - `headers`(`HTTPHeaders`或者字典): 传入这个请求的额外HTTP头部
    - `body`: 字符串形式的HTTP请求body(byte或者utf8)
    - `body_producer`: 惰性或异步的请求body可调用对象(工厂函数)。它通过一个参数调用，一个`write`函数，并且应该返回一个`Future`对象。它应该调用write函数获取新的数据。write函数返回一个Future对象用于控制流。只可以设定`body`和`body_producer`中的一个。`curl_httpclient`不支持使用`body_producer`。当使用`body_producer`时，推荐传入一个`Content-Type`头部。
    - `auth_username`(字符串)：HTTP验证的用户名
    - `auth_password`(字符串): HTTP验证的密码
    - `auth_mode`(字符串): 验证模式；默认为"basic"。`curl_httpclient`支持"basic"和"digest"；`simple_httpclient`支持"basic"。
    - `connect_timeout`(浮点数)：开始连接后的超时秒数，默认为20秒。
    - `request_timeout`(浮点数): 整个请求的超时秒数，默认为20秒。
    - `if_modified_since`(`datetime`或者浮点数): `If-Modified-Since`头部的时间戳的值。
    - `follow_redirects`(bool)：是否应该自动跟随重定向。默认为True。
    - `max_redirects`(整数): `follow_redirects`的限制次数，默认为5
    - `user_agent`(字符串): 这个字符串会发送到`User-Agent`头部。
    - `decompress_response`(bool): 从服务器请求一个压缩的response，并在下载后将它解压缩。
    - `user_gzip`(bool): `decompress_response`的一个别称，已经弃用。
    - `network_interface`(字符串): 请求使用的网络接口。只可以让`curl_httpclient`使用。
    - `streaming_callback`(可调用对象): 如果设定，`streaming_callback`会在每次接收到的(部分的)数据时都调用，最终response对象的`HTTPResponse.body`和`HTTPResponse.buffer`都将为空。
    - `header_callback`(可调用对象): 如果设定，`header_callback`会在接受到每行头部时都会被调用(包括第一行，也就是：`HTTP/1.0 200 OK\r\n`, 以及只有`\r\n`的最后一行，所有行都具有换行字符)。`HTTPResponse.headers`在最终的response将会为空。这个参数一般与`streaming_callback`结合使用，因为只有这一个方法可以在请求进行时访问头部数据。
    - `prepare_curl_callback`(可调用对象): 如果设定，将会调用一个`pycurl.Curl`对象来允许应用进行额外的`setopt`调用。
    - `proxy_host`(字符串): HTTP代理host。想要使用代理，必须设定`proxy_host`和`proxy_port`；`proxy_username`, `proxy_pass`以及`proxy_auth_mode`是可选的。目前只支持在`curl_httpclient`中使用代理。
    - `proxy_port`(整数): HTTP代理端口
    - `proxy_username`(字符串): HTTP代理用户名
    - `proxy_pass`(字符串): HTTP代理密码
    - `proxy_auth_mode`(字符串): HTTP代理验证模式；默认为"basic"。支持"basic"和"digest"。
    - `allow_nonstandard_methods`(bool): 是否允许`method`参数传入非常规值。默认为False。
    - `validate_cert`(bool): 对于HTTPS请求，是否验证服务器的证书。默认为True。
    - `ca_certs`(字符串): PEM格式CA证书的文件名，或者传入None来使用默认值。
    - `client_key`(字符串): 客户端SSL key的文件名。
    - `client_cert`(字符串): 客户端SSL证书的文件名。
    - `ssl_options`(`ssl.SSLContext`): 用于`simple_httpclient`的`ssl.SSLContext`对象。覆盖`validate_cert, ca_certs, client_key, client_cert`这些参数.
    - `allow_ipv6`(bool): 是否在可获取时使用IPv6。默认为True。
    - `expect_100_continute`(bool): 如果为True，发送头部`Expect: 100-continue`并在发送请求body之前等待一个表示继续的response。只支持在`simple_httpclient`中使用。

    > 注意
    >> 当使用`curl_httpclient`时，某些可能会继承而获得，因为`pycurl`不允许它们完全重置。包括`ca_certs, client_key, client_certs, network_interface`参数。如果你想使用这些选项，你必须在每个请求中传入它们。

#### Response对象

- `tornado.httpclient.HTTPResponse(request, code, headers=None, buffer=None, effective_url=None, error=None, request_time=None, time_info=None, reason=None)`

    HTTP Response对象。

    属性：

    - `request`: HTTPRequest对象。
    - `code`: 数字HTTP状态码，比如200或者404。
    - `reason`: 秒数状态码的供人理解的理由短语。
    - `headers`: `tornado.httputil.HTTPHeaders`对象。
    - `effective_url`: 资源的最终位置。
    - `buffer`: response body的`cStringIO`对象。
    - `body`: byte类型的response body.
    - `error`: 一个错误对象。
    - `request_time`: 请求开始到结束所需要的时间(秒)。
    - `time_info`: 请求的时间诊断信息(字典形式).如果`AsyncHTTPClient`设置了`max_clients`，那么就会加入一个delay延迟。
    - `rethrow()`: 如果请求中有一个错误，抛出一个`HTTPError`。


#### 异常

- 异常`tornado.httpclient.HTTPError(code, message=None, response=None)`

    一个不成功的请求抛出的异常。

    属性：

    - `code`: HTTP错误整数状态码，比如404。如果没有接收到HTTP response，将会使用599状态码，比如timeout。
    - `response`: `HTTPResponse`对象。

    注意如果`follow_redirects=False`，重定向将会变成一个`HTTPError`，你可以通过`error.response.headers['Location']`来看重定向的终点所在。

#### 命令行接口

这个模块提供了一个简单的命令行接口，使用HTTP客户端来获取一个URL。使用例子：

```python
# 获取一个URL并打印它的body
python -m tornado.httpclient http://www.google.com

# 只打印头部
python -m tornado.httpclient --print_headers --print_body=false http://www.google.com
```

#### (子类)实现

- `tornado.httpclientSimpleAsyncHTTPClient`

    不依赖第三方库的非堵塞HTTP客户端。

    这个类基于`tornado.IOStream`实现了一个HTTP1.1的客户端。`CurlAsyncHTTPClient`支持的一些特性在这个类中并不支持。特别是，这个类不支持代理，连接不可有复用，调用者不可以选择网络接口(networking interface)。

    - `initialize(io_loop, max_clients10, hostname_mapping=None, max_buffer_size=104857600, resolver=None, defaults=None, max_header_size=None, max_body_size=None)`

        创建一个`AsyncHTTPClient`实例。

        每个IOLoop只可以存在一个`AsyncHTTPClient`实例，用来限制待定链接的数量。使用`force_instance=True`可以废止这个行为。

        注意因为这个实例是隐式可复用的，除非使用`force_instance=True`，否则只会使用第一次调用构造器时传入的参数。推荐使用`configure()`方法而不是直接使用构造器，这可以确保参数生效。

        - `max_clients`: 是指可以进行的最大并发数;当达到这个限制时，之后的请求都会在队列中等待。注意，在队列中的时间同样会在`request_timeout`计数。

        - `hostname_mapping`: 是一个映射域名和IP地址的字典。当不能系统级别修改DNS配置时，可以用这个参数来做局部的DNS修改(比如在单元测试中使用)。

        - `max_buffer_size`: (默认100MB)是一次性读入内存中的总byte大小。`max_body_size`(默认等于`max_buffer_size`)是客户端可以接受的最大响应body。如果不设定`streaming_callback`，这两个限制将会生效;如果设置了`streaming_callback`，只有`max_body_size`会生效。

- `tornado.httpclient.CurlAsyncHTTPClient(io_loop, max_clients=10, defaults=None)`

    基于`libcurl`的HTTP客户端。


