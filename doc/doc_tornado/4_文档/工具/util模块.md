## tornado.util -- 通用的工具函数(utilities)

杂项使用的工具函数及类。

这个模块在Tornado内部使用。不要期待这个模块定义的函数对其它应用同样适用。

这个模块的一个对公共使用的部分即`Configurable`类和它的`configure`方法，将会变为子类的一部分接口，包括`AsyncHTTPClient`， `IOLoop`, 和`Resolver`。

- 类`tornado.util.ObjectDict`

    创建一个行为像对象的字典，可以通过属性访问方式来使用它。

- 类`tornado.util.GzipDecompressor`

    流化(streaming)gzip解压缩器。

    这个接口很像`zlib.decompressobj`.

    - `decompress(value, max_length=None)`

        解压缩一个chunk，返回可用的数据。

        一些数据可能会缓存供之后使用；如果没有更多输入数据，必须调用`flush()`来确保所有的数据都会被处理。

        如果给定了`max_length`，一些输入数据将会剩余给`unconsumed_tail`；你必须取回这个值，然后将之传回给future。

    - `unconsumed_tail`

        返回剩余部分的压缩数据。

    - `flush()`

        返回未被decompress返回的残留缓存数据。

        并且会检查错误，如被删节输入。在`flush`之后就不要调用其它方法了。


- `tornado.util.import_object(name)`

    通过一个名称来import一个对象。

    `import_object('x')`等同于`import x`, `import_object(‘x.y.z’)`等同于`from x.y import z`

    ```python
    >>> import tornado.escape
    >>> import_object('tornado.escape') is tornado.escape
    True
    >>> import_object('tornado.escape.utf8') is tornado.escape.utf8
    True
    >>> import_object('tornado') is tornado
    True
    >>> import_object("tornado.missing_module")
    Traceback (most recent call last):
    ...
    ImportError: No module named missing_module
    ```

- `tornado.util.errno_from_exception(e)`

    通过一个Exception对象，返回errno。

    有些时候没有设置errno属性，我们会将会把errno从args中拉出来，如果实例化Exception没有使用参数，你将会获得一个tuple error。所以这个方法抽象了这些情况，给你看一个方便的方法来获取errno.

- `tornado.util.re_unescape(s)`

    将一个通过`re.escape`转义的字符串反转义。

    如果对一个不是由`re.escape`生成的正则(比如，包含`\d`的字符串就不能反转义)使用，将会抛出一个ValueError。
    
- 类`tornado.util.Configurable`

    configurable接口的基类。

    configurable接口是一个(抽象)类，它的构造器扮演工厂函数的功能，工厂返回的是子类实现之一。子类实现以及初始化器的可选关键字参数可以在运行时通过`configure`来全局配置。

    使用这个构造器当作一个工厂方法，它的接口类似一个普通类，`isinstance`和平常一样使用。这个设计模式在需要从实现子类中选择一个当作全局决定时很有用(比如，如果`epoll`可用，总是使用它来替代`select`)，或者当先前很巨大的类切分成特殊的子类时也很有用。

    Configurable子类必须定义类方法`configurable_base`, `configurable_default`, 并使用实例方法`initialize`来替代`__init__`。

    - 类方法`configurable_base()`

        返回configurable结构的基类。

        通常返回它定义的那个类(并不一定和`cls`参数相同)。

    - 类方法`configurable_default()`

        返回使用的类实现。

    - `initialize()`

        初始化一个`Configurable`子类实例。

        Configurable类必须使用`initialize`来替代`__init__`。

    - 类方法`configure(impl, **kwargs)`

        当基类实例化后，选择使用的类。

        关键字参数将会保存并传入到构造器参数列表中。这个方法可以用来设置一些参数的全局默认值。

    - 类方法`configured_class()`

        返回当前的configured类。


- `tornado.util.ArgReplacer(func, name)`

    替换`arg, kwargs`对中的一个值。

    将会审查`func`的参数，根据一个name来找到参数。用于装饰器和类似wrapper。

    - `get_old_value(args, kwargs, default=None)`

        返回name参数替换之前的旧值。

        如果给定的参数没有存在，返回default。

    - `replace(new_value, args, kwargs)`

        通过new_value来替换args,kwargs中的一个name参数。

        返回`(old_value, args, kwargs)`.返回的`args`和`kwargs`对象可能和输入时不同。

        如果name参数没有找到，`new_value`将会加入到kwargs, `old_value`将会返回None。


- `tornado.util.timedelta_to_seconds(td)`

    等同于`td.total_seconds()`

