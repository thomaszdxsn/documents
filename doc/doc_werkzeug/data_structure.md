# Data Structures

Werkzeug提供了一些Python对象的子类，加入了一些额外的特性。

它们中的一些类型是不可变的，其它的是用于HTTP用途的数据结构.

## General Purpose

- class`werkzeug.datastructures.TypeConversionDict`

    和平常的dict一样，但是`get()`方法可以执行类型转换.

    `MultiDict`和`ConbinedMultiDict`都是这个类的子类，都提供了类型转换功能.

    - `get(key, default=None, type=None)`

        如果请求的数据不存在，返回`default`。

        如果提供了`type`参数，并且这个参数是一个callble，可以用它来转换值的类型，
        如果不能转换则抛出`ValueError`.(但是实际不会抛出，只会返回`default`值)

        ```python
        >>> d = TypeConversionDict(foo='42', bar='blub')
        >>> d.get('foo', type=int)
        42
        >>> d.get('bar', -1, type=int)
        -1
        ```

        参数:

        - key: 要查询的key
        - default: 如果没有查询的key，默认的返回值.
        - type: 要转换的类型.如果抛出`ValueError`则返回`default`.

- class`werkzeug.datastructures.ImmutableTypeConversionDict`

    和`TypeConversionDict`一样，但是不支持修改.

    - `copy()`

        返回这个对象的一个浅拷贝.注意，标准库的`copy()`函数对这个类无用，就像
        所有的不可变对象一样(比如`tuple`).

- class`werkzueg.datastructures.MultiDict(mapping=None)`

    `MultiDict`是一个dict的子类，用来处理同一个键有多个值的情况，在wrappers的
    解析函数中有用到.

    这个数据结构是必须的，因为某些HTML表单元素会为相同的键传入多个值。

    基础用法:

    ```python
    >>> d = MultiDict([('a', 'b'), ('a', 'c')])
    >>> d
    MultiDict([('a', 'b'), ('a', 'c')])
    >>> d['a']
    'b'
    >>> d.getlist('a')
    ['b', 'c']
    >>> 'a' in d
    True
    ```

    它的行为像普通的dict，因此所有的dict函数都会返回一个键中找到的首个值。

    从Werkzeug0.3开始，这个字典抛出`KeyError`同样是`BadRequest`异常的子类，
    将会在全局异常捕获中被捕获，并渲染`400 BAD REQUEST`.

    `MultiDict`可以通过`(key, value)`元祖的迭代对象来构造.

    参数:

    - `mapping`: `MultiDict`的初始值。可以是一个正常的字典，一个`(key, value)`
        元祖的可迭代对象，或者是None.

    方法:

    - `add(key, value)`

        为一个键加入新的值.

    - `clear()` -> None

        移除字典中所有的items.

    - `copy()`

        返回这个对象的浅拷贝.

    - `deepcopy(memo=None)`

        返回这个对象的深拷贝.

    - `fromkeys(S[, v])` -> 一个新的字典, key从S开始，值等于v

        v 默认为None

    - `get(key, default=None, type=None)`

        如果请求的数据不存在，返回default.

        如果提供了`type`参数，并且它是一个callble，那么就用它来转换该指，返回
        转换后的值，或者在抛出`ValueError`的时候返回default。(即TypeConversionDict的行为).

    - `getlist(key, type=None)`

        返回给定key的item list。

        如果key不存在于MultiDict，返回的就是一个空list。

        和`.get()`一样，`.getlist()`也接受一个`type`参数。

    - `has_key(k)` -> 如果D有key k则返回True，否则返回False.

    - `items(*a, **kw)`

        和`iteritems()`一样，只是返回一个list.

    - `iteritems(multi=False)`

        返回`(key, value)`对的迭代器.

        参数:

        - `multi`: 如果为True，那么迭代器会为每个键的每个值都返回一对items。否则，
            只会返回每个键包含的第一个值组成的item。

    - `iterlists()`

        返回`(key, values)`对的list，values是所有关联这个键的值。

    - `iterlistvalues()`

        返回一个键关联所有值的迭代器。

    - `keys(*a, **kw)`

        和`iterkeys()`一样，但是返回一个list。

    - `lists(*a, **kw)`

        和`iterlists()`一样，但是返回一个list.

    - `listvalues(*a, **kw)`

        和`iterlistvalues()`一样，但是返回一个list。

    - `pop(key, default=None)`

        弹出这个dict item的第一个list member.

        然后这个键将会从字典中移除.

        ```python
        >>> d = MultiDict({'foo': [1, 2, 3]})
        >>> d.pop('foo')
        1
        >>> 'foo' in d
        False
        ```

        参数:

        - `key`: 要弹出的key
        - `default`: 如果key不存在，则返回这个值.

    - `popitem()`

        弹出dict的一个item。这个item的value只包含list中的第一个member.

    - `popitemlist()`

        从字典中弹出一个`(key, list)`元祖。

    - `poplist(key)`

        将字典中一个键的所有值弹出，以list的形式。

        如果这个键不存在，则会返回一个空list。

    - `setdefault(key, default=None)`

        如果键存在，则返回它的值，否者返回`default`，并且将它设置为这个key
        的值。

    - `setlist(key, new_list)`

        移除一个键的旧值，加入新的值。

        注意，你传入的list是一个浅拷贝。

        ```python
        >>> d = MultiDict()
        >>> d.setlist('foo', ['1', '2'])
        >>> d['foo']
        '1'
        >>> d.getlist('foo')
        ['1', '2']
        ```

    - `setlistdefault(key, default_list)`

        类似`setdefault`，但是可以设置多个值。

        返回的list不是一个拷贝，而是内部使用的list。

        意味着你可以直接对返回的list进行操作。

        ```python
        >>> d = MultiDict({"foo": 1})
        >>> d.setlistdefault("foo").extend([2, 3])
        >>> d.getlist('foo')
        [1, 2, 3]
        ```

    - `to_dict(flat=True)`

        返回一个常规字典。

        如果`flat`为True，返回的字典只会包含原来的第一个value，如果设置为False，
        返回的字典键将会是list形式。

    - `update(other_dict)`

        `update()`将会扩展当前的字典，而不是替换已经存在的key list：

        ```python
        >>> a = MultiDict({'x': 1})
        >>> b = MultiDict({"x": 2, "y": 3})
        >>> a.update(b)
        >>> a
        MultiDict([('y', 3), ('x', 1), ('x', 2)])
        ```

        如果`other_dict`的一个键是空的list，不会为dict加入新的值，这个key也不会被创建：

        ```python
        >>> x = {"empty_list": []}
        >>> y = MultiDict()
        >>> y.update(x)
        >>> y
        Multidict([])
        ```

    - `values(*a, **kw)`

        类似`itervalues()`，但是返回一个list。

    - `viewitems(*a, **kw)`

    - `viewkeys(*a, **kw)`

    - `viewlists(*a, **kw)`

    - `vliewlistvalues(*a, **kw)`

    - `viewvalues(*a, **kw)`

