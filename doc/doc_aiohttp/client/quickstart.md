# Client Quickstart

## Make a Request

```python
# 首先import这个模块
import aiohttp


# 现在让我们来获取一个web页面
# ClientSession调用之后返回一个`session`对象
# session.get()返回一个`ClientResponse`对象
async with aiohttp.ClientSession() as session:
    async with session.get('https://api.github.com/events') as resp:
        print(resp.status)
        print(await resp.text())

# 如果想要发送HTTP POST请求
# 可以使用ClientSession.post()协程
session.post('http://httpbin.org/post', data=b'data')

# 同样支持其它的HTTP方法
session.put('http://httpbin.org/put', data=b'data')
session.delete('http://httpbin.org/delete')
session.head('http://httpbin.org/get')
session.options('http://httpbin.org/get')
session.patch('http://httpbin.org/patch', data=b'data')

# 注意:不要每个请求都创建一个session。
# 最好的情况是每个应用创建一个session，然后将所有的请求一起执行。
# session里面包含连接池。连接重用和keep-alives可以加速性能.
```

## Passing Parameters In URLs

```python
# 有往往想在URL的query string中发送某种类型的数据
# 如果你手动构建这个URL，这些数据将会在URL的？后面以键值对的形式显示
# Requests允许你以字典的形式传入参数，使用`params`关键字参数
params = {'key1': 'value1', 'key2': 'value2'}
async with session.get('http://httpbin.org/get',
                       params=params) as resp:
    assert str(resp.url) == 'http://httpbin.org/get?key2=value2&key1=value1'

# 如果同一个键有多个值，可以使用MultiDict,
# 也可以使用2位元组的形式
params = [('key', 'value1'), ('key', 'value2')]
async with session.get('http://httpbin.org/get',
                        params=params) as f:
    assert str(r.url) == 'http://httpbin.org/get?key=value2&key=value1'

# 你可以对`params`传入字符串形式的参数，不过这些参数不会编码
async with session.get('http://httpbin.org/get',
                       params='key=value+1') as r:
    assert str(r.url) == 'http://httpbin.org/get?key=value+1'

# 注意：aiohttp会在发送请求之前对URL执行规整。
# 比如URL('http://example.com/путь%30?a=%31')将会转换为
# URL('http://example.com/%D0%BF%D1%83%D1%82%D1%8C/0?a=1').
# 如果不想开启URL规整，可以对URL构造器传入`encoded=True`，例如:
# await session.get(URL('http://example.com/%30', encoded=True))
```

## Response Content and Status Code

```python
# 我们可以阅读服务器响应的内容和状态码
async with session.get('https://api.github.com/events') as resp:
    print(resp.status)          # output: 200
    print(await resp.text())    # output: '[{"created_at":"2015...

    # aiohttp会自动把来自服务器的响应数据解码，
    # 不过你可以针对text()方法指定自己要的编码
    await resp.text(encoding='windows-1251')
```

## Binary Response Content

```python
# 你也可以以bytes的形式读取response body
print(await resp.read())
b'[{"created_at":"2015-06-12T14:06:22Z","public":true,"actor":{...

# gzip和deflate的传输编码会为你自动解码
```

## JSON Request

```python
# 任何session方法如`.request()`，`.get()`, `.post()`等，
# 都可以接受`json`参数
async with aiohttp.ClientSession() as session:
    async with session.post(url, json={'test': 'object'})

# 默认情况下会使用Python标准库json模块来进行序列化。
# 但也可以使用其它的序列化器，可以对ClientSession传入json_serialize来指定
import ujson

async with aiohttp.ClientSession(json_serialize=ujson.dumps) as session:
    async with session.post(url, json={'test': 'object'})
```

## JSON Response Content

```python
# 另外内置有JSON的decoder，让你可以处理JSON数据
async with session.get('https://api.github.com/events') as resp:
    print(await resp.json())
```

## Streaming Response Content

```python
# `.read()`, `.josn()`, `.text()`这些方法你都应该小心使用，
# 这些方法都会把整个response读取进内存中。
# 如果你需要下载上G大小的文件，这些方法也会把数据载入到内存。
# 这时候你应该使用`.content`属性，它是一个`aiohttp.StreamReader`实例
async with session.get('https://api.github.com/events') as resp:
    await resp.content.read(10)

# 一般来说，你应该使用类似下面的代码来处理流式数据
with open(filename, 'wb') as fd:
    while True:
        chunk = await resp.content.read(chunk_size)
        if not chunk:
            break
        fd.write(chunk)
```

