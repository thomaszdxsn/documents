[TOC]

## tornado.websocket -- 和浏览器的双向通信

实现**Websocket协议**.

[Websocket](http://dev.w3.org/html5/websockets/)允许浏览器和服务器之间实现双向通信。

Websocket目前已经被大多数浏览器支持。

这个模块(`tornado.websocket`)实现了Websocket在[RFC6455](http://tools.ietf.org/html/rfc6455)中定义的最终版本。有些浏览器版本实现的是早期的草案协议(称为"草案76")，和这个模块并不兼容。

- `tornado.websocket.WebSocketHandler(application, request, **kwargs)`

    继承这个类来创建一个基础的WebSocker handler。

    重写`on_message()`方法来处理刚收到的消息，使用`write_message()`来把消息发送到客户端。你同样可以重写`open()`和`close()`来处理连接的开启和关闭。

    自定义upgrade response头部，可以通过`set_default_headers()`或`prepare()`来实现。

    请看[http://dev.w3.org/html5/websockets/](http://dev.w3.org/html5/websockets/)获取JavaScript接口的细节。

    下面是一个WebSocket handler的例子，它将收到的消息返回给客户端：

    ```python
    class EchoWebSocket(tornado.websocket.WebSocketHandler):
        def open(self):
            print("WebSocket 开启")
        
        def on_message(self, message):
            self.write(u"你说: " + message)

        def on_close(self):
            print("WebSocket 关闭")
    ```

    WebSocket并不是标准的HTTP连接。“握手”仍然使用HTTP，但是在握手之后，这个协议是以消息为基础的。因此，多数Tornado HTTP设施并不支持在这个handler中使用。通信的方法只包含`write_message()`, `ping()`以及`close()`。同样的，你的请求handler应该实现`open()`方法而不是`get()`或者`post()`。

    如果你将上面的handler映射到`/websocket`，你可以在JavaScript中这么调用：

    ```python
    var ws = new WebSocket("ws://localhost:8888/websocket")
    ws.onopen = function() {
        ws.send("Hello World");
    }
    ws.onmessage = function(evt) {
        alert(evt.data);
    }
    ```

    这个JS脚本将会弹出一个alert框，上面显式:"You said: Hello, world"。

    web浏览器允许任何站点开启一个websocket连接，而不是使用相同源政策。这是很让人惊讶的并且是一个潜在的安全漏洞，所以自从Tornado4.0开始`WebSocketHandler`要求应用通过重写`check_origin`来检查跨站信息。如果检查失败，将会抛出403错误。

    当使用安全的websocket连接(`wss://`)以及一个自签名验证时，浏览器的连接可能会失败，应为它想要显式一个"accept this certificate"对话框但是不知道在哪里显式它。在websocket连接成功之前，你必须受用相同的验证访问一个常规的HTML页面。

    如果这个app的setting`websocket_ping_interval`是一个非零值，将会周期性地发送ping，在`websocket_ping_timeout`之前没有收到一个response的话，这个连接将会关闭。

    大于setting`websocket_max_messsage_size`(默认为10M)的消息将不会被接收。

### 事件handler

- `WebSocketHandler.open(*args, **kwargs)`

    在一个新的WebSocket开启时被调用。

    `open()`的参数提取自`tornado.web.URLSpec`正则表达式，就像`RequestHandler.get`获取参数的方式一样。

- `WebSocketHandler.on_message(message)`

    在WebSocket中处理刚接收的消息。

    这个方法必须重写。

- `WebSocketHandler.on_close()`

    在一个WebSocket关闭时被调用。

    如果一个连接被干净的关闭，将会发出一个状态码和rason短语，它们的值可以通过属性`self.close_code`和`self.close_reason`获取。

- `WebSocketHandler.select_subprotocol(subprotocols)`

    在一个新的WebSocket请求特定的子协议时被调用。

    `subprotocols`是一个字符串列表，代表客户端要求自子协议的标识符。这个方法可以重写来选择其中的一个字符串。选择自协议失败并不会自动关闭连接，但是客户端如果没有选择到子协议那么就会关闭连接。

- `WebSocketHandler.on_ping(data)`

    在收到一个ping frame(包)时调用。

### 输出

- `WebSocketHandler.write_message(message, binary=False)`

    发送给定的消息到WebSocket的客户端。

    这个消息可以是字符串或者字典(将会被编码为JSON)。如果`binary=False`，这个消息会以utf-8形式发送，否则任何byte格式都可以接收。

    如果连接已经关闭，抛出`WebSocketClosedError`。

- `WebSocketHandler.close(code=None, reason=None)`

    关闭这个WebSocket。

    一旦关闭“握手”成功，这个socket将会被关闭。

    `code`可以是一个数字状态码，可以从[RFC 6455 section 7.4.1.](https://tools.ietf.org/html/rfc6455#section-7.4.1)中定义的状态码中选取一个。`reason`是关于连接关闭的文本型消息。这个消息可以在客户端获取，但是并不被WebSocket协议解释。


### 配置


- `WebSocketHandler.check_origin(origin)`

    重写这个方法来支持可以更换的origin。

    `origin`参数是HTTP头部`Origin`的值，这是一个负责初始化这个请求的URL。这个方法并不被客户端调用去发送这个头部；而是说这样的请求总是被允许(因为所有实现WebSocket的浏览器都支持这个头部，非浏览器客户端没有同样的跨站安全问题)。

    如果返回True即接收请求，返回False即拒绝。默认会拒绝所有origin与本服务器不相符的请求。

    这是一个安全防护功能，确保不会受到浏览器跨站脚本的攻击，因为WebSocket允许绕过通常的同源政策并且没有使用CORS头部。

    > 警告
    >> 这是一个重要的安全标准；如果不理解安全的复杂性不要禁用这个功能。特别是，如果你的验证是基于Cookie的，你必须要么通过`check_origin()`来限制origin，要么实现你自己的websocket-XSRF防护。

    想要接受所有的跨站流量(在Tornado4.0之前这是默认的)，只要重写这个方法并总是返回True即可：

    ```python
    def check_origin(self, origin):
        return True
    ```

    想要允许你站点的任何子域名可以连接，只需要这么作：

    ```python
    def check_origin(self, origin):
        parsed_origin = urllib.parse.urlparse(origin)
        return parsed_origin.netloc.endswith(".mydomain.com")
    ```

- `WebSocketHandler.get_compression_options()`

    重写这个方法返回连接的压缩选项。

    如果这个方法返回None(默认)，压缩将会被禁用。如果它返回一个字典(即使是空字典)，压缩也会被激活。字典的内容可以用来控制如下的压缩选项：

    - `compression_level`: 设定压缩等级。

    - `mem_level`: 设定内部压缩状态使用的内存总量。

    这些参数的讨论细节在这里：[https://docs.python.org/3.6/library/zlib.html#zlib. compressobj](https://docs.python.org/3.6/library/zlib.html#zlib. compressobj)

- `WebSocketHandler.set_nodelay(value)`

   设置这个流的no-delay(无延迟)标志。

   默认情况下，小的消息可能会延迟等待更多内容再打包成数据包发送。这可能会在Nagle算法和TCP延迟ACK之间的交互之间引起200-500ms的延迟。想要减少这个延迟(代价是会增加带宽的使用)，只要在websocket连接后调用`self.set_nodelay(True)`即可。

### 其它

- `WebSocketHandler.ping(data)`

    将ping数据包发送到远端。

- `WebSocketHandler.on_pong(data)`

    在接收到ping数据包时调用。

- 异常`tornado.websocket.WebSocketClosedError`

    在一个关闭的连接上进行操作，则会抛出这个异常。

### 客户端支持

- `tornado.websocket.websocket_connect(url, io_loop=None, callback=None, connect_timeout=None, on_message_callback=None, compression_options=None, ping_interval=None, ping_timeout=None, max_message_size=None)`

    客户端websocket支持。

    接收一个URL并返回一个Future，它的结果是一个`WebSocketClientConnection`.

    `compression_options`的选项和`WebSocketHandler.get_compression_options`的解释相同。

    这个连接支持两种风格的操作。在协程风格中，这个应用通常在一个循环中调用`read_message()`:

    ```python
    conn = yield websocket_connect(url)
    while True:
        msg = yield conn.read_message()
        if msg is None: break
        # 对msg做一些事情
    ```

    如果是callback风格，那么需要传入一个关键字参数`on_message_callback`。在两种风格中，一个值为None的message都意味着连接已经关闭。

- `tornado.websocket.WebSocketClientConnection(io_loop, request, on_message_callback=None, compression_options=None, ping_iterval=None, ping_timeout=None, max_message_size=None)`

    Websocket客户端连接。

    这个类不应该被直接实例化；使用`websocket_connect()`函数来替代它。

    - `close(code=None, reason=None)`

        关闭websocket连接。

    - `write_message(message, binary=False)`

        发送消息到WebSocket服务器。

    - `read_message(callback=None)`

        从一个WebSocket服务器接收消息。

        如果在WebSocket初始化时设定了`on_message_callback`，这个函数永远不会返回消息。

        如果有消息则会返回一个Future，如果连接关闭则会返回None。
        