- class `werkzeug.datastructures.OrderedMultiDict(mapping=None)`

    和`MultiDict`累屎，但是会保留字段的顺序。

    > 因为Python内部的限制，你不可以使用`dict(multidict)`将OrderMultiDict转换为
    普通字典。你应该使用`to_dict()`方法，否则内部的bucket对象将会暴露。

- class `werkzeug.datastructures.ImmutableMultiDict(mapping=None)`

    一个不可变类型的`MultiDict`.

    - `copy()`

        返回这个对象的一个浅拷贝.

- class `werkzeug.datastructures.ImmutableOrderedMultiDict(mapping=None)`

    一个不可变类型的`OrderedMultiDict`.

- class `werkzeug.datastructures.CombinedMultiDict(dicts=None)`

    一个只读的MultiDict，你可以将多个`MultiDict`实例传入它的构造器，
    它会组合起来，返回一个封装好的dict：

    ```python
    >>> from werkzeug.datastructures import CombinedMultiDict, MultiDict
    >>> post = MultiDict([('foo', 'bar')])
    >>> get = MultiDict([('blab', 'blah')])
    >>> combined = CombinedMultiDict([get, post])
    >>> combined['foo']
    'bar'
    >>> combined['blab']
    'blah'
    ```

    这个对象只可以进行读操作，修改数据的话会抛出`TypeError`.

- class `werkzeug.datastructres.ImmutableDict`

    一个不可变类型的`dict`.

- class `werkzeug.datastructures.ImmutableList`

    一个不可变类型的`list`.

- class `werkzeug.datastructures.FileMultiDict(mapping=None)`

    一个特殊类型的`MultiDict`，可以有一些方便的方法用来加入文件。

    这个类主要用于`EnvironBuilder`，一般用于单元测试.

    方法:

    - `add_file(name, file, filename=None, content_type=None)`

        为字典加入一个文件。文件可以是一个文件名，或者一个类文件对象，抑或是
        一个`FileStorage`对象.

        参数:

        - `name`: 这个字段的名称
        - `file`: 一个类文件对象
        - `filename`: 一个可选的文件名
        - `content_type`: 一个可选的content type.


