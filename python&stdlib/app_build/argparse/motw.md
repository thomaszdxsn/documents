## argparse -- 命令行选项和参数的解析

*用途：命令行选项和参数的解析*

`argparse`库包含的工具，用于创建命令行参数和选项处理器(processor).这个库在Python2.7中作为`optparse`的替代加入到标准库。因为`argparse`实现的特性并不能轻松的加入到`optparse`，因为需要牵涉到很多向后兼容的API改动问题，所以引入了这个新的标准库。`optparse`现在已经弃用。

### Setting Up a Parser(设立一个解析器)

使用`argparse`的第一步就是创建一个parser对象，然后告诉它想要接受哪些参数。在程序运行时可以使用这个parser来处理命令行参数。parser类(`ArgumentParser`)的构造器可以接收一个`description`参数用来当作程序的帮助文本一部分，另外还可以接受一些全局配置参数。

```python
import argparser 

parser = argparser.ArgumentParser(
    description='This is a PyTOMW sample program',
)
```

### Defining Arguments(定义参数)

`argparser`是一个完整的(命令行)参数处理库。可以通过在`add_argument()`中指定`action`参数，来让参数触发不同的动作。支持的动作包括：存储参数(单个，或者作为列表的一部分)，在碰到参数时存储一个常量值(比如`store_true`能够根据是否遇到了该选项参数而在True/False之间切换)，为参数出现的次数计数，或者调用一个callback使用你自定义的指令。

默认的action是存储一个参数。如果提供了`type`参数，将会把值先转换成type以后再存储。如果指定了`dest`参数，命令行参数的值会使用dest中的名称来存储。

### Parsing a Command-Line(解析命令行)

在完成所有的参数定义后，将会把一个参数字符串序列传入到`parse_args()`，让它来解析命令行。默认情况下，这些参数将会提取自`sys.argv[1:]`，但是也可以使用其它任意的字符串列表。选项参数的处理使用了GNU/POSIX语法，所有选项参数和位置参数可以混合使用。

`parse_args()`返回的值是一个`Namespace`对象，它包含命令中的所有参数。这个对象将参数当作属性，所以如果一个参数设置了`dest=myoption`，这个参数值可以通过`args.myoption`来访问。

### Simple Examples(简单的例子)

下面是一个简单的例子，拥有3种不同的选项参数：一个布尔选项(`-a`)，一个简单的字符串选项(`-b`)，以及一个整数选项(`-c`).

#### argparse_short.py

```python
# argparse_short.py

import argparse

parser = argparse.ArgumentParser(description='Short sample app')

parser.add_argument('-a', action='store_true', default=False)
parser.add_argument('-b', action='store', dest='b')
parser.add_argument('-c', action='store', dest='c', type=int)

print(parser.parse_args(['-a', '-bval', '-c', '3']))
```

对单字符选项参数的传值也有几种方式。上面例子使用了两种不同的形式，`-bval`和`-c val`.

```shell
$ python3 argparse_short.py

Namespace(a=True, b='val', c=3)
```

在输出中，`c`关联值的类型是int，因为`ArgumentParser`在存储参数之前会将它作类型转换(如果需要的话).

#### argparse_long.py

"长"选项名称，是指参数名多于一个字符的情况，也可以用相同的方式处理：

```python
# argparse_long.py

import argparse

parser = argparser.ArgumentParser(
    description='Example with long option names',
)

parser.add_argument('--noarg', action='store_true',
                    default=False)
parser.add_argument('--witharg', action='store',
                    dest='witharg')
parser.add_argument('--witharg2', action='store',
                    dest='witharg2', type=int)


print(
    parser.parse_args(
        ['--noarg', '--witharg1', 'val', '--witharg2=3']
    )
)
```

结果也类似:

```shell
$ python3 argparse_long.py

Namespace(noarg=True, witharg='val', witharg2=3)
```

#### argparse_arguments.py

`argparse`是一个功能完整的命令行参数解析工具，可以同时处理选项参数和必填位置参数：

