# Commands and Groups

Click最重要的特性就是它的命令行任意嵌套的概念。这是通过`Command`和`Group`(实际上是`MultiCommand`)来实现的.

## Callback Invocation

对于一个常规的命令，callback在运行命令的时候被执行。如果脚本只有这个命令，它会立即启动。

对于group和multi命令，情况有些不同。在这种情况下，callback在子命令运行的时候执行。也就是说外层命令在内层命令执行的时候才会执行。

```python
@click.group()
@click.option('--debug/--no-debug', default=False)
def cli(debug):
    click.echo('Debug mode is %s' %('on' if debuf else 'off'))


@cli.command()
def sync():
    click.echo('Synching.')
```

命令行如下：

```shell
$ tool.py
Usage: tool.py [OPTIONS] COMMAND [ARGS]...

Options:
  --debug / --no-debug
  --help                Show this message and exit.

Commands:
  sync

$ tool.py --debug sync
Debug mode is on
Synching
```

## Passing Parameters

Click严格区分命令和子命令的参数。也就是说一个特定命令的options和arguments都会定义在一个单独的命名空间内。

这个行为可以通过`--help`看到。假设你有一个程序叫做`tool.py`，包含子命令`sub`.

- `tool.py --help`: 将会返回整个程序的帮助文本(列出子命令)。
- `tool.py sub --help`: 将会返回`sub`子命令的帮助文本。
- `tool.py --help sub`: 将会把`--help`看作是主程序的一个参数。Click然后会调用`--help`的回调，打印帮助文本并退出，不会在处理子命令`sub`

## Nested Handing and Contexts

你可以从之前的例子看到，基础命令组接受一个`debug`参数并传给它的callback，而不是`sync`命令。`sync`命令只可以接受它自己的参数。

这让tools各自之间完全独立，但是如何让命令之间通讯呢？答案是使用`Context`.

每次一个命令被调用的时候，都会创建一个新的context并且会与父命令的context相关联。一般来说，你看不到这些contexts，但是它们就在那里。context将会和value以前传给参数的callback。Commands也可以要求context传给它(需要装饰`@pass_context`)，然后context会以第一个位置参数的形式传入。

```python
@click.group()
@click.option('--debug/--no-debug', default=False)
@click.pass_context
def cli(ctx, debug):
    ctx.obj['DEBUG'] = debug


@cli.command()
@click.pass_context
def sync(ctx):
    click.echo("Debug is %s" % (ctx.obj['DEBUG'] and 'on' or 'off'))


if __name__ == '__main__':
    cli(obj={})
```

如果提供了这个obj，每个context都会把这个obj传给它的子命令，但是这个context的obj可以被覆盖。想要获取父命令的context，可以使用`context.parent`.

另外，你可以直接使用全局变量。

## Decorating Commands

你在上面的例子可以看到，一个装饰器可以决定一个命令如何被调用。那么在幕后究竟发生了什么，为什么调用`Context.invoke()`方法会自动调用正确的命令。

如果你想要编写自定义装饰器的话这很有用。例如，一个常见的情况是配置一个代表状态的对象，将它存储到context中，然后使用自定义装饰器来找到最近的这个对象。

例如，`pass_obj()`装饰器：

```python
from functools import update_wrapper


def pass_obj(f):
    @click.pass_context
    def new_func(ctx, *args, **kwargs):
        return ctx.invoke(f, ctx.obj, *args, **kwargs)
    return update_wrapper(new_func, f)
```

## Group Invocation Without Command

默认情况下，一个group或者一个multi命令是不会直接调用的，除非传入了子命令。可以通过传入`invoke_without_command=True`来修改这个默认行为。在这种情况下，callback总是会被调用。context对象包含是否调用的信息。

```python
@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    if ctx.invoked_subcommand is None:
        click.echo('I was invoked without subcommand')
    else:
        click.echo('I am about to invoke %s ' %(ctx.invoked_subcommand))


@click.command()
def sync():
    click.echo('The subcommand')
```

命令行：

```shell
$ tool
I was invoked without subcommand
$ tool sync
I am about to invoke sync
The subcommand
```

## Custom Multi Commands

除了使用`click.group()`，你也可以创建自定义的multi命令。

```python
import click
import os

plugin_folder = os.path.join(os.path.dirname(__file__), 'commmannds')


class MyCLI(click.MultiCommand):
    rv = []
    for filename in os.listdir(plugin_folder):
        if filename.endswith('.py'):
            rv.append(filename[:-3])
    rv.sort()
    return rv


def get_command(self, ctx, name):
    ns = {}
    fn = os.path.join(plugin_folder, name + '.py')
    with open(fn) as f:
        code = complie(f.read(), fn, 'exec')
        eval(code, ns, ns)
    return ns['cli']

cli = MyCLI(
    help='This tool\'s subcommand are loaded from a plugin folder dynamically.'
)

if __name__ == '__main__':
    cli()   
```

也可以这么用：

```python
@click.command(cls=MyCLI)
def cli():
    pass
```

## Merging Multi Commmands

除了实现自定义multi命令，也可以把多个multi命令合并到一个脚本中。

合并系统的默认实现叫做`CommandCollection`类。它接受多个multi命令参数的列表。

例子:

```python
import click


@click.group()
def cli1():
    pass


@cli1.command()
def cmd1():
    pass


@click.group()
def cli2():
    pass


@cli2.command()
def cmd2():
    pass


cli = click.CommandCollection(sources=[cl1, cl2])


if __name__ == '__main__':
    cli()
```