## More complicated POST requests

```python
# 一般来说，使用POST的时候你都会想发送一些form编码的数据，
# 比如HTML form。只需要传入一个字典给`data`关键字参数即可
payload = {'key1': 'value1', 'key2': 'value2'}
async with session.post('http://httpbin.org/post',
                        data=payload) as resp:
    print(await resp.text())

# 如果你要发送的数据不是form编码，
# 你可以传入bytes而不是dict。
# aiohttp将会把content-type转换为application/octet-stream
async with session.post(url, data=b'\x00Binary-data\x00') as resp:
    ...

# JSON数据可以这么传
async with session.post(url, json={'example': 'test'}) as resp:
    ...

# 普通文本数据可以这样传
async with session.post(url, text='Тест') as resp:
    ...
```

## Post a Multipart-Encoded File

```python
# 想要上传Multipart-encoded的文件
url = 'http://httpbin.org/post'
files = {'file': open('report.xls', 'rb')}

await session.post(url, data=files)

# 你可以自行指定"filename"和"content_type"
url = 'http://httpbin.org/post'
data = FormData()
data.add_field('file',
               open('report.xls', 'rb'),
               filename='report.xls',
               content_type='application/vnd.ms-excel')

await session.post(url, data=data)
```

## Streaming uploads

```python
# aiohttp支持多种类型的streaming上传，
# 允许你上传大文件而不用把它们一次性读入内存

# 最简单的情况，你可以直接传入一个类file对象
with open('massive-body', 'rb') as f:
    await session.post('http://httpbin.org/post', data=f)


# 或者也可以使用装饰器`@aiohttp.streamer`
@aiohttp.streamer
def file_sender(writer, file_name=None):
    with open(file_name, 'rb') as f:
        chunk = f.read(2**16)
        while chunk:
            yield from writer.write(chunk)
            chunk = f.read(2**16)

# 然后你可以使用`file_sender`来提供数据
async with session.post('http://httpbin.org/post',
                        data=file_sender(file_name='huge_file')) as resp:
    print(await resp.text())


# 另外你可以使用`StreamReader`对象.
# 假设我们想要计算一个文件的SHA1 hash，然后把它上传
async def feed_stream(resp, stream):
    h = hashlib.sha256()

    while True:
        chunk = await resp.content.readany()
        if not chunk:
            break
        h.update(chunk)
        stream.feed_data(chunk)
    
    return h.hexdigest()

resp = session.get('http://httpbin.org/post')
stream = StreamReader()
loop.create_task(session.post('http://httpbin.org/post', data=stream))

file_hash = await feed_stream(resp, stream)

# 因为response的.content属性即是`StreamReader`对象，
# 你可以将get和post方法连接起来
r = await session.get('http://python.org')
await session.post('http://httpbin.org/post',
                   data=r.content)
```

## Websockets

```python
# aiohttp的websocket client可以开箱即用

# 对于websocket client连接，你必须使用`aiohttp.ClientSession.ws_connect()协程，
# 它接受一个`url`作为参数，然后返回一个`ClientWebSocketResponse`,
# 使用这个对象你可以和websocket服务器进行通信
session = aiohttp.ClientSession()
async with session.ws_connect('http://example.org/websocket') as ws:

    async for msg in ws:
        if msg.type == aiohttp.WSMsgType.TEXT:
            if msg.data == 'close cmd':
                await ws.close()
                break
            else:
                await ws.send_str(msg.data + '/answer')
        elif msg.type == aiohttp.WSMsgType.CLOSED:
            break
        elif msg.type == aiohttp.WSMsgType.ERROR:
            break

# 你必须使用一个websocket task来进行
# 读取(比如`await ws.receive()`或者`async for msg in ws:`),
# 写入的话可以有多个writer task来异步发送数据(比如`await ws.send_str('data')`)
```

## Timeouts

```python
# 默认情况下，所有的IO操作都有5分钟的超时.
# 可以通过传入timeout参数来覆盖这个超时设置:
async with session.get('https://github.com', timeout=60) as r:
    ...

# 如果传入None或者0，则没有超时检查.

# 另外可以使用`async_timeout.timeout()`上下文管理器来封装
# 一个客户端调用，它底下的操作都会应用这个timeout
import async_timeout

with async_timeout.timeout(0.001):
    async with session.get('https://github.com') as r:
        await r.text()
```