```python
# argparse_arguments.py

import argparse

parser = argparse.ArgumentParser(
    description='Example with nonoptional arguments',
)

parser.add_argument('count', action='store', type=int)
parser.add_argument('units', action='store')

print(parser.parse_args())
```

在这个例子中，"count"参数是一个整数，"units"参数以字符串形式存储。如果在命令行中缺了它们中任意一个，或者给定的值不能转换为正确的类型，将会曝出错误。

```shell
$ python3 argparse_arguments.py 3 inches

Namespace(count=3, units='inches')

$ python3 argparse_arguments.py some inches

usage: argparse_arguments.py [-h] count units
argparse_arguments.py: error: argument count: invalid int value:
'some'

$ python3 argparse_arguments.py

usage: argparse_arguments.py [-h] count units
argparse_arguments.py: error: the following arguments are
required: count, units
```

#### Argument Actions(参数动作)

有６种内置的动作可以由参数触发:

- `store`

    保存参数值，可以选择转换成其它类型再保存。这是默认的action选择.

- `store_const`

    保存一个符合参数规范的参数值。通常用于实现非布尔值的命令行flag.

- `store_true/store_false`

    保存合适的布尔值。这个动作用来实现布尔值切换。

- `append`

    将参数值保存到一个列表中。如果参数重复出现，就会保存多个参数值。

- `append_const`

    将参数规范中的值保存到一个列表中。

- `version`

    打印程序的版本细节，然后退出.

##### argparse_action.py

这个例子讲解了每个action类型，其它的配置尽量保持最简化:

```python
# argparse_action.py

import argparse

parser = argparse.ArgumentParser()

parser.add_argument('-s', action='store',
                    dest='simple_value',
                    help='Store a simple value')

parser.add_argument('-c', action='store_const',
                    dest='constant_value',
                    const='value-to-store',
                    help='Store a constant value')

parser.add_argument('-t', action='store_true',
                    default=False,
                    dest='boolean_t',
                    help='Set a switch to true')
parser.add_argument('-f', action='store_false,
                    default=True,
                    dest='boolean_f',
                    help='Set a switch to False')

parser.add_argument('-a', action='append',
                    dest='collection',
                    default=[],
                    help='Add repeated value to a list')

parser.add_argument('-A', action='append_const',
                    dest='const_collection',
                    const='value-1-to-append',
                    default=[],
                    help='Add different values to list')
parser.add_argument('-B', action='append_const',
                    dest='const_collection',
                    const='value-2-to-append',
                    help='Add different values to list')

parser.add_argument('--version', action='version',
                    version='%(prog)s 1.0')

results = parser.parse_args()
print("simple_value         = {!r}".format(results.simple_value))
print("constant_value       = {!r}".format(results.constant_value))
print("boolean_t            = {!r}".format(results.boolean_t))
print("boolean_f            = {!r}".format(results.boolean_f))
print("collection           = {!r}".format(result.collection))
print("const_collection     = {!r}".format(result.const_collection))
```

`-t`和`-f`配置用来修改不同的布尔值.`-A`和`-B`的`dest`是一样的，所以它们的值都会追加到同一个列表中。

```shell
$ python3 argparse_action.py -h


usage: argparse_action.py [-h] [-s SIMPLE_VALUE] [-c] [-t] [-f]
                          [-a COLLECTION] [-A] [-B] [--version]

optional arguments:
  -h, --help       show this help message and exit
  -s SIMPLE_VALUE  Store a simple value
  -c               Store a constant value
  -t               Set a switch to true
  -f               Set a switch to false
  -a COLLECTION    Add repeated values to a list
  -A               Add different values to list
  -B               Add different values to list
  --version        show program's version number and exit

$ python3 argparse_action.py -s value

simple_value     = 'value'
constant_value   = None
boolean_t        = False
boolean_f        = True
collection       = []
const_collection = []

$ python3 argparse_action.py -c

simple_value     = None
constant_value   = 'value-to-store'
boolean_t        = False
boolean_f        = True
collection       = []
const_collection = []

$ python3 argparse_action.py -t

simple_value     = None
constant_value   = None
boolean_t        = True
boolean_f        = True
collection       = []
const_collection = []

$ python3 argparse_action.py -f

simple_value     = None
constant_value   = None
boolean_t        = False
boolean_f        = False
collection       = []
const_collection = []

$ python3 argparse_action.py -a one -a two -a three

simple_value     = None
constant_value   = None
boolean_t        = False
boolean_f        = True
collection       = ['one', 'two', 'three']
const_collection = []

$ python3 argparse_action.py -B -A

simple_value     = None
constant_value   = None
boolean_t        = False
boolean_f        = True
collection       = []
const_collection = ['value-2-to-append', 'value-1-to-append']

$ python3 argparse_action.py --version

argparse_action.py 1.0
```

