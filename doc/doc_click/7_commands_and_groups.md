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

pass