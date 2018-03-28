# Web Server Quickstart

## Run a Simple Web Server

为了实现一个web服务器，首先要创建一个request handler.

request handler是一个协程或者一个常规程序，它接受一个`Request`实例作为它的
唯一参数，需要返回一个`Response`实例.

```python
from aiohttp import web

async def hello(request):
    return web.Response(text='Hello, world')
```

然后，创建一个`Application`的实例，用它来将handler注册到一个特定的HTTP方法和路由上面.

```python
app = web.Application()
app.add_routes([web.get('/', hello)])
```

之后，可以通过`run_app()`来运行这个app：

```python
web.run_app(app)
```

现在我们可以在`http://localhost:8000`看到结果了。

另外你可以使用路由装饰器来注册request handler:

```python
routes = web.RouteTableDef()

@routes.get('/')
async def hello(request):
    return web.Response(text='Hello, world')


app = web.Application()
app.add_routes(routes)
web.run_app(app)
```

这两种方法都可以用，随你喜欢。

## Command Line Interface(CLI)

`aiohttp.web`实现了一个基础的CLI，可以快速地通过TCP/IP来私服一个Application实例:

```python
$ python -m aiohttp.web -H localhost -P 8080 package.module:init_func
```

`package.module:init_func`应该是一个可以引入的callble，可以接受命令行参数，
最后返回一个Application实例。

## Handler

一个request handler必须是一个协程或者常规函数，它接受一恶搞`Request`实例作为
它的唯一参数，然后返回一个Response实例.

```python
async def handler(request):
    return web.Response()
```

handlers通过`Application.add_routes()`来注册到一个给定的路由.

```python
app.add_routes([
  web.get('/', handler),
  web.post('/post', post_handler),
  web.put('/put', put_handler)
])
```

或者使用route装饰器:

```python
routes = web.RouteTableDef()

@routes.get('/')
async def get_handler(request):
    ...


@routes.post('/post')
async def put_handler(request):
    ...


app.add_routes(routes)
```


还支持通配符匹配HTTP方法，`route()`和`RouteTableDef.route()`都支持.

```python
app.add_routes(web.route('*', '/path', all_handler)]
```

HTTP方法可以在handler内部通过`Request.method`这个属性来获取.

默认情况下，接受`GET`方法的端点也会自动加入接受`HEAD`请求，返回和`GET`请求一致
的HTTP头部。你可以在route中拒绝加入`HEAD`请求:

```python
web.get('/', handler, allow_head=False)
```
这个`handler`不可以使用`HEAD`请求访问，服务端会返回`405: Method Not Allowed`.

## Resources and Routes

内部的routes通过`Application.router(UrlDispatcher实例)`来处理.

`router`是resources list.

`resource`是route表的一个入口，它对应所请求的URL。

`resource`最少有一个route。

`router`通过调用web handler来处理HTTP方法.

在你加入一个route的时候，resouce会自动在幕后创建。

这个库的实现会合并所有加入的route，如果随后加入的是同一个path不同的方法只会被加入一个resource。

考虑下面两个示例：

```python
app.add_routes([web.get('/path1', get_1),
                web.post('/path1', post_1),
                web.get('/path2', get_1),
                web.post('/path2', post_2)]
```

以及:

```python
app.add_routes([web.get('/path1', get_1),
                web.get('/path2', get_2),
                web.post('/path2', post_2),
                web.post('/path1', post_1)])
```

第一个示例会得到优化。你应该知道怎么做了.

## Variable Resources

Resource也可以拥有`variable path`(变量路径)。

举例来说，一个路径为`/a/{name}/c`的资源将会匹配所有诸如`/a/b/c`，`/a/1/c`和`a/etc/c`这种路径.

变量部分通过`{identifier}`来进行标识，`identifier`之后可以在`request handler`中
获取。可以通过`Request.match_info`这个字典来获取`identifier`:

```python
@routes.get('/{name}')
async def variable_handler(request):
    return web.Response(
        text="Hello, {}".format(request.match_info['name'])
    )
```

默认情况下，每个part都会通过正则表达式`[^{}/]+`来进行匹配.

你可以可以通过`{identifier:regex}`的形式自定义正则表达式:

`web.get(r'/{name:\d+}', handler)`

## Reverse URL Constructing using Named Resources

Routes也可以给定一个名称:

```python
@routes.get('/root', name='root')
async def handler(request):
    ...
```

no more translation

## WebSockets

`aiohttp.web`支持开箱即用型websocket.

想要建立一个`Websocket`，需要在一个`request handler`中创建一个`WebSocketResponse`，
然后使用它来和另一个端点进行通讯:

```python
async def websocket_handler(request):
    
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    
    async for msg in ws:
        if msg.type == aiohttp.WSMsgType.TEXT:
            if msg.data = 'close':
                await ws.close()
            else:
                await ws.send_str(msg.data + '/answer')
        elif msg.type == aiohttp.WSMsgType.ERROR:
            print('ws connection closed with exception %s' % 
                  ws.exception())
    
    print('websocket connection closed')

    return ws
```
