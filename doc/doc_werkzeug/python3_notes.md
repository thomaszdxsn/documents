# Python 3 Notes

在Werkzeug0.9开始，Werkzeug支持Python3.3+.

文档的这一部分主要描述在Python3中使用Werkzeug和WSGI的特殊要求。

## WSGI Environment

Python3 中的WSGI environment和Python2 有一个不同。

Werkzeug大部分时候会将底层的细节为你隐藏好。

Python2和Python3的之间的主要差异就是WSGI environment的内容是bytes还是其它字符串。

Python3中的WSGI environ有两种不同类型的strings：

- 限制为latin-1编码的unicode。用于HTTP头部和其它的一些地方。

- 带binary payload的unicode。在Werkzeug中这通常叫做"WSGI encoding dance"

Werkzeug帮你自动处理了这些事情，所以你不需要为此过多担心。

下面的函数和类可以用来读取WSGI environ的信息:

- `get_current_url()`

- `get_host()`

- `get_script_name()`

- `get_query_string()`

- `EnvironHeaders()`

强烈不鼓励在Python3中手动创建和修改WSGI environ，除非确定自己能处理好解码问题。


## URLs

Werkzeug中的URLs在Python3里面会以unicode字符串来表示。

## Request Cleanup

Python3和PyPy中的Request对象要求在文件上传的时候显式关闭(closing).

这要求multipart解析器创建的临时文件对象能够适当地关闭。

所以引入了一个`close()`方法。

除此之外，request对象可以作为上下文管理器来进行自动关闭。