命令行输出:

```shell
$ cli --help
Usage: cli [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  cmd1  Command on cli1
  cmd2  Command on cli2
```

## Multi Command Chaining

有时想要调用多个子命令。比如你安装一个package之前需要熟悉`setup.py`的`sdist`、`bdist_wheel`上传命令链。在multi command传入`chain=True`即可实现。

```python
@click.group(chain=True)
def cli():
    pass


@cli.command('sdist')
def sdist():
    click.echo('sdist called')


@cli.command('bdist_wheel')
def bdist_wheel():
    click.echo('bdist_wheel called')
```

现在你可以这么来调用:

```shell
$ setup.py sdist bdist_wheel
sdist called
bdist_wheel called
```

## Multi Command Pipelines

multi命令的常见使用场景是后者使用前者的输出。有很多方式可以实现，比如可以通过装饰`@pass_context()`来实现输出的存储转移。

另一个方式是使用管道符号。

一个函数的返回将会导向哪里？链接的multi命令可以通过`MultiCommand.resultcallback()`注册一个callback。

```python
@click.group(chain=True, invoke_without_command=True)
@click.option('-i', '--input', type=click.File('r'))
def cli(input):
    pass


@cli.resultcallback()
def process_pipeline(processors, input):
    iterator = (x.rstrip('\r\n') for x in input)
    for processor in processors:
        iterator = processor(iterator)
    for item in iterator:
        click.echo(item)


@cli.command('uppercase')
def make_uppercase():
    def process(iterator):
        for line in iterator:
            yield line.upper()
    return processor


@cli.command('lowercase')
def make_lowercase():
    def processor(iterator):
        for line in iterator:
            yield line.lower()
    return processor


@cli.command('strip')
def make_strip():
    def processor(iterator):
        for line in iterator:
            yield line.strip()
    return processor
```

让我们一条一条来梳理：

1. 首先是让`group()`变成可以链接的(传入`chain=True`)。另外我们指定即使没有定义子命令，这个callback也总是会被调用(传入`invoke_without_command=True`)。如果不这么做，那么调用一个空的pipeline就会生成帮助文本，而不是运行result callback。

2. 第二件事就是为我们的group注册一个result callback。这个callback会传入一个参数，它代表所有子命令返回的值(`processes`)。另外还会传入一个和group同名的关键字参数，即`input`，这意味着我们可以在不使用context对象的情况下，很轻松的访问这个文件对象。

3. 在result callback中，我们将input文件的所有行来创建了一个迭代器，然后将它传入所有子命令返回的processor并打印最终的值。

我们可以使用这种方式创建任意数量的子命令，每个子命令返回一个`processor`函数用来修改原始值。

## Overrding Defaults

默认情况下，一个参数的默认值是通过命令行参数定义时的`default`参数指定的，但是这并不是唯一的默认值读取方式。另一个方式是使用context的`Context.default_map`。它允许从一个配置文件来读取默认值并覆盖常规的默认值。

比如你使用第三方package但是不满意它的默认值，可以使用这个方法。

默认的map可以任意的嵌套来满足每个子命令。另外它属于默认值读取的最上层级(会覆盖其它所有定义).

```python
import click


@click.group()
def cli():
    pass


@cli.command()
@click.option('--port', default=8000)
def run_server(port):
    click.echo('Serving on http://127.0.0.1:%d' % port)


if __name__ == '__main__':
    cli(default_map={
        'runserver': {
            'port': 5000
        }
    })
```

命令行:

```shell
$ cli runserver
Serving on http://127.0.0.1:5000/
```

## Context Defaults

从Click2.0开始，你可以覆盖context的默认值了。比如之前使用`default_map`的例子可以这样改写。

```python
import click


CONTEXT_SETTINGS = dict(
    default_map={
        'run_server': {
            'port': 5000
        }
    }
)


@click.group(context_settings=CONTEXT_SETTINGS)
def cli():
    pass


@cli.command()
@click.option('--port', default=8000)
def runserver(port):
    click.echo('Serving on http://127.0.0.1:%d/' % port)


if __name__ == '__main__':
    cli()
```

命令行:

```shell
$ cli runserver
Serving on http://127.0.0.1:5000/
```

## Command Return Values

Click3.0的一个重要特性就是它完全支持命令callback返回的值。

任何命令的callback都可以返回值。这个返回值会向上冒泡给特定的接收者。比如之前**Multi Command Chaining**的例子使用了子命令返回的processor。

在使用Click的callback返回值特性时，你需要知道这些：

- 一个命令callback的返回值本质上是由`BaseCommand.invoke()`方法返回的。例外情况是`Group`:

    - 一个Group返回的值通常是它的子命令返回的值。不过如果设定了`invoke_without_command`的话，也可能是这个group的callback本身返回的值。

    - 如果一个Group设置为Chain，那么它的返回值就是一个list，包含所有子命令的结果。

    - Gruop返回的值可以通过一个`MultiCommand.result_callback`来处理。

- 返回值通过`Context.invoke()`和`Context.forward()`来冒泡传递。

- Click并不要求一定要使用命令callback的返回值。

- 当一个Click脚本以命令行形式调用时(通过`BaseCommand.main()`)，那么返回的值会被忽略。除非你关闭了`standalone_mode`设定，这种情况下冒泡将会继续.


