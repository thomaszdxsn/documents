# yarl

这个模块提供一个方便的`URL`类，用于url解析和更改.

## Introduce

Url是通过`str`来构建的:

```
>>> from yarl import URL
>>> url = URL('https://www.python.org/~guido?arg=1#frag')
>>> url
URL('https://www.python.org/~guido?arg=1#frag')
```

所有的url组件: scheme, user, password, host, port, path, query和fragment都
可以通过属性来访问:

```
>>> url.scheme
'https'
>>> url.host
'www.python.org'
>>> url.path
'/~guido'
>>> url.query_string
'arg=1'
>>> url.query
<MultiDictProxy('arg': '1')>
>>> url.fragment
'frag'
```

所有的url操作都会生产一个新的url对象:

```
>>> url.parent / 'downloads/source'
URL('https://www.python.org/downloads/source')
```

传入构造器的字符串将会自动进行URL转义:

```
>>> url = URL('https://www.python.org/путь')
>>> url
URL('https://www.python.org/%D0%BF%D1%83%D1%82%D1%8C')
```

正规的属性都是百分比转义形式，使用`raw_`前缀的属性可以访问被编码的字符串:

```
>>> url.path
'/путь'

>>> url.raw_path
'/%D0%BF%D1%83%D1%82%D1%8C'
```

使用`human_repr()`可以阅读URL的人类友好形式:

```
>>> url.human_repr()
'https://www.python.org/путь'
```

## Public API

yarl中唯一的一个公开类就是`URL`:

`>>> from yarl import URL`

- class `yarl.URL(arg, *, encoded=False)`

    URL的表现形式为:

    `[scheme:]//[user[:password]@]host[:port][/path][?query][#fragment]`

    一般是绝对URL加上:

    `[/path][?query][#fragment]`

    URL的结构为:

    ```
    http://user:pass@example.com:8042/over/there?name=ferret#nose
    \__/   \__/ \__/ \_________/ \__/\_________/ \_________/ \__/
     |      |    |        |       |      |           |        |
    scheme  user password host    port   path       query   fragment
    ```

    内部来说，所有的数据都是以编码前的形式保留。

    构造器和修改操作符都会自动对参数和操作对象执行编码。这个库假设所有的数据都
    使用UTF-8的百分比编码形式。

    ```
    >>> URL('http://example.com/path/to/?arg1=a&arg2=b#fragment')
    URL('http://example.com/path/to/?arg1=a&arg2=b#fragment')
    ```

    如果URL的部分都是ascii形式，那么它编码后也不会有什么变化。

    否则：

    ```
    >>> str(URL('http://εμπορικόσήμα.eu/путь/這裡'))
    'http://xn--jxagkqfkduily1i.eu/%D0%BF%D1%83%D1%82%D1%8C/%E9%80%99%E8%A3%A1'
    ```

    已经编码的URL不会再被修改了:

    ```
    >>> URL('http://xn--jxagkqfkduily1i.eu')
    URL('http://xn--jxagkqfkduily1i.eu')
    ```

    使用`URL.human_repr()`可以获得阅读友好的表达形式:

    ```
    >>> url = URL('http://εμπορικόσήμα.eu/путь/這裡')
    >>> str(url)
    'http://xn--jxagkqfkduily1i.eu/%D0%BF%D1%83%D1%82%D1%8C/%E9%80%99%E8%A3%A1'
    >>> url.human_repr()
    'http://εμπορικόσήμα.eu/путь/這裡'
    ```

## URL properties

有两种类型的properties: 解码形式和编码形式(带有`raw_`前缀):

- URL.scheme

    ```
    >>> URL('http://example.com').scheme
    'http'
    >>> URL('//example.com').scheme
    ''
    >>> URL('page.html').scheme
    ''
    ```

- URL.user

    ```
    >>> URL('http://john@example.com').user
    'john'
    >>> URL('http://андрей@example.com').user
    'андрей'
    >>> URL('http://example.com').user is None
    True
    ```

- URL.raw_user

    ```
    >>> URL('http://андрей@example.com').raw_user
    '%D0%B0%D0%BD%D0%B4%D1%80%D0%B5%D0%B9'
    >>> URL('http://example.com').raw_user is None
    True
    ```

