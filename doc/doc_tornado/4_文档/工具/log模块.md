## tornado.log -- 支持日志功能

Tornado的日志功能。

Tornado使用三个logger流：

- `tornado.access`: 针对HTTP服务器每个请求的日志记录
- `tornado.application`: 应用代码的错误日志(比如callback中未捕获的错误)
- `tornado.general`: 一般性用途的日志，包含任何Tornado本身的错误和警告

这些流可以通过Python标准库`logging`来单独配置。例如，你可以把`tornado.access`日志记录到一个独立的文件，以供将来分析。

- `tornado.log.LogFormatter(fmt='%(color)s[%(levelname)1.1s    %(asctime)s    %(module)s:%(lineno)d]%(end_color)s       %(message)s', date_fmt='%y%m%d %H:%M:%S', style='%', color=True, colors={40: 1, 10: 4, 20: 2, 30: 3})`

    Tornado中使用的日志格式器。

    这个格式器的关键特性：

    - 当日志在终端输出时，支持为文字添上颜色
    - 每行日志加入时间戳
    - 稳健解决byte/str的编码问题

    这个格式器在调用`tornado.options.parse_command_line`或者`tornado.options.parse_config_file`时自动启用(除非设定了`--loging=none`)。

    Windows平台并不支持ANSI颜色代码标准，可以通过`colorama`来支持着色功能。应用必须使用`colorama.init`来初始化。

    **参数:**

    - `color`(布尔值): 提供着色特性。
    - `fmt`(字符串): 日志消息格式。
    - `colors`(字典): 终端颜色代码的映射。
    - `datefmt`(字符串): 日期时间格式。

    **方法:**

    - `tornado.log.enable_pretty_logging(options=None, logger=None)`
        开启配置的格式化日志输出。

        这个方法在调用`tornado.options.parse_command_line`或者`tornado.options.parse_config_file`时自动调用(除非设定了`--loging=none`)。

    - `tornado.log.define_logging_options(options=None)`

        为options增加了一些日志相关的参数options。

        这个选项已经加入到默认的OptionParser对象。

    