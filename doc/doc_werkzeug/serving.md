# Serving WSGI Applications

有多种方式可以伺服一个WSGI application。

在你开发的时候，你一般不需要一个高级的web服务器，如Apache，因为它麻烦了。

你可以使用一个简单的开发服务器。而Werkzeug为你提供了一个简单的开发服务器。

下面这个脚本`start-myproject.py`可以将application运行在内置的服务器中：

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-

from werkzeug.serving import run_simple
from myproject import make_app


app = make_app(...)
run_simple('localhost', 8080, app, use_reloader=True)
```

你可以传入`extra_files`这个关键字参数来加入你想要观察的一些额外的文件(比如配置文件)

- `werkzeug.serving.run_simple(hostname, port, application, user_reloader=False,user_debugger=False, user_evalex=True, extra_files=None, reloader_interval=1,reloader_type='auto', threaded=False, processes=1, request_handler=None, static_files=None, passthrough_errors=False, ssl_context=None)`

    开启一个WSGI应用.可选特性包括一个reloader，多线程和fork的支持。

    这个函数还包含命令行接口:

    `python -m werkzeug.serving --help`

    参数:

    - `hostname`: 应用程序使用的host，比如'localhost'
    - `port`: 服务器使用的端口，比如: '8080'
    - `application`: 要执行的WSGI应用
    - `use_reloader`: 在模块发生变动的时候，服务器会自动重启.
    - `user_evalex`: 开启werkzeug的debugging系统.
    - `use_evalex`: 激活exception eval特性.
    - `extra_files`: 一组需要额外监控的文件.
    - `reloader_interval`: 执行重启检查的间隔.
    - `reloader_type`: 使用的reloader类型.可选'stat'或者'watchdog'
    - `threaded`: 应该为每个request开启一个单独的线程来处理吗？
    - `processes`: 开启多进程.
    - `request_handler`: 可选参数，可以用来替换默认的request handler。
    - `static_files`: 一组静态文件路径.
    - `passthrough_errors`: 设置为True的时候，会禁用错误捕获.
    - `ssl_context`: 一个用于连接的SSL context.

- `werkzeug.serving.is_running_from_reloader()`

    检查应用是否运行了reloader。

- `werkzeug.serving.make_ssl_devcert(base_path, host=None, cn=None)`

    为开发环境创建一个SSL key。

## Reloader

Werkzeug会持续监控你的web应用摩卡，在发现文件改动时会重启服务器.

从0.10版本开始，支持了两种reloader: stat和watchdog.

- 默认的`stat` reloader会在一个定时的间隔中检查所有文件的`mtime`。

- `watchdog`使用文件系统events，它比`stat`更加快速.但是需要安装`watchdog`模块.

要切换使用的reloader，可以通过`run_simple()`函数的`reloader_type`参数来指定。

## Colored Logging

Werkzeug可以为终端的日志输出渲染颜色，但是需要安装`termcolor`软件包.

## Virtual Hosts

很多web应用利用了多个子域名。

可以在本地模仿这种行为。通过`host file`。

-- | --
-- | --
Windows | %SystemRoot%\system32\drivers\etc\hosts
Linux / OS X | /etc/hosts

你可以用文本编辑器打开这个文件，然后修改它:

`127.0.0.1       localhost yourapplication.local api.yourapplication.local
`

然后你可以通过这些额外的hostname来访问开发服务器了。

你可以使用`URL Routing`系统来分发给不同的host，或者由你自己来解析`request.host`.

## Shutting Down The Server

从Werkzeug0.7开始，开发服务器提供来一种方式可以在一个request之后关闭服务器。

你需要调用一个函数: `werkzeug.server.shutdown`，这个函数存在于WSGI environ中.

```python
def shutdown_server(environ):
    if not 'werkzeug.server.shutdown' in environ:
        raise RuntimeError('Not running the development server')
    environ['werkzeug.server.shutdown']()
