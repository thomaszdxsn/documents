# Quickstart

这篇文档展示了如何使用Werkzeug中最重要的部分。它需要开发者对于[PEP333](https://www.python.org/dev/peps/pep-0333)(WSGI)和[RFC2616](https://tools.ietf.org/html/rfc2616.html)(HTTP)有基本的理解。

## WSGI Environment

WSGI environment包含了用户请求引用的一些信息。

它会传入到WSGI application，但是你可以通过`create_environ()`来创建一个WSGI environ dict.

```python
>>> from werkzeug.test import create_environ
>>> environ = create_environ('/foo', 'https://localhost:8080/')
```

现在我们有了一个environ:

```python
>>> environ['PATH_INFO']
'/foo'
>>> environ['SCRIPT_NAME']
''
>>> environ['SERVER_NAME']
'localhost'
```

一般来说，用户不需要直接访问environ，因为它必须使用bytestrings。

## Enter request

想要访问request数据，可以使用Request对象。

它封装了`environ`，对其中的数据提供了自读访问：

```python
>>> from werkzeug.wrappers import Request
>>> request = Request(environ)
```

现在你可以访问其中的变量了，Werkzeug会为你解析它并且将它解码。


默认的字符集设置为`utf8`，但是你可以通过继承`Request`来修改字符集:

```python
>>> request.path
u'/foo'
>>> request.script_root
u''
>>> request.host
'localhost:8080'
>>> request.url
'http://localhost:8080/foo'
```

还可以查看这次请求使用的方法:

```python
>>> request.method
'GET'
```

我们可以访问URL参数(即query string)，以及POST/PUT请求带入的数据。

处于测试，我们可以自行创建一个request对象，使用`from_values()`来提供数据：

```python
>>> from cStringIO import StringIO
>>> data = 'name=this+is+encodeed+form+data&another_key=another+one'
>>> request = Request.from_values(
...     query_string='foo=bar&blah=blafasel',
...     content_length=len(data),
...     input_stream=StringIO(data),
...     content_type='application/x-www-form-urlencoded',
...     method='POST')
...
>>> request.method
'POST'
```

我们可以这样访问它的URL参数:

```python
>>> request.args.keys()
['blah', 'foo']
>>> request.args['blah']
u'blafasel'
```

可以这样来访问它的数据:

```python
>>> request.form['name']
u'this is encoded form data'
```

处理上传的文件也并不会很难:

```python
def store_file(request):
    file = request.files.get('my_file')
    if file:
        file.save('/where/to/store/the/file.txt')
    else:
        handle_the_error()
```

文件通过`FileStorage`对象来代表。

可以通过`headers`属性来访问request的头部：

```python
>>> request.headers['Content-Length']
'54'
>>> request.haders['Content-Type']
'application/x-www.form-urlencoded'
```

## Header Parsing

让我们创建一个request对象，提供一个正常浏览器提供的所有数据:

```python
>>> environ = create_environ()
>>> environ.update(
...     HTTP_USER_AGENT='Mozilla/5.0 (Macintosh; U; Mac OS X 10.5; en-US; ) Firefox/3.1',
...     HTTP_ACCEPT='text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
...     HTTP_ACCEPT_LANGUAGE='de-at,en-us;q=0.8,en;q=0.5',
...     HTTP_ACCEPT_ENCODING='gzip,deflate',
...     HTTP_ACCEPT_CHARSET='ISO-8859-1,utf-8;q=0.7,*;q=0.7',
...     HTTP_IF_MODIFIED_SINCE='Fri, 20 Feb 2009 10:10:25 GMT',
...     HTTP_IF_NONE_MATCH='"e51c9-1e5d-46356dc86c640"',
...     HTTP_CACHE_CONTROL='max-age=0'
... )
...
>>> request = Request(environ)
```

让我们从最没用的头部开始：user agent:

```python
>>> request.user_agent.browser
'firefox'
>>> request.user_agent.platform
'macos'
>>> request.user_agent.version
'3.1'
>>> request.user_agent.language
'en-US'
```

更有用的头部是accept头部。这些浏览器传入的头部可以告诉web应用它可以处理那些mimetypes。

```python
>>> request.accept_mimetypes.best
'text/html'
>>> 'application/xhtml+xml' in request.accept_mimetypes
True
>>> print(request.accept_mimetypes['application/json'])
0.8
```

accept_language也一样:

```python
>>> request.accept_language.best
'de-at'
>>> request.accept_languages.values()
['de-at', 'en-us', 'en']
```

当然还有encoding和charset：

```python
>>> 'gzip' in request.accept_encodings
True
>>> request.accept_charsets.best
'ISO-8859-1'
>>> 'utf-8' in request.accept_charsets
True
```

你可以对它们执行包含检查:

```python
>>> 'UTF8' in request.accept_charsets
True
>>> 'de_AT' in request.accept_languages
True
```

其它的可以被解析的头部:

```python
>>> request.if_modified_since
datetime.datetime(2009, 2, 20, 10, 10, 25)
>>> request.if_none_match
<ETags '"e51c9-1e5d-46356dc86c640"'>
>>> request.cache_control
<RequestCacheControl 'max-age=0'>
>>> request.cache_control.max_age
0
>>> 'e51c9-1e5d-46356dc86c640' in request.if_none_match
True
```

## Responses

Response对象是request相反方面的对象。它可以将数据返回给客户端。

想象你有一个标准的WSGI “hello world”应用：

```python
def application(environ, start_response):
    start_response('200 OK', [('Content-Type', 'text/plain')])
    return ['Hello World!']
```

也可以直接返回Response对象:

```python
from werkzeug.wrappers import Response

def application(environ, start_response):
    response = Response('Hello World!')
    return response(environ, start_response)
```

另外，和request对象不一样，response对象是可以修改的。

```python
>>> from werkzeug.wrappers import Response
>>> response = Response('Hello World')
>>> response.headers['content-type']
'text/plain; charset=utf-8'
>>> response.data
'Hello World!'
>>> response.headers['content-length'] = len(response.data)
```

你可以以同样的方式修改response的状态码：

```python
>>> response.status
'200 OK'
>>> response.status = '404 Not Found'
>>> response.status_code
404
>>> response.status_code = 400
>>> response.status
'400 BAD REQUEST'
```

你可以看到`status`和`status_code`这两个属性会互相影响。所以请设置正确的状态码。

response头部被暴露为一个属性或者一些set/get方法:

```python
>>> response.content_length
12
>>> from datetime import datetime
>>> response.date = datetime(2009, 2, 20, 17, 42, 51)
>>> response.headers['Date']
'Fri, 20 Feb 2009 17:42:51 GMT'
```

因为etags分为weak和strong两种，所以可以通过方法来设置它:

```python
>>> response.set_etag('12345-abcd')
>>> response.headers['etag']
'"12345-abcd"'
>>> response.get_etag()
('12345-abcd', False)
>>> response.set_etag("12345-abcd", weak=True)
>>> response.get_etag()
('12345-abcd', True)
```

一些头部属性可以是可变对象。例如Content-头部的属性就是set对象:

```python
>>> response.content_language.add('en-us')
>>> response.content_language.add('en')
>>> response.headers['Content-Language']
'en-us, en'
```

除了通过属性设置，也可以通过headers字典:

```python
>>> response.headers['Content-Language'] = 'de-AT, de'
>>> response.content_language
HeaderSet(['de-AT', 'de'])
```

鉴权头部可以这样来设置:

```python
>>> response.www_authenticate.set_basic("My protected resource")
>>> response.headers['www-authenticate']
'Basic realm="My protected resource"'
```

Cookies可以这样:

```python
>>> response.set_cookie('name', 'value')
>>> response.headers['Set-Cookie']
'name=value; Path=/'
>>> response.set_cookie('name2', 'value2')
```

如果一个头部出现多次，你可以使用`.getlist()`方法取回所有头部:

```python
>>> response.headers.getlist('Set-Cookie')
['name=value; Path=/', 'name2=value2; Path=/']
```


