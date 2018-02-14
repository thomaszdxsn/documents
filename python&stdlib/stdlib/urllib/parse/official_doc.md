# urllib.parse -- Parse URLs into components

源代码：[Lib/urllib/parse.py](https://github.com/python/cpython/tree/3.5/Lib/urllib/parse.py)

这个模块定义了一套标准的接口，可以将URL字符串分解为组件(addressing scheme, network locaotion, path等等.)，也可以将组件组合成一个URL字符串，并且可以把一个相对URL(加上给定的基础URL)变为绝对URL。

这个模块的URL是匹配网络RFC提案。它支持以下的URL scheme:`file`,`ftp`,`gopher`,`hdl`,`http`,`https`,`imap`,`mailto`,`mms`,`news`,`nntp`,`prospero`,`rsync`,`rtsp`,`rtspu`,`sftp`,`sip`,`sips`,`snews`,`svn`,`svn+ssh`,`telnet`,`wais`,`ws`,`wss`.

`urllib.parse`模块定义了很多函数，并可以按照功能划归两个类别：URL解析和URL quoting.

## URL Parsing

URL解析函数主要是把URL字符串分隔为不同的组件，或者把URL组件组合成一个URL字符串。

- `urllib.parse.urlparse(urlstring, scheme="", allow_fragments=True)`

    将一个URL解析为6个组件，返回一个6位长的元组。一个URL大概的结构为:`scheme://netloc/path;parameters?query#fragment`.每一个元组的item都是一个字符串，这些item都可以为空。组件不会分隔为更小的部分(例如，netwowk location是一个简单的字符串)，另外`%`转义不会被扩展。分隔符不会包括在结果中，除了path中的反斜杠，如果path中有的反斜杠的话会保留。例如：

    ```python
    >>> from urllib.parse import urlparse
    >>> o = urlparse('http://www.cwi.nl:80/%7Eguido/Python.html')
    >>> o
    ParseResult(scheme='http', netloc='www.cwi.nl:80', path='/%7Eguido/Python.html',
                params='', query='', fragment='')
    >>> o.scheme
    'http'
    >>> o.port
    80
    >>> o.get_url()
    'http://www.cwi.nl:80/%7Eguido/Python.html'                
    ```
    
    下面的语法是RFC1808的规范，只有以`//`开头的字符串会被识别为`netloc`.否则输入会被假定为是一个相对的URL。

    ```python
    >>> from urllib.parse import urlparse
    >>> urlparse('//www.cwi.nl:80/%7Eguido/Python.html')
    ParseResult(scheme='', netloc='www.cwi.nl:80', path='%7Eguido/Python.html',
                params='', query='', fragment='')
    >>> urlparse('www.cwi.nl/%7Eguido/Python.html')
    ParseResult(scheme='', netloc='', path='www.cwi.nl/%7Eguido/Python.html',
                params='', query='', fragment='')
    >>> urlparse('help/Python.html')
    ParseResult(scheme='', netloc='', path='help/Python.html', params='',
                query='', fragment='')
    ```

    `scheme`参数是默认的addressing scheme，只有在URL未指定的时候会被使用。它应该使用和`urlstring`相同的类型(文本或者bytes)，默认值为`''`，也会根据情况转换为`b''`.

    如果`allow_fragments`参数为False，fragment标识符不会被识别。而是会在解析的时候把它识别为path的一部分，在返回的结果中`fragment`会被认为是空字符串。

    返回的值是一个`tuple`子类的实例。这个类有下面这些额外的“只读”属性:

    属性 | 索引 | 值 | 默认值
    -- | -- | -- | --
    scheme | 0 | URL scheme标识符 | scheme参数
    netloc | 1 | network location部分 | 空字符串
    path | 2 | path部分 | 空字符串
    params | 3 | path最后部分的parameters | 空字符串
    query | 4 | query部分 | 空字符串
    fragment | 5 | fragment标识符 | 空字符串
    username | | 用户名 | None
    password | | 密码 | None
    hostname | | Host名称(小写形式) | None
    port | | 端口号(整数形式) | None

    请看`Structured Parse Results`章节，有关于结果对象的更多信息。

    在`netloc`属性中如果存在非对称的方括号，会抛出`ValueError`.

- `urllib.parse.parse_qs(qs, keep_blank_values=False, strict_parsing=False, encoding='utf-8', errors='replace')`

    将一个给定的字符串参数(application/x-www-form-urlencoded类型的数据)按照query string来解析。数据以字典形式返回。字典的键是唯一的query变量名称，值是每个名称的值的list。

    可选参数`keep_black_values`是一个flag，代表是否把百分比编码的query中的空白值当作空白字符串。True代表保留空白字符串。默认值为False，代表空白字符串将会被忽略。

    可选参数`strict_parsing`是一个flag，代表在解析错误的时候应该怎么做。如果是False(默认值)，错误会被忽略。如果设置为True，将会抛出`ValueError`异常。

    可选参数`encoding`和`errors`代表传入编码方法的参数。

    使用`urllib.parse.urlencode()`(将`doesq`参数设置为True)函数可以把这样的字符串重新转换为字符串。

- `urllib.parse.parse_qsl(qs, keep_blank_values=False, strict_parsing=False, encoding='utf-8', errors='replace')`

    将一个给定的字符串参数(application/x-www-form-urlencoded类型的数据)按照query string来解析。数据以list形式返回，(name, value)对

    可选参数`keep_black_values`是一个flag，代表是否把百分比编码的query中的空白值当作空白字符串。True代表保留空白字符串。默认值为False，代表空白字符串将会被忽略。

    可选参数`strict_parsing`是一个flag，代表在解析错误的时候应该怎么做。如果是False(默认值)，错误会被忽略。如果设置为True，将会抛出`ValueError`异常。

    可选参数`encoding`和`errors`代表传入编码方法的参数。

    使用`urllib.parse.urlencode()`(将`doesq`参数设置为True)函数可以把这样的字符串重新转换为字符串。

- `urllib.parse.urlunparse(parts)`

    用`urlparse()`返回的元组构成一个URL。`parts`参数可以是任何6位长度的元组。结果可能有些微妙的差别，但是URL本质上是相等的，URL中的一些
    多余的分隔符会被移除。

- `urllib.parse.urlsplit(urlstring, scheme='', allow_fragments=True)`

    这个函数和`urlparse()`类似，但是不会分隔URL的`params`部分。如果是实用最近的URL语法允许parameters应用到URL的path每部分(请看RFC2396)，可以使用它来提到`urlparse()`.需要另外一个独立的函数来分隔path和parameter。这个函数返回一个长度为5的元组：`(addressing scheme, network location, path, query, fragment identifier)`.

    返回的值是一个tuple子类实例。这个类有下面这么一些额外的(只读)属性:

    属性 | 索引 | 值 | 默认值
    -- | -- | -- | --
    scheme | 0 | URL scheme标识符 | scheme参数
    netloc | 1 | Network location部分 | 空字符串
    path | 2 | Hierarchical path | 空字符串
    query | 3 | Query组件 | 空字符串
    fragment | 4 | Fragment标识符 | 空字符串
    username | | 用户名 | None
    password | | 密码 | None
    hostname | | Host名称(小写) | None
    port | | 端口号码(整数形式) | None

    请看`Structured Parse Results`章节，有关于结果对象的更多信息。

    在`netloc`属性中如果存在非对称的方括号，会抛出`ValueError`.

- `urllib.parse.urlunsplit(parts)`

    将`urlsplit()`返回的元组重新组合成一个完整的URL。`parts`参数可以任意的长度为5的可迭代对象。可能有些细微的区别，但是是相等的URL，只是会去除一些多余的分隔符。

- `urllib.parse.urljoin(base, url, allow_fragments=True)`

    通过组合"base URL"(base参数)和另一个URL(url参数)，构建一个完整的(绝对)URL，为一个相对URL提供它缺失的部分。例如:

    ```python
    >>> from urllib.parse import urljoin
    >>> urljoin('http://www.cwi.nl/%7Eguido/Python.html', 'FAQ.html')
    'http://www.cwi.nl/%7Eguido/FAQ.html'
    ```

    参数`allow_fragments`的意义和`urlparse()`中的参数一样。

    > 注意: 如果`url`是一个绝对URL(也就是说，以`//`或者`scheme://`开头)，那么URL的host名/scheme名将会出现在结果中:
    >
    >> ```python
    >> >>> urljoin('http://www.cwi.nl/%7Eguido/Python.html',
    >> ...         '//www.python.org/%7Eguido')
    >> 'http://www.python.org/%7Eguido'

    如果你不想这样，那么需要使用`urlsplit()`或者`urlunsplit()`对传入的url预先处理，将`netloc`和`scheme`部分都移除。
    

- `urllib.parse.urldefrag(url)`

    如果`url`包含fragment标识符，返回一个去除fragment标识符的新的URL，fragment作为一个单独的字符串返回。如果不存在fragment标识符，返回URL和一个空字符串。

    返回的值是一个`tuple`子类的实例。这个类包含下面这些只读属性:

    属性 | 索引 | 值 | 默认值
    url | 0 | 不包含fragment的url | 空字符串
    fragment | 0 | fragment标识符 | 空字符串

## Parsing ASCII Encoded Bytes

URL解析函数最开始的时候只是用来解析字符串。在实际编程中，可以用它来
正确的把URL quote或编码为ASCII Bytes。因此，这个模块中所有的URL解析函数
除了针对`str`对象，也可以针对`bytes`和`bytearray`对象。

如果传入的是`str`数据，那么结果也会只包含`str`数据。如果传入的是`bytes`或者`bytearray`数据，那么结果也只包含`bytes`数据。

如果数据中混合了`str`和`bytes`，将会抛出`TypeError`，如果试图传入非ASCII数据，将会抛出`UnicodeDecodeError`.

为了支持结果对象(result object)在str和bytes之间方便的转换，URL解析函数返回的对象都提供了`encode()`方法(str转换为bytes)和`decode()`方法(bytes转换为str)。这些方法的参数签名和`str`与`bytes`同名方法一样(除了默认的编码为`ascii`而不是`utf-8`)。

这些规则只适用于解析函数。URL quoting函数使用它们自己的规则来生产和消费bytes。

## Structutred Parse Results

`urlparse()`, `urlsplit()`, `urldefrag()`函数返回的结果对象都是`tuple`类型的子类。这些子类的属性在这些函数的文档中都由说明，下面描述了编码和解码的支持情况，以及一些额外的方法:

- `urllib.parse.SplitResult.geturl()`

    将原始的URL转换为一个重新编译版本的字符串。原始字符串中的字母都会转换为小写，空的组件都会被删节。特别是，空的parameters，queries，和fragment标识符都会被移除。

    至于`urldefrag()`的结果，只有空的fragment标识符会被移除。对于`urlsplit()`和`urlparse()`的结果，所有改动都会反映在这个方法返回的URL。

    如果传入了原始的解析函数，这个方法的结果将会保持不变：

    ```python
    >>> from urllib.parse import urlsplit
    >>> url = 'HTTP://www.python.org/doc/#'
    >>> r1 = urlsplit(url)
    >>> url.geturl()
    'http://www.python.org/doc/'
    >>> r2 = urlsplit(r1.geturl())
    >>> r2.geturl()
    'http://www.python.org/doc'
    ```

    在操作`str`对象的时候，下面的类提供了结构化的解析结果(structured parse result)的实现。

- class`urllib.parse.DefragResult(url, fragment)`

    `urldefrag()`操作`str`结果的实体类。它的`.encode()`方法将会返回一个`DefragResultBytes`实例。

- class`urllib.parse.ParseResult(scheme, netloc, path, params, query, fragment)`

    `urlparse()`操作`str`结果的实体类。它的`.encode()`方法将会返回一个`ParseResultBytes`实例。

- class`urllib.parse.SplitResult(scheme, netloc, path, query, fragment)`

    `urlsplit()`操作`str`结果的实体类。它的`.encode()`方法将会返回一个`SplitResultBytes`实例。

下面的类是操作`bytes`或`bytearray`对象是解析结果的实现:

- class`urllib.parse.DefragResultBytes(url, fragment)`

    `urldefrag()`操作`bytes`结果的实体类。它的`.decode()`方法将会返回一个`DefragResult`实例。

- class`urllib.parse.ParseResultBytes(scheme, netloc, path, params, query, fragment)`

    `urlparse()`操作`bytes`结果的实体类。它的`.decode()`方法将会返回一个`ParseResult`实例。

- class`urllib.parse.SplitResultBytes(schema, netloc, path, query, fragment)`

    `urlsplit()`操作`bytes`结果的实体类。它的`.decode()`方法将会返回一个`SplitResult`实例。
    
## URL Quoting

URL quoting函数聚焦于把程序的数据通过quoting特殊字符和编码非ASCII文本，这些手段来将它们转换为可以安全使用的URL组件。也包含一些逆操作函数可以把数据归还原样。

- `urllib.parse.quote(string, safe='/', encoding=None, errors=None)`

    URL的每一部分，比如:path,query,等等...，都有属于它们的
    一部分保留字符需要被quoted。

    RFC 2396 Uniform Resource Identifiers (URI): 下面的
    保留字符属于基础的quote语法.

    保留    = ";" | "/" | "?" | ":" | "@" | "&" | "=" | "+" |
                  "$" | ","

    每个字符都只是在URL中的某些部分作为保留，而不是在URL所有地方都
    算作保留字符.

    默认情况下，`quote()`函数主要是为了quote掉URL的path部分。
    因此，它不会编码'/'。这个字符属于保留字符，
    但是一般情况下它在path的时候，
    并不需要将它看作是保留字符。

    `string`和`safe`要么是str，要么是bytes.
    如果string是一个bytes对象，不需要指定`encoding`和`errors`参数.

    可选参数`encoding`和`errors`可以决定如何处理非ASCII字符，
    它们也是`str.encode()`方法接受的参数。
    默认情况下，encoding='utf-8'(字符会以UTF-8编码)，
    errors='strict'(不支持的字符将会抛出`UnicodeEncodeError`).
    如果string是bytes对象，那么不要提供这两个可选参数，否则会抛出`TypeError`.
    
    注意`quote(string, safe, encoding, errors)`等同于`quote_from_bytes(string.encoding(encoding, errors), safe)`

    例子: quote('/El Niño/') == '/El%20Ni%C3%B1o/'


- `urllib.parse.quote_plus(string, safe='', encoding=None, errors=None)`

    和`quote()`类似，不过会把" "替换为"+"，HTML中的quoting是
    这么要求的。加号(+)在原始的字符串中需要被转义，除非它们被包括在
    safe中。并且这个函数的safe默认值并不包括'/'.

    例子: quote_plus('/El Niño/') == '%2FEl+Ni%C3%B1o%2F'

- `urllib.parse.quote_from_bytes(bytes, safe='/')`

    和`quote()`类似，但是接受`bytes`对象参数而不是`str`参数，
    并且不会执行str -> bytes的转码.

    例子: quote_from_bytes(b'a&\xef') == 'a%26%EF'

- `urllib.parse.unquote(string, encoding='utf-8', errors='replace')`

    将`%xx`替换为它们对等的单字符。可选参数`encoding`和`errors`代表`bytes.decode()`方法接受的参数。

    string必须是`str`.

    encoding默认为`utf-8`,errors默认为`replace`，意思是非法的序列(sequence)将会被替换为一个占位符。

    例子：`unquote('/E1%20Ni%C3%B1o/') == '/E1 Niño/`

- `urllib.parse.unquote_plus(string, encoding='utf-8', errors='replace')`

    想`unquote()`一样，不过会同时把加号"+"替换为空格，HTML表单数据需要这样的格式。

    string必须是`str`。

    例子: `unquote('/E1+Ni%C3%B1o/') == '/E1 Niño/`.

- `urllib.parse.unquote_to_bytes(string)`

    将`%xx`转义字符替换为它们对等的8进制值，返回一个`bytes`对象。

    `string`可以是一个`str`或者`bytes`对象。

    如果是一个`str`对象，将它们编码为UTF-8 bytes.
    
    例子: `unquote_to_bytes('a%26%EF) == b'a&\xef`.

- `urllib.parse.urlencode(query, doesq=False, safe='', encoding=None, errors=None, quote_via=quote_plus)`

    将一个映射(mapping)对象或者以2位元组为元素的序列转换为一个URL query string。结果可以是`str`或者`bytes`对象。

    返回的字符串结果是一系列`key=value`对,它们以`&`字符分隔，key和value都会使用`quote_via`函数来quote。默认情况下，使用`quote_plus()`，它会把空格编码为`+`，把`/`字符编码为`%2F`，这是标准的GET请求query string的方式。还可以传入另一个函数`quote`，它会把空格编码为`%20`，不会编码`/`字符。想要完全的控制quote的方式，可以传入`quote`并指定哪些值应该加入到safe中。

    `safe`，`encoding`，`errors`参数最终都会传入到`quote_via`.

    想要逆操作，可以使用`parse_qs()`和`parse_qsl()`.它们可以把一个query string转换为Python数据结构。

    


