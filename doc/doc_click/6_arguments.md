# Arguments

Arguments和options类似，不过它是位置参数。它只支持options的部分特性。Click不会为arguments自动添加帮助文本，你需要手动添加。

## Basic Arguments

最基础的argument是一个简单的字符串参数。如果没有提供type，那么使用默认值的类型，如果没有指定默认值，那么使用STRING：

```python
@click.command()
@click.argument('filename')
def touch(filename):
    click.echo(filename)
```

结果如下：

```shell
$ touch foo.txt
foo.txt
```

## Variadic Arguments

Arguments第二个常见的特性是可以接受任意数量的参数。可以通过`nargs`来控制。如果传入`-1`那么就不会限制参数的数量。

如果多于1个参数，那么这个参数将会以tuple的形式存在。

```python
@click.command()
@click.argument('src', nargs=-1)
@click.argument('dst', nargs=1)
def copy(src, dst):
    for fn in src:
        click.echo('move %s to folder %s' % (fn, dst))
```

命令行：

```shell
$ copy foo.txt bar.txt my_folder
move foo.txt to folder my_folder
move bar.txt to folder my_folder
```

> 如果你熟悉argparse，你会发现`nargs`好像不能传入`+`来限制最少一个参数。
>
> 可以通过`required=True`来限制这个参数必须传入。

## File Arguments

```python
@click.command()
@click.argument('input', type=click.File('rb'))
@click.argument('output', type=click.File('wb'))
def inout(input, output):
    while True:
        chunk = input.read(1024)
        if not chunk:
            break
        output.write(chunk)
```

命令行为:

```shell
$ inout - hello.txt
hello
^D
$ inout hello.txt -
hello
```

## File Path Arguments

```python
@click.command()
@click.argument('f', type=click.Path(exists=True))
def touch(f):
    click.echo(click.format_filename(f))
```

命令行:

```shell
$ touch hello.txt
hello.txt

$ touch missing.txt
Usage: touch [OPTIONS] F

Error: Invalid value for "f": Path "missing.txt" does not exist.
```

## File Opening Safety

pass

## Environment Variables

使用方法：

```python
@click.command()
@click.argument('src', envvar='SRC', type=click.File('r'))
def echo(src):
    click.echo(src.read())
```

命令行为:

```shell
$ export SRC=hello.txt
$ echo
Hello World!
```

## Option-Like Arguments

有时，你想让arguments看起来像options。例如，想象你有个文件名为`-foo.txt`。如果你将它直接传入命令行，Click会把它看作是一个option。

为了解决这个问题，Click使用POSIX风格命令行脚本常用的方式，即使用字符串`--`来分隔options和arguments。在`--`标记之后，所有的参数都看作是arguments。

```python
@click.command()
@click.argument('files', nargs=-1, type=click.Path())
def touch(files):
    for filename in files:
        click.echo(filename)
```

命令行：

```shell
$ touch -- -foo.txt bar.txt
-foo.txt
bar.txt
```