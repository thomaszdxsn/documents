## argparse -- Parser for command-line options, arguments and sub-commands(命令行选项，参数和子命令的解析器)

`argparse`模块可以简单地编写用户友好的命令行接口。要求程序里面来定义参数，`argparse`将会根据这些定义来解析`sys.argv`。`argparse`模块可以自动生成帮助文本和用法信息，并且在指定不合法参数时发出一个错误消息。

### Example(示例)

下面的代码是一个Python程序，可以接受一组整数作为参数，并且返回这组整数的合计或者最大值.

```python
import argparse

parser = argparse.ArgumentParser(description='Process some integers')
parser.add_argument(
    "integers",
    metavar='N',
    type=int,
    nargs='+',
    help='an integer for the accumulator'
)
parser.add_argument(
    '--sum',
    dest='accumulate',
    action='store_const',
    const=sum,
    default=max,
    help='sum the integers (default: find the max)'
)

args = parser.parse_args()
print(args.accumulate(args.integers))
```

假定上面的代码保存到了文件`prog.py`中.可以使用命令行来运行它，它提供了一些实用的帮助文本：

```shell
$ python prog.py -h
usage: prog.py [-h] [--sum] N [N ...]

Process some integers.

positional arguments:
 N           an integer for the accumulator

optional arguments:
 -h, --help  show this help message and exit
 --sum       sum the integers (default: find the max)
```

来使用合适的参数来运行它时，它可以打印命令行提供的整数值的最大值或者合计：

```shell
$ python prog.py 1 2 3 4
4

$ python prog.py 1 2 3 4 --sum
10
```

如果传入了不合法的参数，它会发错一个错误信息：

```shell
$ python prog.py a b c
usage: prog.py [-h] [--sum] N [N ...]
prog.py: error: argument N: invalid int value: 'a'
```

下面的章节将会带领你理解这个示例。

#### Creating a parser(创建一个解析器--parser)

使用`argparse`的首个步骤就是创建一个`ArgumentParser`对象:

```python
>>> parser = argparse.ArgumentParser(description='Process some integers.')
```

`ArgumentParser`对象包含要把命令行解析为Python数据类型的所有必须信息/方法。

#### Adding arguments(增加参数)

通过调用`add_argument()`方法，可以为`ArgumentParser`对象填充程序所需参数的信息。大致的意思就是，这个方法告诉`ArgumentParser`如何拿去命令行上的一个字符串并把它转换为对象。再调用`parse_args()`以后，这些信息才会被存储起来。例如：

```python
>>> parser.add_argument('integers', metavar='N', type=int, nargs='+',
...                     help='an integer for the accumulator')
>>> parser.add_argument('--sum', dest='accumulate', action='store_const',
...                     const=sum, default=max,
...                     help='sum the integers (default: find the max)')
```

然后，调用`parse_args()`会返回一个带有两个属性的对象，这两个属性分别是`integers`和`accumulate`.`integers`是一个列表，持有一个或多个整数元素；`accumulate`默认是`sum()`函数，如果命令行指定了选项`--sum`，那么它就是`max()`函数.

#### Parsing Arguments(解析函数)

`ArgumentParser`使用`parse_args()`方法来解析参数。这个方法将会检查命令行参数，然后将参数转换为适当的类型，触发适当的动作。大多数情况下，`Namespace`对象即由命令行解析而来的：

```python
>>> parser.parse_args(['--sum', '7', '-1', '42'])
Namespace([accumulate=<bultin-in fumction sum>, integers=[7, -1, 42]])
```

在脚本中，通常会直接调用`parse_args()`，不传入任何参数。`ArgumentParser`将会自动从`sys.argv`拿取命令行参数。


### ArgumentParser objects(ArgumentParser对象)

class`argparse.ArgumentParser(proj=None, usage=None, description=None, epilog=None, parents[], formatter_class=argparse.HelpFormatter, prefix_chars='-', fromfile_prefix_chars=None, argument_default=None, 
conflict_handler='error', add_help=True, allow_abbrev=True)`

构建新的`ArgumentParser`对象时，所有传入的参数都必须是关键字形式。每个关键字参数我们都会在之后详细讨论，下面是它们的简介:

- `prog`: 程序的名称(默认为`sys.argv[0]`)
- `usage`: 描述程序用法的字符串(默认会根据加入到这个parser的参数而自动生成)
- `description`: 参数帮助之前显示的文本(默认:`None`)
- `epilog`: 在参数帮助之后显示的文本(默认:`None`)
- `parents`: 一个`ArgumentParser`对象的列表。应该包含它们定义的参数。
- `formatter_class`: 一个自定义的类，用于帮助文本输出的格式化处理。
- `prefix_chars`: 选项参数的前缀(默认为`-`)
- `fromfile_prefix_chars`: 额外从含有这个前缀的文件名中读取一些数据(默认:`None`)
- `argument_default`: 参数的全局默认值(默认:`None`)
- `conflict_handler`: 解决冲突选项的策略(通常不需要指定)
- `add_help`: 为parser加入`-h/--help`选项(默认:`True`)
- `allow_abbrev`: 如果缩写不是模棱两个容易混淆的话，运行长选项使用缩写形式(默认:`True`)

下面的章节详细描述了每一个参数.

#### prog

默认情况下，`ArgumentParser`使用`sys.argv[0]`来作为显示在程序名称。默认行为大多数时候是合理的，因为它符合实际情况。比如，假设有一个叫做`myprogram.py`的文件：

```pyhton
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--foo', help='foohelp')
args = parser.parse_args()
```

这个程序的帮助文本中，`myprogram.py`作为程序名称出现(不管程序从哪里被调用):

```shell
$ python myprogram.py --help
usage: myprogram.py [-h] [--foo FOO]

optional arguments:
 -h, --help  show this help message and exit
 --foo FOO   foo help
$ cd ..
$ python subdir/myprogram.py --help
usage: myprogram.py [-h] [--foo FOO]

optional arguments:
 -h, --help  show this help message and exit
 --foo FOO   foo help
```

可以通过修改`prog`参数来改变这个默认的行为：

```python
>>> parser = argparse.ArgumentParser(prog='myprogram')
>>> parser.print_help()
usage: myprogram [-h]

optional arguments:
 -h, --help  show this help message and exit
```

注意无论是使用`sys.argv[0]`还是`prog=`指定的程序名称，都可以在帮助文本中使用`%(prog)s`格式化标识符来获取：

```shell
>>> parser = argparse.ArgumentParser(prog='myprogram')
>>> parser.add_argument('--foo', help='foo of the %(prog)s program')
>>> parser.print_help()
usage: myprogram [-h] [--foo FOO]

optional arguments:
 -h, --help  show this help message and exit
 --foo FOO   foo of the myprogram program
```

#### usage

默认情况下，`ArgumentParser`会根据它包含的参数计算出使用方法信息:

