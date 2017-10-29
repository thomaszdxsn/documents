[TOC]

## tornado.routing - 基础路由实现

弹性的路由实现。

Tornado使用`Router`将HTTP请求路由自相应的handler。`tornado.web.Application`类
是一个Router实现，可以直接使用它，或者使用模块中的类来增加额外的弹性。`RuleRouter`相比Application可以匹配更加多的标准，或者可以继承`Router`来实现最大幅度的自定义。

`Router`接口扩展`HTTPServerConnectionDelegate`来提供额外的路由能力。这意味着任何Router实现都可以直接用于`HTTPServer`构造器中的`request_callback`。

`Router`子类必须实现一个`find_handler`方法，提供一个合适的`HTTPMessageDelegate`实例来处理请求：

```python
class CustomRouter(Router):
    def find_handler(self, request, **kwargs):
        # 一些路由逻辑提供一个合适的HTTPMessageDelegate实例
        return MessageDelegate(request.connection)


class MessageDelegate(HTTPMessageDelegate):
    def __init__(self, connection):
        self.connection = connection

    def finish(self):
        self.connection.write_headers(
            ResponseStartLine("HTTP/1.1", 200, "OK"),
            HTTPHeaders({"Content-Length": "2"}),
            b"OK"
        )
        self.connection.finish()

router = CustomerRouter()
server = HTTPServer(router)
```

Router的主要责任就是为一个请求和`HTTPMessageDelegate`之间提供一个映射。在这个例子中，我们看到设置路由甚至不需要实例化一个Application。

下面是一个简单的例子，将我们如何路由到一个RequestHandler子类:

```python
resources = {}

class GetResource(RequestHandler):
    def get(self, path):
        if path not in resources:
            raise HTTPError(404)
        self.finish(resouces[path])


class PostResouce(RequestHandler):
    def post(self, path):
        resources[path] = self.request.body


class HTTPMethodRouter(Router):
    def __init__(self, app):
        self.app = app

    def find_handler(self, request, **kwargs):
        handler = GetResource if request.method == 'GET' else PostResouce
        return self.app.get_handler_delegate(request, handler, path_args=[request.path])

router = HTTPMethodRouter(Application())
server = HTTPServer(router)
```

`ReversibleRouter`接口增加了区分路由和使用路由名和额外参数解析原始url的功能。`Application`本身就是一个`ReversibleRouter`的实现。

`RuleRouter`和`ReversibleRuleRouter`都实现了Router和ReversibleRouter接口，可以用来创建一个以rule为基础的路由配置。

`Rule`的实例可以包含一个`Matcher`,它可以提供一个逻辑来决定是否这个rule能否匹配特定的请求和目标，可以是下面的一种：

1. 一个`HTTPServerConnectionDelegate`的实例:

```python
router = RuleRouter([
    Rule(PathMatches("/handler"), ConnectionDelegate()),
    # ...更多规则
])

class ConnectionDelegate(HTTPServerConnectionDelegate):
    def start_request(self, server_conn, request_conn):
        return MessageDelegate(request_conn)
```

2. 一个接受单个参数的`HTTPServerRequest`类型可调用对象：

```python
router = RuleRouter([
    Rule(PathMatches("/callable"), request_callable)
])


def request_callable(request):
    request.write(b"HTTP/1.1 200 OK\r\nContent-Length: 2\r\n\r\nOK")
    request.finish()
```

3. 另一个`Router`实例：

```python
router = RuleRouter([
    Rule(PathMatches("/router.*"), CustomRouter())
])
```

当然，也允许使用嵌套的`RuleRouter`和`Application`:

```python
router = RuleRouter([
    Rule(HostMatches("example.com"), RuleRouter([
        Rule(PathMatches("/app1/.*"), Application([r"/app1/handler", Handler]))
    ]))
])

server = HTTPServer(router)
```

下面例子中`RuleRouter`用来建立两个应用间的路由：

```python
app1 = Application([
    (r"/app1/handler", Handler1),
    # 其它handlers
])

app2 = Application([
    (r"/app2/handler", Handler2),
    # 其它handlers
])

router = RuleRouter([
    Rule(PathMatches('/app1.*'), app1),
    Rule(PathMatches('/app2.*'), app2),
])

server = HTTPServer(router)
```

- 类`tornado.routing.Router`

    抽象router接口。

    - `find_handler(request, **kwargs)`

        必须实现这个方法，返回请求匹配的一个`HTTPMessageDelegate`实例。路由实现可以传入额外的关键字参数来扩展路由逻辑。

        参数：

        - `request`: 当前的HTTP请求。
        - `kwargs`: 传入实现路由的额外关键字参数。

        **返回**：一个`HTTPMessageDelegate`的实例，用来处理这个请求。