- URL.password

    ```
    >>> URL('http://john:pass@example.com').password
    'pass'
    >>> URL('http://андрей:пароль@example.com').password
    'пароль'
    >>> URL('http://example.com').password is None
    True
    ```

- URL.raw_password

    ```
    >>> URL('http://user:пароль@example.com').raw_password
    '%D0%BF%D0%B0%D1%80%D0%BE%D0%BB%D1%8C'
    ```

- URL.host

    ```
    >>> URL('http://example.com').host
    'example.com'
    >>> URL('http://хост.домен').host
    'хост.домен'
    >>> URL('page.html').host is None
    True
    >>> URL('http://[::1]').host
    '::1'
    ```

- URL.raw_host

    ```
    >>> URL('http://хост.домен').raw_host
    'xn--n1agdj.xn--d1acufc'
    ```

- URL.port

    URL的port部分。

    ```
    >>> URL('http://example.com:8080').port
    8080
    >>> URL('http://example.com').port
    80
    >>> URL('page.html').port is None
    True
    ```

- URL.path

    ```
    >>> URL('http://example.com/path/to').path
    '/path/to'
    >>> URL('http://example.com/путь/сюда').path
    '/путь/сюда'
    >>> URL('http://example.com').path
    '/'
    ```

- URL.path_qs

    ```
    >>> URL('http://example.com/path/to?a1=a&a2=b').path_qs
    '/path/to?a1=a&a2=b'
    ```

- URL.raw_path_qs

    ```
    >>> URL('http://example.com/путь/сюда?ключ=знач').raw_path_qs
    '/%D0%BF%D1%83%D1%82%D1%8C/%D1%81%D1%8E%D0%B4%D0%B0?%D0%BA%D0%BB%D1%8E%D1%87=%D0%B7%D0%BD%D0%B0%D1%87'
    ```

- URL.raw_path

    ```
    >>> URL('http://example.com/путь/сюда').raw_path
    '/%D0%BF%D1%83%D1%82%D1%8C/%D1%81%D1%8E%D0%B4%D0%B0'
    ```

- URL.query_string

    ```
    >>> URL('http://example.com/path?a1=a&a2=b').query_string
    'a1=a&a2=b'
    >>> URL('http://example.com/path?ключ=знач').query_string
    'ключ=знач'
    >>> URL('http://example.com/path').query_string
    ''
    ```

- URL.raw\_query\_string

    ```
    >>> URL('http://example.com/path?ключ=знач').raw_query_string
    '%D0%BA%D0%BB%D1%8E%D1%87=%D0%B7%D0%BD%D0%B0%D1%87'
    ```

- URL.fragment

    ```
    >>> URL('http://example.com/path#fragment').fragment
    'fragment'
    >>> URL('http://example.com/path#якорь').fragment
    'якорь'
    >>> URL('http://example.com/path').fragment
    ''
    ```

- URL.raw_fragment

    ```
    >>> URL('http://example.com/path#якорь').raw_fragment
    '%D1%8F%D0%BA%D0%BE%D1%80%D1%8C'
    ```

- URL.parts

- URL.raw_parts

- URL.name

    parts的最后一部分.

- URL.raw_name

- URL.query

    使用`multidict.MultiDictProxy`来代表query string.

## Absolute and relative URLs

这个模块支持绝对路径和相对路径.

区队路径应该以scheme或者`//`开头.

- URL.is_absolute()

    检查是否为绝对路径。

    如果是绝对路径则返回True。

    ```
    >>> URL('http://example.com').is_absolute()
    True
    >>> URL('//example.com').is_absolute()
    True
    >>> URL('/path/to').is_absolute()
    False
    >>> URL('path').is_absolute()
    False
    ```

## New URL generation

URL是一个不可变对象，每个对它的操作都会生成新的URL实例。

