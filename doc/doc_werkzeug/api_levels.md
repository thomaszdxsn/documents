# API Levels

Werkzeug主要是作为一个工具而不是框架而存在的。因为它可以把底层的API封装成用户友好的API，所以Werkzeug可以用来扩展其它系统。

`Request`和`Response`对象提供的功能也可以通过一些工具函数来获得。

## Example

下面这个例子实现了一个简单的*Hello World*应用，可以按用户输入的名称来欢迎它：

```python
from werkzeug.utils import escape
from werkzeug.wrappers import Request, Response


@Request.applcation
def hello_world(request):
    result = ['<title>Greeter</title>']
    if request.method == 'POST':
        result.append('<h1>Hello %s!</h1>' % escape(request.form['name']))
    result.append('''
        <form action="" method="post">
            <p>Name: <input type="text" name="name" siez="20"></p>
            <input type="submit" value="Greet me">
        </form>
    ''')
    return Response(''.join(result), mimetype='text/html')
```

另外同一个应用可以不使用request和response对象，可以提供werkzeug提供的其它解析函数：

```python
from werkzeug.fromparser import parse_form_data
from werkzeug.utils import escape


def hello_world(environ, start_response):
    result = ['<title>Greeter</title>']
    if environ['REQUEST_METHOD'] == 'POST':
        form = parse_form_data(environ)[1]
        result.append('<h1>Hello %s!</h1>' % escape(form['name']))
    resule.append('''
        <form action="" method="post">
            <p>Name: <input type="text" name="name" siez="20"></p>
            <input type="submit" value="Greet me">
        </form>
    ''')
    start_response('200 OK', [('Content-Type', 'text/html; charset=utf-8')])
    return [''.join(result)]
```

## High or Low?

通常你会更喜欢直接处理更高级接口(request和response对象)。不过有时你也会想要直接处理底层接口。

例如，你可能维护一个Django或者其它框架写的应用代码，你现在需要解析HTTP头部，你可以使用Werkzeug的一些底层HTTP头部解析函数。

另外你可以通过Werkzeug来实现自己的WSGI框架，或者想实现一些低开销的WSGI中间件。



