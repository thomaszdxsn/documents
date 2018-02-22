# Quickstart

你可以从pypi直接下载安装这个库：

`$ pip install click`

## virtualenv

pass

## Screencast and Examples

有一个录屏教学，通过创建一个简单的应用来告诉你怎么使用Click的基本API:

- [通过Click来创建一个命令行接口应用](https://www.youtube.com/watch?v=kNke39OZ2k0)

下面是一些Click应用的例子：

- [文件输入和输出](https://github.com/mitsuhiko/click/tree/master/examples/inout)
- [docopt的port例子](https://github.com/mitsuhiko/click/tree/master/examples/naval)
- [command alias例子](https://github.com/mitsuhiko/click/tree/master/examples/aliases)
- [类Git/Mercurial命令行接口的一个例子](https://github.com/mitsuhiko/click/tree/master/examples/repo)
- [插件载入的复杂例子](https://github.com/mitsuhiko/click/tree/master/examples/complex)
- [自定义参数验证的例子](https://github.com/mitsuhiko/click/tree/master/examples/validation)
- [ANSI颜色的支持](https://github.com/mitsuhiko/click/tree/master/examples/colors)
- [终端UI的函数demo](https://github.com/mitsuhiko/click/tree/master/examples/termui)
- [多命令链接demo](https://github.com/mitsuhiko/click/tree/master/examples/imagepipe)

## Basic concepts

Click基于装饰器来声明命令。另外，在一些复杂的请看可以使用非装饰器方法。

一个函数通过`@click.command()`装饰以后就变成了一个Click命令。最简单的情况是，将一个函数使用这个装饰器装饰后会变为一个可调用的脚本：

```python
import click

@click.command()
def hello():
    click.echo('Hello World!')

# 然后你可以这样调用它
if __name__ == '__main__':
    hello()
```

输出如下：

```shell
$ python hello.py
Hello World!
```

帮助文本：

```shell
$ python hello.py --help
Usage: hello.py [OPTIONS]

Options:
  --help  Show this message and exit.
```

## Echoing

为什么上面的例子使用`echo()`来代替`print()`？因为Click想要同时支持Python2/3而不用你另外加一些配置。

另外作为福利，从Click2.0开始，echo函数同样支持ANSI color。如果输出流是一个文件它会自动去除ANSI代码。

如果你不需要这些特性，当然也可以使用`print()`...

## Nesting Commands

命令可以依附与其它类似为`Group`的命令。这可以允许任意嵌套的脚本。例如下面是一个脚本，实现了管理数据库的两种命令：

```python
@click.group()
def cli():
    pass


@click.command()
def initdb():
    click.echo('Initialized the database')
    

@click.command()
def dropdb():
    click.echo('Dropped the database')

cli.add_command(initdb)
cli.add_command(dropdb)
```

你可以看到`group()`装饰器和`command()`使用方法一样，但是会创建一个`Group`对象，它具有`.add_command()`方法。

另外，你可以直接使用`Group.command()`命令来替代。上面的脚本可以这样重写：

```python
import click


@click.group()
def cli():
    pass


@cli.command()
def initdb():
    print("initdb")


@cli.command()
def dropdb():
    print("dropdb")
```

## Adding Parameters

想要加入参数，可以使用`option()`和`argument()`装饰器:

```python
import click


@click.command()
@click.option('--count', default=1, help='number of greetings')
@click.argument('name')
def hello(count, name):
    for x in range(count):
        click.echo("Hello %s" % name)
```

它的帮助文本为:

```shell
$ python hello.py --help
Usage: hello.py [OPTIONS] NAME

Options:
  --count INTEGER  number of greetings
  --help           Show this message and exit.
```

## Switching to setuptools

迄今为止你编写的脚本都以`if __name__ == '__main__'`来结尾：这是独立Python脚本运行的标准方式。Click也可以这么写，不过它可以通过setuptools达到更好的效果。

两个主要的原因：

- 首先，setuptools会自动生成可以在Windows执行的封装，所以你的命令也可以在Windows执行。

- 其次，setuptools的脚本如果依赖Unix下的virtualenv，可以在这个虚拟环境没有激活的情况下执行。