```python
>>> parser = argparse.ArgumentParser(profg='PROG')
>>> parser.add_argument('--foo', nargs='?', help='foo help')
>>> parser.add_argument('bar', nargs='+', help='bar help')
>>> parser.print_help()
usage: PROG [-h] [--foo [FOO]] bar [bar ...]

positional arguments:
 bar          bar help

optional arguments:
 -h, --help   show this help message and exit
 --foo [FOO]  foo help
```

默认的信息可以通过`usage=`关键字参数来覆盖：

```python
>>> parser = argparse.ArgumentParser(prog='PROG', usage='%(prog)s [options])
>>> parser.add_argument('--foo', nargs='?', help='foo help')
>>> parser.add_argument('bar', nargs='+', help='bar help')
>>> parser.print_help()
usage: PROG [options]

positional arguments:
 bar          bar help

optional arguments:
 -h, --help   show this help message and exit
 --foo [FOO]  foo help
```

在你的使用方法信息中就可以加入格式化字符串`%(prog)s`.

#### description

大多数时候，调用`ArgumentParser`构造器时都会传入`description`参数。这个参数将会赋予程序一个简短的描述。在帮助文本中，description出现在位于命令行使用方法(usage)字符串和各种参数帮助文本之间的位置：

```python
>>> parser = argparse.ArgumentParser(description='A foo that bars')
>>> parser.print_help()
usage: argparse.py [-h]

A foo that bars

optional arguments:
 -h, --help  show this help message and exit
```

默认情况下，这个description会自动换行(line-wrapped).要想不开启自动换行，需要了解一下`formatter_class`参数.

#### epilog

一些程序需要在参数的帮助文本之后再显示一段文本。可以通过`epilog=`参数来指定这一段文本:

```python
>>> parser = argparse.ArgumentParser(
...     description='A foo that bars',
...     epilog="And that's how you'd foo a bar")
>>> parser.print_help()
usage: argparse.py [-h]

A foo that bars

optional arguments:
 -h, --help  show this help message and exit

And that's how you'd foo a bar
```

和`description`一样，`epilog`默认也是会自动换行的。

#### parents

有时，几个parser需要共享一组参数。手动重复定义这些参数的话太蠢了，一个parser将会共享`parents`中所有`ArgumentParser`对象中的参数。这个`parents=`参数接受一个`ArgumentParser`对象的list：

```python
>>> parent_parser = argparse.ArgumentParser(add_help=False)
>>> parent_parser.add_argument('--parent', type=int)

>>> foo_parser = argparse.ArgumentParser(parents=[parent_parser])
>>> foo_parser.add_argument('foo')
>>> foo_parser.parse_args(['--parent', '2', 'XXX'])
Namespace(foo='XXX', parent=2)

>>> bar_parser = argparse.ArgumentParser(parents=[parent_parser])
>>> bar_parser.add_argument('--bar')
>>> bar_parser.parse_args(['--bar', 'YYY'])
Namespace(bar='YYY', parent=None)
```

注意，一般情况下parent parser都会设定`add_help=False`.否则，`ArgumentParser`将会看到两个`-h/--help`选项，出现了这种冲突程序就不能运行。

> 注意
>
>> 在将对象传入到`parents=`之前必须将对象实例化。如果你在子类实例化之后修改父类解析器，这个改动不会映射到子类.

#### formatter_class

`ArgumentParser`允许你自定义一个格式化类来格式化帮助文本。目前，有4个内置的格式化类:

- class`argparse.RawDescriptionHelpFormatter`
- class`argparse.RawTextHelpFormatter`
- class`argparse.ArgumentDefaultHelpFormatter`
- class`argpatse.MetavarTypeHelpFormatter`

`RawDescriptionHelpFormatter`和`RawTextHelpFormatter`运行显示更加原生的描述文本。默认情况下，`ArgumentParser`会将帮助文本中的`description`和`epilog`文本自动换行:

```python
>>> parser = argparse.ArgumentParser(
...     prog='PROG',
...     description='''this description
...         was indented weired
...             but that is okay''',
...     epilog='''
...             likewise for this epilog whose whitespace will
...         be cleaned up and whose words will be wrapped
...         across a couple line''')
>>> parser.print_help()
usage: PROG [-h]

this description was indented weird but that is okay

optional arguments:
 -h, --help  show this help message and exit

likewise for this epilog whose whitespace will be cleaned up and whose words
will be wrapped across a couple lines
)
```

将`RawDescriptionHelpFormatter`当作`formatter_class`参数后，`description`和`epilog`可以正常显示了，不会再自动换行:

```python
>>> parser = argparse.ArgumentParser(
...     prog='PROG',
...     formatter_class=argparse.RawDescriptionHelpFormatter,
...     description=textwrap.dedent('''\
...         Please do not mess up this text!
...         --------------------------------
...             I have indented it
...             exactly the way
...             I want it
...         '''))
>>> parser.print_help()
usage: PROG [-h]

Please do not mess up this text!
--------------------------------
   I have indented it
   exactly the way
   I want it

optional arguments:
 -h, --help  show this help message and exit
```

`RawTextHelpFormatter`将会保持所有帮助文本的空格符不变，即使是参数的帮助文本也一样。

`ArgumentDefaultHelpFormatter`自动为每个参数的帮助文本加入默认值的信息:

```python
>>> parser = argparse.ArgumentParser(
...     prog='PROG',
...     formatter_class=argparse.ArgumentParserDefaultHelpFormatter)
>>> parser.add_argument('--foo', type=int, default=42, help='Foo!')
>>> parser.add_argument('bar', nargs='*', default=[1, 2, 3], help='Bar!')
>>> parser.print_help()
usage: PROG [-h] [--foo FOO] [bar [bar ...]]

positional arguments:
 bar         BAR! (default: [1, 2, 3])

optional arguments:
 -h, --help  show this help message and exit
 --foo FOO   FOO! (default: 42)    
```

`MetavarTypeHelpFormatter`将参数的`type`显示为参数值(而不是使用`dest`):

```python
>>> parser = argparse.ArgumentParser(
...     prog='PROG',
...     formatter_class=argparse.MetavarTypeHelpFormatter)
>>> parser.add_argument('--foo', type=int)
>>> parser.add_argument('bar', type=float)
>>> parser.print_help()
usage: PROG [-h] [--foo int] float

positional arguments:
  float

optional arguments:
  -h, --help  show this help message and exit
  --foo int
```

#### prefix_chars

大多数命令行选项都是使用`-`作为前缀字符，比如`-f/--foo`.但解析器可以支持不同的前缀字符，或者额外支持一些前缀字符。通过`perfix_chars=`来指定：

```python
>>> parser = argparse.ArgumentParser(prog='PROG', prefix_chars='-+')
>>> parser.add_argument('+f')
>>> parser.add_argument('++bar')
>>> parser.parse_args('+f X ++bar Y'.split())
Namespace(bar='Y', f='X')
```

默认的`prefix_chars`值为`-`.

#### fromfile_prefix_chars

有时可能需要处理一个特别长的参数列表，这些参数先让放在文件中更加合适(而不是一个个用手敲)。如果为`ArgumentParser`构造器赋予了`fromfile_prefix_chars`参数，那么参数重任何以这个特殊字符开头的都会当作文件：

