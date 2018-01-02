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

pass