- `URL.build(*, scheme, user, password, host, port, path, query, query_string,
    fragment, strict=False)`

    创建并返回一个新的URL。

    ```
    >>> URL.build(scheme='http', host='example.com')
    URL('http://example.com')

    >>> URL.build(scheme='http', host='example.com', query={"a": "b"})
    URL('http://example.com/?a=b')

    >>> URL.build(scheme='http', host='example.com', query_string='a=b')
    URL('http://example.com/?a=b')

    >>> URL.build()
    URL('')
    ```

- `URL.with_scheme(scheme)`

    替换scheme并返回一个新的URL。

- `URL.with_user(user)`

    替换user并返回一个新的URL。

- `URL.with_password(password)`

    替换password并返回一个新的URL。

- `URL.with_host(host)`

    替换host并返回一个新的URL，如果需要的话会自动为host转义.

- `URL.with_port(port)`

- `URL.with_path(path)`

- `URL.with_query(query)`

- `URL.with_query(**kwargs)`

- `URL.update_query(query)`

- `URL.update_query(**kwargs)`

- `URL.with_fragment(port)`

- `URL.with_name(name)`

- `URL.parent`

    ```
    >>> URL('http://example.com/path/to?arg#frag').parent
    URL('http://example.com/path')
    ```

- `URL.origin()`

    一个新的URL，只包含scheme, host和port.

    ```
    >>> URL('http://example.com/path/to?arg#frag').origin()
    URL('http://example.com')
    >>> URL('http://user:pass@example.com/path').origin()
    URL('http://example.com')
    ```

- `URL.relative()`

    一个新的相对URL，只包含path, query和fragment.

    ```
    >>> URL('http://example.com/path/to?arg#frag').relative()
    URL('/path/to?arg#frag')
    ```

    除法操作符(`/`)也可以用来创建一个新的URL，会把第二个操作数追加到
    原来的URL上面.**但是**，会移除掉query string和fragment部分.

    ```
    >>> url = URL('http://example.com/path?arg#frag') / 'to/subpath'
    >>> url
    URL('http://example.com/path/to/subpath')
    >>> url.parts
    ('/', 'path', 'to', 'subpath')
    >>> url = URL('http://example.com/path?arg#frag') / 'сюда'
    >>> url
    URL('http://example.com/path/%D1%81%D1%8E%D0%B4%D0%B0')
    ```

- `URL.join(url)`

    可以通过组合一个"base URL"和另一个URL来组成一个完整的URL。

    ```
    >>> base = URL('http://example.com/path/index.html')
    >>> base.join(URL('page.html'))
    URL('http://example.com/path/page.html')
    ```

    如果`url`是一个绝对URL，那么url的host名称或者scheme会出现在结果中:

    ```
    >>> base = URL('http://example.com/path/index.html')
    >>> base.join(URL('//python.org/page.html'))
    URL('http://python.org/page.html')
    ```

## Human readable representation

...

## Default port substitution

scheme | port
-- | --
'http' | 80
'https' | 443
'ws' | 80
'wss' | 443

- `URL.is_default_port()`

    判断是否使用了默认port。

    相对URL没有默认port。

    ```
    >>> URL('http://example.com').is_default_port()
    True
    >>> URL('http://example.com:80').is_default_port()
    True
    >>> URL('http://example.com:8080').is_default_port()
    False
    >>> URL('/path/to').is_default_port()
    False
    ```

## Reference

这么模块借用了`pathlib`的设计。

同样使用了`urllib.parse`.

RFC提案| 标题 | 描述
-- | -- | -- 
RFC5891 | Internationalized Domain Names in Applications | 描述了非ascii的domain名称的编码方式
RFC3987 | Internationalized Resouce Identifiers | 描述了URL中非ascii字符的处理方法
RFC3986 | Uniform Resource Identifiers | 这是当前的URI标准.
RFC2732 | Format for Literal IPv6 Addresses in URL's | 描述了URL中IPv6的解析
RFC2396 | Uniform Resource Identifiers(URI): Generic Syntax | 描述了URN和URL的语法
RFC2368 | The mailto URL scheme | 描述了mailto URL schemes
RFC1808 | Relative Uniform Resource Locators This Request For | 描述了如何将绝对URL和相对URL join起来，以及一些异常情况
RFC1738 | Uniform Resource Locators(URL) | 描述了URL的语义和语法.