#### Option Prefiexs(选项参数前缀)

默认的选项参数语法遵循Unix系统的惯例，以`-`作为前缀.`argparse`也支持使用其它前缀，比如window中的`/`:

##### argparse_prefix_chars.py

```python
# argparse_prefix_chars.py

import argparse

parser = argparse.ArgumentParser(
    description='Change the option prefix characters',
    prefix_chars='-+/',
)

parser.add_argument('-a', action='store_false',
                    default=None,
                    help='Turn A Off')
parser.add_argument('+a', action='store_true',
                    default=None,
                    help='Turn A on')
parser.add_argument('//noarg', '++noarg',
                    action='store_true',
                    default=False)

print(parser.parse_args())
```

设置`ArgumentParser`的参数`prefix_chars`，这个参数字符串的所有字符串都允许被当做选项参数前缀。注意通过使用`prefix_chars`可以实现字符转换。这可以显示的控制参数是否能够通过不同的前缀又不同的行为。在上面例子中，`+a`和`-a`是两个不同的参数，`//noarg`和`++arg`是同一个参数，但是没有`--noarg`：

```shell
$ python3 argparse_prefix_chars.py -h

usage: argparse_prefix_chars.py [-h] [-a] [+a] [//noarg]

Change the option prefix characters

optional arguments:
  -h, --help        show this help message and exit
  -a                Turn A off
  +a                Turn A on
  //noarg, ++noarg

$ python3 argparse_prefix_chars.py +a

Namespace(a=True, noarg=False)

$ python3 argparse_prefix_chars.py -a

Namespace(a=False, noarg=False)

$ python3 argparse_prefix_chars.py //noarg

Namespace(a=None, noarg=True)

$ python3 argparse_prefix_chars.py ++noarg

Namespace(a=None, noarg=True)

$ python3 argparse_prefix_chars.py --noarg

usage: argparse_prefix_chars.py [-h] [-a] [+a] [//noarg]
argparse_prefix_chars.py: error: unrecognized arguments: --noarg
```

#### Source of Arguments(参数的来源)

迄今为止的所有示例中，parser解析的参数列表都是要么靠显示传入，要么靠使用`sys.argv`隐式传入。如果想要处理一些类似命令行的指定，那么应该使用显式传入的方式：

##### argparse_with_shlex.py

```python
# argparse_with_shlex.py

import argparse
from configparser import ConfigParser
import shlex

parser = argparser.ArgumentParser(description='Short sample app')

parser.add_argument('-a', action='store_true', default=False)
parser.add_argument('-b', action='store', dest='b')
parser.add_argument('-c', action='store', dest='c', type=int)

config = ConfigParser()
config.read('argparse_with_shlex.ini')
config_value = config.get('cli', 'options')
print("Config  :", config_value)

argument_list = shlex.split(config_value)
print('Arg List: ', argument_list)

print("Results: ", parser.parse_args(argument_list))
```

这个例子使用`configparser`模块来读取配置文件.

```ini
[cli]
options = -a -b 2
```

`shlex`模块可以用来分割p配置文件中的字符串:

```shell
$ python3 argparse_with_shlex.py

Config  : -a -b 2
Arg List: ['-a', '-b', '2']
Results : Namespace(a=True, b='2', c=None)
```

##### argparse_fromfile_prefix_chars.py

