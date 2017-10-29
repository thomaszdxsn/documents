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

pass