```

## Troubleshooting

在支持ipv6的操作系统上面，一些用户可能在访问本地服务器的时候发现非常慢。

这是因为"localhost"同时设置了ipv4和ipv6，一些浏览器会试图首先访问ipv6。

不过现在的一些集成浏览器会首先试图使用ipv4。

如果你注意到浏览器试图访问ipv6，你可以在hosts文件中移除下面这一行:

`::1        localhost`

另外你也可以通过浏览器端的设置来搞定。

## SSL

内置服务器支持用于测试的SSL。

### Quickstart

在本地开发使用SSL，首先要生产SSL证书以及私钥。

1. 生成SSL key，并且把它们存储在某地:

    ```python
    >>> from werkzeug.serving import make_ssl_devcert
    >>> make_ssl_devcert('/path/to/the/key', host='localhost')
    ('/path/to/the/key.crt', '/path/to/the/key.key')
    ```

2. 将这个元祖当作`ssl_context`传入`run_simple()`方法:

    ```python
    run_simple('localhost', 4000, application,
               ssl_context=('/path/to/the/key.crt',
                            '/path/to/the/key.key'))
    ```

### Loading Contextx by Hand

在Python2.7.9以及3+版本中，你可以选择使用`ssl.SSLContext`对象来代替元祖.

```python
import ssl
ctx = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
ctx.load_cert_chain('ssl.cert', 'ssl.key')
run_simple('localhost', 4000, application, ssl_context=ctx)
```

### Generating Certificates

可以使用openssl工具来创建key和证书.

这要求你在你的操作系统中安装了openssl命令

```shell
$ openssl genrsa 1024 > ssl.key
$ openssl req -new -x509 -nodes -sha1 -days 365 -key ssl.key > ssl.cert
```

### Adhoc Certificates

激活SSL最简单的方式就是以"adhoc"模式来开启服务器。

在这种情况下，Werkzeug会为你生成一个SSL证书:

```python
run_simple('localhost', 4000, application, ssl_context='adhoc')
```

坏处就是每次server重启都必须ack证书。

不推荐使用这个方式.

## Reading Source

`serving.py`第89行:

`# important: do not use relative imports here or python -m will break`

上面注释是一个技巧，如果使用`python -m`，那么这个脚本(模块)就不应该使用相对import。

`_reloader.py`文件的254-259行:

```python
try:
    __import__('watchdog.observers')
except ImportError:
    reloader_loops['auto'] = reloader_loops['stats']
else:
    reloader_loops['auto'] = reloader_loops['watchdog']
```

这几行代码根据用户是否安装了`watchdog`包来决定默认使用的reloader_loop，
另外它使用了`__import__`而不是import语句.我们知道`__import__`可以接受字符串作为
参数，这样可以避免同命名空间下的变量名冲突，比如之前你不小心定义了一个变量
叫做`watchdog`，这时候使用`import watchdog`是会失败的。而werkzeug这个import代码
在模块很深的地方，所以它必须担心这个问题.

另外还有大量的函数内import，这可能是因为一些条件因素才需要的import，所以放在执行
阶段再import。

在`serving.py`文件中还有两端有趣的import代码，分别是55-61行，64-71行:

```python
try:
    import ssl
except ImportError:
    class _SslDummy(object):
        def __getattr__(self, name):
            raise RuntimeError('SSL support unavailable')
    ssl = _SslDummy()


def _get_openssl_crypto_module():
    try:
        from OpenSSL import crypto
    except ImportError:
        raise TypeError('Using ad-hoc certificates requires the pyOpenSSL '
                        'library.')
    else:
        return crypto
```

这两段代码看起来差不多，都是处理一个库不存在的情况，但是处理方式不一样，
前者会返回一个伪对象，后者直接使用函数来Import。

不过看起来两者都是在被执行的时候才会报错？那么为什么要使用这两种不同的方式呢？
不会是因为异常信息的原因，因为这是可以通过一种方式解决的。

可以在这个文件中查询`crypto`，然后你就会明白了:

```python
def generate_adhoc_ssl_pair(cn=None):
    from random import random
    crypto = _get_openssl_crypto_module()   # 393行


def generate_adhoc_ssl_context():
    """Generates an adhoc SSL context for the development server."""
    crypto = _get_openssl_crypto_module()   # 456行


def make_ssl_devcert(base_path, host=None, cn=None):
    from OpenSSL import crypto # 438行
```

看到没，`_get_openssl_crypto_module()`是提供给adhoc ssl专用的，这和它的
Exception msg也是吻合的。而438行使用了正常的import，如果import错误会抛出
`ImportError`，这些情况返回给用户的异常信息是完全不一样但是有意义的。