可以通过`fromfile_prefix_chars`来告诉`argparse`使用带该前缀的文件作为参数来源：

```python
# argparse_fromfile_prefix_chars.py

import argparse

parser = argparse.ArgumentParser(
    description='Short sample app',
    fromfile_prefix_chars='@',
)

parser.add_argument('-a', action='store_true', default=False)
parser.add_argument('-b', action='store', dest='b')
parser.add_argument('-c', action='store', dest='c')

print(parser.parse_args(['@argparse_fromfile_prefix_chars.txt']))
```

这个例子会在找到带`@`前缀的文件时停止,然后读取这个文件获取更多参数.这个文件应该保持每行一个参数的格式：

```txt
# argparse_fromfile_prefix_chars.txt

-a
-b
2
```

运行py文件的输出如下:

```shell
$ python3 argparse_fromfile_prefix_chars.py

Namespace(a=True, b='2', c=None)
```

### Help Output(输出帮助信息)

#### Automatically Generated Help(自动生成帮助文本)

##### argparse_with_help.py

配置完成后，`argparse`会自动加入一个选项当做帮助选项。`ArgumentParser`的`add_help`参数可以控制帮助相关的选项:

```python
# argparse_with_help.py

import argparse

parser = argparse.ArgumentParser(add_help=True)

parser.add_argument('-a', action='store_true', default=False)
parser.add_argument('-b', action='store', dest='b')
parser.add_argument('-c', action='store', dest='c', type=int)

print(parser.parse_args())
```

##### argparse_without_help.py

帮助选项(`-h`和`--help`)默认会自动加入，但是可以通过设置`add_help=False`来选择不加入帮助选项.

```python
# argparse_without_help.py

parser = argparse.ArgumentParser(add_help=False)

parser.add_argument('-a', action='store_true', default=False)
parser.add_argument('-b', action='store', dest='b')
parser.add_argument('-c', action='store', dest='c', type=int)

print(parser.parse_args())
```

##### Output

虽然`-h`和`--help`是命令行程序显示帮助的事实标准，但也有些应用希望不显示帮助文本或者希望使用其它的选项名称:

```shell
$ python3 argparse_with_help.py


usage: argparse_with_help.py [-h] [-a] [-b B] [-c C]

optional arguments:
  -h, --help  show this help message and exit
  -a
  -b B
  -c C

$ python3 argparse_without_help.py -h

usage: argparse_without_help.py [-a] [-b B] [-c C]
argparse_without_help.py: error: unrecognized arguments: -h
```

#### Custmozing Help(自定义帮助文本)

一些应用如果想要直接输出帮助文本，可以通过自定义`actions`类时定义一些方法来实现.

##### argparse_custom_help.py

```python
# argparse_custom_help.py

parser = argparse.ArgumentParser(add_help=True)


parser.add_argument('-a', action="store_true", default=False)
parser.add_argument('-b', action="store", dest="b")
parser.add_argument('-c', action="store", dest="c", type=int)

print('print_usage output: ')
parser.print_usage()
print()

print('print_help output: ')
parser.print_help()
```

`print_usage()`打印一个参数解析器的简短用法信息，`print_help()`将会打印完整的帮助信息.

```shell
$ python3 argparse_custom_help.py

print_usage output:
usage: argparse_custom_help.py [-h] [-a] [-b B] [-c C]

print_help output:
usage: argparse_custom_help.py [-h] [-a] [-b B] [-c C]

optional arguments:
  -h, --help  show this help message and exit
  -a
  -b B
  -c C
```

##### argparse_raw_description_help_formatter.py

`ArgumentParser`使用一个`Formatter`类来控制帮助文本的表现形式。想要修改这个类，可以在实例化`ArgumentParser`的时候传入到参数`formatter_class`中。

例如，`RawDescriptionHelpFormatter`不使用默认Formatter提供的行包裹的打印方式：

```python
# argparse_raw_description_help_formatter.py

import argparse

parser = argparse.ArgumentParser(
    add_help=True,
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description="""
    description
        not
            wrapped""",
    epilog="""
    epilog
        not
            wrapped""",
)

parser.add_argument(
    "-a", action="store_true",
    help="""argument
    help is
    wrapped
    """,
)

parser.print_help()
```

