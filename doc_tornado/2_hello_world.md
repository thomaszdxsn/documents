下面是使用Tornado建立的简单“Hello World”web app例子：

```python
import tornado.ioloop
import tornado.web


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello World")


def make_app():
    return tornado.web.application([
        (r"/", MainHandler)
    ])


if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
```

这个例子没有用到Tornado的任何异步特性；