- 类`tornado.routing.ReversibleRouter`

    抽象路由接口，可以将请求路由至handler，也可以反向将handler解析为原始的url。

    - `reverse_url(name, *args)`

        通过给定的路由名称和参数返回匹配的URL字符串，如果没有匹配则返回None。

        参数：

        - `name`: 路由名称
        - `args`: URL参数

        **返回**： 返回参数化后的URL字符串。

- `tornado.routing.RuleRouter(rules=None)`

    以规则为基础的Router实现。

    通过排序的规则列表来构造一个router：

    ```python
    RuleRouter([
        Rule(PathMatches("/handler"), Target),
        # ...更多规则
    ])
    ```

    你也可以忽略显式的`Rule`构造器，使用元组参数的形式:

    ```python
    RuleRouter([
        (PathMatches("/handler"), Target),
    ])
    ```

    `PathMatches`是默认的matcher，所以上面的例子可以简化为：

    ```python
    RuleRouter([
        ("/handler", Target),
    ])
    ```

    在上面的例子中，`Target`可以是一个嵌套的`Router`实例，一个`HTTPServerConnectionDelegate`的实例，或者一个老式风格的可调用对象，它们都接受一个request参数。

    参数：

    - `rules`: 一个Rule实例或者Rule构造器参数元组的列表。
    
    方法：

    - `add_rules(rules)`

        为router追加新的rules。

        参数:

        - `rules`: 一个Rule实例的列表(或者参数形式元组)

    - `process_rule(rule)`

        重写这个方法，可以为每个rule增加预处理。

        参数:

        - `rule`: 一个要处理的rule。

        返回:

        相同的或被处理后的Rule实例。

    - `get_target_delegate(target, request, **target_params)`

        对一个Rule目标返回一个`HTTPMessageDelegate`实例。这个方法通过`find_handler`调用，可以扩展来提供额外的目标类型。

        参数：

        - `target`: 一个Rule目标
        - `request`: 当前的请求对象
        - `target_params`: 用于`HTTPMessageDelegate`的额外参数

- `tornado.routing.ReversibleRuleRouter(rules=None)`

    一个以规则为基础的router，并且实现了`reverse_url`方法。

    每个加入到这个router的规则应该都有一个`name`属性，用来重构原始的URI。

- `tornado.routing.Rule(matcher, target, target_kwargs=None, name=None)`

    构建一个Rule实例。

    参数：

    - `matcher`: 一个Matcher实例，用来决定一个规则是否匹配一个特定的请求。
    - `target`: 一个Rule的目标(通常是一个`RequestHandler`或者`HTTPServerConnectionDelegate`子类，甚至可以是一个嵌套的`Router`)
    - `target_kwargs`: 一个参数字典，在target实例化的时候很有用。
    - `name`: 这个规则的名称，可以用来逆向获得URI。

- `tornado.routing.Matcher`

    相当于一个请求的匹配器。

    方法：

    - `match(request)`

        匹配当前实例和请求。

        参数：

        - `request`: 当前的HTTP请求。

        返回：一个参数字典，将会传入到目标handler中(比如`handler_kwargs`, `path_args`, `path_kwargs`)

    - `reverse(*args)`

        通过给定的实例和额外的参数重构完整的URL。

- `tornado.routing.AnyMatches`

    匹配任何请求。

- `tornado.routing.HostMatches(host_pattern)`

    通过`host_pattern`正则模式串来匹配请求的host。

- `tornado.routing.DefaultHostMatches(application, host_pattern)`

    请求匹配的host，等同于应用中的`default_host`。如果使用`X-Real-Ip`，总是返回不匹配。

- `tornado.routing.PathMatches(path_pattern)`

    通过给定的`path_pattern`正则模式串来匹配请求的路径。

- `tornado.routing.URLSpec(pattern, handler, kwargs=None, name=None)`

    设定URL和handler之间的映射。

    参数：

    - `pattern`: 用于匹配的正则表达式。任何捕获组中的值将会传入到handler的HTTP动词方法中(get/post/等等)。
    - `handler`: 想要调用的`RequestHandler`子类。
    - `kwargs`: 传入handler构造器的额外参数(关键字参数)
    - `name`: 这个handler(或者说这个匹配URLSpec)的名称，用于`reverse_url()`方法。

    