# Github README.md

werkzeug是一个德语的名词，代表：工具('tool'). werk('work'), zeug('stuff')

Werkzeug是一个综合型的WSGI web应用库。它最开始由很多WSGI application工具组成，
现在可能是最高级的一个WSGI工具库了。

包含:

- 一个交互式的debugger，允许在浏览器中看到堆栈回溯以及源代码.

- 一个拥有完整特性的request对象，可以以对象的方式和头部，query-string，
form数据，文件，cookies进行交互。

- 一个response对象，可以封装WSGI application，处理streaming数据。

- 一个路由系统，可以匹配URLs和端点，还可以从URLs中获取变量。

- 一些HTTP工具，可以用来处理ETag，缓存，日期，user-agents，cookies，files等等。

- 一个基于线程的WSGI server，可以用来在本地开发app。

- 一个test client，在测试的时候可以模拟HTTP请求，不需要运行一个server。

Werkzeug是基于Unicode的，不需要额外的依赖。

可以让开发者决定使用哪种模版引擎，数据库，甚至如何处理request。

可以用它来开发所有的端用户app(end user applications)，比如blogs, wikis, bulletin boards).

Flask封装了Werkzeug，使用它来处理WSGI的细节。

## Installing

`$ pip install -U Werkzeug`

## A Simple Example

```python
from werkzeug.wrappers import Request, Response


@Request.application
def application(request):
    return Response('Hello, World!')


if __name__ == '__main__':
    from werkzeug.serving import run_simple
    run_simple('localhost', 4000, application)
```