命令行中的描述(descrption)和收场白(epilog)都会保持原样:

```shell
$ python3 argparse_raw_description_help_formatter.py

usage: argparse_raw_description_help_formatter.py [-h] [-a]

    description
        not
           wrapped

optional arguments:
  -h, --help  show this help message and exit
  -a          argument help is wrapped

    epilog
      not
         wrapped
```

##### argparse_raw_text_help_formatter.py

`RawTextHelpFormatter`将会把所有帮助文本当做已经格式化好的(即它不会再去加工)：

```python
# argparse_raw_text_help_formatter.py

import argparse

parser = argparse.ArgumentParser(
    add_help=True,
    formatter_class=argparse.RawTextHelpFormatter,
    description="""
    description
        not
           wrapped""",
    epilog="""
    epilog
      not
         wrapped""",
)

parser.add_argument(
    '-a', action='store_true',
    help="""argument
    help is not
    wrapped
    """,
)

parser.print_help()
```

`-a`参数的帮助文本现在也不会被整齐的封装了.

```shell
$ python3 argparse_raw_text_help_formatter.py

usage: argparse_raw_text_help_formatter.py [-h] [-a]

    description
        not
           wrapped

optional arguments:
  -h, --help  show this help message and exit
  -a          argument
                  help is not
                  wrapped


    epilog
      not
         wrapped
```

如果在帮助我们文本中有示例那么最好使用`rawformatter`这种不再加工的格式化方法，否则你的示例排版会被弄乱。

##### argparse_metavar_type_help_formatter.py

`MetavarTypeHelpFormatter`打印每个选项的类型名称，而不是它对应的变量名称，适用于你的程序中有大量不同类型的选项。

```python
# argparse_metavar_type_help_formatter.py

import argparse

parser = argparse.ArgumentParser(
    add_help=True,
    formatter_class=argparse.MetavarTypeHelpFormatter
)

parser.add_argument('-i', type=int, dest='notshow1')
parser.add_argument('-f', type=float, dest='notshow2')

parser.print_help()
```

输出如下：

```shell
$ python3 argparse_metavar_help_formatter.py

usage: argparse_metavar_type_help_formatter.py [-h] [-i int] [-f
 float]

optional arguments:
  -h, --help  show this help message and exit
  -i int
  -f float
```

### Parser Organization(解析器的组织)

`argparse`包含了若干特性用来组织参数解析器，目的是让代码更容易写或者让帮助文本更加有用。

#### Sharing Parser Rules(分享解析器原则)

程序员有时需要实现一组命令行工具，让它接受所有的参数，然后在其它的地方使用它们。例如，如果一个程序需要验证用户身份之后才允许使用，那么它们就都需要支持`--user`和`--password`选项。本方法是为每个`ArgumentParser`都加入相同的参数，但是也可以定义一个基类Parser，为它定义一些可以用来分享的选项参数，然后每个独立的程序都可以继承(使用另一种方式的继承)这个基类。

##### argparse_parent_base.py & argparse_uses_parent.py

第一步是建立一个可以分享参数定义的parser。因为之后每个子类都要有自己的帮助选项，需要关闭`add_help`这个参数。

```python
# argparse_parent_base.py

import argparse

parser = argparse.ArgumentParser(add_help=False)

parser.add_argument('--user', action='store')
parser.add_argument('--password', action='store')
```

然后，创建另一个解析器，继承这个基类：

```python
# argparse_uses_parents.py

import argparse
import argparse_parent_base

parser = argparse.ArgumentParser(
    parents=[argparse_parent.base.parser],
)

parser.add_argument('--local-arg',
                    action='store_true',
                    default=False)

print(parser.parse_args())
```

然后下面这个解析器就可以接受３个选项参数啦:

```shell
$ python3 argparse_uses_parent.py -h

usage: argparse_uses_parent.py [-h] [--user USER]
                               [--password PASSWORD]
                               [--local-arg]

optional arguments:
  -h, --help           show this help message and exit
  --user USER
  --password PASSWORD
  --local-arg
```