## HTTP Related
        
- class `werkzeug.datastructures.Headers([defaults])`

    一个存储头部信息的对象。

    它拥有类字典的接口，但是它是有序的，并且可以为一个key存储多个值。

    这个数据接口主要是方便处理WSGI 头部.

    在Werkzeug0.3以后，这个类抛出的`KeyError`会由全局捕获，并抛出`BadRequest`
    异常，渲染一个`400 BAD REQUEST`页面.

    Header尽量和Python标准库的`wsgiref.headers.Header`类相兼容，有一个例外情况
    就是`__getitem__`。`wsgiref`在碰到值缺失的时候会返回None，而`Headers`类则
    会抛出`KeyError`.

    参数:

    - `default`: 这个`Header`的默认值， list。

    方法：

    - `add(_key, _value, **kw)`

        为list加入一个新的 header 元祖.

        关键字参数可以为header值设置额外的参数，下划线将会被转换为dash(横线):

        ```python
        >>> d = Headers()
        >>> d.add('Content-Type', 'text/plain')
        >>> d.add('Content-Type', 'attachment', filename='foo.png')
        ```

        关键字参数将会传入到`dump_option_header()`中, 用来把下划线转换。

    - `add_header(_key, _value, **_kw)`

        为list加入一个新的header tuple.

        这个方法名是`add()`的一个alias，主要是为了和`wsgiref add_header()`相兼容.

    - `clear()`

        清除所有的头部.

    - `extend(iterable)`

        使用一个字典或者iterable来扩充这个headers。

    - `get(key, default=None, type=None, as_bytes=False)`

        如果请求的数据不存在，返回default的值.

        其实就是`TypeConvertionDict.get()`.

        ```python
        >>> d = Headers([('Content-Length', '42')])
        >>> d.get('Content-Length', type=int)
        42
        ```

    - `get_all(name)`

        返回一个字段的所有值.

        这个方法主要是为了兼容`wsgiref get_all()`方法.

    - `getlist(key, type=None, as_bytes=False)`

        返回给定key的所有items。

    - `has_key(key)`

            检查key是否存在.

    - `items(*a, **kw)`

    - `keys(*a, **kw)`

    - `pop(key=None, default=None)`

    - `popitem()`

    - `remove()`

        移除一个键.

    - `set(_key, _value, **kw)`

        移除一个键的所有header元祖，然后加入新的一个。

    - `setdefault(key, default)`

    - `to_list(charset='iso-8859-1')`

        将headers转换为适合WSGI的list.

    - `to_wsgi_list()`

    - `values(*a, **kw)`

    - `viewitems(*a, **kw)`

    - `viewkeys(*a, **kw)`

    - `viewvalues(*a, **kw)`

- class `werkzeug.datastructures.EnvironHeaders(envion)`

    Headers的自读保本.

    它提供和Headers的相同接口，并且通过一个WSGI environ来构建。

- class `werkzeug.datastructures.HeaderSet(headers=None, on_update=None)`

    类似`Etag`类，实现了类set的接口。

    但是不像`Etag`，它是大小写不敏感的，可以用于vary，allow和content-language头部.

    如果没有使用`parse_set_header()`函数来构建，那么初始化的情况会类似下面这样:

    ```pyhton
    >>> hs = HeaderSet(['foo', 'bar', 'baz'])
    >>> hs
    HeaderSet(['foo', 'bar', 'baz'])
    ```

- class `werkzeug.datastructures.Accept(values=())`:

    一个`Accpet`对象，是一个list的子类。

    包含`(value, quatity)`元祖的list。

    所有的`Accept`对象都像list一样，不过他提供了一些额外的功能可以处理数据。

    包含性检测可以按照header的规则标准来实现:

    ```python
    >>> a = CharsetAccept([('ISO-8859-1', 1), ('utf-8', 0.7)])
    >>> a.best
    'ISO-8859-1'
    >>> 'iso--8859-1' in a:
    True
    >>> 'UTF8' in a
    True
    >>> 'utf7' in a
    False
    ```

    像要获取一个item的quanlity，你可以使用普通的item查询:

    ```python
    >>> print(a['utf-8'])
    0.7
    >>> a['utf7']
    0
    ```

    - `best`

        最佳匹配值.

    - `best_match(matches, default=None)`

        根据client的qualtity返回一个list中的最佳匹配.

        如果qualtity相同，先找到的那个会被返回.

        参数:

        - `matches`: 一个要检查match的list.
        - `default`: 如果没有匹配，则返回这个默认值.

    - `find(key)`

        获取一个entry的位置，或者返回-1.

    - `index(key)`

    - `itervalues()`

    - `qualtity(key)`

    - `to_header()`

        将这个header set转换为HTTP header string.

    - `values(*a, **kw)`

    - `viewvalues(*a, **kw)`

