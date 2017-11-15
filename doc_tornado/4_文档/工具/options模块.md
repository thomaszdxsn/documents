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

pass