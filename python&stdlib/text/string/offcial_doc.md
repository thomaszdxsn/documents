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

`str.format()`方法和`Formatter`类都使用相同的字符串格式化语法(虽然在`Formatter`中，通过继承可以定义你自己的格式化语法)。这个语法和Python词法分析的[formatted string literals](https://docs.python.org/3/reference/lexical_analysis.html#f-strings)有关，但是有一些区别。

格式化字符串中包含待替换字段(也叫作占位符)，通过一对大括号`{}`包裹。任何不在大括号里面的内容都认为是普通文本，它们会在输出时原样拷贝。如果你需要在普通文本中使用大括号，你可以使用两个相同字符来转义它，比如`{{`或`}}`.

待替换字段的语法如下:

```python
replacement_field   ::= "{"[field_name] ["!" conversion] [":" format_spec] "}"
field_name          ::= arg_name("." attribute_name | "[" element_index "]")*
arg_name            ::= [identifier | integer]
attribute_name      ::= identifier
element_index       ::= integer | index_string
index_string        ::= <任何原生字符，除了 "]">+
conversion          ::= "r" | "s" | "a"
format_spec         ::= <在下章节有描述>
```

用不正式的话来说，replacement field(待替换字段)可以以一个`field_name`开始，用来指定一个对象，它的值将会被格式化然后替换掉带替换掉字段，最后输出。`field_name`后面可选跟上一个`conversion`字段，它前面加上一个惊叹号`!`。以及可选跟上`format_spec`，它前面跟上冒号`:`.这指定了带替换字段的非默认格式。

`field_name`本身开始于一个`arg_name`，可以是一个数字或者关键字。如果是一个数字，它会当做是一个位置参数，如果是关键字，它会当做一个命名参数。如果一个字符串格式化参数`arg_names`是以数字序列来指定的，如`0, 1, 2...`，那么可以忽略掉这些索引，最后会根据位置自动生成参数索引。因为`arg_name`不是引号包裹的，所以不是所有的字典键都可以设定的(比如字符串`10`或者`:-]`).`arg_name`后面可追加任意数量的索引或属性表达式。一个`.name`形式的表达式会使用`getattr()`来选择命名属性，`[index]`形式的表达式将会使用`__getitem__()`来获取。

3.1以后的变更: 位置参数标识符可以忽略，所以`"{}{}"`等同于`"{0}{1}"`

一些简单的字符串格式化例子:

```python
"First, thou shalt count to {0}"        # 引用了第一个位置参数
"Bring me a {}"                         # 暗含引用了第一个位置参数
"From {} to {}"                         # 等同于"From {0} to {1}"
"My quest is {name}"                    # 引用了关键字参数"name"
"Weight in tons {0.weight}"             # 第一个位置参数的"weight"属性
"Units desctoryed: {players[0]}"        # 关键字参数"players"的第一个元素
```

`conversion`字段在格式化之前会作一个类型转换。一般来说，一个值的格式化是通过这个值本身的`__format__`方法来完成的。但是，一些情况下，需要强制把一个类型格式化为字符串，覆盖它自定义的格式化。在调用`__format__`之前把它转换为字符串，那么就会绕过一般的格式化逻辑。

当前支持三种转换标识: `!s`将会对值调用`str()`, `!r`将会对值调用`repr()`, `!a`将会对值调用`ascii()`.

例子:

```python
"Harold's a clever {0!s}"       # 对第一个位置参数调用`str()`
"Bring out the holy {name!r}"   # 对关键字参数"name"调用`repr()`
"More {!a}"                     # 对第一个位置参数调用`ascii()`
```

`format_spec`字段包含值应该如何表现的规则，包含字段宽段，对齐，padding，小数精度等等。每种类型的值都可以定义它自己的"formatting mini-language"或者使用`format_spec`插值。

多数内置类型使用一个通用的"format mini-language"，在下个章节有描述。

`format_spec`字段可以包含嵌套的`replacement field`.嵌套的待替换字段可以包含字段名称，转换标识，以及格式化规则，但是不允许更深的嵌套。`format_spec`之中的待替换字段将会在解释格式化规则之前被替换。通过这种技术可以动态指定一个值的格式化方式。

#### Format Specification Mini-Language

"Format specification"用于格式化字符串中的待替换字段(replacement field)，用于定义一个单独的值应该如何表现。它们会被传入到内置的`format()`函数。每个可以格式化的类型(formattable type)都可以定义如何解释"format specification".

多数内置类型实现了下面的格式化规则选项，不过一些格式化选项只对数值类型有用。

一个惯例就是对一个空的格式化字符串(`""`)将会和对它执行`str()`产生一样的结果。空的格式化字符串也会更改原来的字符串对象。(生成的结果不是同一个对象)。

标准的*格式化标识符*一般类型为:

```python
format_spec     ::= [[fill]align][sign][#][0][width][grouping_option][.precision][type]
fill            ::= <任何字符>
align           ::= "<" | ">" | "=" | "^"
sign            ::= "+" | "-" | " "
width           ::= 整数
grouping_option ::= "_" | ","
precision       ::= 整数
type            ::= "b" | "c" | "d" | "e" | "E" | "f" | "F" | "g" | "G" | "n" | "o" | "s" | "x" | "X" | "%"
```

如果指定了一个合法的`align`值，可以在它前面加上一个`fill`字符，`fill`默认为空格.不可以在`fill`中使用一般的`"{"`, `"}"`，需要使用它们的转义形式。

不同的`align`(对齐)选项之意义如下:

选项 | 意义
-- | --
`<` | 强制字段在可用空间中向左对齐(对于大多数对象来说，这是默认选项)
`>` | 强制字段在可用空间中向右对齐(对于数值类型来说，这是默认选项)
`=` | 强制padding放置在sign(如果存在)之后，但是在digits之前。使用它来打印类似`+000000120`这种字符串。这个对齐选项只针对数值类型有效。如果在字段宽度(width)之前加入0，会自动使用这个对齐选项.
`^` | 强制字段在可用空间中居中对齐

注意，除非定义了最小字段宽度，否则宽度总是和数据长度一致，这种情况下对齐没有任何意义。

`sign`选项只可用应用于数值类型，可以是下面中的一种：

选项 | 意义
-- | --
`+` | 这个符号应用于所有的正数和复数
`-` | 这个符号只应用于负数(这是默认选项)
空格 | 如果是正数，会在最前面加上空格。如果是负数，则加上一个减符号

`#`选项用来作为转换的"另一种形式(alternate form)".另一种形式根据类型的不同而不同。这个选项只对integer, float, complex和Decimal类型有效。对于整数integer来说，在使用二进制，八进制，十六进制输出的时候，这个选项会为它们分别加上前缀`0b`, `0o`, `0x`.对于float, complex, Decimal，转换的结果总是会包含一个小数点字符，即使小数点以后并没有数字。

`,`选项，使用逗号作为千位分隔符。

*3.1版本以后加入：  增加`,`选项([PEP378](https://www.python.org/dev/peps/pep-0378))*

`_`选项，使用下划线来作为千位分隔符(针对float, 和d形式的整数)。对于b, o, x, 和 X形式的整数，每4位插入一个下划线。对于其它类型，指定这个选项会抛出错误.

*3.6版本以后加入:   增加`_`选项[PEP515](https://www.python.org/dev/peps/pep-0515)*

`width`是一个小数整数(decimal integer)，定义了字段的最小宽度。如果没有指定这个选项，宽度将会由内容来决定。

当没有给定显式对齐选项时，`width`之前将会使用`0`字符。等同于`fill`为`0`, 对齐方式为`=`.

`precision`是一个小数数值，指明在小数点以后应该显式多少位数字。对于非数值类型，这个选项用于指定字段的最大宽度。`precision`不允许用于integer类型的值。

最后，`type`决定数据的表现形式。

字符串类型的可用表现形式包括：

类型 | 意义
-- | --
`s` | 字符串格式。这是字符串的默认类型，可以忽略它
`None` | 和`s`相同

整数类型的可用表现形式包括：

类型 | 意义
-- | --
`b` | 二进制格式.
`c` | 字符.将整数转换为相符的Unicode字符
`d` | 十进制格式.
`o` | 八进制格式
`x` | 十六进制格式
`X` | 十六进制格式，字母是大写形式.
`n` | 数字。和`d`相同，除了它会根据本地设置而插入适当的数值分隔符
`None` | 和`d`一样

除了上面的表现类型，整数可以使用浮点数的表现形式(除了`n`和`None`).当使用浮点数的选项以后，格式化之前，将会使用`float`将整数转换为浮点数.

浮点数类型的可用表现形式包括：

类型 | 意义
-- | --
`e` | 指数记号法
`E` | 指数记号法.E以大写表示
`f` | fixed point
`F` | 和f一样，不过把`nan`转换为`NAN`，`inf`转换为`INF`
`g` | 一般格式
`G` | 和g一样，除了使用大写形式字母
`n` | 数值。等同于`g`,除了会根据本地设置插入数值分隔符
`%` | 百分比。将浮点数乘以100，然后以`f`格式显示，最后加上一个`%`字符
`None` | 和`g`类似


#### Format examples

这部分包含`str.format()`语法的例子，以及和`%`格式化的比较。

多数情况下，这个语法和`%`格式化很类似，使用`{}`加上`:`来代替`%`.比如`%03.2f`可以翻译为`{:03.2f}`.

这种新的语法同样支持若干新的选项，下面的例子有提到。

通过位置访问参数：

```python
>>> "{0}, {1}, {2}".format("a", "b", "c")
"a, b, c"
>>> "{}, {}, {}".format("a", "b", "c")  # 3.1以上可以忽略索引
"a, b, c"
>>> "{2}, {1}, {0}".format("a", "b", "c")
"c, b, a"
>>> "{2}, {1}, {0}".format(*"abc")      # 将序列unpack然后传入
"c, b, a"
>>> "{0}{1}{0}".format("abra", "cad")   # 参数索引可以重复
"abracadabra"
```

通过名称范围参数:

```python
>>> "Coordinates: {latitude}, {longitude}".format(latitude='37.24N', longitude='-115.81W')
"Coordinates: 37.24N, -115.81W"
>>> coord = {"latitude": "37.24N", "longitude": "-115.81W"}
>>> "Coordinates: {latitude}, {longitude}".format(**coord)
"Coordinates: 37.24N, -115.81W"
```

访问参数的参数:

```python
>>> c = 3 - 5j
>>> ("The complex number {0} is formed from the real part {0.real} "
...  "and the imaginary part {0.imag}.".format(c))
'The complex number (3-5j) is formed from the real part 3.0 and the imaginary part -5.0.'
>>> class Point:
...     def __init__(self, x, y):
...         self.x, self.y = x, y
...     def __str__(self):
...         return "Point({self.x}, {self.y})".format(self=self)
...
>>> str(Point(4, 2))
'Point(4, 2)'
```

访问参数的items:

```python
>>> coord = (3, 5)
>>> "X: {0[0]}; Y: {0[1]}".format(coord)
'X:3; Y:5'
```

`%s`和`%r`的替代品:

```python
>>> "repr() show quotes: {!r}; str() doesn't: {!s}".format("test1", "test2")
"repr() shows quotes: 'test1'; str() doesn't: test2"
```

文本对齐和指定宽度:

```python
>>> "{:<30}".format("left aligned")
'left aligned                  '
>>> "{:>30}".format("right aligned")
'                 right aligned'
>>> "{:^30}".format("centerd")
'           centered           '
>>> "{:*^30}".format("centered")    # 使用'*'作为填充字符
'***********centered***********'
```

`%+f`, `%-f`和`%f`的替代品:

```python
>>> "{:+f};{:+f}".format(3.14, -3.14)   # 展示原来的样子
'+3.140000; -3.140000'
>>> "{: f};{: f}".format(3.14, -3.14)   # 在整数前面加一个空格
' 3.140000; -3.140000'
>>> "{:-f};{:-f}".format(3.14, -3.14)   # 只显示减号(默认)
'3.140000; -3.140000'
```

`%x`和`%o`的替代品:

```python
>>> # format()还支持二进制
>>> "int: {0:d}; hex: {0:x}; oct: {0:o}; bin: {0:b}".format(42)
'int: 42;  hex: 2a;  oct: 52;  bin: 101010'
>>> # 加上前缀:0x, 0o, 0b
>>> "int: {0:d}; hex: {0:#x}; oct: {0:#o}; bin: {0:#b}".format(42)
'int: 42;  hex: 0x2a;  oct: 0o52;  bin: 0b101010'
```

使用逗号来作为千位分隔符:

```python
>>> "{:,}".format(1234567890)
"1,234,567,890"
```

以百分比形式表达:

```python
>>> points = 10
>>> total = 22
>>> "Correct precentage: {:.2%}".format(points/total)
'Correct answers: 86.36%'
```

使用*特定类型(type-specific)*的格式化：

```python
>>> import datetime
>>> d = datetime.datetime(2010, 7, 4, 12, 15, 58)
>>> "{:%Y-%m-%d %H:%M:%s}".format(d)
'2010-07-04 12:15:58'
```

嵌套参数和更复杂的例子:

```python
>>> for align, text in zip("<^>", ['left', 'center', 'right']):
...     '{0:{fill}{align}16}'.format(text, fill=align, align=align)
... 
'left<<<<<<<<<<<<'
'^^^^^center^^^^^'
'>>>>>>>>>>>right'
>>>
>>> octets = [192, 168, 0, 1]
>>> "{:02x}{:02x}{:02x}{:02x}".format(*octets)
'COA8001'
>>> int(_, 16)
3232235521
>>>
>>> width = 5
>>> for num in range(5, 12):
...     for base in 'dXob':
...         print("{0:{width}{base}}".format(num, base=base, width=width), end=' ')
...     print()
...
    5     5     5   101
    6     6     6   110
    7     7     7   111
    8     8    10  1000
    9     9    11  1001
   10     A    12  1010
   11     B    13  1011
```





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

    转义序列的匹配组，比如`$$`这个默认的模式.

- `named`

    这个匹配组用来匹配没有大括号的占位符名称；匹配组里面不需要包含定界符(delimiter).

- `braced`

    这个匹配组用来匹配包含在大括号的占位符名称；不需要在匹配组里面包含定界符或括号(不一定是大括号).

- `invalid`

    这个匹配组用来匹配其它定界符模式(通常是单个定界符)，它应该出现在正则表达式的最后(因为匹配组的顺序很重要).


### Helper functions(辅助函数)

- `string.capwords(s, sep=None)`

    使用`str.spilit()`将参数分割成单词，使用`str.captitalize()`来将每个单词都首字母大写，最后使用`str.join()`将首字母大写化以后的字母连接起来。如果可选参数`sep`没有传入，那么就使用空格作为分隔符,否则使用`sep`来分隔和连接字符串。

    