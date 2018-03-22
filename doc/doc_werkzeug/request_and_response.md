# Request/Response Objects

`request`和`response`对象封装了一个WSGI app返回的WSGI environment，
所以它是另一个WSGI application.

## How they Work

你的WSGI application总是传入两个参数.WSGI "environ" 以及 WSGI `start_response`
函数，可以用来开启response阶段.

`request`类封装了`environ`，所以可以快速访问request变量(表单数据，request头部,等等).

`Response`是一个创建WSGI application的标准方式。下面是一个最简单的Werkzeug "hello world" app:

```python
from werkzeug.wrappers import Response
application = Response('Hello World!')
```

可以将它替换成一个函数:

```python
from werkzeug.wrappers import Request, Response


def application(environ, start_response):
    request = Request(environ)
    resposne = Response("Hello %s!" %request.args.get('name', "Hello!"))
    return response(environ, start_response)
```

因为这是非常常见的常见，所以Request对象提供了一个helper。

上面的代码可以重写成下面这样:

```python
from werkzeug.wrappers import Request, Response


@Request.application
def application(resquest):
    return Response("Hello %s! % request.args.get('name', 'Hello!'))
```

`application`仍然是一个合法的WSGI app，它仍然会接受envion和start_response，只是被
装饰器接受了.


