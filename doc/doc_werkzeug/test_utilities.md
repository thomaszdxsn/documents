# Test Utilities

很多时候你都想对你的应用程序进行单元测试，或者通过REPL来检查输出.

理论上这是很简单的，只要模拟一个WSGI environ，然后通过一个伪造的`start_response`
可以迭代这个app迭代器。

## Diving in

Werkzeug提供了一个`Client`对象，让你传入到一个WSGI application中。你可以
将它看作是这个application的虚拟request。

response wrapper是一个可调用对象，它接受三个参数: application迭代器，status，
以及头部list。默认的response wrappers返回一个数组。

因为response对象拥有同样的参数签名，你可以将它作为response wrapper，最好是
继承它们并加入一个测试的钩子.

```python
>>> from werkzeug.test import Client
>>> from werkzeug.testapp import test_app
>>> from werkzeug.wrappers import BaseResponse
>>> c = Client(test_app, BaseResponse)
>>> resp = c.get('/')
>>> resp.status_code
200
>>> resp.headers
Headers([('Content-Type', 'text/html; charset=utf-8'), ('Content-Length', '8339')])
>>> resp.data.splitlines()[0]
'<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"'
```

或者不定义wrapper:

```python
>>> c = CLient(test_app)
>>> app_iter, status, headers = c.get('/')
>>> status
'200 OK'
>>> headers
[('Content-Type', 'text/html; charset=utf-8'), ('Content-Length', '8339')]
>>> ''.join(app_iter).splitlines()[0]
'<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"'
```

## Environment Building

和测试app交互最简单的方式是使用`EnvironBuilder`。它可以创建标准的WSGI envion和
request对象。

下面的示例创建了一个WSGI environ，包含一个上传文件字段，和一个普通的表单字段:

```python
>>> from werkzeug.test import EnvironBuilder
>>> from StringIO import StringIO
>>> builder = EnvironBuilder(
    method='POST',
    data={"foo": "this is some text",
...       "file": (StringIO("my file contents"), "text.txt)})
>>> env = builder.get_envion()
```

返回的envion是一个标准的WSGI environ，可以用来进一步处理:

```python
>>> from werkzeug.wrappers import Request
>>> req = Request(env)
>>> req.form['foo']
u"this is some text"
>>> req.files['file']
<FileStorage: u'test.txt' ('text/plain')>
>>> req.files['file'].read()
'my file contents'
```

如果你传入一个字典，`EnvironBuilder`会自动推算出内容类型。

如果你传入字符串或者一个input流，你需要自己传入内容类型。

默认情况下，它会推算使用`application/x-www-form-urlencoded`，只有在当碰到
文件上传的时候会使用`multipart/form-data`:

```python
>>> builder = EnvironBuilder(method='POST', data={'foo': 'bar'})
>>> builder.content_type
'application/x-www-form-urlencoded'
>>> builder.files['foo'] = StringIO('contents')
>>> builder.content_type
'multipart/form-data'
```

如果数据以字符串形式提供，你必须手动指定content type:

```python
>>> builder = EnvironBuilder(method='POST', data='{"json": "this is"}')
>>> builder.content_type
>>> builder.content_type = 'application/json'
```

## Testing API

