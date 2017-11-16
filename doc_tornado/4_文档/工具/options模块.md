## tornado.options -- 命令行解析

一个命令行解析库，可以使用这个模块定义自己的options。

每个模块都能定义自身的options，最后会把它们加入到全局option命名空间，例如:

```python
from tornado.options import define, options

define("mysql_host", default="127.0.0.1:3306", help="Main user DB")
define("memcache_hosts", default="127.0.0.1:11011", multiple=True,
        help="Main user memcache servers")


def connect():
    db = database.Connection(options.mysql_host)
    ...
```

你的应用的`main()`方法并不需要单独处理别的模块定义的options；这些options会在模块被读取时自动被读取。但是，在命令行解析前，必须把定义了options的模块都importe进来。

你的`main()`方法可以解析命令行或者解析配置文件：

```python
tornado.options.parse_command_line()
# 或者
tornado.options.parse_config_file('/etc/server.conf')
```

命令行格式就像你期待的一样`--myoption=myvalue`。配置文件即平常的Python文件，里面的全局变量可以变为option，例如：

```python
myoption = "myvalue"
myotheroption = "myothervalue"
```

我们支持`datetime`, `timedelta`，整数和浮点数(只需要传入`define`函数的`type`关键字参数即可)。另外可以支持多值options。

`tornado.options.options`是`OptionParser`的一个单例，这个模块中的全局函数(`difine`,`parse_command_line`等等)只是调用这个单例的方法而已。你可以自己定义一个`OptionParser`实例用来设置你自己的一套options，比如子命令。

> 注意
>
>> 默认情况下，在调用`parser_command_line`或者`parse_config_file`以后，将会定义若干和`logging`相关配置的options。如果你想让Tornado不要管logging配置，你自己来设置，可以传入options`--logging=none`，或者在代码中加入：
>> ```python
>> from tornado.otpions import options, parse_command_line
>> options.logging = None
>> parse_command_line()
>> ```

横杠(dash`-`)和下划线在options名称中是可以混合使用的（自动替换)。dash一般用在命令行，下划线用在配置文件中。

### 全局函数

- `tornado.options.define(name, default=None, type=None, help=None, metavar=None, multiple=False, group=None, callback=None)`

    在全局命名空间定义一个options。

- `tornado.options.options`

    全局Options对象。所有定义的options都会作为这个对象的属性。

- `tornado.options.parse_command_line(args=None, final=True)`

    解析命令行中出现的全局options。

- `tornado.options.parse_config_file(path, final=True)`

    从一个配置文件中解析options。

- `tornado.options.print_help(file=sys.stderr)`

    将所有的命令行options打印到stderr(或者其它文件).

- `tornado.options.add_parse_callback(callback)`

    增加一个option解析的回调函数，在option解析完成后调用。

- 异常`tornado.options.Error`

    options模块抛出的异常。


### OptionParser类

- `tornado.options.OptionParser`

    一个options集合，一个支持“属性访问方式”的字典。

    通常通过`tornado.options`模块中的静态方法来访问，它引用了一个全局实例。

    - `items()`

        一个`(name, value)对`的序列。

    - `groups()`

        这个方法会显式`define`创建的option-groups。

    - `group_dict(group)`

        一个group中的所有options的字典形式。

        可以用这个方法把options拷贝到Application的settings:

        ```python
        from tornado.options import define, parse_command_line, options

        define('template_path', group='application')
        define('static_path', group='application')

        parse_command_line()

        application = Application(
            handlers, **options.group_dict('application')
        )
        ```

    - `as_dict()`

        所有options的字典形式。

    - `define(name, default=None, type=None, help=None, metavar=None, multiple=False, group=None, callback=None)`

        定义一个新的命令行option。

        如果给定了`type`(在str, float, int, datetime, timedelta中的一个)或者根据`default`推理出了类型，我们根据给定的类型来解析命令行参数。如果`multiple`为True，可以接受以逗号分割的值，option的值这时是一个列表。

        对于多值整数值，我们可以接收语法`x:y`，在内部会将这个语法解析为`range(x, y)` - 大于大范围的数字很有用。

        `help`和`metavar`用来构建一个自动生成的命令行帮助字符串。帮助信息的格式类似于：

        `--name=METAVAR     help string`

        `group`用来把定义的options收集到一个逻辑分组中。默认情况下，命令行options会被分组到它们定义的模块。

        命令行参数opitons的名称必须全局唯一。

        如果给定一个`callback`，在options的值改动时，都会以这个新的值来运行：

        ```python
        define("config", type=str, help="path to config file",
            callback=lambda path: parse_config_file(path, final=False))
        ```

    - `parse_command_line(args=None, final=True)`

        解析所有命令行给定的options。

        注意`argv[0]`会被忽略，因为这个变量是脚本名称。

        这个方法返回一个参数列表。

        如果`final=False`，解析callback不会被调用。

    - `parse_config_file(path, final=True)`

        在给定的路径上解析并读取Python配置文件。

        如果`final=False`, 解析callback不会被调用。

    - `print_help(file=None)`

        将所有的命令行options打印到stderr(或者其它文件).

    - `add_parse_callback(callback)`

        增加一个解析回调，将会在option解析完成后调用。

    - `mockable()`

        返回一个封装，它兼容了`mock.patch`.

        