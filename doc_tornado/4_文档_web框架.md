## tornado.web -- RequestHandler以及Application类

`tornado.web`提供了一个简单的web框架以及异步特性允许大规模的连接开启，灵感来自与长轮询(long polling)。

下面是一个"Hello World"的例子：

```python
import tornado.ioloop
import tornado.web


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")

if __name__ == "__main__":
    application = tornado.web.Application([
        (r"/", MainHandler),
    ])
    application.listen(8888)
    tornado.ioloop.IOLoop.current().start()
```

### 线程安全的注意事项

一般来说，`RequestHandler`中和Tornado其它地方的方法不是线程安全的。尤其是，类似`write()`，
`finish()`和`flush()`这些方法必须在主线程调用。如果你使用多线程，那么必须使用
`IOLoop.add_callback`在一个请求结束前把他交还给主线程。

### Request handlers

- `tornado.web.RequestHandler(application, request, **kwargs)`

    HTTP请求handler的基类。

    子类必须定义至少一个下面的"入口点(entry points）"方法。

### Entry points

- `RequestHandler.initialize()`

    子类初始化的钩子。每个请求都会调用它。

    传入URLSpec的第三个位置的字典参数将会作为`initialize()`的关键字参数。

    例子：

    ```python
    class ProfileHandler(RequestHandler):
        def initialize(self, database):
            self.database = database

        def get(self, username):
            ...


    app = application([
        (r"/user/(.*)", ProfileHandler, dict(database=database)),
    ])
    ```

