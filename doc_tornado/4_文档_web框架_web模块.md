[TOC]

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

- `RequestHandler.application`

    这个request绑定的`Application`实例。

- `RequestHandler.check_etag_header()`

    如果请求出现`If-None-Match`，那么检查`Etag`头部。

    如果请求的Etag匹配返回`True`以及一个304状态码。例如：

    ```python
    self.set_etag_header()
    if self.check_etag_header():
        self.set_status(304)
        return
    ```

    在请求结束后这个方法会自动调用，但是如果重写了`compute_tag`那么可能会提前调用。
    `Etag`头部应该在调用这个方法之前设置。

- `RequestHandler.check_xsrf_cookie()`

    检测`_xsrf`cookie是否匹配`_xsrf`参数。

    为了防范跨站请求伪造，我们设置了一个cookie`_xsrf`并且在所有POST请求要求增加一个
    非cookie的`_xsrf`字段。如果这两个值不匹配，我们会拒绝提交的表单并将它看作有可能是伪造的。

    `_xsrf`的值既可以在表单中，以字段名`_xsrf`设置；也可以设置一个自定义HTTP头部，以
    `X-XSRFToken`或者`X-CSRFToken`(这个方式同样兼容Django）。

- `RequestHandler.compute_etag()`

    计算这个请求使用的etag头部。

    默认使用之前所写内容的hash值。

    可以重写，自己提供一个etag实现，或者可以设置返回None来禁用Tornado默认的etag支持。

- `RequestHandler.create_template_loader(template_path)`

    根据给定的路径返回一个新的模版读取器。

    可以重写这个方法。

    默认会根据路径返回一个文件夹为基础的读取器，默认会使用setting
    `autoescape`和`template_whitespace`。如果提供了setting`template_loader`，
    使用提供的值来替代。

- `RequestHandler.current_user`

    发送这个请求的已验证用户。

    可以通过两种方式来设置这个属性：

    - 重写`get_current_user()`，在首次访问`self.current_user`时将会调用这个方法，
    `get_current_user()`在每个请求只会被调用一次，它的返回值将会缓存(使用`@property`装饰器)
    以便将来使用。

        ```python
        def get_current_user(self):
            user_cookie = self.get_secure_cookie("user")
            if user_cookie:
                return json.loads(user_cookie)
            return None
        ```

    - 可以设置为一个一般的变量，通常在`prepare()`中设置：

        ```python
        @gen.coroutine
        def prepare(self):
            user_id_cookie = self.get_secure_cookie("user_id")
            if user_id_cookie:
                self.current_user = yield load_user(user_id_cookie)
        ```

    注意`prepare()`可以是协程而`get_current_user()`不可以，所以如果读取用户要求必须
    是异步操作的话，只能使用后一种形式。

    用户类型可以是任意的类型。

- `RequestHandler.get_browser_locale(default='en_US')`

    通过`Accept-Language`头部决定用户的位置。

- `RequestHandler.get_current_user()`

    重写这个方法来决定当前用户的获取方式。比如：cookie。

    这个方法不可以设置为协程。

- `RequestHandler.get_login_url()`

    重写这个方法，根据请求来自定义登陆页面的URL。

    默认情况下，使用setting`login_url`。

- `RequestHandler.get_status()`

    返回我们response的状态码。

- `RequestHandler.get_template_path()`

    重写这个方法来对每个handler自定义模版文件的路径。

    默认情况下，我们使用setting`template_path`。如果返回None，那么就会根据相对路径
    的形式调用文件。

- `RequestHandler.get_user_locale()`

    重写这个方法来决定已验证用户的位置。

    如果返回None，我们调转使用`get_browser_locale()`。

    这个方法应该返回一个`tornado.locale.Locale`对象。

- `RequestHandler.locale`

    当前会话的地理位置。

    取决于`get_user_locale`的设置。比如可以使用用户存入数据库的偏好设置，或者通过
    `get_browser_locale`使用`Accept-Language`头部来决定位置。

- `RequestHandler.log_exception(typ, value, tb)`

    继承这个方法来为未捕捉的异常记录日志。

    默认会把`HTTPError`的警告信息记录为日志，不设置堆追溯信息(使用`tornado.general`
    记录器)。其它所有的异常将会被当作错误，和堆追溯信息一起记录(使用`tornado.application`记录器)。

- `RequestHandler.on_connection_close()`

    在异步handler中，如果用户关闭连接，调用这个方法。

    重写这个方法，来清理长连接的关联资源。注意这个方法在连接在异步操作过程中关闭时才会调用；
    如果你需要在每个请求结束后做清理，重写`on_finish()`方法。

    在客户端离开后代理可能会保持连接开启(可能无期限开启),所以这个方法可以在用户离开后迅速
    被调用。

- `RequestHandler.require_setting(name, feature='this feature')`

    如果给定的setting没有设置，则会抛出一个异常。

- `RequestHandler.reverse_url(name, *args)`

    `Application.reverse_url()`的别称。

- `RequestHandler.set_etag_header()`

    使用`self.compute_etag()`来设置response的Etag头部。

    注意：如果`self.compute_etag()`返回None，就不会设置头部。

    在请求完成后这个方法会被自动调用。

- `RequestHandler.settings`

    `self.application.settings`的别称。

- `RequestHandler.static_url(path, include_host=None, **kwargs)`

    通过给定的静态文件相对路径返回一个静态URL。

    这个方法需要你在application中设置setting`static_url`(设置为你静态文件的根目录)。

    这个方法将会返回一个带版本的URL(默认追加`?v=<signature>`)，它准许静态文件能够独立
    缓存。可以通过`include_version=False`来禁用这个行为(在默认的实现中；其它的静态资源
    并不支持使用这个(缓存)方法，但是可能有其它的选择）。

    默认这个方法将会返回当前host的相对URL，但是如果设置了setting`include_host=True`，
    返回的URL将会是绝对路径。如果这个handler包含一个`include_host`属性，这个值会用在
    所用`static_url`的调用中并且会作为关键字参数传入。

- `RequestHandler.xsrf_form_html()`

    一个用来包含在所有POST表单中的HTML`<input />`元素。

    这个方法会定义`_xsrf`input值，它将会在所有的POST请求中被检查以防范跨站请求伪造。如果
    你设置了setting`xsrf_cookies`，你必须在所有的HTML表单中包含这个元素。

    在模版中，这个函数的调用方式为：`{% module xsrf_form_html() %}`

- `RequestHandler.xsrf_token`

    当前用户/会话的XSRF预防token。

    为了预防跨站请求伪造，我们设置了一个`_xsrf`cookie并且在所有的POST请求中加入一个`_xsrf`
    参数。

### Application配置

- `tornado.web.Application(handlers=None, default_host=None, transform=None, **settings)`

    一个请求handler的集合，用之创建一个web应用。

    这个类的实例可以直接传入一个HTTPServer中用来伺服一个应用：

    ```python
    application = web.Application([
        (r"/", MainPageHandler),
    ])

    http_server = httpserver.HTTPServer(application)
    http_server = listen(8080)
    ioloop.IOLoop.current().start()
    ```

    这个构造器接受一个`Rule`对象列表，或者值符合`Rule`(`matcher`, `target`, `[target_kwargs]`, `name`)
    构造器的元组，值中的方括号是可选的。默认的`matcher`是一个`PathMatches`，所以
    元组`(regexp, target)`可以用来替代`(PathMatches(regexp), target)`。

    常见的路由目标是一个`RequestHandler`子类，但是你可以将一个规则(rule)列表作为目标，
    可以创建一个嵌套的路由配置：

    ```python
    application = web.Application([
        (HostMatches("example.com"), [
            (r"/", MainPageHandler),
            (r"feed", FeedHandler),
        ]
    ])
    ```

    另外你可以设置嵌套的`Router`实例，`HTTPMessageDelegate`子类和可调用对象作为路由目标。

    当我们接收到一个请求时，会迭代这个列表并且把第一个正则匹配的路径对应的目标handler实例化。
    目标可以指定为一个类对象或者一个(pyhton path格式)的字符串名称。

    元组中的第三个参数可以传入一个字典(`target_kwargs`)，这个参数将会作为关键字参数传入
    handler的构造器和`initialize`方法。这个模式用于下面例子中的`StaticFileHandler`
    (注意一个`StaticFileHandler`可以自动安置)：

    ```python
    application = web.Application([
        (r"/static/(.*)", web.StaticFileHandler, {"path": "/var/www"})
    ])
    ```

    我们支持通过`add_handlers`方法实现虚拟host，它接受一个host正则表达式作为首个参数：

    ```python
    application.add_handler(r"www\.myhost\.com", [
        (r"/article/(0-9)+)", ArticleHandler),
    ])
    ```

    如果当前请求的host不匹配，那么将会使用`default_host`参数值来替代。

    你可以通过传入一个关键字参数`static_path`来伺服静态文件。我们将会在URI`/static/`
    来伺服这些文件(这个URI可以通过setting`static_url_prefix`来配置)，我们可以在同个
    目录伺服`/favicon.ico`和`/robots.txt`。

    另外可以继承`StaticFileHandler`并将它设置为setting`static_handler_class`。

    **settings**

    传入构造器的额外关键字参数，通常在文档中提及它的时候叫做"application settings"。
    settings用来定制化Tornado的各个方面(虽然一些深入的定制化是通过重写`RequestHandler`
    子类的方法来实现)。一些应用同样喜欢使用`settings`字典来获取一些application特定的
    配置参数，而不是使用全局变量。Tornado使用的setting描述如下。

    *一般的settings*:

    - `autoreload`： 如果为True，源代码的任何改动都会使服务器进程重启。

    - `debug`: 若干debug模式settings的快捷方式。设置`debug=True`等同于同时设置
        `compiled_template_cache=False`， `static_hash_cache=False`，
        `serve_traceback=True`。

    - `default_handler_class`和`default_handler_args`：如果没有其它匹配，将会
        使用这个handler。使用它来实现自定义404页面。

    - `compress_response`： 如果为`True`，文本形式的response将会自动压缩。

    - `gzip`: `compress_response`的废弃别名。

    - `log_function`: 这个函数将会在每个请求的最后调用来记录结果日志(传入一个参数，
        `RequestHandler`对象）。默认的实现将会被日志写入`logging`模块的根记录器。
        可以通过重写`application.log_request`来定制化。

    - `serve_traceback`：如果为True，默认的错误页面将会包含错误的回溯。

    - `ui_modules`和`ui_methods`：可以设置为`UIModule`或者`UI methods`的一个映射。
        可以设置为一个模块，字典，或者模块／字典的一个列表。

    - `websocket_ping_interval`: 如果设置一个数字，每个websocket将会每n秒ping一下，
        因为某些的代理(proxies)可能会关闭闲置的连接，这个setting可以帮助保持连接，并且
        它可以发现websocket因为不恰当关闭导致的失败。

    - `websocket_ping_timeout`: 如果ping间隔指定，并且服务器并没有在n秒收到一个"pong"，
        它将会关闭websocket。默认为3次ping间隔无响应，最少30秒无响应的情况下关闭。如果没有
        设置ping间隔，那么这个setting将会被忽略。

    *验证和安全setting*：

    - `cookie_secret`: 用于`RequestHandler.get_secure_cookie`和`set_secure_cookie`
        签名cookie的使用。

    - `key_version`: 如果`cookie_secret`设置为字典形式，这个setting用来决定
        `RequestHandler.set_secure_cookie`生成签名cookie的指定key。

    - `login_url`: 如果用户没有登陆，装饰器`@authenticated`将会将它重定向到这个URL。
        可以通过重写`RequestHandler.get_login_url`来进一步定制化。

    - `xsrf_cookies`: 如果设置为True，将会激活XSRF防护。

    - `xsrf_cookie_version`: 控制这个服务器生成的新的XSRF cookie的版本。通常应该
        让它使用默认值(总是使用支持的最高版本），但是可以在版本过渡时临时设置一个更低版本
        的值。

    - `xsrf_cookie_kwargs`: 可以设置为一个字典，作为传入这个xsrf cookie使用
        `RequestHandler.set_cookies`的额外参数。

    - `twitter_consumer_key, twitter_consumer_secret, friendfeed_consumer_key, friendfeed_consumer_secret, google_consumer_key, google_consumer_secret, facebook_api_key, facebook_secret`

        用于`tornado.auth`模块。

    *模版settings*：

    - `autoescape`: 控制模版的自动转义。可以设置为`None`来禁用自动转义。或者传入一个
        函数的名称，所有的输出将会使用它来转义。默认为"xhtml_escape"。可以在每个模版
        基础上设置`{% autoescape %}`。

    - `compiled_template_cache`：默认为True；如果设置为False，模版将会在每个请求后
        重新编译。

    - `template_path`：包含模版文件的目录。可以通过重写`RequestHandler.get_template_path`
        来进一步自定义。

    - `template_loader`: 继承`tornado.template.BaseLoader`来定制化模版读取。如果
        使用了这个setting，那么`template_path`和`autoescape`将会被忽略。可以通过覆盖
        `RequestHandler.create_template_loader`进一步定制化。

    - `template_whietespace`: 控制模版中的空白值处理。


    *静态文件settings*:

    - `static_hash_cache`: 默认为True；如果设置为False那么每次请求都会重新计算。

    - `static_path`: 想要伺服的静态文件目录。

    - `static_url_prefix`: 静态文件的URL前缀，默认为`/static/`

    - `static_handler_class, static_handler_args`:

        可以对静态文件使用不同的handler，用来替代默认的`tornado.web.StaticFileHandler`。
        `static_handler_args`如果指定一个字典，将会作为关键字参数传入这个handler的`initialize`方法。


    - `listen(port, address='', **kwargs)`

        通过给定的端口，开启一个HTTP服务器来伺服这个应用。

        这是一个方便的接口，用来创建一个`HTTPServer`并且调用它的`listen()`方法。
        `HTTPServer.listen`并不支持关键字参数。对于高级用法(多进程模式)，不要使用
        这个方法；创建一个`HTTPServer`并且直接调用它的`TCPServer.bind/TCPServer.start`方法。

        注意在调用这个方法之后，你仍然需要调用`IOLoop.current().start()`来开启服务器。

        返回`HTTPServer`对象。

    - `add_handlers(host_pattern, host_handlers)`

        将给定的handler追加到我们的handlers列表中。

    - `get_handler_delegate(request, target_class, target_kwargs=None, path_args=None, path_kwargs=None)`

        返回一个`HTTPMessageDelegate`并且可以对一个应用和`RequestHandler`子类伺服一个request。

        参数：

        - `request(httputil.HTTPServerRequest)` - 当前的HTTP请求。
        - `target_class(RequestHandler)` - 一个`RequestHandler`实例。
        - `target_kwargs(dict)` - 传入`target_class`构造器的关键字参数。
        - `path_args(list)` - `target_class`中HTTP方法的位置参数
        - `path_kwargs(dict)` - `target_class`中HTTP方法的关键字参数`

    - `reverse_url(name, *args)`

        通过handler名称`name`来返回一个URL路径。

        这个handler必须通过一个带名称的`URLSpec`加入的application中。

        参数可以替换`URLSpec`正则表达式中的捕获组。如果有必要它会被转换为字符串，
        并且编码为utf8，以及url转义。

    - `log_request(handler)`

        对日志记录一个完整的HTTP请求。

        默认会写入到Python的根记录器。想要改变这个行为，可以继承Application并且重写
        这个方法，或者传入一个setting`log_function`。

- `tornado.web.URLSpec(pattern, handler, kwargs=None, name=None)`

    在URL和handler中指定映射。

    参数：

    - `pattern`: 用来匹配的正则表达式。任何的捕获组都会传入handler的`get/post/etc`
        HTTP方法中。命名捕获组以关键字参数形式传入，非命名捕获组以位置参数形式传入。

    - `handler`: 想要调用的`RequestHandler`子类。

    - `kwargs`(可选): 传入handler构造器的额外参数字典。

    - `name`(可选): 这个handler的名称。供`reverse_url`使用。

    这个类同样可以在`tornado.web.url`模块下面获取。


### 装饰器

- `tornado.web.asynchronous`(方法装饰器)

    如果一个handler请求方法为异步，使用这个装饰器包裹它。

    这个装饰器用于回调函数风格的异步方式；对于协程来说，应该使用`gen.coroutine`装饰器。

    这个装饰器应该仅用于`HTTP动词方法`；对于其它方法，这个行为都会为未定义状态。这个方法
    并**不会**让方法异步化，而是告诉框架："这个方法是异步的"。所以这个装饰器应用的方法必须
    做一些异步的事情。

    如果加入这个装饰器，response不会在方法返回时结束。直到调用`self.finish()`时才会
    结束请求并返回响应。如果没有这个装饰器，请求会在`get()`,`post()`方法返回时自动结束：

    ```python
    class MyRequestHandler(RequestHandler):
        @asynchronous
        def get(self):
            http = httpclient.AsyncHTTPClient()
            http.fetch("http://friendfeed.com/", self._on_download)

        def _on_download(self, response):
            self.write("Download!")
            self.finish()
    ```

- `tornado.web.authenticated`(方法)

    装饰的方法要求用户必须登入。

    如果用户没有登入，将会重定向到setting`login_url`。

    如果你配置的一个login url加上query string，Tornado会假定你是有意这么做的。如果
    没有加上query string，它会为login url加上`next`参数，让登陆页面成功后将用户带去
    原来的地方。

- `tornado.web.addslash`(方法)

    使用这个装饰器，为请求的路径增加一个结尾斜杠。

    例如，一个`/foo`的请求将会被重定向到`/foo/`。为了结合这个装饰器，这个handler对应的
    url正则表达式应该类似于`r'/foo/?`。

- `tornado.web.removeslash`(方法)

    使用这个装饰器，为请求的路径移除一个结尾斜杠。

    例如，一个`/foo/`的请求将会被重定向到`/foo`。为了结合这个装饰器，这个handler对应的
    url正则表达式应该类似于`r'/foo/*`。

- `tornado.web.stream_request_body`(类装饰器)

    装饰一个`RequestHandler`子类，让它能够支持流式body。

    这个装饰器隐式作出如下改动：

    - `HTTPServerRequest.body`将会为None，body中的参数也不会包括在
        `RequestHandler.get_argument`中。

    - `RequestHandler.prepare()`在请求的头部被读取后即调用，而不是在整个body读取
        完之后。

    - 这个子类必须定义一个`data_received(self, data)`；在获取数据后它可能会被调用0次
        或多次。注意如果这个请求有一个空的body，`data_received`将不会被调用。

    - `prepare`和`data_received`可能返回Futures(比如使用了`@gen.coroutine`协程，
        在这种情况下，直到这个future运行完之前，下一个方法都不会被调用。

    - 常规的HTTP方法(`post`, `put`等等)可以在整个body被读取后调用。


### 其它一切

- 异常`tornado.web.HTTPError(status_code=500, log_message=None, *args, **kwargs)`

    一个转向HTTP错误响应的异常。

    抛出一个`HTTPError`有时相比调用`RequestHandler.send_error`会更加方便，因为
    它会自动终结当前的函数。

    想要自定义HTTPError发送的响应，应该重写`RequestHandler.send_error`。

    参数：

    - `status_code`(整数): HTTP状态码。除非给定了关键字参数`reason`，否则必须使用
        `httplib.responses`清单中的状态码。

    - `log_mesage`(字符串): 这个错误写入到日志中的消息(如果不是DEBUG模式，这个消息
        不会展示给用户观看)。可以使用`%s`形式占位符，它们将会以剩下的位置参数来填充。

    - `reason`(字符串): **仅**关键字参数。HTTP协议中和`status_code`共处于一列的
        "reason"短语。通常由`status_code`自动决定，但是如果使用非标准状态码则可以使用
        这个参数。

- 异常`tornado.web.Finish`

    一个结束请求而不生成错误响应的异常。

    如果在一个`RequestHandler`中抛出一个`Finish`，这个请求将会被结束(如果还没有调用
    `self.finish()`的话，调用它)，但是错误处理方法(包括`RequestHandler.send_error`)
    将不会被调用。

    如果无参数调用`Finish()`，待定的response将会被发送。如果给定`Finish()`参数，
    这个参数将会发送给`RequestHandler.finish()`。

    相比重写`write_error()`方法，这个异常可以更方便的实现自定义错误页面(尤其在库代码中)：

    ```python
    if self.current_user is None:
        self.set_status(403)
        self.set_header("WWW-Authenticate", "Basic realm='something'")
        raise Finish()
    ```

- 异常`tornado.web.MissingArgumentError(arg_name)`

    `RequestHandler.get_argument()`抛出的异常。

    这是`HTTPError`的子类，所以它能够抛出400响应码而不是500响应码。

- 类`tornado.web.UIModule(handler)`

    在一个页面中可重用的，模块化的UI单元。

    UI模块通常执行额外的查询，可以包含额外的CSS和Javascript，这些代码将会自动插入到
    渲染的页面中。

    UIModule的子类必须重写`render`方法。

    - `render(*args, **kwargs)`

        子类中重写，返回这个模块的输出。

    - `embeded_javascript()`

        重写来返回嵌入到这个页面中的JavaScript字符串。

    - `javascript_files()`

        重写来返回这个模块需要的JavaScript文件列表。

        如果返回的值是相对路径，它们将使用`RequestHandler.static_url()`来转义。

    - `embedded_css()`

        重写来返回嵌入到这个页面中的CSS字符串。

    - `css_files()`

        重写来返回这个模块需要的CSS文件列表。

        如果返回的值是相对路径，它们将使用`RequestHandler.static_url()`来转义。

    - `html_head()`

        重写来返回放置于`<head/>`元素之前的字符串。

    - `html_body()`

        重写来返回放置于`<body/>`元素之前的字符串。

    - `render_string()`

        重写一个模版，并将它以字符串返回。


- 类`tornado.web.ErrorHandler(application, request, **kwargs)`

    对所有请求生成一个带`status_code`的错误响应。

- 类`tornado.web.FallbackHandler(application, request, **kwargs)`

    一个包裹其它HTTP服务器回调的`RequestHandler`。

    它接受的fallback关键字参数必须是可调用对象，并且可以接受一个`HTTPServerRequest`，以及一个
    `Application`或者`tornado.wagi.WAGIContainer`。这个类最有用的情况是在一个
    服务器同时使用Tornado的`RequestHandlers`和WSGI。典型用法：

    ```python
    wsgi_app = tornado.wsgi.WSGIContainer(
        django.core.handlers.wsgi.WSGIHandler()
    )

    application = tornado.web.Application([
        (r"/foo", FooHandler),
        (r".*", FallbackHandler, dict(fallback=wsgi_app)),
    ])
    ```

- 类`tornado.web.RedirectHandler(application, request, **kwargs)`

    将所有的GET请求重定向到给定的URL。

    你需要对这个handler提供一个关键字参数参数`url`:

    ```python
    application = tornado.web.Application([
        (r"/oldpath", tornado.web.RedirectHandler, {"url": "/newpath"}),
    ])
    ```

    `RedirectHandler`支持正则表达式替换：

    ```python
    application = tornado.web.Application([
        (r"/(.*?)/(.*?)/(.*)", tornado.web.RedirectHandler, {"url": "/{1}/{0}/{2}"}),
    ])
    ```

    最后的URL将会以`str.format()`方法来格式化。在上面的例子中，针对`/a/b/c`URL的请求
    将会格式化为：

    ```python
    str.format("/{1}/{0}/{2}", "a", "b", "c") # -> "/b/a/c"
    ```

- 类`tornado.web.StaticFileHandler(application, request, **kwargs)`

    一个简单的handler，可以针对一个文件夹伺服静态内容。

    如果你设置了setting`static_path`，那么就会自动配置一个`StaticFileHandler`。
    这个handler可以通过settings`static_url_prefix`, `static_handler_class`,
    `static_handler_args`来自定义。

    想要为静态文件夹的映射URL加入额外路径，可以这样：

    ```python
    application = tornado.web.Application([
        (r"/content/(.*)", web.StaticFileHandler, {"path": "/var/www"}),
    ])
    ```

    这个handler构造器要求必须传入一个`path`参数，它会指定要伺服的本地根目录。

    注意正则中的捕获组是必须的，它解析的值将会以`path`参数传入到`get()`方法中(注意和
    构造器中的同名参数不一样)。

    想要在请求一个目录时自动伺服一个类似`index.html`的文件，为你的setting添加
    `static_handler_args=dict(default_filename='index.html')`或者
    为你自己的`StaticFileHandler`添加一个初始化参数`default_filename`。

    想要最大化浏览器缓存的性能，这个类支持版本URL(默认使用参数`?v=`)。如果给定一个版本，
    我们发出指令让浏览器无期限缓存这个文件。`make_static_url`(也可以在
    `RequeHandler.static_url`中获取)可以用来构造一个版本URL。

    这个handler主要用于开发用途和轻量级的文件伺服；对于高流量的情况下，为了更好的性能最好
    使用专门的静态文件伺服(比如nginx或Apache）。我们支持HTTP的`Accept-Ranges`机制
    来返回部分内容（因为浏览器需要这个功能来实现HTML5的video和audio浏览）。

    **继承的注意事项**

    这个类设计通过继承来扩展，但是因为静态URL是通过类方法而不是实例方法来生成的，这个类的
    继承模式稍微有些不同。在重写一个类方法时确保使用装饰器`@classmethod`。实例方法可能
    会用到这些属性：`self.path`, `self.absolute_path`, `self.modified`。

    子类应该只重写这章节讨论的方法；重写其它的方法会容易导致错误。重写`StaticFileHandler.get`
    是尤其容易出问题的，因为它和`compute_etag`和其它方法紧密耦合。

    想要改变静态url的生成方式(比如想匹配其它服务器或者CDN)，请重写:

    - `make_static_url`

    - `parse_url_path`

    - `get_cache_time`

    - `get_version`

    想要替换文件系统的交互方式(比如伺服数据库的内容），请重写：

    - `get_content`

    - `get_conetent_size`

    - `get_modifed_time`

    - `get_absolute_path`

    - `validate_absolute_path`

    方法介绍：

    - `compute_etag()`

        根据静态URL的版本来设置Etag头部。

        这将会允许针对缓存版本高效的`If-None-Match`检查，对一部分response发送正确的
        `Etag`。

    - `set_headers()`

        对response设置内容和缓存头部。

    - `should_return_304()`

        如果头部应该返回状态码304，这个方法返回True。

    - 类方法`get_absolute_path(root, path)`

        返回path针对root的绝对路径。

        `root`是这个`StaticFileHandler`配置的path(多数情况是setting`static_path`)。

        这个类方法可以在子类中重写。默认会返回一个文件系统路径，但是可以通过
        重写`get_content`来理解这个字符串。

    - `validate_absolute_path(root, absolute_path)`

        验证和返回绝对路径。

        `root`是这个`StaticFileHandler`配置的path，`path`是`get_absolute_path()`
        返回的结果。

        这是一个实例方法，在请求处理阶段被调用，所以它可能会抛出`HTTPError`错误或者
        使用`RequestHandler.redirect()`方法。如果静态文件不存在，就会返回404错误。

        这个方法可能在返回路径之前修改它，但是注意这个修改不会被`make_static_url`理解。

        在实例方法中，这个方法的结果可以通过`self.absolute_path`获取。

    - 类方法`get_content(abspath, start=None, end=None)`

        通过给定的绝对路径取回请求的静态资源内容。

        这个类方法可以在子类中重写。注意它的参数签名和其它类方法不一样(没有`settings`参数)。

        这个方法应该返回一个byte字符串或者一个byte字符串的迭代器。后者对大型文件适用并且
        会大幅减少内存碎片。

    - 类方法`get_content_version(abspath)`

        通过给定的路径返回这个资源的版本字符串。

        这个类方法可以在子类中重写。默认的实现是返回文件内容的hash。

    - `get_content_size()`

        pass