- class`werkzeug.test.EnvironBuilder(path='/', base_url=None, query_string=None, method='GET', input_stream=NOne, content_type=None, content_length=None, errors_stream=None, multithread=False, multiprocess=False, run_once=False, headers=None, data=None, environ_base=None, envrion_overrides=None, charset='utf-8', mimetype=None)` 
    这个类可以用来创建测试用途的WSGI environment.

    它可以快速地创建WSGI environment或者request对象。

    这个类的签名和Werkzeug0.5的create_environ()，BaseResponse.from_values()，
    Client.open()相同。

    文件和表单数据可以通过form和files属性独立操作，也可以通过构造器属性data传入。

    data可以是下面这些值:

    - 一个str或者bytes对象：这个对象将会被转换为`input_stream`，`content_length`
    会自动搞定，但是你必须提供`content_type`.

    - 一个dict或者`MultiDict`。

        它的键必须是字符串，值可以是下列的对象：

        - 类file对象：它们会被自动转换为`FileStorage`对象.

        - 一个元祖: `add_file()`方法会调用这个键，元祖元素会作为位置参数.

        - 一个字符串：这个字符串会作为表单数据.

    - 一个类file对象：这个对象的内容会被读取到内存中，然后将它作为常规的str或bytes来处理.

    参数:

    - `path`:

        这个请求的path。在WSGI environment中这叫做*PATH_INFO*。如果没有传入
        query string，那么这个path的问好后面的部分就会作为query string.

    - `base_url`:

        base URL是一个用来提取WSGI URL scheme, host和script root的URL.

    - `query_strinh`:

        一个可选参数，作为query string。可以是字符串或者字典。

    - `method`:

        HTTP方法，默认为GET.

    - `input_stream`:

        一个可选的input stream，不要将它和`data`同时指定。

        只要设置了input stream，你就不能修改`args`和`files`了，除非将input stream
        重新设置回None.

    - `content_type`:

        这个请求的content type.

    - `content_length`:

        这个请求的content length.

    - `errors_stream`:

        一个可选的error stream，用于`wsig.errors`。默认为`stderr`.

    - `multithread`:

        控制`wsgi.multithread`。默认为False。

    - `multiprocess`:

        控制`wsgi.multiprocess`。默认为False。

    - `run_once`:

        控制`wsgi_run_once`。默认为False.

    - `headers`:

        一个可选的头部list。

    - `data`:

        见上面的解释...

    - `environ_base`:

        默认的environment，可选传入dict。

    - `environ_overrides`:

        environment overrides，可选传入dict

    - `charset`

        用于编码unicode数据的字符集.


    属性：

    ...


- class`werkzeug.test.Client(application, response_wrapper=None, use_cookies=True, allow_subdomain_redirects=False)`

    这个类用来发送请求给一个wrapped的应用。

    这个response wrapper可以是一个类或者工厂函数，它必须接受的那个参数:
    `app_iter, status, headers`。默认的response wrapper只会返回一个元祖.

    示例：

    ```python
    class ClientResponse(BaseResponse):
        ...

    client = Client(MyApplication(), response_wrapper=ClientResponse)
    ```

    `use_cookies`参数代表是否存储cookies，并且在随后的请求中发送这个cookies.
    默认为True。

    如果你想要请求你的应用中的一些子域名，你可以设置`allow_subdomain_redirects`
    为True。

    - `open(*args, **kwargs)`

        接受`EnvironBuilder`类相同的参数以及一些额外的参数：你可以直接传入一个
        `EnvironBuilder`对象或者一个WSGI environment。

        参数:

        - `as_tuple` 返回一个`(environ, result)`形式的元祖.
        - `buffered` 设置为True可以缓冲应用的运行。在应用关闭的时候，会自动为你关闭这个buffer。
        - `follow_redirects` 设置为True，Client将会跟随HTTP重定向.

    - `get(*args, **kw)`

    - `patch(*args, **kw)`

    - `post(*args, **kw)`

    - `head(*args, **kw)`

    - `put(*args, **kw)`

    - `delete(*args, **kw)`

    - `options(*args, **kw)`

    - `trace(*args, **kw)`

- `werkzeug.text.create_environ([options])`

    根据传入的值创建一个新的WSGI environ。

    第一个参数为request的path。

    第二个参数是一个绝对路径.

    其它的参数和`EnvironBuilder`构造器的参数一致。

- `werkzeug.test.run_wsgi_app(app, environ, buffered=False)`

    以`(app_iter, status, headers)`的元祖形式作为app的输出。

    有时候app可能要使用`start_response`函数返回的`write()`。如果你没有获得期待
    中的输出，可以设置`buffered`为True。

    参数:

    - app: 要执行的application
    - buffered: 设置为True可以激活buffering.

    返回:

    元祖`(app_iter, status, headers)`

## Reading Source Code

发现一行有趣的代码, `test.py`文件第373-375行:

```python
def _get_base_url(self):
    return url_unparse((self.url_scheme, self.host,
                        self.script_root, '', '')).rstrip('/') + '/'
```

乍一看我没反应过来，还去想了一个`rstrip()`方法的作用是什么。

然后一想，这样写听聪明的，一行代码就可以确保最后的URL以`/`结尾.如果是我写，
可能还用`.endswith()`这种方法作一下判断。后者效率未必更高，只是脑袋没转过弯
想不到罢了.

`test.py`主要入口就是两个类，`BuilderEnviron`和`Client`。分别用于测试时模拟
response和发起WSGI请求.


