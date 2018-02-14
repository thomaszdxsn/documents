# urllib.parse -- Split URLs into Components

原链接: [https://pymotw.com/3/urllib.parse/index.html](https://pymotw.com/3/urllib.parse/index.html)

 *用途:将URL分割为Components*

 `urllib.parse`模块提供了一些函数用来操纵URL和它的Components，可以分割也可以组装。

 ## Parsing

 `urlparse()`函数返回的值是一个`ParserResult`对象，它是一个包含6个元素的类tuple对象。

 ### urllib_parse_urlparse.py

 ```python
# urllib_parse_urlparse.py

from urllib.parse import urlparse

url = 'http://netloc/path;param?query=arg#frag'
parsed = urlparse(url)
print(parsed)
```

可以访问的URL各部分分别是: scheme, network location, path, path segment parameters (separated from the path by a semicolon), query, and fragment.

```shell
$ python3 urllib_parse_urlparse.py

ParseResult(scheme='http', netloc='netloc', path='/path',
params='param', query='query=arg', fragment='frag')
```

### urllib_parse_urlparseattrs.py

虽然返回的值可以作为元组访问，不过它实际上是`nametuple`数据结构的一个子类，也就是说可以通过属性名来访问元组的元素。另外，处于方便的原因，根据这些属性计算了一些额外的可读属性。

```python
# urllib_parse_urlparseattrs.py

from urllib.parse import urlparse

url = 'http://user:pwd@Netloc:80/path;param?query=arg#frag'
parsed = urlparse(url)
print('scheme  :', parsed.scheme)
print('netloc  :', parsed.netloc)
print('path    :', parsed.path)
print('params  :', parsed.params)
print('query   :', parsed.query)
print('fragment:', parsed.fragment)
print('username:', parsed.username)
print('password:', parsed.password)
print('hostname:', parsed.hostname)
print('port    :', parsed.port)
```

一般没有出现的值都会有一个默认值。上面程序的输出如下:

```shell
$ python3 urllib_parse_urlparseattrs.py

scheme  : http
netloc  : user:pwd@NetLoc:80
path    : /path
params  : param
query   : query=arg
fragment: frag
username: user
password: pwd
hostname: netloc
port    : 80
```

### urllib_parse_urlsplit.py

`urlsplit()`函数是`urlparse()`函数之外的另一个选择。它们有些稍微的区别，`urlsplit()`不会解析URL的parameter部分。这种规则遵守了RFC2396，parameter可以追加到path中每个segment中。

```python
# urllib_parse_urlsplit.py

from urllib.parse import urlsplit

url = 'http://user:pwd@NetLoc:80/p1;para/p2;para?query=arg#frag'
parsed = urlsplit(url)
print(parsed)
print('scheme  :', parsed.scheme)
print('netloc  :', parsed.netloc)
print('path    :', parsed.path)
print('query   :', parsed.query)
print('fragment:', parsed.fragment)
print('username:', parsed.username)
print('password:', parsed.password)
print('hostname:', parsed.hostname)
print('port    :', parsed.port)
```

因为parameter没有被分割出来，元组的API只有5个元素，也没有`params`属性.

```shell
$ python3 urllib_parse_urlsplit.py

SplitResult(scheme='http', netloc='user:pwd@NetLoc:80',
path='/p1;para/p2;para', query='query=arg', fragment='frag')
scheme  : http
netloc  : user:pwd@NetLoc:80
path    : /p1;para/p2;para
query   : query=arg
fragment: frag
username: user
password: pwd
hostname: netloc
port    : 80
```

### urllib_parse_urldefrag.py

如果只要把URL的fragment部分分割出来，可以使用`urldefrag()`.

```python
# urllib_parse_urldefrag.py

from urllib.parse import urldefrag

original = 'http://netloc/path;param?query=arg#frag'
print('original:', original)
d = urldefrag(original)
print('url     :', d.url)
print('fragment:', d.fragment)
```

返回的值是一个`DefragResult`对象，也是继承自`namedtuple`，包含基础URL和fragment。

```shell
$ python3 urllib_parse_urldefrag.py

original: http://netloc/path;param?query=arg#frag
url     : http://netloc/path;param?query=arg
fragment: frag
```

## Unparsing

### urllib_parse_geturl.py

有几种方式可以把分割的URL部分重新组装成一个字符串。首先每个返回的Result对象都有一个`.geturl()`方法.

```python
# urllib_parse_geturl.py

from urllib.parse import urlparse

original = 'http://netloc/path;param?query=arg#frag'
print('ORIG  :', original)
parsed = urlparse(original)
print('PARSED:', parsed.geturl()
```
输出:

```shell
$ python3 urllib_parse_geturl.py

ORIG  : http://netloc/path;param?query=arg#frag
PARSED: http://netloc/path;param?query=arg#frag
```

### urllib_parse_urlunparse.py

一个普通的包含字符串的元组也可以通过`urlunparse()`重新组合成一个URL字符串.

```python
# urllib_parse_urlunparse.py

from urllib.parse import urlparse, urlunparse

original = 'http://netloc/path;param?query=arg#frag'
print('ORIG  :', original)
parsed = urlparse(original)
print('PARSED:', type(parsed), parsed)
t = parsed[:]
print("TUPLE :", type(t), t)
print("NEW   :", urlunparse(t))
```

输出如下:

```shell
$ python3 urllib_parse_urlunparse.py

ORIG  : http://netloc/path;param?query=arg#frag
PARSED: <class 'urllib.parse.ParseResult'>
ParseResult(scheme='http', netloc='netloc', path='/path',
params='param', query='query=arg', fragment='frag')
TUPLE : <class 'tuple'> ('http', 'netloc', '/path', 'param',
'query=arg', 'frag')
NEW   : http://netloc/path;param?query=arg#frag
```

### urllib_parse_urlunparseextra.py

如果URL包含多余的部分，这些多余的部分将会被移除。

```python
# urllib_parse_urlunparseextra.py

from urllib.parse import urlparse, urlunparse

original = 'http://netloc/path;?#'
print('ORIG  :', original)
parsed = urlparse(original)
print('PARSED:', type(parsed), parsed)
t = parsed[:]
print('TUPLE :', type(t), t)
print('NEW   :', urlunparse(t))
```

在这个例子中有很多多余的分隔符，这些分隔符在重新组合的时候都会被移除。

```shell
$ python3 urllib_parse_urlunparseextra.py

ORIG  : http://netloc/path;?#
PARSED: <class 'urllib.parse.ParseResult'>
ParseResult(scheme='http', netloc='netloc', path='/path',
params='', query='', fragment='')
TUPLE : <class 'tuple'> ('http', 'netloc', '/path', '', '', '')
NEW   : http://netloc/path
```

## Joining

### urllib_parse_urljoin.py

除了解析URL，`urllib.parse`模块包含`urljoin()`函数，可以把相对URL构建为绝对URL。

```python
# urllib_parse_urljoin.py

from urllib.parse import urljoin

print(urljoin('http://www.example.com/path/file.html',
              'anotherfile.html'))
print(urljoin('http://www.example.com/path/file.html',
              '../anotherfile.html'))
```

在这个例子中，第二个URL的path的相对部分(`../`)将会纳入考虑.

```shell
$ python3 urllib_parse_urljoin.py

http://www.example.com/path/anotherfile.html
http://www.example.com/anotherfile.html
```

### urllib_parse_urljoin_with_path.py

非相对path将会被和`os.path.join()`一样的方式来处理。

```python
# urllib_parse_urljoin_with_path.py

from urllib.parse import urljoin

print(urljoin('http://www.example.com/path/',
              '/subpath/file.html'))
print(urljoin('http://www.example.com/path/',
              'subpath/file.html'))
```

如果要连接的URL(第二个参数)以斜杠开头，它将会把URL的path重置为根目录。如果不以斜杠开头，那么就追加到当前URL的末尾。

```shell
$ python3 urllib_parse_urljoin_with_path.py

http://www.example.com/subpath/file.html
http://www.example.com/path/subpath/file.html
```

## Encoding Query Arguments

在参数追加到URL之前，可以将它们编码。

### urllib_parse_urlencode.py

```python
# urllib_parse_urlencode.py

from urllib.parse import urlencode

query_args = {
    'q': 'query string',
    'foo': 'bar'
}
encoded_args = urlencode(query_args)
pritn('Encoded:', encoded_args)
```

编码会把一些特殊字符给替换掉，让这些参数符合RFC规范.

```shell
$ python3 urllib_parse_urlencode.py

Encoded: q=query+string&foo=bar
```

### urllib_parse_urlencode_doseq.py

如果想让一个值出现多次，那么在调用`urlencode()`的时候传入参数`doseq=True`.

```python
# urllib_parse_urlencode_doseq.py

from urllib.parse import urlencode

query_args = {
    'foo': ['foo1', 'foo2']
}
print('Single  :', urlencode(query_args))
print('Sequence:', urlencode(query_args, doseq=True))
```

输出如下:

```shell
$ python3 urllib_parse_urlencode_doseq.py

Single  : foo=%5B%27foo1%27%2C+%27foo2%27%5D    #! 方括号[]都被转义
Sequence: foo=foo1&foo=foo2
```

### urllib_parse_parse_qs.py

想要解码一个query string，可以使用`parse_qs()`和`parse_qsl()`.

```python
# urllib_parse_parse_qs.py

from urllib.parse import parse_qs, parse_qsl

encoded = 'foo=foo1&foo=foo2'

print('parse_qs :', parse_qs(encoded))
print('parse_qsl:', parse_qsl(encoded))
```

`parse_qs()`返回一个字典，`parse_qsl()`返回包含元组的序列.

```shell
$ python3 urllib_parse_parse_qs.py

parse_qs : {'foo': ['foo1', 'foo2']}
parse_qsl: [('foo', 'foo1'), ('foo', 'foo2')]
```

### urllib_parse_quote.py

query参数中的特殊字符需要被quote。可以使用`qoute()`和`quote_plus()`函数来进行。

```python
# urllib_parse_quote.py

from urllib.parse import quote, quote_plus, urlencode

url = 'http://localhost:8080/~hellmann/'
print("urlencode()  :", urlencode({"url": url}))
print("quote()      :", quote(url))
print("quote_plus() :", quote_plus(url))
```

输出:

```shell
$ python3 urllib_parse_quote.py

urlencode() : url=http%3A%2F%2Flocalhost%3A8080%2F%7Ehellmann%2F
quote()     : http%3A//localhost%3A8080/%7Ehellmann/
quote_plus(): http%3A%2F%2Flocalhost%3A8080%2F%7Ehellmann%2F
```

### urllib_parse_unquote.py

想要逆quote，可以使用`unquote()`和`unquote_plus()`函数.

```python
# urllib_parse_unquote.py

from urllib.parse import unquote, unquote_plus

print(unquote('http%3A//localhost%3A8080/%7Ehellmann/'))
print(unquote_plus(
    'http%3A%2F%2Flocalhost%3A8080%2F%7Ehellmann%2F'
))
```

结果:

```shell
$ python3 urllib_parse_unquote.py

http://localhost:8080/~hellmann/
http://localhost:8080/~hellmann/
```



