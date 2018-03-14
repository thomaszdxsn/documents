# Options

为命令加入options可以通过`@option()`来实现。因为options可以有很多不同的版本，所以参数的配置组合加起来无穷无尽。Click中的options和位置参数有所不同。

## Basic Value Options

最基础的option是值option。这些options接受一个参数作为它的值。如果没有设置type，那么会使用默认值的type。如果没有提供默认只，那么会使用`STRING`。默认情况下，参数的名称会使用碰到的第一个定义的长option；否则使用第一个定义的短option。

```python
@click.command()
@click.option('--n', default=1)
def dots(n):
    click.echo('.' * n)
```

命令行使用:

```shell
$ dots --n=2
..
```

因为默认值是一个整数，所以使用`INT`类型。

## Multi Value Options

有时，你的options接受多个参数。对于options来说，只支持固定数量的参数。可以通过`nargs`来指定，然后这些值会以一个元组来存储。

```python
@click.command()
@click.option('--pos', nargs=2, type=float)
def findme(pos):
    click.echo('%s / %s' % pos)
```

命令行中的使用:

```shell
$ findme --pos 2.0 3.0
2.0 / 3.0
```

## Tuples as Multi Value Options

有时你想要对元组中不同索引的值使用不同的类型。你可以直接对type指定一个元组：

```python
@click.command()
@click.option('--item', type=(unicode, int))
def putitem(item):
    click.echo('name=%s id=%d' % item)
```

命令行中使用：

```shell
$ putitem --item peter 1338
name=peter id=1338
```

上面的代码可以重写成下面这样，可以使用`Tuple`类型：

```python
@click.command()
@click.option('--item', nargs=2, type=click.Tuple([unicode, int]))
def putitem(item):
    click.echo('name=%s id=%d' % item)
```

## Multiple Options

除了nargs，还可以多次传入一个option。例如，`git commit -m foo -m bar`将会把记录两行到最终的commit message中。在click中可以使用`@option`中的`multiple`flag参数：

```python
@click.command()
@click.option('--message', '-m', multiple=True)
def commit(message):
    click.echo('\n'.join(message))
```

命令行中使用:

```shell
$ commit -m foo -m bar
foo
bar
```

## Counting

在一些罕见的情况下，有使用重复options当作计数的情况。比如verbosity flag：

```python
@click.command()
@click.option('-v', '--verbosity', count=True)
def log(verbose):
    click.echo('verbosity: %s' % verbose)
```

命令行的使用：

```shell
log -vvv
verbosity: 3
```

## Boolean Flags

option可以用作boolean flag。可以定义两个flag，以一个斜杠`/`来分隔。

```python
import sys


@click.command()
@click.option('--shout/--no-shout', default=False)
def info(shout):
    rv = sys.platform
    if shout:
        rv = rv.upper() + '!!!!111'
    click.echo(rv)
```

命令行:

```shell
$ info --shout
LINUX2!!!!111
$ info --no-shout
linux2
```

如果你不想对这个flag进行开关操作，你可以只定义一个flag，然后手动告诉Click这是一个flag：

```python
import sys


@click.command()
@click.option('--shout', is_flag=True)
def info(shout):
    rv = sys.platform
    if shout:
        rv = rv.upper() + '!!!!111'
    click.echo(rv)
```

命令行：

```shell
$ info --shout
LINUX2!!!!111
```

注意如果斜杠已经包含在你的option中，你可以使用`;`来分隔两个flag：

```python
@click.command()
@click.option('/debug;/no-debug')
def log(debug):
    click.echo('debug=%s' % debug)


if __name__ == '__main__':
    log()
```

## Feature Switches

除了boolean flags，还有feature switches。可以将多个option设置为同一个名称并定义个flag值。注意，使用`flag_value`参数之后，Click将会默认添加`is_flag=True`.

```python
import sys


@click.command()
@click.option('--upper', 'transformation', flag_value='upper',
              default=True)
@click.option('--lower', 'transformation', flag_value='lower')
def info(transformation):
    click.echo(getattr(sys.platfrom, trasformation)())
```

命令行如下：

```shell
$ info --upper
LINUX2
$ info --lower
linux2
$ info
LINUX2
```