```python
>>> with open('args.txt', 'w') as fp:
...     fp.write('-f\nbar')
>>> parser = argparse.ArgumentParser(fromfile_prefix_chars='@')
>>> parser.add_argument('-f')
>>> parser.parse_args(['-f', 'foo', '@args.txt'])
Namespace(f='bar')
```

包含参数的文件必须是每行一个参数的格式(但是可以自定义`convert_arg_line_to_args()`方法来改变这个行为)。所以在上面例子中，表达式`['-f', 'foo', '@args.txt']`将会等同于表达式`['-f', 'foo', '-f', 'bar']`.

这个参数`fromfile_prefix_chars`默认为`None`，意思就是参数用于不会被当作是文件的引用。

#### argument_default

一般来说，参数的默认值要么是调用`add_argument()`的时候传入，要么可以调用`set_defaults()`再加上一个特殊的键值对集合。但是有时候可能需要对解析器设置一个全局的默认值。可以通过`argument_default`这个参数来实现。比如可以设置在没有传入参数时不在调用`parse_args()`后创建参数属性，可以通过常量`SUPPRESS`来实现:

```python
>>> parser = argparse.ArgumentParser(argument_default=argparse.SUPPRESS)
>>> parser.add_argument('-foo')
>>> parser.add_argument('bar', nargs='?')
>>> parser.parse_args(['--foo', '1', 'BAR'])
Namespace(bar='BAR', foo='1')
>>> parser.parse_args([])
Namespace()
```

#### allow_abbrev

通常，在你为`parse_args()`方法传入一个参数list之后，它可以识别出长选项的缩写形式。

这个特性可以通过`allow_abbrev=False`来关闭:

```python
>>> parser.argparser.ArgumentParser(prog='PROG', allow_abbrev=False)
>>> parser.add_argument('--foobar', action='store_true')
>>> parser.add_argument('--foonley', action='store_false')
>>> parser.parse_args(['--foon'])
usage: PROG [-h] [--foobar] [--foonley]
PROG: error: unrecognized arguments: --foon
```

#### conflict_handler

`ArgumentParser`不允许对同一个选项支持两个不一样的动作。默认情况下，用一个已经使用的选项名重新定义参数时，会抛出异常：

```python
>>> parser = argparse.ArgumentParser(prog='PROG')
>>> parser.add_argument('-f', '--foo', help='old foo help')
>>> parser.add_argument('--foo', help='new foo help')
Traceback (most recent call last):
 ..
ArgumentError: argument --foo: conflicting option string(s): --foo
```

有时(特别是使用`parents`参数的情况)，我们想要只是让后定义的参数覆盖之前定义的参数。可以通过设置参数`conflict_handler='resolve'`来实现：

```python
>>> parser = argparse.ArgumentParser(prog='PROG', conflict_handler='resolve')
>>> parser.add_argument('-f', '--foo', help='old foo help')
>>> parser.add_argument('--foo', help='new foo help')
>>> parser.print_help()
usage: PROG [-h] [-f FOO] [--foo FOO]

optional arguments:
 -h, --help  show this help message and exit
 -f FOO      old foo help
 --foo FOO   new foo help
```

注意`ArgumentParser`只会移除那些被后来的参数定义覆盖的选项。在上面的例子中，`-f/--foo`选项仍然保留了`-f`的动作，因为只用`--foo`这个选项被覆盖了。

#### add_help

默认情况下，`ArgumentParser`对象会自动加入一个选项，使用它可显示帮助文本。比如，假设有一个程序叫做`myprogram.py`:

```python
import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--foo', help='foo help')
args = parser.parse_args()
```

如果在命令行使用了`-h/--help`选项，`ArgumentParser`将会打印这样的帮助文本:

```pyhton
$ python myprogram.py --help
usage: myprogram.py [-h] [--foo FOO]

optional arguments:
 -h, --help  show this help message and exit
 --foo FOO   foo help
```

偶尔，可能也需要不显示帮助文本的情况。可以设置参数`add_help=False`:

```python
>>> parser = argparse.ArgumentParser(prog='PROG', add_help=False)
>>> parser.add_argument('--foo', help='foo help')
>>> parser.print_help()
usage: PROG [--foo FOO]

optional arguments:
 --foo FOO  foo help
```

版主选项一般是`-h/--help`。有一个例外就是`prefix_chars`没有指定使用`-`，在这种情况下，`-h`和`--help`就不再是合法的选项了，将会使用`prefix_chars`中的第一个字符串作为帮助选项的前缀字符:

```python
>>> parser = argparse.ArgumentParser(prog='PROG', prefix_chars='+/')
>>> parser.print_help()
usage: PROG [+h]

optional arguments:
  +h, ++help  show this help message and exit
```

### The add_argument() method(方法：add_argument())

`ArgumentParser.add_argument(name or flags...[, action][, nargs][, default][, type][, choices][, required][, help][, metavar][, dest]`

定义如何解析一个命令行参数。默认参数都在之后的章节有详细的介绍，下面是它们的简介:

- `name or flags` - 可以是一个名称或者一个选项字符串的list，比如`foo`或者`-f, --foo`。
- `action` - 在参数出现在命令行时发送的动作。
- `nargs` - 应该被消费的命令行参数数量。
- `const` - 一个常量值。需要设定`action`或者`nargs`。
- `default` - 如果参数没有出现在命令行时参数的默认值。
- `type` - 这是命令行参数转换为的类型。
- `choices` - 一个容器，包含允许使用的参数。
- `required` - 参数是否可以被忽略。
- `help` - 这个参数的简短描述。
- `metavar` - 参数在使用方法中显示的名称。
- `dest` - `parse_args()`之后加入到命名空间对象的属性名称。

#### name or flags

`add_argument()`必须知道这个参数是一个选项参数，比如`-f`或者`--foo`，还是一个位置参数，比如一组文件名称。所以传入`add_argument()`的首个参数要么是一系列的flags，或者一个简单的参数名称。比如，一个简单的选项参数可以这样创建:

```python
>>> parser.add_argument('-f', '--foo')
```

一个位置参数可以这样创建：

```python
>>> parser.add_argument('bar')
```

当调用`parse_args()`之后，选项参数将根据前缀`-`来识别，余下的参数都会被假定为位置参数:

```python
>>> parser = argparse.ArgumentParser(prog='PROG')
>>> parser.add_argument('-f', '--foo')
>>> parser.add_argument('bar')
>>> parser.parse_args(['Bar'])
Namespace(bar='BAR', foo=None)
>>> parser.parse_args(['BAR', '--foo', 'FOO'])
Namespace(bar='BAR', foo='FOO')
>>> parser.parse_args(['--foo', 'FOO'])
usage: PROG [-h] [-f FOO] bar
PROG: error: too few arguments
```

#### action

`ArgumentParser`对象可以关联命令行参数和action。action可以对和它们关联的命令行参数做任何事情，虽然大多数action只是简单地为`parse_args()`返回的对象增加属性。`action`关键字参数指定命令行参数应该被怎样处理。内置的action包括：

