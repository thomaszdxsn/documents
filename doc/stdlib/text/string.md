[TOC]

## 官网文档: string -- 普通的字符串操作

### 字符串常量

在这个模块中定义的常量为：

- `string.ascii_letters`

    将下面的`ascii_lowercase`和`ascii_uppercase`变量串联起来。这个值不是locale-dependent的。

- `string.ascii_lowercase`

    小写字母`abcdefghijklmnopqrstuvwxyz`.这个值不是locale-dependent的，也不应该修改它。

- `string.ascii_uppercase`

    大写字母`ABCDEFGHIJKLMNOPQRSTUVWXYZ`.这个值不是locale-dependent的，也不应该修改它。

- `string.digits`

    字符串`0123456789`

- `string.hexdigits`

    字符串`0123456789abcdefABCDEF`

- `string.octdigits`

    字符串`01234567`

- `string.punctuation`

    考虑在C locale中为标点符号的ASCII字符。

- `string.printable`

    可以打印的ASCII字符串。这个字符串组合了`digits`, `ascii_letters`, `punctuation`, 和`whitespace`.

- `string.whitespace`

    考虑为空白字符的ASCII字符串。这个字符串包含空格，tab，linefeed，return，formfeed，和vertical tab。

### 自定义字符串格式化

在`PEP3101`中，描述了内置的`str`类可以通过`.format()`方法实现复杂的变量替换(substitution)和value格式化.`string`模块的`Formatter`类允许你创建和定义自己的字符串格式化行为，它的实现方式和内置函数`format()`一样.

- **class**`string.Formatter`

    `Formatter`类有以下的公共方法:

    - `format(format_string, *args, **kwags)`

        主要的API方法。它接受一个*format string*以及任意的位置和关键字参数。它只是`vformat()`的一个封装。

        Py3.5以后被废弃：以关键字参数形式传入`format_string`的用法已经被废弃.

    - `vformat(format_string, args, kwargs)`

        这个函数用来真正执行格式化。它接受的参数分别是元组args代表位置参数，字典kwargs代表关键字参数，使用这个函数无需再将参数*unpacking*(想想threading模块).`vformat()`做的工作就是将*format string*分割为字符数据以及待替换字段。这个函数将会调用下面描述的若干方法。

    另外，`Formatter`定义了一组方法，主要是用于被子类覆盖的:

    - `parse(format_string)`

        迭代*format_string*，然后返回一个元组的可迭代对象(`literal_text, field_name, format_spec, conversion`).这个方法被`vformat()`用于把字符串分割为literal text或者replacement fields.

        这个值概念上是一个tuple, 代表跟随单个replacement字段之后的一段literal text.如果这里没有literal text(比如两个replacement field接连出现)，那么*literal text*将会是一个长度为0的字符串。如果没有replacement field,那么`field_name, format_spec, conversion`都会是`None`.

    - `get_field(field_name, args, kwargs)`

        给定的`field_name`由`parse()`返回，将它转换成一个格式化的对象.返回一个tuple(`(obj, used_key)`).默认版本接受`PEP 3101`中定义的格式的字符串，比如"**0[name]**"或者"**label.title**".`args`和`kwargs`将会传入到`vformat()`.返回的值`userd_key`(元组中第2个值)和`get_value()`的`key`参数具有相同意义。

    - `get_value(key, args, kwargs)`

        取回一个给定的字段值。`key`参数可以是一个整数或者一个字符串。如果它是一个整数，它代表是`args`中位置参数的索引。如果它是一个字符串，那么它就代表`kwargs`的一个命名参数.

        `args`参数设置为`vformat()`的位置参数列表，`kwargs`参数设置为关键字参数字典.

        对于混合的field名，这些函数只有在field名的第一个component被调用。接下来的components将会当作普通属性和index操作来处理.

        比如，field表达式`"0.name"`将会让`get_value()`调用`key`为0的参数。`name`属性将会调用内置的`getattr()`函数来查询`get_value`的返回值。

        如果参数的索引或者键名不存在，将会抛出一个`IndexError`或者`KeyError`.

    - `checked_unused_args(used_args, args, kwargs)`

        如果需要，实现对未使用参数的检查。这个函数的参数是一组引用自*format string*的参数键(`key`, 整数为位置参数，字符串为命名参数)，然后把`args`和`kwargs`的引用会传入到`vformat`.没有使用的参数可以通过这些参数计算得出。如果检查失败，将会抛出`check_unused_args()`.

    - `format_field(value, format_spec)`

        `format_field()`只是简单的调用内置函数`format()`.这个方法可以被子类覆盖.

    - `convert_field(value, conversion)`

        通过给定的`conversion`类型(通过`parse()`方法返回的元组)， 转变value(值由`get_field()`返回).默认版本可以理解`'s'(str), 'r'(repr), 'a'(ascii)`这些转换类型.

        
        


## PyMOTW-3: string -- 文本变量和模版

### 常量

`string`模块包含一组关于ASCII字符和数字字符集的常量.

#### string_constants.py

```python
import inspect
import string


def is_str(value):
    return isinstance(value, str)


for name, value in inspect.getmembers(string, is_str):
    if name.startswith('_'):
        continue
    print("{0!s}={1!r}\n".format(name, value))
```

在处理ASCII数据时这些常量会很有用，但是由于现在会更常碰到非ASCII即Unicode字符，这些常量的作用也受到了限制：

```python
$ python3 string_constants.py

ascii_letters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVW
XYZ'

ascii_lowercase = 'abcdefghijklmnopqrstuvwxyz'

ascii_uppercase = 'ABCDEFGHIJKLMNOPQRSTUVW
XYZ'

digits = '0123456789'

hexdigits = '0123456789abcdefABCDEF'

octdigits = '01234567'

printable = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQ
RSTUVWXYZ!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~ \t\n\r\x0b\x0c'

punctuation = '!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~'

whitespace = ' \t\n\r\x0b\x0c'
```

## 参考

- [string库的官方文档](https://docs.python.org/3.5/library/string.html)

- [str的方法 - 这些str方法替换了string模块中的函数](https://docs.python.org/3/library/stdtypes.html#string-methods)

- [PEP292 - 简单的字符串替换](https://www.python.org/dev/peps/pep-0292)

- [PEP3103 - 高级字符串格式化](https://www.python.org/dev/peps/pep-3103)

- [格式化字符串语法 - `Formatter`和`str.format()`的DSL语言](https://docs.python.org/3.5/library/string.html#format-string-syntax)

## 源代码 

[github🔗](https://github.com/python/cpython/blob/3.6/Lib/string.py)