- `RequestHandler.prepare()`

    在请求开始时`get/post/等等`之前调用。

    重写这个方法来执行一些一般的初始化，无关使用哪个HTTP方法。

    异步支持：可以使用`gen.coroutine`或者`return_future`来让这个方法异步化(`@asynchronous`
    不能用在这个方法上面）。如果这个方法返回一个`Future`，执行将不会继续，直到`Future`完成。

- `RequestHandler.on_finish()`

    一个请求结束后被调用。

    重写这个方法来执行清理工作，日志记录，等等...这个方法是`prepare`的尾部对照物。
    `on_finish`可能不会有任何输出，因为在它调用的时候response已经返回给客户端了。

实现下面的方法来对应相应的HTTP方法。这些方法都可以异步化，允许使用的装饰器包括:
`gen.coroutine`、`return_future`或者`asynchronous`。

这些方法的参数来自于`URLSpec`：任何在正则表达式捕获组捕获的参数都会变成HTTP动词方法的
参数(如果是命名捕获组则传入关键字参数，如果是普通捕获组则是位置参数）。

想要支持的方法不在这里，需要覆盖类变量`SUPPORTED_METHODS`:

```python
class WebDAVHanlder(RequestHandler):
    SUPPORTED_METHODS = RequestHandler.SUPPORTED_METHODS + ("PROPFIND",)

    def propfind(self):
        pass
```

- `RequestHandler.get(*args, **kwargs)`

- `RequestHandler.post(*args, **kwargs)`

- `RequestHandler.head(*args, **kwargs)`

- `RequestHandler.delete(*args, **kwargs)`

- `RequestHandler.patch(*args, **kwargs)`

- `RequestHandler.put(*args, **kwargs)`

- `RequestHandler.options(*args, **kwargs)`


### 输入

- `RequestHandler.get_argument(name, default=<object object>, strip=True)`

    返回给定名称的参数值。

    如果没有提供`default`，参数就被认为是必须的，如果没有发现则会发出`MissingArgumentError`错误。

    如果参数出现在URL中多次，我们会返回最后一个值。

    返回的值总是unicode。

- `RequestHandler.get_arguments(name, strip=True)`

    通过给定的name来返回参数列表。

    如果参数不存在，返回一个空列表。

    返回的值总是unicode。

- `RequestHandler.get_query_argument(name, default=<object object>, strip=True)`

    返回给定名称在url query string中的参数值。

    如果没有提供`default`，参数就被认为是必须的，如果没有发现则会发出`MissingArgumentError`错误。

    如果参数出现在URL中多次，我们会返回最后一个值。

    返回的值总是unicode。

- `RequestHandler.get_query_arguments(name, strip=True)`

    通过给定的name来返回url query string中的参数列表。

    如果参数不存在，返回一个空列表。

    返回的值总是unicode。

- `RequestHandler.get_body_argument(name, default=<object object>, strip=True)`

    返回给定名称在request body中的参数值。

    如果没有提供`default`，参数就被认为是必须的，如果没有发现则会发出`MissingArgumentError`错误。

    如果参数出现在URL中多次，我们会返回最后一个值。

    返回的值总是unicode。

- `RequestHandler.get_body_arguments(name, strip=True)`

    通过给定的name来返回request body中的参数列表。

    如果参数不存在，返回一个空列表。

    返回的值总是unicode。

- `RequestHandler.decode_argument(value, name=None)`

    从请求中解码一个参数。

    这个参数会以百分号形式编码，并且现在是byte类型。默认情况下，这个方法解码的参数是utf8
    那么返回的值也是unicode字符串，但是这个行为可以通过子类继承来更改。

    这个方法被`get_argument()`当作筛选器使用，以及从url提取的值最后传入`get()/post()/等等...`。

    参数的名称可能存在也可能不存在(比如url中的普通捕获组）。

- `RequestHandler.request`

    一个`tornado.httputil.HTTPServerRequest`对象，包含额外的请求参数，包括头部和body数据。

- `RequestHandler.path_args`

- `RequestHandler.path_kwargs`

    `path_args`和`path_kwargs`属性包含传入HTTP动词方法的位置参数和关键字参数。这些
    属性在这些方法调用之前已经设置，所以在`prepare`中也可以获取它的值。

- `RequestHandler.data_received(chunk)`

    实现这个方法来处理流式请求数据。

    需要`@stream_request_body`装饰器。

### 输出

- `RequestHandler.set_status(status_code, reason=None)`

    为我们的响应设置状态码。

    参数：

    - `status_code`(整数)：响应状态码。如果`reason=None`，那么它必须出现在
        `httplib.responses`
    - `resonse`(字符串):这个状态码供人读的理由短句。如果为`None`，那么将会填
        入`httplib.responses`

- `RequestHandler.set_header(name, value)`

    设置给定的响应头名称和值。

    如果给定一个`datetime`对象，将会按照HTTP规范自动转换格式。如果值不是字符串，我们
    将会把它转换为一个字符串。所有的头部值都换被编码为utf-8。

- `RequestHandler.add_header(name, value)`

    增加给定的响应头和值。

    不像`set_header()`，`add_header()`可能会调用多次，让相同的头部返回多个值。

- `RequestHandler.clear_header(name)`

    清除一个设置的头部，取消之前一次的`set_header`调用。

    注意这个方法不会应用于`add_header`方法实现的多个值的头部。

- `RquestHandler.set_default_headers()`

    重写这个方法，在请求开始时设置一些默认的HTTP头部。

    例如，在这里可以设置自定义的`Server`头部。注意设置的头部经过请求处理流程后可能就
    不是你期望的那样了，因为头部可能会在中间或者错误处理时期重设。

- `RequestHandler.write(chunk)`

    写入给定的数据块到输出缓冲中。

    想要把内容输出到网络上，使用`flush()`方法。

    如果给定的`chunk`是一个字典，内部将会把他转换为JSON并且设置响应的`Content-Type`
    为`application/json`。(如果你想设置一个不同的Content-Type，那么在`write()`之后
    调用`set_header`。

    注意列表不会转换为JSON，因为有潜在的跨站安全漏洞。所有的JSON输出应该封装到一个字典中。

- `RequestHandler.flush(include_footers=False, callback=None)`

    将当前的输出缓冲输出到网络中。

    如果给定了`callback`参数，将会使用它来进行流程控制：它会在所有刷新的数据写入到socket
    时候运行。注意一次只能运行一个flush callback；如果之前的callback没有结束又出现一个
    flush，之前的callback将会被丢弃。

    如果没有给定callback，将会返回一个`Future`

- `RequestHandler.finish(chunk=None)`

    结束这个响应，结束这个HTTP请求。

- `RequestHandler.render(template_name, **kwargs)`

    通过给定的参数渲染模版，并将它作为response内容输出。

- `RequestHandler.render_string(template_name, **kwargs)`

    通过给定的参数生成给定的模版。

    我们会直接返回生成模版的字符串。想要生成模版并将它作为response内容输出，请使用
    `render()`方法。

- `RequestHandler.get_template_namespace()`

    返回一个用于默认模版命名空间的字典。

    可能需要在子类中重写来增加或修改值。

    这个方法的结果将会组合`tornado.template`模块的额外默认，以及`render`和`render_string`
    中的关键字参数。

- `RequestHandler.redirect(url, permanent=False, status=None)`

    对给定的URL(可以是相对URL）发送一个重定向。

    如果指定`status`，这个值将作为response的状态码；或者根据`permanent`参数
    使用301(永久重定向)或302(临时重定向)。默认为302(临时重定向)。

- `RequestHandler.send_error(status_code=500, **kwargs)`

    发送指定的HTTP状态码到浏览器。

    如果已经调用了`flush()`，那么就不再可能发送一个错误了，所以这个方法应该用在response
    结束的时候。如果输出缓冲已经有内容写入但是还没有刷新，那么其中的东西都会被丢弃并换成一个
    错误页面。

    重写`write_error()`方法来自定义返回的错误页面。这个方法的另外的关键字参数将会传入到
    `write_error()`中。

- `RequestHandler.write_error(status_code, **kwargs)`

    重写这个方法来实现自定义错误页面。

    `write_error`可能会调用`write`，`render`,`set_header`，以及常用的输出方法。

    如果这个错误由一个未捕获的错误引起(包括`HTTPError`），可以通过`kwargs['exc_info']`
    获取`exc_info`三位元组。

- `RequestHandler.clear()`

    重置这个响应的所有头部和内容。

- `RequestHandler.render_linked_js(js_files)`

    一个默认方法，用来在渲染页面渲染最终的js链接。

    在子类中重写这个方法来改变输出。

- `RequestHandler.render_embed_js(js_embed)`

    一个默认方法，用来在渲染页面渲染最终的内嵌js。

    在子类中重写这个方法来改变输出。

- `RequestHandler.render_linked_css(css_files)`

    一个默认方法，用来在渲染页面渲染最终的css链接。

    在子类中重写这个方法来改变输出。

- `RequestHandler.render_embed_css(css_embed)`

    一个默认方法，用来在渲染页面渲染最终的内嵌css。

    在子类中重写这个方法来改变输出。


### Cookies

- `RequestHandler.cookies`

    一个`self.request.cookies`的别称。

- `RequestHandler.get_cookie(name, default=None)`

    通过给定的名称获得cookie值，如果没有则使用default，如果default也没有设置则报错。

- `RequestHandler.set_cookie(name, value, domain=None, expires=None, path='/', expires_days=None, **kwargs)`

    通过给定的选项设置给定的cookie键／值。

    另外的关键字参数将会直接设置在`Cookie.Morsel`，
    请看[标准库文档](https://docs.python.org/2/library/cookie.html#Cookie.Morsel)

- `RequestHandler.clear_cookie(name, path='/', domain=None)`

    通过给定的名称删除cookie。

    由于cookie协议的限制，你必须传入和设置cookie时候同样的`path`和`domain`。

- `RequestHandler.clear_all_cookies(path='/', domain=None)`

    将用户发送的这个request的cookies全部删除。

- `RequestHandler.get_secure_cookie(name, value=None, max_age_days=31, min_version=None)`

    如果验证合法，返回给定的签名cookie，否则返回None。

    解码的cookie值以byte string返回(和`get_cookie`不一样)。

- `RequestHandler.get_secure_cookie_key_version(name, value=None)`

    返回secure cookie的签名键版本(version)。

    这个版本(version)是int类型。

- `RequestHandler.set_secure_cookie(name, value, expires_days=30, version=None, **kwargs)`

    对一个cookie签名和加入时间戳，所以不能(轻易的)伪造。

    想要使用这个方法，你必须设置setting`cookie_secret`。这个setting应该是一个很长的，
    随机的字符串序列，用作签名的HMAC加密。

    注意`expires_days`参数设置浏览器中cookie的生命周期，但是可以在`get_secure_cookie`
    方法中独立使用`max_age_days`参数(过期则失效，无论`set_secure_cookie`中是不是设置的更长)。

- `RequestHandler.create_signed_value(name, value, version=None)`

    对一个字符串和加入时间戳，所以不能(轻易的)伪造。

    通常通过`set_secure_cookie`来使用，但是将它分离出来以便非cookie用法使用。这个方法
    解码的值不是用在cookie中，而是传入`get_secure_cookie()`的可选`value`参数。

- `tornado.web.MIN_SUPPORTED_SIGNED_VALUE_VERSION = 1`

    Tornado支持的最旧的签名值版本。

    旧于这个版本的签名值将不能被解码。

- `tornado.web.MAX_SUPPORTED_SIGNED_VALUE_VERSION = 2`

    Tornado支持的最新的签名值版本。

    新于这个版本的签名值将不能被解码。

- `tornado.web.DEFAULT_SIGNED_VALUE_VERSION = 2`

    `RequestHandler.create_signed_value`使用的默认签名值版本。但是可以传入`version`
    关键字参数来覆盖它。

- `tornado.web.DEFAULT_SIGNED_VALUE_MIN_VERSION = 1`

    `RequestHandler.get_secure_cookie`可接受的最旧的签名值。但是可以通过传入一个
    `min_version`关键字参数来覆盖它。


### 其它





