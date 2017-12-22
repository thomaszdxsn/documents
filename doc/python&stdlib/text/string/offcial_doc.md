## 官网文档: string -- 普通的字符串操作

### String constants(字符串常量)

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

### Custom String Formatting(自定义字符串格式化)

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


### Format String Syntax(字符串格式化语法)

TODO:

#### Format Specification Mini-Language

TODO:

#### Format examples

TODO:

### Template strings

`Template`实现了`PEP292`，提供了一种简单的字符串替换。除了常见的`%`替换方法，`Template`支持`$`替换，主要有以下的规则:

- `$$`是一个转义字符，它会被替换为单个`$`.
- `$identifier`是一个要替换的占位符名称，它会匹配一个映射键，所以叫做"identifier".默认情况下，“identifier”的命名规则和Python变量名一样，只可以下划线和ascii字符开头，整个名称只能包含下划线，ascii字符和数字。在`$`以后的第一个非identifier字符会指明这个占位符的结束位置。
- `${identifier}`等同于`$identifier`。在占位符之后的字符是合法identifier的时候需要它，比如`${noun}ification`.

字符串中任何其它形式的`$`都会导致异常`ValueError`.

`string`模块提供了一个`Template`类，实现了这些规则。`Template`的方法包括:

- class`string.Template(template)`     

    构造器只接受一个参数，即模版字符串。

    - `substitute(mapping, **kwds)`

        执行模板替换，返回一个新的字符串。`mapping`可以是任何类字典对象，它的键代表模板中的占位符。另外，你也可以提供关键字参数，关键字即占位符。当mapping和`kwds`都传入并且发生重复的时候，将关键字参数优先使用。

    - `safe_substitute(mapping, **kwds)`

        和`substitute()`一样，除了在模板中的占位符没有出现对应的映射键时不会抛出`KeyError`错误，而是把原本的占位符文本原封不动的返回。另外，`$`的其它形式也不会抛出`ValueError`错误，而是保持为`$`的样子。

        其它的异常仍然会抛出。这个方法之所以叫做“safe”，是因为这个方法总是试图返回一个字符串而不是抛出错误。但是从另一个角度来说，`safe_substitute()`也可以说并不“safe”，因为在发生代码编写错误，映射不对的时候它也不会报错。

    `Template`实例同样提供了一个公共数据属性：

    - `template`

        这是传入到构造器的`template`参数。大部分情况下，你不应该改变它。但是你要改的话也是可以的。


下面是使用`Template`的一个例子：

```pyhton
>>> from string import Template
>>> s = Template('$who likes $what')
>>> s.substitute(who='tim', what='kung pao')
'tim likes kung pao'
>>> d = dict(who='tim')
>>> Template('Give $who $100').substitute(d)        #! 因为$后面非正规的identify，将会抛出ValueError
Traceback (most recent call last):
...
ValueError: Invalid placeholder in string: line 1, col 11   
>>> Template('$who like $what').substitute(d)       #! 因为有一个占位符没有填充，所以会抛出KeyError
Traceback (most recent call last):
...
KeyError: 'what'
>>> Template('$who likes $what').safe_substitute(d)
'time likes $what'
```

**高级用法**：你可以继承`Template`，自定义你的占位符语法，delimiter字符，或者用于解析模版字符串的整个正则表达式。如果想达到这些目的，你需要覆盖这些类属性：

- `delimiter`

    这是一个字符串，描述一个**占位符引入delimiter**.默认的值是`$`.注意这个值不是正则表达式，实现层会对这个值调用`re.escape()`。

- `idpattern`

    这是一个正则表达式，描述非括号类型占位符的pattern(括号会以合适的方式自动加上)。默认值是一个正则表达式`[_a-z][_a-z0-9]*`.

- `flags`

    这个属性代表正则表达式标识，将会在正则表达式编译时用到。默认值是`re.INGORECASE`.注意`re.VERBOSE`总是会被加入到标识中，所以自定义的正则表达式必须遵循使用verbose正则表达式的习惯.

另外，你可以通过覆盖类属性`pattern`来提供一个完整的正则表达式.如果你覆盖你这个属性，必须提供一个包含4个具名捕获组的正则表达式:

- `escaped`: 

    

    