## Choice Options

有时，你想要参数必须从一个list中选择一个值。在这种情况你需要使用`Choice`类型：

```python
@click.command()
@click.option('--hash-type', type=click.Choice(['md5', 'sha1']))
def digest(hash_type):
    click.echo(hash_type)
```

怎么用呢？

```shell
$ digest --hash-type=md5
md5

$ digest --hash-type=foo
Usage: digest [OPTIONS]

Error: Invalid value for "--hash-type": invalid choice: foo. (choose from md5, sha1)

$ digest --help
Usage: digest [OPTIONS]

Options:
  --hash-type [md5|sha1]
  --help                  Show this message and exit.
```

## Prompting

有时候，你需要参数由命令行来提供，但是如果没有提供，那么就要求用户输入。

```python
@click.command()
@click.option('--name', prompt=True)
def hello(name):
    click.echo('Hello %s!' % name)
```

命令行：

```shell
$ hello --name=John
Hello John!
$ hello
Name: John
Hello John!
```

如果你不想要默认的提示文本，你可以自定义一个文本：

```python
@click.command()
@click.option('--name', prompt='Your name please')
def hello(name):
    click.echo('Hello %s!' % name)
```

命令行：

```shell
$ hello
Your name please: John
Hello John!
```

## Password Prompts

Click支持Unix类型的密码输入：

```python
@click.command()
@click.option('--password', prompt=True, hidden_input=True,
              confirmation_prompt=True)
def encrypt(password):
    click.echo('Encrypting password to %s' % password.encode('rot13'))
```

命令行：

```shell
$ encrypt
Password: 
Repeat for confirmation: 
Encrypting password to frperg
```

因为这种组合很常用，所以另外提供了一个装饰器来专门提供该功能：

```python
@click.command()
@click.password_option()
def encrypt(password):
    click.echo('Encrypting password to %s' %password.encode('rot13'))
```

## Dynamic Defaults for Prompts

`auto_envvar_prefix`和`default_map`options允许程序从环境变量或者配置文件中读取option。不过，它会覆盖prompting机制，所以用户不能改为交互式输入了。

如果你允许用户配置默认值，但是如果没有配置的时候仍然提示用户输入，你可以传入一个callable作为默认值。比如，获取一个环境变量作为默认值：

```python
@click.command()
@click.option('--username', prompt=True,
              default=lambda: os.environ.get('USER', ''))
def hello(username):
    print('Hello, ', username)
```

## Callbacks and Eager Options

有时，你想要让一个参数能够完全的改变执行流。例如，你可能需要一个`--version`参数，它会打印版本信息然后退出应用。

注意：`--version`参数实际可以通过`@click.version_option()`来实现。

在这种情况，你首先需要明白两个概念：eager参数和callback。eager参数是优先处理的参数，callback是这个参数处理后调用的对象。必须让这个参数eager，所以不会在处理其它参数的时候报错。

callback是一个函数，它以两个参数来调用：当前的`Context`和这个参数值。context对象提供了一些有用的功能，比如退出应用或者能够访问其它参数。

下面是实现`--version` flag的一个示例:

```python
def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo('Version 1.0')
    ctx.exit()


@click.command()
@click.option('--version', is_flag=True, callback=print_version,
              expose_value=False, is_eager=True)
def hello():
    click.echo('Hello World!')
```

参数`expose_value`会预防无用的version参数传入到callback中。如果没有指定这个参数，将会把一个布尔值传入到*hello*脚本。context的`resilient_parsing`flag代表不会对执行流有毁坏性的行为。

下面是使用例子：

```shell
$ hello
Hello World!
$ hello --version
Version 1.0
```

## Yes Parameters

对于危险的操作，有必要让用户进行确认操作。可以加入一个`--yes`flag来征询用户的确认意见：

```python
def abort_if_false(ctx, param, value):
    if not value:
        ctx.abort()
        

@click.command()
@click.option('--yes', is_flag=True, callback=abort_if_false,
              expose_value=False,
              prompt='Are you sure you want to drop the db?')
def dropdb():
    click.echo('Dropped all tables')
```

