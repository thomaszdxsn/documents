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

## Mutability and Reusability of Wrappers

Werkzeug的request和response对象的实现会保护你不掉入常见的陷阱中，所以它会限制
你做一些事情。

它主要有两个目标：高性能和避免陷阱。

对于request对象，有下面的一些规则:

1. request对象是不可变的。默认不支持修改，如果你真的想要修改，你可以把不可变属性
替换为可变属性。

2. request对象在同一个线程内共享，但是它本身不是线程安全的。如果你需要多线程
来访问同一个对象，请使用lock。

3. request对象不是可以pickle的。

对于response对象，有下面这些规则：

1. response对象是可变的。

2. reponse对象在调用`freeze()`之后是可以被pickle或者copy的

3. 在Werkzeug0.6开始，可以在多个WSGI response中使用同一个response对象.

4. 可以通过`copy.deepcopy`创建copy.

## Base Wrappers

这些对象实现了一套通用的操作。但是很多有用的功能没有实现，别入user-agent解析
和etag处理。这些特性可以通过加入Mixin来实现。

- class `werkzeug.wrappers.BaseRequest(environ, populate_request=True, shallow=False)`

    非常基本的request对象.

    并没有实现高级特性，如Etag解析或者缓存控制。

    Request对象通过将WSGI environ作为首个参数来实现，并且会把它自己加入到WSGI environ
    中，叫做`werkzeug.request`。除非设置`populate_request=False`.

    有很多Mixin可以加入到这个类中，用以实现更多的功能，另外有一个`Request`类，
    它是`BaseRequest`的子类，加入了所有重要的Mixin。

## TODO

终止werkzeug框架的学习，改为aiohttp


