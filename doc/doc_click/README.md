# CLick

Click是一个Python的软件包，可以使用尽量少的代码来创建优美的命令行接口。它是一个“创建命令行接口的工具”。它是可以高度配置化的，但是也能按需直接使用。

它的目标是让命令行接口的编写更加快速和有趣。

Click有三个要点：

- 能够让命令嵌套
- 自动化生成help页面
- 在运行时支持惰性载入子命令

那么它看起来是怎么样的呢？下面是一个简单的Click程序:

```python
import click

@click.command()
@click.option('--count', default=1, help='Number of greetings.')
@click.option('--name', promp='Your name',
              help='The person to greet.')
def hello(count, name):
    """Simple program that greets NAME for a total of COUNT times."""
    for x in range(count):
        click.echo("Hello %s!" % name)


if __name__ == '__main__':
    hello()
```

你将会看到如何运行它:

```shell
$ python hello.py --count=3
Your name: John
Hello John!
Hello John!
Hello John!
```

而且它会自动生成帮助文本:

```shell
$ python hello.py --help
Usage: hello.py [OPTIONS]

  Simple program that greets NAME for a total of COUNT times.

Options:
  --count INTEGER  Number of greetings.
  --name TEXT      The person to greet.
  --help           Show this message and exit.
```

你可以从pypi直接下载安装Click:

`$ pip install click`

