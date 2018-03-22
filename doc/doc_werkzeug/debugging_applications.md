# Debugging Applications

不同的WSGI gateway/server，处理异常的方式是不一样的。

但是大多数时间，异常都会输出到stderr或者错误日志。

不过这并不是最佳的调试环境，Werkzeug提供了一个WSGI中间件，可以渲染调试信息，
可以选择AJAX形式的debugger。

但是这个debugger**不能**用在生产环境！！！

## Enabling the Debugger

你可以将application封装一个`DebuggedApplication`中间件来开启debugger。

另外，也可以通过传入参数到`run_simple()`来开启。

- class`werkzeug.debug.DebuggedApplication(app, evalex=False, request_key='werkzeug.request', console_path='/console', console_init_func=None, show_hidden_frames=False, lodgeit_url=None, pin_security=True, pin_logging=True)`

    将给定的app激活debugger.

    ```python
    from werkzeug.debug import DebuggedApplication
    from myapp import app
    app = DebuggedApplication(app, evalex=True)
    ```

    `evalex`关键字参数允许在traceback环境中执行表达式.

    参数:

    - `app`: 要运行debugger的WSGI应用.

    - `evalex`: 开启exception eval特性.要求non-forking服务器.

    - `request_key`: 这个key指定了环境中的request对象。不过当前版本会忽略这个参数。

    - `console_path`: URL

    - `console_init_func`: 在开启console之前执行的函数.

    - `show_hidden_frames`: 默认情况下，隐藏的traceback frames会被跳过.

    - `pin_security`: 可以基于安全系统来禁用pin

    - `pin_logging`: 开启pin系统的logging。


## Using the Debugger

开启debugger以后，如果请求遇到错误，那么你可以看到错误页面。

在点击控制台选项时可以执行这些代码.

## Debugger PIN

...

## Pasting Errors

...
