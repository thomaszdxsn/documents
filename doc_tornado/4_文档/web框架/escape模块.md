[TOC]

## tornado.escape -- 转义和字符串操作

用于HTML, JSON, URL以及其它的转义／反转义方法。

同样包括一些杂七杂八的字符串操作函数。

### 转义函数

- `tornado.escape.xhtml_escape(value)`

    转义一个字符串，让它变成合法的HTML或XML的值。

    转义`<, >, ", ', &`这些字符。当在属性值中使用这些字符串时必须使用引号包裹。

- `tornado.escape.xhtml_unescape(value)`

    反转义一个XML转义后的字符串。

- `tornado.escape.url_escape(value, plus=True)`

    将给定的值使用URL编码转义后并返回。

    如果`plus=True`(默认值)，空格将会替换为"+"而不是`%20`。这放在query string和表单数据中很合适，但是在一个URL的路径部分就不正确了。注意这个默认值和Python的urllib模块相反。

- `tornado.escape.url_unescape(value, encoding='utf-8', plus=True)`

    将给定的值通过URL编码解码。

    参数可以是byte或者unicode字符串。

    如果`encoding=None`，结果将会是byte字符串。否则将会使用默认值unicode。

    如果`plus=True`(默认值)，空格将会替换为"+"而不是`%20`。这放在query string和表单数据中很合适，但是在一个URL的路径部分就不正确了。注意这个默认值和Python的urllib模块相反。

- `tornado.escape.json_encode(value)`

    返回给定Python对象的JSON编码形式。

- `tornado.escape.json_decode(value)`

    通过给定的JSON字符串，返回Python对象。

### Byte/Unicode转换

这些函数在Tornado源码中到处可见，但是大多数应用可能并不需要直接使用。注意这些函数的复杂性是为了让Tornado同时支持Python2和Python3.

- `tornado.escape.utf8(value)`

    将一个字符串参数转换为一个byte字符串。

    如果这个参数已经是一个byte字符串或者None，会将它原样返回。其它情况下它必须是一个utf编码的unicode字符串。

- `tornado.escape.to_unicode(value)`

    将一个字符串参数转换为一个unicode字符串。

    如果这个参数已经是一个unicode字符串或者None，会将它原样返回。其它情况下它必须是一个byte字符串。

- `tornado.escape.native_str()`

    将一个byte或者unicode字符串转换为原生`str`类型。在Python2中等同于调用`utf8()`，在Python3中等同于调用`to_unicode()`。

- `tornado.escape.to_basestring(value)`

    将一个字符串参数转换为一个basestring的子类。

    在Python2中，byte和unicode字符串大多数情况下是可变换的。在Python3中这两个类型不可变换，所以这个方法需要把byte转换为unicode。

- `tornado.escape.recursive_unicode(obj)`

    迭代简单的数据结构，将byte转换为unicode。

    支持列表，元组和字典。

### 杂项函数

- `tornado.escape.linkify(text, shorten=False, extra_params='', require_protocol=False, permited_protocol=['http', 'https'])`

    将一个平文本转换为HTML的A标签文本。

    例如：
    ```python
    linkify("Hello http://tornadoweb.org!")

    # 将会返回
    Hello <a href="http://tornadoweb.org">http://tornadoweb.org</a>!
    ```

    参数：

    - `shorten`: 长的url将会在显示时缩短。

    - `extra_params`: 这个a标签包含的额外文本，或者传入一个可调用对象，接受这个连接为参数并返回额外的文本。

        比如 `linkify(text, extra_params='rel="nofollow" class="external"')`

        或者:

        ```python
        def extra_params_cb(url):
            if url.startswith("http://example.com"):
                return 'class="internal"'
            else:
                return 'class="external" rel="nofollow"'
        linkify(text, extra_params=extra_params_cb)
        ```
    
    - `require_protocol`: 只讲包含协议的URL转换为a标签。如果这个值为False，那么类似**www.facebook.com**的值也会被转换为a标签。

    - `permitted_protocol`: 一个应该被转换为连接的URL允许使用的协议列表／集合。比如`linkify(text, permitted_protocols=["http", "ftp", "mailto"])`，注意不要在这里加入javascript(伪)协议，这是很不安全的做法。

- `tornado.escape.squeeze(value)`

    将所有连续出现的多个空白字符变为一个字符。

