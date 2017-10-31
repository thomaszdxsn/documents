## tornado.httputil -- 操作HTTP头部和URL

包含HTTP客户端和服务器使用的工具代码。

这个模块同样定义了一个`HTTPServerRequest`类，它还有一个大家都属性的引用，即`tornado.web.RequestHandler.request`。

- `tornado.httputil.HTTPHeaders(*args, **kwargs)`

    一个字典，它的所有键都是`Http-Header-Case`。

    通过一对新方法`add()`和`get_list()`来为一个键支持多个值。常规的字典接口一个键只会返回一个值，多个值需要用逗号来拼接。

    ```python
    >>> h = HTTPHeaders({"content-type": "text/html"})
    >>> list(h.keys())
    ['Content-Type']
    >>> h['Content-Type']
    'text/html'
    ```

    ```python
    >>> h.add("Set-Cookie", "A=B")
    >>> h.add("Set-Cookie", "C=D")
    >>> h['set-cookie']
    'A=B, C=D'
    >>> h.get_list("set-cookie')
    ['A=B', 'C=D']
    ```

    ```python
    >>> for (k, v) in sorted(h.get_all()):
    ...     print("%s: %s" %(k, v))
    ...     
    Content-Type: text/html
    Set-Cookie: A=B
    Set-Cookie: C=D
    ```

    - `add(name, value)`

        对给定的键增加一个新的value。

    - `get_list(name)`

        通过给定的头部名称返回所有值，以列表形式返回。

    - `get_all()`

        返回所有(name, value)键值对的一个可迭代对象。

        如果一个头部名称具有多个值，将会以这个同样的名称返回多个键值对。

    - `parse_line(line)`

        通过一个头部行(字符串)更新这个字典。

        ```python
        >>> h = HTTPHeaders()
        >>> h.parse_line('Content-Type: text/html')
        >>> h.get('content-type')
        'text/html'
        ```

    - 类方法`parse(headers)`

        将一个HTTP头部文本解析，并返回一个字典(HTTPHeaders对象)。

        ```python
        >>> h = HTTPHeaders.parse("Content-Type: text/html\r\nContent-Length: 42\r\n")
        >>> sorted(h.items())
        [('Content-Length', '42'), ('Content-Type', 'text/html')]
        ```

        

