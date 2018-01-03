URL: [https://docs.python.org/3.6/howto/argparse.html#id1](https://docs.python.org/3.6/howto/argparse.html#id1)

[TOC]

## Argparse Tutorial(argparse模块的教程)

作者：Tshepang Lekhonkhobe

这篇教程的是针对`argparse`的入门级介绍，`argparse`是一个Python标准库，被官方推荐用来作命令行解析工作。

### Concepts(概念)

让我们使用`ls`命令来展示我们这篇教程要教给你的东西：

```shell
$ ls
cpython  devguide  prog.py  pypy  rm-unused-function.patch
$ ls pypy
ctypes_configure  demo  dotviewer  include  lib_pypy  lib-python ...
$ ls -l
total 20
drwxr-xr-x 19 wena wena 4096 Feb 18 18:51 cpython
drwxr-xr-x  4 wena wena 4096 Feb  8 12:04 devguide
-rwxr-xr-x  1 wena wena  535 Feb 19 00:05 prog.py
drwxr-xr-x 14 wena wena 4096 Feb  7 00:59 pypy
-rw-r--r--  1 wena wena  741 Feb 18 01:01 rm-unused-function.patch
$ ls --help
Usage: ls [OPTION]... [FILE]...
List information about the FILEs (the current directory by default).
Sort entries alphabetically if none of -cftuvSUX nor --sort is specified.
...
```

从上面的４个命令中我们可以学到的概念包括:

- 即使没有添加任何选项,`ls`命令也很有用。它默认会显示当前目录的内容。
- 如果的需求不是默认选项可以满足的，你可以告诉它一些别的东西。在这个例子中，我们想让它显示别的目录，`pypy`。我们通过位置参数的形式将pypy这个目录名称告诉了它。然后程序就知道拿这个名称做什么了。这个概念和命令行`cp`也很像，它的基础用法就是`cp SRC DEST`。第一个位置参数是你想要拷贝的东东，第二个位置参数是你想要拷贝到的地方。
- 有时我们想要改变程序的行为。在我们的例子中，我们显示了每个文件的额外信息，而不单单是它的文件名。这里使用的`-l`叫做选项(optional)参数
- 第４条命令显示了帮助文本的一部分。如果你使用一个你从未使用过的程序，可以通过阅读它的帮助文本来学会怎么使用它。

### The basics(基础)

让我们从一个非常简单的，几乎什么事都没做的示例开始:

```python
import argparse

parser = argparse.ArgumentParser()
parser.parse_args()
```

下面是运行以上代码的结果：

```shell
$ python3 prog.py
$ python3 prog.py --help
usage: prog.py [-h]

optional arguments:
  -h, --help show this help message and exit
$ python3 prog.py --verbose
usage: prog.py [-h]

prog.py:error:unrecognized arguments: --verbose
$ python3 prog.py foo
usage: prog.py [-h]
prog.py: error: unrecognized arguments: foo
```

让我们看看发生了什么:

- 直接运行脚本，没有传入任何选项参数的时候，stdout没有显示任何东东。看起来没什么用。
- 第二个命令开始展示为什么`argparse`模块很实用。我们差不多什么都没做，但是已经有了一个看起来还可以的帮助文本。
- `--help`选项，可以简写为`-h`，这个选项是自带的(不需要我们指定).指定其它的任何选项都会导致错误。但是即使是错误选项，我们也看到它会输出一个很有帮助的文本，让我们知道问题所在。

### Introduce Positional arguments(介绍位置参数)

一个例子:

```python
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('echo')
args=parser.parse_args()
print(args.echo)
```

然后运行这份代码:

```shell
$ python3 prog.py
usage: prog.py [-h] echo
prog.py: error: the following arguments are required: echo
$ python3 prog.py --help
usage: prog.py [-h] echo

positional arguments:
  echo

optional arguments:
  -h, --help show this help and exit
$ python3 prog.py foo
foo
```

让我们看看发生了什么:

- 我们使用了`add_argument()`方法，这个方法用来为程序定义可以接受的命令行选项，我将它命名为`echo`，顾名思义就它的功能就是原样打印。
- 现在调用我们的程序会要求必须指定一个选项。
- `parse_args()`实际上返回的是指定的选项中的数据，在这个例子中，即`echo`.
- 变量`args`是`parse_args()`的返回值。你可能主要到了，它有一个属性名和我们定义的选项名一样，即`echo`

现在，虽然help显示的样子看起来还可以，但它目前并没有帮助我们理清任何东西。比如，我们看到`echo`是一个位置参数，但是我们并不知它能干些什么，只有靠猜和阅读源码才能明白。所以，让我们再加工一下：

```python
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('echo', help='echo the string you use here')
args = parser.parse_args()
print(args.echo)
```

然后，可以看到帮助文本:

```shell
$ python3 prog.py -h
usage: prog.py [-h] echo

positional arguments:
  echo        echo the string you use here

optional arguments:
  -h, --help  show this help message and exit
```

让我们用它来做些更有用的事情：

```python
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('square', help='display a square of a given number')
args = parser.parse_args()
print(args.square**2)
```

下面是运行代码后的结果:

```shell
$ python3 proj.py 4
Traceback (most recent call last):
  File "prog.py", line 5, in <module>
    print(args.square**2)
TypeError: unsupported operand type(s) for ** or pow(): 'str' and 'int'
```

看起来运行不畅。这是因为`argparse`默认会被选项参数当做字符串来对待，除非你明确告诉它类型。所以，让我们告诉`argparse`这个选项是一个整数类型:

```python
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('square', help='display a square of a give number', type=int)
args = parser.parse_args()
print(args.square ** 2)
```

然后运行代码获得结果:

```shell
$ python3 proj.py 4
16
$ python3 prog.py four
usage: prog.py [-h] square
prog.py: error: argument square: invalid int value: 'four'
```

这很好。程序在碰到非法输入时也能告诉你发生了什么，然后再退出.

### Introduce Optional arguments(介绍选项参数)

到目前为止，我们已经知道怎么定义位置参数了，让我们看看怎么加入选项参数:

```python
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--verbosity', help='increase output verbosity')
args = parser.parse_args()
if args.verbosity:
    print("verbosity turned on")
```

输出如下:

```shell
$ python3 proj.py --verbosity 1
verbosity turned on
$ python3 prog.py
$ python3 prog.py --help
usage: prog.py [-h] [--verbosity VERBOSITY]

optional arguments:
  -h, --help            show this help message and exit
  --verbosity VERBOSITY
                        increase output verbosity
$python3 proj.py --verbosity
usage: proj.py [-h] [--verosity VERBOSITY]
proj.py:error:argument --verbosity:expected one argument
```

发生了什么呢:

- 使用`--verbosity`来运行程序会显示一些东西，如果没有这个选项参数则不显示。
- 为了展示这个选项参数是**可选**的，我们可以看到不指定它的时候也不会出现错误信息。注意，默认情况下，如果一个选项参数未被使用，它相对应的属性，比如本例中的`args.verbosity`，将会获得一个`None`作为值，这个值可以让`if`语句判断为否。
- 帮助文本有些不一样。
- 当使用`--verbosity`选项时，必须使用一些值，任何值都可以。

上面例子中的`--verbosity`可以接受任意的整数值，但是对于我们这个简单的例子来说，只需要两个布尔值就够用了，分别是True和False。让我们修改一下代码:

```python
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--verbose', help='increase output verbosity',
                    action='store_true')
args = parser.parse_args()
if args.verbose:
    print("verbosity turned on")                    
```

输出如下:

```shell
$ python3 prog.py --verbose
verbosity turned on
$ python3 prog.py --verbose 1
usage: prog.py [-h] [--verbose]
prog.py: error: unrecognized arguments: 1
$ python3 prog.py --help
usage: prog.py [-h] [--verbose]

optional arguments:
  -h, --help  show this help message and exit
  --verbose   increase output verbosity
```

发生了什么:

- 现在这个选项更像是一个标识(flag)而再必须要求有一个值。我们将参数名称也改了(verbose动词)，更加符合我们的想法。注意我们指定了`action`参数，然后给定它一个值`store_value`。这个动作的意思是，如果指定该选项，将它的`args.verbose`赋为True。否则它的值就是False。
- 在你为这个选项指定值的时候它会抱怨
- 注意帮助文本的不同之处(这个例子没有大写的VERBOSE)

#### Short options(短选项)

如果你属性命令行的用法，你会注意到本教程还没有涉及到短选项。它也很简单:

```python
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-v', '--verbose', help='increase output verbosity',
                    action='store_true')
args = parser.parse_arg()
if args.verbose:
    print("verbosity turned on")
```

下面是结果:

```shell
$ python3 prog.py -v
verbosity turned on
$ python3 prog.py --help
usage: prog.py [-h] [-v]

optional arguments:
  -h, --help     show this help message and exit
  -v, --verbose  increase output verbosity
```

注意短选项也出现在帮助文本中。

### Combining Positional and Optional arguments

程序都是逐渐复杂起来的:

```python
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('square', type=int,
                    help='display a square of a given number')
parser.add_argument('-v', '--verbose', action='store_true',
                    help='increase output verbosity')                    
args = parser.parse_args()
answer = args.sqaure ** 2
if args.verbose:
    print("the square of {} equals {}".format(args.square, answer))                    
else:
    print(answer)
```

输出如下:

```shell
$ python3 prog.py
usage: prog.py [-h] [-v] square
prog.py: error: the following arguments are required: square
$ python3 prog.py 4
16
$ python3 prog.py 4 --verbose
the square of 4 equals 16
$ python3 prog.py --verbose 4
the square of 4 equals 16
```

- 我们又加入了位置参数，所以它不会再抱怨了
- 注意参数的顺序不重要

如果我们想让程序具有多重verbosity等级应该怎么办:

```python
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('sqaure', type=int,
                    help='display a square of a given number')
parser.add_argument('-v', '--verbosity', type=int,
                    help='increase output verbosity')
args = parser.parse_args()
answer = args.square ** 2
if args.verbosity == 2:
    print("the square of {} equals {}".format(args.square, answer))
elif args.verbosity == 1:
    print("{}^2 == {}".format(args.square, answer))
else:
    print(answer)
```

输出如下:

```shell
$ python3 prog.py 4
16
$ python3 prog.py 4 -v
usage: prog.py [-h] [-v VERBOSITY] square
prog.py: error: argument -v/--verbosity: expected one argument
$ python3 prog.py 4 -v 1
4^2 == 16
$ python3 prog.py 4 -v 2
the square of 4 equals 16
$ python3 prog.py 4 -v 3
16
```

看起来不错，除了最后必须要输入的哪个verbose值，我们为自己的程序暴露了一个bug。我们应该限制`--verbosity`可以接受的值：

```python
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('sqaure', type=int,
                    help='display a square of a given number')
parser.add_argument('-v', '--verbosity', type=int, choices=[0, 1, 2],
                    help='increase output verbosisty')                    
args = parser.parse_args()
answer = args.square ** 2
if args.verbosity == 2:
    print("the square of {} equals {}".format(args.square, answer))
elif args.verbosity == 1:
    print("{}^2 == {}".format(args.square, answer))
else:
    print(answer)           
```

输出如下:

```shell
$ python3 prog.py 4 -v 3
usage: prog.py [-h] [-v {0,1,2}] square
prog.py: error: argument -v/--verbosity: invalid choice: 3 (choose from 0, 1, 2)
$ python3 prog.py 4 -h
usage: prog.py [-h] [-v {0,1,2}] square

positional arguments:
  square                display a square of a given number

optional arguments:
  -h, --help            show this help message and exit
  -v {0,1,2}, --verbosity {0,1,2}
                        increase output verbosity
```

注意我们的改动同样会映射到错误信息和帮助文本中。

让我们使用一个新方式来使用verbosity，这种方式也相当常见。这个方式甚至是CPython处理自己的verbosity参数(请看`python --help`):

```python
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('square', type=int,
                    help='display the square of a give number')
parser.add_argument('-v', '--verbosity', action='count',
                    help='increase output verbosity')                    
args = parser.parse_args()
answer = args.square**2
if args.verbosity == 2:
    print("the square of {} equals {}".format(args.square, answer))
elif args.verbosity == 1:
    print("{}^2 == {}".format(args.square, answer))
else:
    print(answer)                    
```

我们引进了另一个动作,"count"，可以计数一个特定选项参数出现的次数:

```shell
$ python3 prog.py 4
16
$ python3 prog.py 4 -v
4^2 == 16
$ python3 prog.py 4 -vv
the square of 4 equals 16
$ python3 prog.py 4 --verbosity --verbosity
the square of 4 equals 16
$ python3 prog.py 4 -v 1
usage: prog.py [-h] [-v] square
prog.py: error: unrecognized arguments: 1
$ python3 prog.py 4 -h
usage: prog.py [-h] [-v] square

positional arguments:
  square           display a square of a given number

optional arguments:
  -h, --help       show this help message and exit
  -v, --verbosity  increase output verbosity
$ python3 prog.py 4 -vvv
16
```

- 现在这个选项并不仅是一个flag了
- 它的行为仍然类似`store_action`
- 然后我们介绍了`count`动作的用法，你可能以前见过
- 如果你没有指定`-v`选项，它的值将会保持为`None`.
- 无论输入长选项还是短选项，结果一样
- 不过遗憾的是，我们的帮助文本没有包含这种新用法，你需要通过`help`参数自己提供帮助文本
- 最后的输出算我们程序的一个bug

让我们修复这个bug:

```python
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("square", type=int,
                    help="display a square of a given number")
parser.add_argument("-v", "--verbosity", action="count",
                    help="increase output verbosity")
args = parser.parse_args()
answer = args.square**2

# bugfix: replace == with >=
if args.verbosity >= 2:
    print("the square of {} equals {}".format(args.square, answer))
elif args.verbosity >= 1:
    print("{}^2 == {}".format(args.square, answer))
else:
    print(answer)
```

输出如下:

```shell
$ python3 prog.py 4 -vvv
the square of 4 equals 16
$ python3 prog.py 4 -vvvv
the square of 4 equals 16
$ python3 prog.py 4
Traceback (most recent call last):
  File "prog.py", line 11, in <module>
    if args.verbosity >= 2:
TypeError: '>=' not supported between instances of 'NoneType' and 'int'
```

- 第一个输出看起来不错，修复了我们之前的bug
- 第三个输出出现了问题，看来我们引入了新的bug

让我们来修复这个bug:

```python
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("square", type=int,
                    help="display a square of a given number")
parser.add_argument("-v", "--verbosity", action="count", default=0,
                    help="increase output verbosity")
args = parser.parse_args()
answer = args.square**2
if args.verbosity >= 2:
    print("the square of {} equals {}".format(args.square, answer))
elif args.verbosity >= 1:
    print("{}^2 == {}".format(args.square, answer))
else:
    print(answer)
```

我们只不过引入了一个新的关键字参数,`default`，就解决了我们的问题。

输出:

```shell
$ python3 prog.py 4
16
```

你学的很快，因为我们现在只是初略皮毛。`argparse`模块非常强大，在结束这篇教程之前我们可以看看它的高级用法。


### Getting a little more advanced

如果我们想要程序做点别的呢:

```python
import argparse

parser = argument.ArgumentParser()
parser.add_argument('x', type=int, help='the base')
parser.add_argument('y', type=int, help='the exponent')
parser.add_argument("-v", "--verbosity", action="count", default=0)
args = parser.parse_args()
answer = args.x ** args.y
if args.verbosity >= 2:
    print("{} to the power {} equals {}".format(args.x, args.y, answer))
elif args.verbosity >= 1:
    print("{}^{} == {}".format(args.x, args.y, answer))
else:
    print(answer)
```

输出如下:

```shell
$ python3 prog.py
usage: prog.py [-h] [-v] x y
prog.py: error: the following arguments are required: x, y
$ python3 prog.py -h
usage: prog.py [-h] [-v] x y

positional arguments:
  x                the base
  y                the exponent

optional arguments:
  -h, --help       show this help message and exit
  -v, --verbosity
$ python3 prog.py 4 2 -v
4^2 == 16
```

目前位置我们使用verbosity来修改显示的文本。下面的例子换了种方式，它使用verbosity来显示更多的文本:

```python
import argparse

parser = argument.ArgumentParser()
parser.add_argument('x', type=int, help='the base')
parser.add_argument('y', type=int, help='the exponent')
parser.add_argument("-v", "--verbosity", action="count", default=0)
args = parser.parse_args()
answer = args.x ** args.y
if args.verbosity >= 2:
    print("Running '{}'".format(__file__))
if args.verbosity >= 1:
    print("{}^{} == {}".format(args.x, args.y, answer))
else:
    print(answer)
```

输出如下:

```shell
$ python3 prog.py 4 2
16
$ python3 prog.py 4 2 -v
4^2 == 16
$ python3 prog.py 4 2 -vv
Running 'prog.py'
4^2 == 16
```

#### Conflicting options(冲突选项)

迄今为止，我们只使用了`argparse.ArgumentParser`实例的两个方法。让我们引入第三个方法，`add_mutually_exclusive_group()`.它可以引入可以和其它选项冲突的选项：

```python
import argparse

parser = argparse.ArgumentParser()
group = parser.add_mutually_exclusive_group()
group.add_argument('-v', '--verbose', action='store_true')
group.add_argument('-q', '--quie', action='store_true')
parser.add_argument('x', type=int, help='the base')
parsre.add_argument('y', type=int, help='the exponent')
args = parser.parse_args()
answer = args.x ** args.y

if args.quiet:
    print(answer)
elif args.verbose:
    print("{} to the power {} equals {}".format(args.x, args.y, answer))
else:
    print("{}^{} == {}".format(args.x, args.y, answer))
```

为了简单我们没有使用`count`动作的verbose.输出如下：

```shell
$ python3 prog.py 4 2
4^2 == 16
$ python3 prog.py 4 2 -q
16
$ python3 prog.py 4 2 -v
4 to the power 2 equals 16
$ python3 prog.py 4 2 -vq
usage: prog.py [-h] [-v | -q] x y
prog.py: error: argument -q/--quiet: not allowed with argument -v/--verbose
$ python3 prog.py 4 2 -v --quiet
usage: prog.py [-h] [-v | -q] x y
prog.py: error: argument -q/--quiet: not allowed with argument -v/--verbose
```

我们注意到,`-q`和`-v`在一个可变独占组(`mutually_exclusive_group`)中，所以只能选择它们中的一个.

你可能想要告诉用户你的程序主要用途是什么：

```python
import argparse

parser = argparse.ArgumentParser(description="calculate X to the power of Y")
group = parser.add_mutually_exclusive_group()
group.add_argument("-v", "--verbose", action="store_true")
group.add_argument("-q", "--quiet", action="store_true")
parser.add_argument("x", type=int, help="the base")
parser.add_argument("y", type=int, help="the exponent")
args = parser.parse_args()
answer = args.x**args.y

if args.quiet:
    print(answer)
elif args.verbose:
    print("{} to the power {} equals {}".format(args.x, args.y, answer))
else:
    print("{}^{} == {}".format(args.x, args.y, answer))
```

现在`description`的内容会出现在帮助文本中。

另外值得注意的是`[-v | -q]`，意思是你只可以选择它们中的一个:

```shell
$ python3 prog.py --help
usage: prog.py [-h] [-v | -q] x y

calculate X to the power of Y

positional arguments:
  x              the base
  y              the exponent

optional arguments:
  -h, --help     show this help message and exit
  -v, --verbose
  -q, --quiet
```

### Conclusion(结尾)

`argparse`模块还有很多功能因为时间的关系没有讲到。它的文档非常详细和周密，有很多的例子。学完这篇教程以后，让你可以慢慢消化文档，而不会感觉崩溃。