- `store` - 简单地存储参数值。这是默认的action。例如:

    ```python
    >>> parser = argparse.ArgumentParser()
    >>> parser.add_argument('--foo')
    >>> parser.parse_args('--foo 1'.split())
    Namespace(foo='1')
    ```

- `store_const` - 这个action将`const`关键字参数作为值来存储。`store_const`通常用来将选项参数装饰为flag。例如:

    ```python
    >>> parser = argparse.ArgumentParser()
    >>> parser.add_argument('--foo', action='store_const', const=42)
    >>> parser.parse_args(['--foo'])
    Namespace(foo=42)
    ```

- `store_true`和`store_false` - 它们都是`store_const`的一种特殊形式，分别用来存储`True`和`False`。另外，如果没有指定这些参数，它们会就会分别代表相反的值，即`False`和`True`：

    ```python
    >>> parser = argparse.ArgumentParser()
    >>> parser.add_argument('--foo', action='store_true')
    >>> parser.add_argument('--bar', action='store_false')
    >>> parser.add_argument('--baz', action='store_false')
    >>> parser.parse_args('--foo --bar'.split())
    Namespace(foo=True, bar=False, baz=True)
    ```

- `append` - 这个action将会把参数以一个list的形式存储，每个参数值都会追加到这个list中。如果需要让选项可以多次指定这个action就很有用：

    ```python
    >>> parser = argparse.ArgumentParser()
    >>> parser.add_argument('--foo', action='append')
    >>> parser.parse_args('--foo 1 --foo 2'.split())
    Namespace(foo=['1', '2'])
    ```

- `append_const` - 这个action将会把参数以一个list的形式存储，每次发现参数后都会把`const`的值追加到list中。这个action一般在需要把多个参数存储在同一个list的时候很有用：

    ```python
    >>> parser = argparse.ArgumentParser()
    >>> parser.add_argument('--str', dest='types', action='append_const', const=str)
    >>> parser.add_argument('--int', dest='types', action='append_const', const=int)
    >>> parser.parse_args('--str --int'.split())
    Namespace(types=[<class 'str'>, <class 'int'>])
    ```

- `count` - 这个action将会计数参数出现的次数。比如，可以用来增加详细的程度:

    ```python
    >>> parser = argparse.ArgumentParser()
    >>> parser.add_argument('--verbose', '-v', action='count')
    >>> parser.parse_args(['-vvv'])
    Namespace(verbose=3)
    ```

- `help` - 在帮助文本中显示该参数的帮助消息。默认会自动加入一个帮助文本信息。

- `version` - 通过`version`参数指定一个版本号，在调用参数时会打印这个版本信息。

    ```python
    >>> import argparse
    >>> parser = argparse.ArgumentParser(prog='PROG')
    >>> parser.add_argument('--version', action='version', version='%(prog)s 2.0')
    >>> parser.parse_args(['--version'])
    PROG 2.0
    ```

你也可以通过实现相同的API接口或者继承`Action`类来创建你的自定义action。推荐的方式是继承`Action`，重写`__call__`方法和`__init__`方法。

下面是一个自定义action的例子:

```python
>>> class FooAction(argparse.Action):
...     def __init__(self, option_strings, dest, nargs=None, **kwargs):
...         if nargs is not None:
...             raise ValueError('nargs not allowed')
...         super(Action, self).__init__(option_strings, dest, **kwargs)
...     def __call__(self, parser, namespace, values, option_string=None):
...         print("%r %r %r" %(namespace, values, option_string))
...         setattr(namespace, self.dest, values)
...
>>> parser = argparse.ArgumentParser()
>>> parser.add_argument('--foo', action=FooAction)
>>> parser.add_argument('bar', action=FooAction)
>>> args = parser.parse_args('1 --foo 2'.split())
Namespace(bar=None, foo=None) '1' None
Namespace(bar='1', foo=None) '2' '--foo'
>>> args
Namespace(bar='1', foo='2') '2' '--foo'
```

#### nargs

`ArgumentParser`通常将一个命令行参数和一个action相关联。`nargs`可以设置不同数量的命令行参数和单个action相关联。支持的参数值包括:

- `N`(一个整数)

    将会从命令行中收集`N`个数量的参数值。例如:

    ```python
    >>> parser = argparse.ArgumentParser()
    >>> parser.add_argument('--foo', nargs=2)
    >>> parser.add_argument('bar', nargs=1)
    >>> parser.parse_args('c --foo a b'.split())
    Namespace(bar=['c'], foo=['a', 'b'])
    ```

    注意`nargs=1`生成了只包含一个值的list。这个行为和默认行为不同，默认不会生成list。

- `?`

    消耗0或1个命令行参数值，如果没有命令行参数，那么就使用`default`定义的值--注意对于选项参数，可能会发生出现有选项字符串但是没有尾随命令行参数的情况。在这种情况下，将会使用`const`中的值。下面是一些例子:

    ```python
    >>> parser = argparse.ArgumentParser()
    >>> parser.add_argument('--foo', nargs='?', const='c', default='d')
    >>> parser.add_argument('bar', nargs='?', default='d')
    >>> parser.parse_args(['XX', '--foo', 'YY'])
    Namespace(bar='XX', foo='YY')
    >>> parser.parse_args(['XX', '--foo'])
    Namespace(bar='XX', foo='c')
    >>> parser.parse_args([])
    Namespace(bar='d', foo='d')
    ```

    `nargs=‘?’`的一个常见的使用场景就是允许对文件的输入/输出可选:

    ```python
    >>> parser = argparse.ArgumentParser()
    >>> parser.add_argument('infile', nargs='?', type=argparse.FileType('r'), 
    ...                     default=sys.stdin)
    >>> parser.add_argument('outfile', nargs='?', type=argparse.FileType('w'), 
    ...                     default=sys.stdout)
    >>> parser.parse_args(['input.txt', 'output.txt'])
    Namespace(infile=<_io.TextIOWrapper name='input.txt' encoding='UTF-8'>,
          outfile=<_io.TextIOWrapper name='output.txt' encoding='UTF-8'>)
    >>> parser.parse_args([])
    Namespace(infile=<_io.TextIOWrapper name='<stdin>' encoding='UTF-8'>,
          outfile=<_io.TextIOWrapper name='<stdout>' encoding='UTF-8'>)
    ```

- `*`

    所有在命令行中出现的值都会收集到一个list中。可以包含0个或多个值。例如:

    ```python
    >>> parser = argparse.ArgumentParser()
    >>> parser.add_argument('--foo', nargs='*')
    >>> parser.add_argument('--bar', nargs='*')
    >>> parser.add_argument('baz', nargs='*')
    >>> parser.parse_args('a b --foo x y --bar 1 2'.split())
    Namespace(bar=['1', '2'], baz=['a', 'b'], foo=['x', 'y'])
    ```

- `+`

    和`*`类似。但是保证最少要有一个参数值，否者会抛出错误消息：

    ```python
    >>> parser = argparse.ArgumentParser()
    >>> parser.add_argument('foo', nargs='+')
    >>> parser.parse_args(['a', 'b'])
    Namespace(foo=['a', 'b'])
    >>> parser.parse_args([])
    usage: PROG [-h] foo [foo ...]
    PROG: error: too few arguments
    ```
    