因为这个组合很常见，所以出于方便提供了一个装饰器`@confirmation_option()`:

```python
@click.command()
@click.confirmation_prompt(help='Are you sure you want to drop the db?')
def dropdb():
    click.echo('Dropped all tables!')
```

## Values from Environment Variables

Click的一个有用的特性就是可以接受环境变量作为参数。这让工具的自动化变得更加简单。例如，你可能想要以`--config hello.cfg`传入一个配置文件，不过也支持使用环境变量`TOOL_CONFIG=hello.cfg`.

Click有两种方式可以支持这种特性。比如可以自动接受环境变量，不过只有options支持。想要支持这个特性，需要在这个脚本传入`auto_envvar_prefix`参数。每个命令和参数都会以大写，下划线分隔的变量形式加入。如果你有一个子命令，有用一个option叫做`bar`，它的前缀为`MY_TOOL`，那么这个环境变量就是`MY_TOOL_FOO_BAR`.

使用例子：

```python
@click.command()
@click.option('--username')
def greet(username):
    click.echo('Hello %s' % username)


if __name__ == '__main__':
    greet(auto_envvar_prefix='GREETER')
```

命令行使用：

```shell
$ export GREETER_USERNAME=john
$ greet
Hello john!
```

**第二种方式**是在option中手动指定它可以接受环境变量，通过参数`envvar`来实现：

```python
@click.command()
@click.option('--username', envvar='USERNAME')
def greet(username):
    click.echo('Hello %s!' % username)


if __name__ == '__main__':
    greet()
```

命令行如下：

```shell
$ export USERNAME=john
$ greet
Hello john!
```

## Multiple Values from Environment Values

options可以接受多个值，但是如果想要从环境变量拉取多个值则复杂的多。环境变量如果要代表多个值，在类Unix系统需要以`:`分隔，在Windos需要以`;`分隔.

例如:

```python
@click.command()
@click.option('paths', '--path', envvar='PATHS', multiple=True,
              type=click.Path())
def perform(paths):
    for path in paths:
        click.echo(path)


if __name__ == '__main__':
    perform()
```

命令行如下：

```shell
$ export PATHS=./foo/bar:./test
$ perfom
./foo/bar
./test
```

## Other Prefix Characters

Click除了`-`以外还支持其它的前缀字符。

```python
@click.command()
@click.option('+w/-w')
def chmod(w):
    click.echo('writable=%s' %w)


if __name__ == '__main__':
    chmod()
```

命令行使用:

```shell
$ chmod +w
writable=True
$ chmod -w
writable=False
```

`/`前缀：

```python
@click.command()
@click.option('/debug;/no-debug')
def log(debug):
    click.echo('debug=%s' % debug)

if __name__ == '__main__':
    log()
```

## Range Options

例子：

```python
@click.command()
@click.option('--count', type=click.IntRange(0, 20, clmap=True)) # clamp代表最多两倍最大值
@click.option('--digit', type=click.IntRange(0, 10))
def repeat(count, digit):
    click.echo(str(digit) * count)


if __name__ == '__main__':
    repeat()
```

示例例子：

```shell
$ repeat --count=1000 --digit=5
55555555555555555555
$ repeat --count=1000 --digit=12
Usage: repeat [OPTIONS]

Error: Invalid value for "--digit": 12 is not in the valid range of 0 to 10.
```

## Callbacks for Validation

如果你想要加入自己的验证逻辑，你可以通过参数的callback来实现。

例子：

```python
def validate_rolls(ctx, param, value):
    try:
        rolls, dice = map(int, value.split('d', 2))
        return (dice, rolls)
    except ValueError:
        raise click.BadParameter('rolls need to be in format NdM')


@click.command()
@click.option('--rolls', callback=validate_rolls, default='1d6')
def roll(rolls):
    click.echo('Rolling a %d-sided dice %d time(s)' % rolls)


if __name__ == '__main__':
    roll()
```

命令行如下：

```shell
$ roll --rolls=42
Usage: roll [OPTIONS]

Error: Invalid value for "--rolls": rolls need to be in format NdM

$ roll --rolls=2d12
Rolling a 12-sided dice 2 time(s)
```
