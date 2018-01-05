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

`RawTextHelpFormatter`将会维持所有帮助文本的空格符，参数的帮助文本也一样。

...