# Advanced Client Usage

## Client Session

`ClientSession`是所有客户端API操作的心脏和主要入口。

首先要创建一个session，然后使用它来执行HTTP请求和初始化WebSocket连接。

session包含一个cookie存储和连接池，因此同一个session发送的HTTP请求会共享cookies和connection。

## Custom Request Headers

```python
# 如果你想要为一个请求加入HTTP头部，可以将一个dict传入`headers`参数
url = 'http://example.com/image'
payload = b'GIF89a\x01\x00\x01\x00\x00\xff\x00,\x00\x00'
          b'\x00\x00\x01\x00\x01\x00\x00\x02\x00;'
headers = {'content-type': 'image/gif'}

await session.post(
    url,
    data=payload,
    headers=headers
)

# 你可以为session中的所有请求设置一个默认的headers
headers = {'Auhorization': 'Basic bG9naW46cGFzcw=='}
async with aiohttp.ClientSession(headers=headers) as session:
    async with session.get('http://httpbin.org/headers') as r:
        json_body = await r.json()
        assert json_body['headers']['Authorization'] == \
            'Basic bG9naW46cGFzcw=='
```

## Custom Cookies

```python
# 想要发送自定义的cookies，
# 可以在ClientSession构造器传入`cookies`参数
url = 'http://httpbin.org/cookies'
cookies = {'cookies_are': 'working'}
async with ClientSession(cookies=cookies) as session:
    async with session.get(url) as resp:
        assert with resp.json() == {
            "cookies": {"cookies_are": "working"}
        }

# `ClientSession`可以为多个请求分享cookies
async with aiohttp.ClientSession() as session:
    await session.get(
        'http://httpbin.org/cookies/set?my_cookie=my_value'
    )
    filtered = session.cookie_jar.filter_cookies('http://httpbin.org')
    assert filtered['my_cookie'].value == 'my_value'
    async with session.get('http://httpbin.org/cookies') as r:
        json_body = await r.json()
        assert json_body['cookies']['my_cookie'] == 'my_value'
```

## Response Headers and Cookies

```python
# 我们可以看服务器response的头部,
# `ClientResponse.headers`，是一个`CIMutiDictProxy`
>>> resp.headers
{'ACCESS-CONTROL-ALLOW-ORIGIN': '*',
 'CONTENT-TYPE': 'application/json',
 'DATE': 'Tue, 15 Jul 2014 16:49:51 GMT',
 'SERVER': 'gunicorn/18.0',
 'CONTENT-LENGTH': '331',
 'CONNECTION': 'keep-alive'}

# 这是一个特殊的字典：专门为HTTP头部设计的。
# 根据RFC7230，HTTP头部是上下文不敏感的。
# 并且同一个名称可以支持多个值。
>>> resp.headers['Content-Type']
'application/json'

>>> resp.headers.get('content-type')
'application/json'

# 原生的头部数据可以通过`.raw_headers`属性来访问
>>> resp.raw_headers
((b'SERVER', b'nginx'),
 (b'DATE', b'Sat, 09 Jan 2016 20:28:40 GMT'),
 (b'CONTENT-TYPE', b'text/html; charset=utf-8'),
 (b'CONTENT-LENGTH', b'12150'),
 (b'CONNECTION', b'keep-alive'))

# 如果一个response包含HTTP Cookies，你可以快速访问它们
url = 'http://example.com/some/cookie/setting/url'
async with session.get(url) as resp:
    print(resp.cookies['example_cookie_name'])  
```

## Redirection History

```python
# 如果一个请求被重定向了，
# 你可以通过`.history`属性查看它之前的response
>>> resp = await session.get('http://example.com/some/redirect/')
>>> resp
<ClientResponse(http://example.com/some/other/url/) [200]>
>>> resp.history
(<ClientResponse(http://example.com/some/redirect/) [301]>,)
```

## Cookie Jar

### Cookie Safety

默认情况下，`ClientSession`使用严格版本的`aiohttp.CookieJar`.RFC2109要求禁止接受从带IP地址的URL中的cookies。

但是有时我们想要获取这些cookies。可以传入`unsafe=False`到`aiohttp.CookieJar`构造器:

```python
jar = aiohttp.CookieJar(unsafe=True)
session = aiohttp.ClientSession(cookie_jar=jar)
```

### Dummy Cookie Jar

有时不想要cookie处理。可以使用`aiohttp.DummyCookieJar`实例:

```python
jar = aiohttp.DummyCookieJar()
session = aiohttp.ClientSession(cookie_jar=jar)
```

## Uploading pre-compressed data

要使用aiohttp上传一些已经压缩的数据，需要在调用请求函数的时候使用压缩算法的名称(通常是`deflate`或者`gzip`)作为`Content-Encoding`头部的值:

