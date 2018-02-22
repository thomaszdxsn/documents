# Parameters

Click针对脚本支持两种类型的参数：options和arguments。一般用户都会在何时使用哪种参数的选择中迷惑过，所以在这篇文档中介绍了它们直接的一些区别。顾名思义，option即可选的。而arguments出于某些原因，也是可选的，但是它的可选有更多限制条件。

为了帮助你在options和arguments做出选择，推荐把子命令或者输入文件/URL作为arguments，其它都作为options。

## Differences

Arguments的功能比options少。以下的特性只有options才有：

- 自动提示缺失的输入
- 当作flag使用
- options值可以拉取环境变量，arguments不可以
- options在帮助页面被完整地说明，arguments不会

另一方面，可以接受任意数量的arguments，而不能接受任意数量的options。options只可以接受固定数量的参数(默认为1)

## Parameter Types

parameters可以有不同的类型：

- str / `click.STRING`:

    默认的参数类型，代表unicode字符串。

- int / `click.INT`:

    一个只接受整数值的参数。

- float / `click.FLOAT`:

    一个只接受浮点数值的参数。

- bool / `click.BOOL`:

    一个接受布尔值的参数。将会自动用作为布尔值flag。如果使用字符串值1，将会把它转换为True，如果传入0，将会把它转换为False。

- `click.UUID`

    一个接受UUID值的参数。它代表`uuid.UUID`.

- class`click.File(mode='r', encoding=None, errors='strict', lazy=None, atomic=False)`

    声明一个参数是用来读或写的文件。在上下文结束的时候这个文件句柄将会自动关闭。

    根据`mode`可以将文件以reading或writing的方式打开。

    默认情况下，文件以reading模式打开，但是也可以以binary模式或者writing模式打开。

    `encoding`参数代表一个特定的编码。

    `lazy`这个flag参数控制文件是否立即打开或者等待first IO。默认为None，即非惰性。

    从Click2.0开始，文件可以原子化(atomic)地打开，意思就是所有的写入操作都会在同目录的一个隔离的文件中进行，在完成后这个隔离的文件将会替代原始的那个文件。如果文件周期性被其它用户读取，这种原子化操作就很有用了。

- class`click.Path(exists=False, file_okay=True, dir_okay=True, writable=False, readable=True, resolve_path=False)`

    `Path`和`File`类似，但是它使用另一种检测(check)方式。首先，它不会返回一个打开的文件句柄，而仅仅是返回一个文件名。其次，它可以根据文件或者目录做一些基础的检查。

    参数：

    - `exists`

        如果设置为True，那么这个文件或者目录的必须存在才是合法的。

    - `file_okay`

        控制一个值是否可能为一个文件。(controls if a file is a possible value.)

    - `dir_okay`

        控制一个值是否可能为一个目录。

    - `writable`

        如果为True，将会对文件作一个可写检查。

    - `readable`

        如果为True，将会对文件作一个可读检查。

    - `resolve_path`

        如果为True，那么在path是完全解析的(fully resolved)。意思就是它是绝对的，symlinks也是被解析的(resolved).

- class`click.Choice(choices)`

    `Choice`类型允许对一个值检查，看它是否是一个固定集合的一个元素。所有的值都必须是字符串。

- class`click.IntRange(min=None, max=None, clamp=False)`

    一个类似与`Int`类型的参数类型，不过它会限制参数值在一个固定范围内。默认会在超出范围之后报错，不过可以设置在两个差值(edges)之间忽略。

## Parameter Names

参数(不管是options还是parameters)都可以接受很多位置参数(参数名称)作为参数声明。每个以单横杠(-)开头的字符串都是短参数；每个以两个横杠(--)开头的字符串都是长参数。如果一个参数没有以横杆开头，它会变为内部参数名称并用作参数名。

如果一个参数没有给定一个没有横杠的名称，它的参数名称将会以长参数作为名称(将所有的横杠转换为下划线)。比如一个option有`('-f', '--foo-bar')`，它的参数名会是**foo_bar**；比如一个option有`('-x',)`，那么参数名为**x**;如果一个option有`('-f', '--filename', 'dest')`，参数名为**dest**。

## Implementing Custom Types

想要实现一个自定义的类型，你需要继承`ParamType`类。Type可以传入/不传入上下文和参数对象来调用。

下面的代码实现了一个整数类型，可以接受八进制，十六进制和普通的整数类型，然后将它们转换为常规整数类型：

```python
import click


class BasedIntParamType(click.ParamType):
    name = 'integer'

    def converter(self, value, param, ctx):
        try:
            if value[:2].lower() == '0x':
                return int(value[2:], 16)
            elif value[:1] == '0':
                return int(value, 8)
            return int(value, 10)
        except ValueError:
            self.fail('%s is not a valid integer' % value, param, ctx)
BASED_INT = BasedIntParamType()
```



    