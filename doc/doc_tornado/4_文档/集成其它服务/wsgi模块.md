## tornado.wsgi -- 和其它Python框架/服务器相互操作

Tornado web服务器支持WSGI操作。

WSGI是Python web服务器的标准，允许Tornado和其它Python服务器之间相互操作。这个模块有两种方式支持WSGI：

- `WSGIAdapter`: 将一个`tornado.web.Application`转换为一个WSGI应用接口。在你想要将tornado运行在其它服务器上面的时候会很有用，比如Google app engine。
- `WSGIContainer`: 让你在Tornado服务器上面运行其它的WSGI应用和框架。例如，用这个类你可以在单个服务器上面混合使用Django和Tornado。

### 在WSGI服务器上面运行Tornado

- `tornado.wsgi.WSGIAdapter`

    将一个`tornado.web.Application`转换为一个WSGI应用。

    例子：

    ```python
    import tornado.web
    import tornado.wsgi
    import wsgiref.simple_server

    
    class MainHandler(tornado.web.RequestHandler):
        def get(self):
            self.write("Hello World")


    if __name__ == "__main__":
        application = tornado.web.Application([
            (r"/", MainHandler)
        ])
        wsgi_app = tornado.wsgi.WSGIAdapter(application)
        server = wsgiref.simple_server.make_server("", 8888, wsgi_app)
        server.server_forever()
    ```

    在WSGI模式下，异步方法不再被支持。意味着你不可以使用`AsyncHTTPClient`，`tornado.auth`，`tornado.websocket`。

- `tornado.wsgi.WSGIApplication(handlers=None, default_host=None, transformsNone, **settings)`

    一个等同于`tornado.web.Application`的WSGI应用。


### 在Tornado服务器上面运行WSGI应用

- `tornado.wsgi.WSGIContainer`

    制造一个兼容WSGI的函数，可以运行TornadoHTTP服务器。

    > 警告
    >
    >> WSGI是一个同步接口，但是Tornado的并发基于单线程异步执行。意味着在Tornado的`WSGIContainer`中运行一个WSGI应用，相比多线程的WSGI服务器如`gunicorn`或者`uwsgi`，速度将会慢很多．

    将一个WSGI函数使用`WSGIContainer`封装并传入到`HTTPServer`中：

    ```python
    def simple_app(environ, start_response):
        status = "200 OK"
        response_headers = [("Content-type", "text/plain")]
        start_response(status, response_headers)
        return ['Hello World\n']

    container = tornado.wsgi.WSGIContainer(simple_app)
    http_server = tornado.httpserver.HTTPServer(container)
    http_server.listen(8888)
    tornado.ioloop.IOLoop.current().start()
    ```

    这个类的作用就是让其它的框架（Django, web.py等)运行在Tornado的HTTP服务器上面．

    `tornado.web.FallbackHandler`通常用来将Tornado和WSGI应用在一个服务器混用．

    - 静态方法`environ(request)`

        将一个`tornado.httutil.HTTPServerRequest`转换为一个WSGI环境.