#### Conflicting Options(相冲突的选项)

上面的例子中，如果在继承后另外定义了相同名称的选项将会抛出异常。冲突问题的解决方式可以通过传入`conflict_handler`参数来实现。两个内置的handler是`error`(默认，就是碰到冲突会抛出异常)和`resolve`，解析器将会根据加入顺序选择一个handler.

##### argparse_conflict_handler_resolve.py

```python
# argparse_conflict_handler_resolve.py

import argparse

parser = argparse.ArgumentParser(conflict_handler='resolve')

parser.add_argument('-a', action='store')
parser.add_argument('-b', action='store', help='Short alone')
parser.add_argument('--long-b', '-b',
                    action='store',
                    help='Long and shor together')
print(parser.parses_args['-h'])
```

在这个例子中，后面定义的`--long-b`将会覆盖`-b`.

```shell
$ python3 argparse_conflict_handler_resolve.py

usage: argparse_conflict_handler_resolve.py [-h] [-a A]
[--long-b LONG_B]

optional arguments:
  -h, --help            show this help message and exit
  -a A
  --long-b LONG_B, -b LONG_B
                        Long and short together
```

##### argparse_conflict_handler_resolve2.py

调换参数定义的顺序以后，独立的`-b`不会被覆盖，不过`--long-b`的简写形式也不能使用了：

```python
# argparse_conflict_handler_resolve2.py

import argparse

parser = argparse.ArgumentParser(conflict_handler='resolver')

parser.add_argument('-a', action='store')
parser.add_argument('--long-b', '-b',
                    action='store',
                    help='Long and short together')
parser.add_argument('-b', action='store', help='Short alone')                    

print(parser.parse_args())
```

现在选项都可以使用了：

```shell
$ python3 argparse_conflict_handler_resolve2.py

usage: argparse_conflict_handler_resolve2.py [-h] [-a A]
                                             [--long-b LONG_B]
                                             [-b B]

optional arguments:
  -h, --help       show this help message and exit
  -a A
  --long-b LONG_B  Long and short together
  -b B             Short alone
```

#### Argument Groups(参数组)

`argparse`可以将参数定义绑定到一个"组(group)"中。默认它会使用两个组，一个是选项组，另一个是必填位置参数的组.

##### argparse_default_grouping

```python
# argparse_default_grouping.py

import argparse

parser = argparse.ArgumentParser(description='Short sample app')

parser.add_argument('--optional', action='store_true',
                    default=False)
parser.add_argument('positional', action='store')                    

print(parser.parse_args())
```

在帮助文本中可以看到分组，分别是"positional arguments"和"optional arguments":

```shell
$ python3 argparse_default_grouping.py -h

usage: argparse_default_grouping.py [-h] [--optional] positional

Short sample app

positional arguments:
  positional

optional arguments:
  -h, --help  show this help message and exit
  --optional
```

分组可以让帮助文本的显示更具逻辑性，因为同一个组的选项都输出在一块。之前的“共享选项”例子就可以使用分组概念，那么用户验证的选项就可以在帮助文本中显示在一起了。

##### argparse_parent_with_group.py & argparse_use_parent_group.py

通过`add_arguments_group()`创建一个分组`authentication`，然后把和用户验证相关的选项都加入到这个分组:

```python
# argparse_parent_with_group.py

import argparse

parser = argparse.ArgumentParser(add_help=False)

group = parser.add_argument_group('authentication')

group.add_argument('--user', action="store")
group.add_argument('--password', action='store')
```

下面这个解析器继承上面的基类:

```python
# argparse_uses_parent_with_group.py

import argparse
import argparse_parent_with_group

parser = argparse.ArgumentParser(
    parents=[argparser_parent_with_group.parser],
)

parser.add_argument(
    '--local-arg',
    action='store_true',
    default=False
)
print(parser.parse_args())
```

下面是输出的帮助文本:

```shell
$ python3 argparse_uses_parent_with_group.py -h

usage: argparse_uses_parent_with_group.py [-h] [--user USER]
                                          [--password PASSWORD]
                                          [--local-arg]

optional arguments:
  -h, --help           show this help message and exit
  --local-arg

authentication:
  --user USER
  --password PASSWORD
```

#### Mutually Exclusive Options(相互排斥的选项)

定义相互排斥选项需要使用一种特殊的分组特性，需要使用`add_mutually_exclusive_group()`来代替`add_argument_group()`:

##### argparse_mutually_exclusive.py

```python
# argparse_mutually_exclusive.py

import argparse

parser = argparse.ArgumentParser()

group = parser.add_mutually_exclusive_group()
group.add_argument('-a', action='store_true')
group.add_argument('-b', action='store_true')

print(parser.parse_args())
```

argparse强制让这个分组的选项相互排除，只可以选择使用这个分组中的一个选项:

```shell
$ python3 argparse_mutually_exclusive.py -h

usage: argparse_mutually_exclusive.py [-h] [-a | -b]

optional arguments:
  -h, --help  show this help message and exit
  -a
  -b

$ python3 argparse_mutually_exclusive.py -a

Namespace(a=True, b=False)

$ python3 argparse_mutually_exclusive.py -b

Namespace(a=False, b=True)

$ python3 argparse_mutually_exclusive.py -a -b

usage: argparse_mutually_exclusive.py [-h] [-a | -b]
argparse_mutually_exclusive.py: error: argument -b: not allowed
with argument -a
```

#### Nesting Parser(嵌套解析器)

上面描述的父级解析器方法是共享选项参数的方法之一。另一个方法是把命令都集中在一个程序中，然后使用子解析器来处理命令行的一部分。比如`svb`, `hg`都是用了这种方法来支持多命令行动作，或者子命令。

##### argparse_subparsers.py

比如一个操作文件系统的程序，可能需要定义创建，删除和列出目录清单这些命令.

```python
# argparse_subparsers.py

import argparse

parser = argparse.ArgumentParser()

subparsers = parser.add_subparsers(help='commands') #! 只是创建子命令解析器工厂

# 一个list命令
list_parser = subparsers.add_parser(        #! 这里才真正的创建了一个子命令解析器
    'list', help='List contents')
list_parser.add_argument(
    'dirname', action='store',
    help='Directory to list'
)

# 一个create命令
create_parser = subparsers.add_parser(
    'create', help="Create a directory"
)
create_parser.add_argument(
    "dirname",
    action='store',
    help='New directory to create'
)
create_parser.add_argument(
    "--read-only", 
    default=False,
    action='store_true',
    help='Set permissions to prevent writing to the directory'
)

# 一个delete命令
delete_parser = subparsers.add_parser(
    'delete', help='Remove a directory'
)
delete_parser.add_argument(
    'dirname', action='store', help='The directory to remove'
)
delete_parser.add_argument(
    '--recursive', '-r', default=False, action='store_true',
    help='Removing the contents of the directory, too'
)

print(parser.parse_args())
```

输出将会把这些“子解析器”以位置参数的形式显示，并且标记为"commands"(在add_subparsers中指定的help):

```shell
$ python3 argparse_subparsers.py -h

usage: argparse_subparsers.py [-h] {list,create,delete} ...

positional arguments:
  {list,create,delete}  commands
    list                List contents
    create              Create a directory
    delete              Remove a directory

optional arguments:
  -h, --help            show this help message and exit
```

每个子解析器都带有它自己的帮助文本:

```shell
$ python3 argparse_subparsers.py create -h

usage: argparse_subparsers.py create [-h] [--read-only] dirname

positional arguments:
  dirname      New directory to create

optional arguments:
  -h, --help   show this help message and exit
  --read-only  Set permissions to prevent writing to the directo
ry
```

在参数被解析后，`parse_args()`返回的包含和选定命令相关的值:

```shell
$ python3 argparse_subparsers.py delete -r foo

Namespace(dirname='foo', recursive=True)
```

### Advanced Argument Processing(参数处理进阶)

pass