```python
async def my_coroutine(session, headers, my_data):
    data = zlib.compress(my_data)
    headers = {'Content-Encoding': 'deflate'}
    async with session.post('http://httpbin.org/post',
                            data=data,
                            headers=headers)
        pass
```

## Client Tracing

*可以理解为请求声明周期内的一些钩子*

说明pass

```python
async def on_request_start(
        session, trace_config_ctx, params):
    print("Starting request")


async def on_request_end(session, trace_config_ctx, params):
    print("Ending request")


trace_config = aiohttp.TraceConfig()
trace_config.on_request_start.append(on_request_start)
trace_config.on_request_end.append(on_request_end)
async with aiohttp.ClientSession(trace_configs=[trace_config]) as client:
    client.get('http://example.com/some/redirect/')

# ...
```

pass

## Connectors

想要修改请求的传输层，你可以传入一个自定义的`connector`到`ClientSession`:

```python
conn = aiohttp.TCPConnector()
session = aiohttp.ClientSession(connector=conn)
```

### Limiting connection pool size

```python
# 同时开启最多的连接数量可以通过`limit`参数来指定(默认:100)
conn = aiohttp.TCPConnector(limit=30)

# 如果你不想有连接数量的限制，可以传入0
conn = aiohttp.TCPConnector(limit=0)

# 你可以通过参数`limit_per_host`来指定每个host的连接限制(默认:0)
conn = aiohttp.TCPConnector(limit_per_host=30)
```

### Tuning the DNS cache

```python
# 默认情况下，TCPConnector会开启DNS缓存表，
# 解析的域名会默认缓存10秒。可以通过参数`ttl_dns_cache`来设置
conn = aiohttp.TCPConnector(ttl_dns_cache=300)
# 如果不想使用DNS缓存
conn = aiohttp.TCPConnector(use_dns_cache=False)
```

### Resolving using custom nameservers

```python
# 可以指定域名服务器，不过需要aiodns库
from aiohttp.resolver import AsyncResolver

resolver = AsyncResolver(nameserver=['8.8.8.8', '8.8.4.4'])
conn = aiohttp.TCPConnector(resolver=resolver)
```

### Unix domain sockets

```python
# 如果你的HTTP服务器使用UNIX域名socket
conn = aiohttp.UnixConnector(path='/path/to/socket')
session = aiohttp.ClientSession(connector=conn)
```

## SSL control for TCP sockets

```python
# aiohttp默认会检查HTTPS协议。不过可以通过`ssl`参数来禁用证书检查
r = await session.get('https://example.com', ssl=False)

# 如果你需要创建自定义的ssl参数，
# 你可以创建一个`ssl.SSLContext`实例并传入ClientSession的方法
sslcontext = ssl.create_default_context(
    cafile='/path/to/ca-bundle.crt'
)
r = await session.get('https://example.com', ssl=sslcontext)

# ...pass
```

## Proxy support

```python
# aiohttp支持HTTP/HTTPS代理
async with aiohttp.ClientSession() as session:
    async with session.get("http://python.org",
                            proxy="http://some.proxy.com") as resp:
        print(resp.status)


# 也支持proxy验证
async with aiohttp.ClientSession() as session:
    proxy_auth = aiohttp.BasicAuth('user', 'pass')
    async with session.get('http://python.org',
                            proxy='http://some.proxy.com',
                            proxy_auth=proxy_auth) as resp:
        print(resp.status)


# 验证信息可以通过proxy URL传入
session.get(
    "http://python.org",
    proxy="http://user:pass@some.proxy.com"
)

# 和`requests`库不同，`aiohttp`不会默认读取环境变量。
# 不过你可以在`ClientSession`构造器传入`trust_env=True`来读取环境变量
# 这两个环境变量为:HTTP_PROXY和HTTPS_PROXY
async with aiohttp.ClientSession(trust_env=True) as session:
    async with session.get("http://python.org") as resp:
        print(resp.status)
```

## Graceful Shutdown

在`ClientSession`通过上下文协议结束(或者直接调用`.close()`方法)而关闭的时候，底层的连接因为asyncio内部的细节仍然会保持开启。实际上，底层的连接会在稍后关闭。不过，如果事件循环在顶层连接关闭之前就停止了，将会发出警告`ResouceWarning`.

为了避免这个问题，必须在关闭事件循环之前加入一小段延时来让开启的底层连接关闭。

对于无SSL的`ClientSession`，一个简单的zero-sleep(`await asyncio.sleep(0)`)就足够了.

```python
async def read_website():
    async with aiohttp.ClientSession() as session:
        async with session.get('http://example.org') as response:
            await response.read()

loop = asyncio.get_event_loop()
loop.run_until_complete(read_website())
# zero-sleep允许底层的连接关闭
loop.run_until_complete(asyncio.sleep(0))
loop.close()

# ...
# 如果是SSL连接，需要等待250ms
loop.run_until_complete(asyncio.sleep(0.250))
loop.close()
```