- class `werkzeug.datastructures.MIMEAccept(values=())`

    和`Accept`类似，但是有一些针对mimetypes的功能.

    - `accept_html`

    - `accept_json`

    - `accept_xhtml`

- class `werkzeug.datastructures.CharsetAccept(values=())`

    和`Accept`类似，但是针对charsets.

- class `werkzeug.datastructures.LanguageAccept(values=())`

    和`Accept`类似，但是针对languages.

- class `werkzeug.datastructures.RequestCacheControl(values=(), on_update=None)`

    针对request的缓存控制.

    这是一个不可变类型，让你可以访问一些关于缓存控制的头部.

    - `no_cache`

    - `no_store`

    - `max_age`

    - `no_trasform`

    - `max_stale`

    - `min_fresh`

    - `no_transform`

    - `only_if_cached`

- class `werkzeug.datastrucutres.ResponseCacheControl(values=(), on_update=None)`

    response端的缓存控制.

    - `no_cache`

    - `no_store`

    - `max_age`

    - `no_transform`

    - `must_revalidate`

    - `private`

    - `proxy_revalidate`

    - `public`

    - `s_maxage`

- class `werkzeug.datastructures.ETags(strong_etags=None, weak_eag=None, star_tag=False`)

    一个集合，可以用来检查etag。

    - `as_set(include_weak=False)`

    - `contains(etag)`

    - `contains_raw(etag)`

    - `contains_weak(etag)`

    - `is_strong()`

    - `is_weak()`

    - `to_header()`


- class `werkzeug.datastructures.Authorization(auth_type, data=None)`

    ...

- class `werkzeug.datastructures.WWWAuthenticate(auth_type=None, value=None, on_update=None)`

    ...

- class `werkzeug.datastructures.IfRange(etag=None, date=None)`

    一个非常简单的对象，可以用来代表`If-Range`头部。

    它可以是一个etag或者一个date，但是不能两者都是.

- class `werkzeug.datastrcutures.Range(units, ranges)`

    代表`Range`头部。

## Others

- class `werkzeug.datastructures.FileStorage(stream=None, filename=None, name=None, content_type=None, content_length=None, headers=None)`

    `FileStorage`类是一个文件对象的简单封装。

    它用于request对象，代表上传的文件。

    这个封装对象代理了stream的所有接口，所以`storage.read()`可以替代`storage.stream.read()`.

    - stream

        上传文件的输入流.通常来说，这是一个临时文件.

    - filename

        客户端的文件名.

    - name

        表单字段的名称

    - headers

        `Headers`对象的`multipart`头部.通常它包含了一些不相干的信息.

    - close()
  
    - content\_length

        头部的`content-length`，通常都没有.

    - content\_type

        头部发送的`content-type`，通常都没有.

    - mimetype

        类似`content_type`，但是没有参数(比如`charset, type`这些参数).并且都是
        小写格式.

    - mimetype\_params

        mimetype参数，以dict表示。

    - `save(dst, buffer_size=16384)`

    将文件保存在指定路径.


## Reading Source

首先这是一个2000行的.py文件，我记忆中行数最多的一个.

首先我自然好奇一个大型文件，各个类的摆放，代码布局。开起来没有什么太新鲜的，
作者为了构建API，但是要避免循环引用，在文件的最后加入了一些额外的引入。其它的
代码并使按字母表顺序摆放，而是按功能分类，每一块分类中把一些Mixin, helper函数
都放在开头的位置.

第二个有趣的地方，`OrderedMultiDict`，作者没有选择继承`collection.OrderedDict`，
我也一窥得知ordered dict的实现细节，原来使用的是链表(link list)! 每个加入到dict
的元素都使用一个link对象相互连接.

我觉得这个模块有用的数据结构包括: `Multi*`, `Immutable*`, `CallbackDict`这些通用
的数据结构。另外一些数据结构和werkzeug框架强绑定，并且主要用于HTTP相关场景.