- `argparse.REMINDER`

    所有**剩余**的参数都会收集到一个list中.通常用于一个命令行需要分发参数给另一个命令行参数的情况:

    ```python
    >>> parser = argparse.ArgumentParser()
    >>> parser.add_argument('--foo')
    >>> parser.add_argument('command')
    >>> parser.add_argument('args', nargs=argparse.REMINDER)
    >>> print(parser.parse_args('--foo B cmd --arg1 XX ZZ'.split()))
    Namespace(args=['--arg1', 'XX', 'ZZ'], command='cmd', foo='B')
    ```

如果没有使用`nargs`，那么参数值的消耗数量取决于`action`。一般情况下，每个参数会消耗一个参数值。

#### const

`add_argument()`的`const`参数用来持有一个常量值。它不会从命令行中读取，但是有几个action都需要这个`const`参数。两个常见的场景是：

- 当`add_argument()`加入了`action='store_const`或者`action='append_const'`的时候。这些action都会把`const`的值加入到`parse_args()`返回的属性中。
- 当`add_argument()`指定了选项字符串(如`-f/--foo`)以及`nargs='?'`的时候。可以创建一个选项参数，接受0或1个数量的参数值。当解析时发现有选项字符串但是没有参数值的时候，会使用`const`的值来替代。

对于`store_const`和`append_const`，必须提供`const`参数。其它情况默认`const=None`。

#### default

除了所有的选项参数可以在命令行不输入外，一些位置参数也可以选择不输入。`add_argument()`有一个关键字参数`default`，它的默认值是`None`，指定一个值以后它可以用来代表命令行没有参数值的情况。对于选项参数，在命令行没有出现选项字符串的时候会使用`default`：

```python
>>> parser = argparse.ArgumentParser()
>>> parser.add_argument('--foo', default=42)
>>> parser.parse_args(['--foo', '2'])
Namespace(foo='2')
>>> parser.parse_args([])
Namespace(foo=42)
```

如果`default`是一个字符串，解析器将会解析这个值。特别是，在将它加入到命名空间之前，会使用`type`参数来把这个字符串转换。如果不是字符串的话就直接使用它：

```python
>>> parser = argparse.ArgumentParser()
>>> parser.add_argument('--length', default='10', type=int)
>>> parser.add_argument('--width', default=10.5, type=int)
>>> parser.parse_args()
Namespace(length=10, width=10.5)
```

对于带有`nargs`为`?`或者`*`的位置参数，在没有参数值的情况下也会使用`default`:

```python
>>> parser = argparse.ArgumentParser()
>>> parser.add_argument('foo', nargs='?', default=42)
>>> parser.parse_args(['a'])
Namespace(foo='a')
>>> parser.parse_args([])
Namespace(foo=42)
```

如果使用`default=argparse.SUPPRESS`，如果没有参数值，也不会为命名空间加入该属性:

```python
>>> parser = argparse.ArgumentParser()
>>> parser.add_argument('--foo', default=argparse.SUPPRESS)
>>> parser.parse_args()
Namespace()
>>> parser.parse_args(['--foo', '1'])
Namespace(foo='1')
```

#### type

默认情况下，`ArgumentParser`会将命令行参数以简单的字符串来读取。不过，很多时候想要让这些命令汗支付转换为其它类型，比如`float`或者`int`。`add_argument()`的`type`关键字参数允许加入类型检查和转换。一般的内置的类型和函数都可以用作`type`：

```python
>>> parser = argparse.ArgumentParser()
>>> parser.add_argument('foo', type=int)
>>> parser.add_argument('bar', type=open)
>>> parser.parse_args("2 temp.txt".split())
Namespace(bar=<_io.TextIOWrapper name='temp.txt' encoding='UTF-8'>, foo=2)
```

