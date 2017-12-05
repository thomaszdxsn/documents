## tornado.autoreload -- 在开发过程中自动探测代码变动

当一个源文件发生改动时，自动重启服务器。

多数应用应该不需要直接访问这个模块。只要把一个关键字参数`autoreload=True`传入到`tornado.web.Application`构造器即可(或者传入`debug=True`， 它也会开启这个配置以及其它若干配置)。这个配置将会开启自动重启模式，除了源代码文件还会检查templates和static目录的变动。注意这个重启是一个毁坏性的操作，任何在这个过程中发起的请求都会失败(如果你想使用debug模式，但是不想开启autoreload，可以同时设置`debug=True`以及`autoreload=False`)。

这个模块同样可以被一个命令行封装，用于比如单元测试runner。

命令行封装和Application-debug模式可以同时启用。这个组合可以促使封装器发现语法错误和其它import-time错误，debug模式会在服务器启动时捕获修改。

这个模块基于`IOLoop`，所以它不适用于WSGI应用以及Goolge App Engine。同样不适用于`HTTPServer`的多进程模式。

重启将会丧失Python解释器参数(如`-u`)，因为它会使用`sys.executable`和`sys.argv`重启服务器。另外，修改这些变量会让重启行为失常。

- `tornado.autoreload.start(io_loop=None, check_time=500)`

    开始观察源文件的修改。

- `tornado.autoreload.wait()`

    等待一个观察的文件发生变动，然后重启进程。

- `tornado.autoreload.watch(fielname)`

    将一个文件加入到观察列表。

    默认会观察所有import的模块。

- `tornado.autoreload.add_reload_hook(fn)`

    将如一个函数，在进程重启之前调用它。

- `tornado.autoreload.main()`

    命令行封装，在源文件改动时，重新运行这个脚本。

    脚本可以指定一个文件名或者模块名：

    ```python
    python -m tornado.autoreload -m tornado.test.runtests
    python -m tornado.autoreload tornado/test/runtests.py
    ```

    


