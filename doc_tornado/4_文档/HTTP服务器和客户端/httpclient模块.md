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

        pass