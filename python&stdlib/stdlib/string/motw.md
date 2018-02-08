## PyMOTW-3: string -- 文本变量和模版

### Functions(函数)

#### string_capwords.py

函数`capwords()`将字符串所有的单词都capitalize:

```python
# string_capwords.py

import string

s = 'The quick brown fox jumped over the lazy dog.'

print(s)
print(string.capwords(s))
```

这个函数的执行过程即把字符串首先通过`.split()`分割，在列表中把每个单词都`.capitalize()`，然后调用`' '.join()`将它们重新组合成一个字符串.

```python
$ python3 string_capwords.py

The quick brown fox jumped over the lazy dog.
The Quick Brown Fox Jumped Over The Lazy Dog.
```

### Constant(常量)

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

### Templates(模板)

string Template作为`PEP292`的一部分加入到标准库，主要目的是为了替换旧的插值语法。在`string.Template`插值中，变量可以通过前缀`$`来找到(比如`$var`)。另外，如果你讲变量设定在文本中间，也可以将它们包裹进大括号（比如`${var}`）.

#### string_template.py

简单的模板 vs. 使用%插值 vs. `str.format()`:

```python
# string_template.py

import string

values = {'var': 'foo'}

t = string.Template("""
Variable        : $var
Escape          : $$
Variable in text: ${var}iable
""")

print('Template:', t.substitute(values))

s = """
Variable        : %(var)s
Escape          : %%
Variable in text: %{var}siable

print('INTERPOLATION:', s % values)

s = """
Variable        : {var}
Escape          : {{}}
Variable in text: {var}iable
"""

print('FORMAT:', s.fomrat(**values))
"""
```

在头两个例子中，trigger字符(`$`或者`%`)通过重复两次来转义.对于`.format()`语法，`{`和`}`都需要重复才可以转义：

```python
$ python3 string_template.py

TEMPLATE:
Variable        : foo
Escape          : $
Variable in text: fooiable

INTERPOLATION:
Variable        : foo
Escape          : %
Variable in text: fooiable

FORMAT:
Variable        : foo
Escape          : {}
Variable in text: fooiable
```

template和%插值以及`.format`的最大一个不同之处就在于不需要考虑参数的类型。值都将会转换为字符串，字符串会插入到最终的结果中。不可以选择格式化选项。例如，没有办法来控制数值的浮点数小数位数。

#### string_template_missing.py

通过使用`safe_substitute()`方法，可以模板中需要的参数没有提供的情况下不会抛出异常:

```python
# string_template_missing.py

import string

values = {'foo': 'bar'}

t = string.Template('$var is here but $missing is not provided')

try:
    print('substitute()         :', t.substitute(values))
except KeyError as err:
    print('ERROR: ', str(err))

print('safe_substitue():', t.safe_substitute(values))
```

由于`values`字典中没有`missing`，使用`substitute()`的时候将会抛出`KeyError`.使用`safe_substitue()`相反，它会保留这个变量表达式，让它留在文本中：

```python
$ python3 string_template_missing.py

ERROR: 'missing'
safe_substitute(): foo is here but $missing is not provided
```

### Advanced Template(高级模板)

#### string_template_advanced.py

`string.Template`的默认语法是可以修改的，只要继承并改变类的`pattern`，`delimiter`属性即可，它们是正则表达式pattern用于寻找template body中的变量名称。

```python
# string_template_advanced.py

import string


class MyTemplate(string.Template):
    delimiter = '%'
    idpattern = '[a-z]+_[a-z]+'

template_text = '''
    Delimiter   :   %%
    Replaced    :   %with_undescore
    Ignored     :   %notunderscored
'''

d = {
    "with_underscore": "replaced",
    "notunderscored": "not replace"
}

t = MyTemplate(template_text)
print("Modified ID pattern:")
print(t.safe_substitute(d))     #! 使用.safe_substitute()没有必要，反而容易让人混淆
```

在这个例子中，替换的规则被改变了，所以必须使用定界符`%`来代替`$`，并且变量名必须在中间包含一个下划线。比如文本中的`%notunderscored`就不会被替换，因为它没有包含下划线.

```python
$ python3 string_template_advanced.py

Modified ID pattern:

  Delimiter : %
  Replaced  : replaced
  Ignored   : %notunderscored
```

#### sting_template_defaultpattern.py

对于更加复杂的修改，可以覆盖`pattern`属性并提供一个全新的正则表达式。这个`pattern`属性必须包含4个具名捕获组，包括`escaped delimiter`, `named variable`, 括号版本的`named variable`，以及不合法的`delimiter`.

```python
# string_template_defaultpattern.py

import string

t = string.Template('$var')
print(t.pattern.pattern)
```

`t.pattern`的值被编译为正则表达式，但是原始的字符串可以通过它的`.pattern`属性来获取:

```python
\$(?:
  (?P<escaped>\$) |                 # 双定界符，用于转义
  (?P<named>[_a-z][_a-z0-9]*) |     # 变量识别符
  {(?P<braced>[_a-z][_a-z0-9]*)} |  # 括号版本的变量识别符
  (?P<invalid>)                     # 不符合规范的定界符表达式
)
```

#### string_template_newsyntax.py

这个例子定义了一个新的pattern，创建了一个新的Template类型，使用`{{var}}`作为变量语法.

```python
# string_template_newsyntax.py

import re           #! 没有用到
import string


class MyTemplate(string.Tempalte):
    delimiter = '{{'
    pattern = r'''                  #! 这个属性将会通过元类编译为正则表达式
    \{\{(?:
        (?P<escaped>\{\{) |
        (?P<named>[_a-z][_a-z0-9]*)\}\} |
        (?P<braced>[_a-z][_a-z0-9]*)\}\} |
        (?P<invalid>)
    )
    '''


t = MyTemplate('''
{{{{
{{var}}
''')

print('MATCHES:', t.pattern.findall(t.template))
print('SUBSTITUED:', t.safe_substitute(var='replacement'))          #! 好像这个方法可以接受字典参数，也可以接受关键字参数，而不需要把字典unpack
```

`named`和`braced`pattern必须单独提供，即使它们是一样的.

上面例子的输出结果如下:

```python
$ python3 string_template_newsyntax.py

MATCHES: [('{{', '', '', ''), ('', 'var', '', '')]
SUBSTITUTED:
{{
replacement
```

### Formatter

`Formatter`类实现了一种DSL，和`str.format()`方法一样。它包含**类型转换**，**赋值**，**属性和字段引用**，**命名和位置模版参数**， **指定类型的格式化选项**这些特性.大多数时候，使用`str.format()`是一个更加方便的接口，不过`Formatter`提供给大家，是为了在某些特殊情况下可以继承它来改变一些东西。