为了适用于不同类型的文件(模式)，`argparse`模块提供了一个工厂`FileType`，它接受`open()`函数的`mode=, buffsize=, encoding=, errors=`这些参数。例如，`FileType('w')`可以创建一个可写的文件句柄(#!可以通过partial来实现):

```python
>>> parser = argparse.ArgumentParser()
>>> parser.add_argument('bar', type=argparse.FileType('w'))
>>> parser.parse_args(['out.txt'])
Namespace(bar=<_io.TextIOWrapper name='out.txt' encoding='UTF-8'>)
```

`type=`关键字参数可以接受可调用对象，这个对象接受一个字符串参数并返回一个转换后的值：

```python
>>> def perfect_square(string):
...     value = int(string)
...     sqrt = math.sqrt(value)
...     if sqrt != int(sqrt):
...         msg = "%r is not a perfect square" % string
...         raise argparse.ArgumentTypeError(msg)
...     return value
...
>>> parser = argparse.ArgumentParser(prog='PROG')
>>> parser.add_argument('foo', type=perfect_square)
>>> parser.parse_args(['9'])
Namespace(foo=9)
>>> parser.parse_args(['7'])
usage: PROG [-h] foo
PROG: error: argument foo: '7' is not a perfect square
```

`choices`可以让类型检查限制在一个范围内:

```python
>>> parser = argparse.ArgumentParser(prog='PROG')
>>> parser.add_argument('foo', type=int, choices=(5, 10))
>>> parser.parse_args(['7'])
Namespace(foo=7)
>>> parser.parse_args(['11'])
usage: PROG [-h] {5,6,7,8,9}
PROG: error: argument foo: invalid choice: 11 (choose from 5, 6, 7, 8, 9)
```

#### choices

一些命令行参数的值可能需要限定一个范围。可以通过为`add_argument()`的`choices`参数传入一个容器对象来实现。当命令行被解析后，参数值会被检查，如果参数值没有列于可接受值list之中则会抛出错误:

```python
>>> parser = argparse.ArgumentParser(prog='game.py')
>>> parser.add_argument('move', choices=['rock', 'paper', 'scissors'])
>>> parser.parse_args(['rock'])
Namespace(move='rock')
>>> parser.parse_args(['fire'])
usage: game.py [-h] {rock,paper,scissors}
game.py: error: argument move: invalid choice: 'fire' (choose from 'rock',
'paper', 'scissors')
```

注意`choices`检查会在`type`类型转换之后进行，所以`choices`容器中的对象应该符合`type`的类型：

```python
>>> parser = argparse.ArgumentParser(prog='doors.py')
>>> parser.add_argument('door', type=int, choices=range(1, 4))
>>> print(parser.parse_args(['3']))
Namespace(door=3)
>>> parser.parse_args(['4'])
usage: doors.py [-h] {1,2,3}
doors.py: error: argument door: invalid choice: 4 (choose from 1, 2, 3)
```

任何支持`in`操作符(`__contain__`方法)的对象都可以传入到`choices`中，所以`dict`，`set`，自定义容器都是可以的。

#### required

一般来说，`argparse`模块假定`-f`和`--bar`这些flag为可选参数，它们是可以在命令行中忽略的。想要让这个可选参数变为必填，可以使用关键字参数`required=`:

```python
>>> parser = argparse.ArgumentParser()
>>> parser.add_argument('--foo', required=True)
>>> parser.parse_args(['--foo', 'BAR'])
Namespace(foo='BAR')
>>> parser.parse_args([])
usage: argparse.py [-h] [--foo FOO]
argparse.py: error: option --foo is required
```

就像例子中显示的这样，如果一个可选参数标记为`required`，那么这个参数就是必填的，否则就会报告错误。

> 注意
>
>> 必填option一般认为不是一个好的方式，因为用户一般都会认为option是可选的，所以应该尽可能避免使用这个参数。

#### help

`help`是一个字符串，包含参数的简短描述。当一个用户请求帮助时(通常使用`-h`或者`--help`)，每个参数都会显示它自己的`help`:

```python
>>> parser = argparser.ArgumentParser(prog='frobble')
>>> parser.add_argument('--foo', action='store_true',
...                     help='foo the bars before forbbing')
>>> parser.add_argument('bar', nargs='+',
...                     help='one of the bars to forbbled')
>>> parser.parse_args(['-h'])
usage: frobble [-h] [--foo] bar [bar ...]

positional arguments:
 bar     one of the bars to be frobbled

optional arguments:
 -h, --help  show this help message and exit
 --foo   foo the bars before frobbling
```

`help`参数可以包含多个格式化标识符，显示程序名称或者参数的`default`。内置的格式化标识符包括程序名称(`%(prog)s`)和`add_argument()`中的大多数关键字参数，比如`%(default)s`，`%(type)s`，等等：

```python
>>> parser = argparse.ArgumentParser(prog='frobble')
>>> parser.add_argument('bar', nargs='?', type=int, default=42,
...                     help='the bar to %(prog)s (default: %(default)s)')
>>> parser.print_help()
usage: frobble [-h] [bar]

positional arguments:
 bar     the bar to frobble (default: 42)

optional arguments:
 -h, --help  show this help message and exit
```

由于`help`字符串支持`%`格式化方式，如果你想要单独使用`%`，必须使用`%%`来转义。

`argparse`允许对特定的option不显示其相应的help，通过对`help`传入`argparse.SUPPRESS`即可：

```python
>>> parser = argparse.ArgumentParser(prog='frobble')
>>> parser.add_argument('--foo', help=argparser.SUPPRESS)
>>> parsre.print_help()
usage: frobble [-h]

optional arguments:
  -h, --help  show this help message and exit
```

#### metavar

当`ArgumentParser`生成help消息时，它需要某些方式来引用每个期待的参数。默认情况下，`ArgumentParser`使用`dest`值作为每个对象的“名称”。默认情况下，对于位置参数，直接使用`dest`的值，对于可选参数，使用大写形式的`dest`值。所以，对于单个位置参数`dest='bar'`将会以`bar`来引用。可选参数`--foo`以`FOO`来引用。例子：

```python
>>> parser = argparse.ArgumentParser()
>>> parser.add_argument('--foo')
>>> parser.add_argument('bar')
>>> parser.parse_args('X --foo Y'.split())
Namespace(bar='X', foo='Y')
>>> parser.print_help()
usage:  [-h] [--foo FOO] bar

positional arguments:
 bar

optional arguments:
 -h, --help  show this help message and exit
 --foo FOO
```

也可以通过`metavar`来直接指定名称：

```python
>>> parser = argparse.ArgumentParser()
>>> parser.add_argument('--foo', metavar='YYY')
>>> parser.add_argument('bar', metavar='XXX')
>>> parser.parse_args('X --foo Y'.split())
Namespace(bar='X', foo='Y')
>>> parser.print_help()
usage:  [-h] [--foo YYY] XXX

positional arguments:
 XXX

optional arguments:
 -h, --help  show this help message and exit
 --foo YYY
```

注意`metavar`只改变**显示的名称** -- `parse_args()`返回对象中的属性名称仍然由`dest`参数来指定。

不同类型的`nargs`可能会让`metavar`使用多次。也可以为`metavar`指定一个元组：

```python
>>> parser = argparse.ArgumentParser(prog='PROG')
>>> parser.add_argument("-x", nargs=2)
>>> parser.add_argument("--foo", nargs=2, metavar=("bar", "baz"))
>>> parser.print_help()
usage: PROG [-h] [-x X X] [--foo bar baz]

optional arguments:
 -h, --help     show this help message and exit
 -x X X
 --foo bar baz
```

#### dest

多数`ArgumentParser`的action都会为`parse_args()`返回的对象加入一些属性。属性的名称取决于`add_argument()`的关键字参数`dest`。对于位置参数的action，`dest`一般默认由`add_argument()`的第一个参数决定：

```python
>>> parser = argparse.ArgumentParser()
>>> parser.add_argument('bar')
>>> parser.parse_args(['XXX'])
Namespace(bar='XXX')
```

对于可选参数的action，一般使用`dest`参数来作为属性名。`ArgumentParser`会提取第一个长选项字符串，去除它的`--`，然后将它作为`dest`的值。如果没有提供长选项字符串，就使用第一个短选项字符串(去除`-`)。为了确保是一个合法的属性名称，字符串中的`-`都会被替换为`_`。下面的例子可以说明这一切：

```python
>>> parser = argparse.ArgumentParser()
>>> parser.add_argument('-f', '--foo-bar', '--foo')
>>> parser.add_argument('-x', '-y')
>>> parser.parse_args('-f 1 -x 2'.split())
Namespace(foo_bar='1', x='2')
>>> parser.parse_args('--foo 1 -y 2'.split())
Namespace(foo_bar='1', x='2')
```

`dest`关键字参数允许你提供自定义的属性名称：

```python
>>> parser = argparse.ArgumentParser()
>>> parser.add_argument('--foo', dest='bar')
>>> parser.parse_args('--foo XXX'.split())
Namespace(bar='XXX')
```

#### Action classes

`Action`类实现了Action API，这个可调用对象返回另一个可调用对象，用它来处理命令行中的参数。任何遵循这个API的对象都可以传入`add_argument()`的`action`参数。

类`argparse.Action(option_strings, dest, nargs=None, const=None, default=None, type=None, choices=None, required=False, help=None, metavar=None)`

Action对象由`ArgumentParser`来使用，代表如何解析命令行中的参数。Action类必须接受两个位置参数和多个关键字参数，它们都是`ArgumentParser.add_argument()`的参数签名，除了`action`本身。

Action实例应该拥有属性"dest", "option_strings", "default", "type", "required", "help"等等。最简单的方式是直接调用`Action.__init__`(或者`super()`).

Action实例应该是可调用的，所以子类必须重写`__call__`方法，它应该接受4个参数：

- `parser`: 包含这个action的`ArgumentParser`对象。
- `namespace`: `parse_args()`返回的`Namespace`对象。多数action都使用`setattr()`为这个对象加入属性。
- `values`: 关联的命令行参数（已经被`type`进行了类型转换）。
- `option_string`: 调用这个action的选项字符串。`option_string`参数是可选提供的，如果参数是位置参数，这个参数自然也不存在。

`__call__`方法可以执行任意的动作，但是通常都会根据`dest`和`values`来设置`namespace`的属性。

### The parse_args() method(方法：parse_args())

`ArgumentParser.parse_args(args=None, namespace=None)`

将参数字符串转换为对象，然后将它们作为属性赋值给`namespace`。最后返回构成的`namespace`。

默认情况下，参数字符串将直接使用`sys.argv`，将会创建一个空的`Namespace`对象。

#### Option value syntax(选项值语法)

`parse_args()`支持多种不同的方式传入选项值。最简单的方式就是，分别传入选项和它的值：

```python
>>> parser = argparse.ArgumentParser(prog='PROG')
>>> parser.add_argument('-x')
>>> parser.add_argument('--foo')
>>> parser.parse_args(['-x', 'X'])
Namespace(foo=None, x='X')
>>> parser.parse_args(['--foo', 'FOO'])
Namespace(foo='FOO', x=None)
```

对于长选项(选项字符串多于一个字符就算**长选项**)，选项和值可以以一个字符串的形式传入，使用`=`来分隔它们：

```python
>>> parser.parse_args(['--foo=FOO'])
Namespace(foo='FOO', x=None)
```

对于短选项(只包含一个字符的选项字符串)，选项和值可以组合在一起(不使用字符分隔):

```python
>>> parser.parse_args(['-xX'])
Namespace(foo=None, x='X')
```

多个短选项可以组合一起使用，使用单个`-`前缀即可，直到最后一个需要传入值的选项为止：

```python
>>> parser = argparse.ArgumentParser(prog='PROG')
>>> parser.add_argument('-x', action='store_true')
>>> parser.add_argument('-y', action='store_true')
>>> parser.add_argument('-z')
>>> parser.parse_args(['-xyzZ'])
Namespace(x=True, y=True, z='Z')
```

#### Invalid arguments(不合法的参数)

在解析命令行的时候，`parse_args()`会检查若干错误，包含混淆的选项，不合法的类型，不合法的选项，错误数量的位置参数，等等。当遇到一个错误的时候，它会退出并打印错误：

```python
>>> parser = argparse.ArgumentParser(prog='PROG')
>>> parser.add_argument('--foo', type=int)
>>> parser.add_argument('bar', nargs='?')

>>> # 不合法的类型
>>> parser.parse_args(['--foo', 'spam'])
usage: PROG [-h] [--foo FOO] [bar]
PROG: error: argument --foo: invalid int value: 'spam'

>>> # 不合法的选项
>>> parser.parse_args(['--bar'])
usage: PROG [-h] [--foo FOO] [bar]
PROG: error: no such option: --bar

>>> # 错误的参数数量
>>> parser.parse_args(['spam', 'badger'])
usage: PROG [-h] [--foo FOO] [bar]
PROG: error: extra arguments found: badger
```

#### Argument containing(参数容纳)

`parse_args()`方法会在用户犯一个显著错误的时候报告错误，但是一些情况本身就容易引起歧义。例如，命令行参数`-1`可以用来指定为一个可选参数，也可以当作位置参数的值。`parse_args()`方法使用的警告在这里：位置参数可以以`-`为前缀的形式，代表负数值。解析器中的可选参数不应该使用负数的形式：

```python
>>> parser = argparse.ArgumentParesr(prog='PROG')
>>> parser.add_argument('-x')
>>> parser.add_argument('foo', nargs='?')

>>> # 没有负数形式的可选参数，所以-1是一个位置参数
>>> parser.parse_args(['-x', '-1'])
Namespace(foo=None, x='-1')

>>> # 没有负数形式的可选参数，所以-1和-5都是位置参数
>>> parser.parse_args(['-x', '-1', '-5'])
Namespace(foo='-5', x='-1')

>>> parser = argparse.ArgumentParser(prog='PROG')
>>> parser.add_argument('-1', dest='one')
>>> parser.add_argument('foo', nargs='?')

>>> # 带有负数形式的可选参数，所以-1是一个option
>>> parsre.parse_args(['-1', 'X'])
Namespace(foo=None, one='X')

>>> # 带有负数形式的可选参数，所以-2是一个option
>>> parser.parse_args(['-2'])
usage: PROG [-h] [-1 ONE] [foo]
PROG: error: no such option: -2

>>> # 带有负数形式的可选参数，所以多个-1都是option
>>> parser.parse_args(['-1', '-1])
usage: PROG [-h] [-1 ONE] [foo]
PROG: error: argument -1: expected one argument
```

如果你必须指定一个非负数形式的位置参数带有`-`前缀，你可以插入一个伪参数`--`，它可以告诉`parse_args()`它之后的是一个位置参数：

```python
>>> parser.parse_args(['--', '-f'])
Namespace(foo='-f', one=None)
```

#### Argument abbreviations(prefix matching)(参数缩写--前缀匹配)

`parse_args()`默认允许长选项使用缩写形式（如果缩写没有模凌两可）：

```python
>>> parser = argparse.ArgumentParser(prog='PROG')
>>> parser.add_argument('-bacon')
>>> parser.add_argument('-badger')
>>> parser.parse_args('-bac MMM'.split())
Namespace(bacon='MMM', badger=None)
>>> parser.parse_args('-bad WOOD'.split())
Namespace(bacon=None, badger='WOOD')
>>> parser.parse_args('-ba BA'.split())
usage: PROG [-h] [-bacon BACON] [-badger BADGER]
PROG: error: ambiguous option: -ba could match -badger, -bacon
```

如果缩写的选项名称不能被解析匹配，将会报告错误。缩写特性可以通过设置`allow_abbrev=False`来取消。

#### Beyond sys.argv(不使用sys.argv)

`ArgumentParser`并不是只能使用`sys.argv`。可以为它传入一个字符串list。这个方式很适合创建交互性提示工具：

```python
>>> parser = argparse.ArgumentParser()
>>> parser.add_argument(
...     'integers', metavar='int', type=int, choices=range(10),
...     nargs='+', help='an integer in the range 0...9')
>>> parser.add_argument(
...     '--sum', dest='accumulate', action='store_const', const=sum,
...     default=max, help='sum the integers (default: find the max)')
>>> parser.parse_args(['1', '2', '3', '4'])
Namespace(accumulate=<built-in function max>, integers=[1, 2, 3, 4])
>>> parser.parse_args(['1', '2', '3', '4', '--sum'])
Namespace(accumulate=<built-in function sum>, integers=[1, 2, 3, 4])
```

#### The Namespace object(Namespace对象)

class `argparse.Namespace`

`parse_args()`默认用这个简单的类来创建一个对象，这个对象持有参数属性。

故意让这个类变得简单化，只是简单的继承了`object`，并且有一个可读性的`__repr__`方法。如果你更想用类字典对象，只需要使用标准的Python idiom - `vars()`:

```python
>>> parser = argparse.ArgumentParser()
>>> parser.add_argument('--foo')
>>> args = parser.parse_args(['--foo', 'BAR'])
>>> vars(args)
{'foo': 'BAR'}
```

也可以为`ArgumentParser`指定一个对象作为`namespace`，而不是默认的`Namespace`对象。可以通过为`parse_args()`指定`namespace=`关键字参数来实现(传入的参数是实例，而不是类):

```python
>>> class C:
...     pass
...
>>> c = C()
>>> parser = argparse.ArgumentParesr()
>>> parser.add_argument('--foo')
>>> parser.parse_args(args=['--foo', 'BAR'], namespace=c)
>>> c.foo
'BAR'
```

### Other utilities(其它工具)

#### Sub-commands(子命令)

`ArgumentParser.add_subparsers([title][, description][, prog][, parser_class][, action][, option_string][, dest][, help][, metavar])`

很多程序都将它们的功能拆分放到若干子命令中，例如，`svn`可以调用子命令：`snv checkout`, `svn update`和`svn commit`。如果程序不同的功能需要不同的命令，拆分为子命令是一个好想法。`ArgumentParser`支持使用`add_subparsers()`方法来创建这些子命令。`add_subparsers()`通常直接调用即可，它返回一个特殊的action对象。这个对象拥有一个简单的方法，`add_parser()`，它接受一个命令行名称以及多个`ArgumentParser`构造器参数，最后返回一个`ArgumentParser`对象。

参数描述:

- `title` -- help输出的字解析器组的标题；如果传入`description`，使用"subcommands"，否者使用位置参数的title。

- `description` -- help输出的子解析器组的描述，默认为`None`。

- `prog` -- 子命令help显示中的程序名称。

- `parser_class` -- 用于创建子解析器实例的解析器类，默认使用当前的parser。

- `action` -- 基础的`action`。

- `dest` -- 基础的`dest`，默认为`None`。

- `help` -- 子解析器组的help，默认为`None`。

- `metavar` -- 子命令help中的字符串；默认为`None`，在子命令中的表现形式为`{cmd1, cmd2, ...}`

用法例子：

```python
>>> # 创建顶级parser
>>> parser = argparser.ArgumentParser(prog='PROG')
>>> parser.add_argument('--foo', action='store_true', help='foo help')
>>> subparsers = parser.add_subparsers(help='sub-command help')
>>>
>>> # 创建一个子parser，命名为"a"命令
>>> parser_a = subparsers.add_parser('a', help='a help')
>>> parser_a.add_argument('bar', type=int, help='bar help')
>>>
>>> # 创建一个子parser，命名为"b"命令
>>> parser_b = subparsers.add_parser("b", help="b help")
>>> parser_b.add_argument("--baz", choices='XYZ', help='baz help')
>>>
>>> # 解析一些参数
>>> parser.parse_args(['a', '12'])
Namespace(bar='12', foo=False)
>>> parser.parse_args(['--foo', 'b', '--baz', 'Z'])
Namespace(baz='Z', foo='b')
```

注意`parse_args()`返回的对象只会包含主解析器中的命令属性和子解析器中被使用的命令属性。所以在上面的例子中，当指定`a`命令后，只出现了`foo`和`bar`属性，在指定`b`命令后，只出现了`foo`和`baz`属性。

同样的，当请求一个子解析器的help消息，只会打印这个特定解析器的help文本，不会包括父解析器或者兄弟级别解析器的帮助文本。

```python
>>> parser.parse_args(['--help'])
usage: PROG [-h] [--foo] {a,b} ...

positional arguments:
  {a,b}   sub-command help
    a     a help
    b     b help

optional arguments:
  -h, --help  show this help message and exit
  --foo   foo help

>>> parser.parse_args(['a', '--help'])
usage: PROG a [-h] bar

positional arguments:
  bar     bar help

optional arguments:
  -h, --help  show this help message and exit

>>> parser.parse_args(['b', '--help'])
usage: PROG b [-h] [--baz {X,Y,Z}]

optional arguments:
  -h, --help     show this help message and exit
  --baz {X,Y,Z}  baz help
```

方法`add_subparsers()`支持`title`和`description`关键字参数。当使用了这些参数以后，这些子解析器命令将会出现在它们所属解析器帮助文本的组中。例如：

```python
>>> parser = argparsr.ArgumentParser()
>>> subparsers = parser.add_subparsers(title='subcommands',
...                                    description='valid subcommands',
...                                    help='additional help')
>>> subparsers.add_parser('foo')
>>> subparsers.add_parser('bar')
>>> parser.parse_args(['-h'])
usage:  [-h] {foo,bar} ...

optional arguments:
  -h, --help  show this help message and exit

subcommands:
  valid subcommands

  {foo,bar}   additional help
```

另外，`add_parser`提供一个额外的`aliases`参数，它允许多个字符串引用同一个子解析器。举个例子，比如`svn`，alias`co`是`checkout`的快捷方式：

```python
>>> parser = argparse.ArgumentParser()
>>> subparser = parser.add_subparsers()
>>> checkout = subparser.add_parse('checkout', aliases=['co'])
>>> checkout.add_argument("foo")
>>> parser.parse_args(['co', 'bar'])
Namespace(foo='bar')
```

一个特别有用的方式是组合`add_subparsers()`方法和`set_defaults()`，让每个subparser都知道调用哪个Python函数：

```python
>>> # 子命令函数
>>> def foo(args):
...     print(args.x * args.y)
...
>>> def bar(args):
...     print("((%s))" % args.z)
...
>>> # 创建顶级的parser
>>> parser = argparse.ArgumentParser()
>>> subparsers = parser.add_subparsers()
>>>
>>> # 创建"foo"命令子解析器
>>> parser_foo = subparsers.add_parser('foo')
>>> parser_foo.add_argument('-x', type=int, default=1)
>>> parser_foo.add_argument('y', type=float)
>>> parser_foo.set_default(func=foo)
>>> 
>>> # 创建"bar"命令子解析器
>>> parser_bar = subparsers.add_parser("bar")
>>> parser_bar.add_argument("z")
>>> parser_bar.set_default(func=bar)
>>>
>>> # 解析args，无论调用哪个函数
>>> args = parser.parse_args('foo 1 -x 2'.split())
>>> args.func(args)
2.0
>>> # 解析args，无论调用哪个函数
>>> args = parser.parse_args('bar XYZYX'.split())
>>> args.func(args)
((XYZYX))
```

是个方式可以让`parse_args()`在解析完成后调用合适的函数来处理。关联的函数用于处理各种不同的subparser。不过，如果你一定要解析调用的解析器名称，可以为`add_subparsers`加入一个`dest`参数：

```python
>>> parser = argparse.ArgumentParser()
>>> subparsers = parser.add_subparsers(dest='subparser_name')
>>> subparser1 = subparsers.add_parser('1')
>>> subparser1.add_argument('-x')
>>> subparser2 = subparsers.add_parser('2')
>>> subparser2.add_argument('y')
>>> parser.parse_args(['2', 'frobble'])
Namespace(subparser_name='2', y='frobble')
```

#### FileType objects(FileType对象)






