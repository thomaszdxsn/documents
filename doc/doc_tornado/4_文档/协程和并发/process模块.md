## tornado.processes -- 多进程的工具

用于多进程编程的工具函数，包含把server fork多个进程，以及管理子进程。

- 异常`tornado.process.CalledProccessError`

    `subprocess.CalledProccessError`的别称。

- `tornado.process.cpu_count()`

    返回这个机器的进程总数。

- `tornado.process.fork_processes(num_proccesses, max_restarts=100)`

    开启多个worker进程。

    如果`num_processes`为None或者小于等于0，我们将会检查当前机器的核心个数并fork这个数量的进程。如果这个参数大于0，我们将会fork这个指定数量的进程。

    由于我们使用的是进程而不是线程，服务器代码之间不会存在共享内存。

    注意多进程和autoreload模式不兼容。

    在每个子进程中，`fork_processes`返回它的`task id`，值是一个数字，在0和进程数量之间。异常退出的进程(由于一个信号或者非0退出状态)，会以相同的`task id`重启(根据`max_restarts`时间)。在父进程中，如果所有的子进程都正常退出，`fork_processes`将会返回None，如果有非正常退出的情况，将会抛出一个异常。

- `tornado.proceess.task_id()`

    如果存在，返回当前的`task id`。

    如果进程不是由`fork_processes`创建的，返回None。

- `tornado.process.Subprocess(*args, **kwargs)`

    封装`subprocess.Popen`，并提供IOStream支持。

    构造器和`subprocess.Popen`相同, 但是有以下附加项：

    1. `stdin, stdout, stderr`将会具有值`tornado.process.Subprocess.STREAM`，它会让相符的属性都又一个`PipeIOStream`。

    2. 将会传入一个新的关键字参数`io_loop`

    `Subprocess.STREAM`选项和`set_exit_callback`以及`wait_for_exit`方法不支持在Windows上面应用。因此在Windows上面还是推荐使用标准库的`subprocess.popen`。

    方法：

    - `set_exit_callback(callback)`

        当进程结束后，运行callback。

        这个callback接受一个参数，即这个进程返回的代码。

        这个方法使用一个`SIGCHLD`处理器，这是一个全局设置，如果你的其它库处理同样的信号，将会引发冲突。如果你使用一个以上的`IOLoop`，必须首先调用`Subprocess.initialize`来指定一个`IOLoop`来运行信号处理器。

    - `wait_for_exit(raise_error=True)`

        返回一个Future，在进程结束后被解析。

        用法：

        `ret = yield proc.wait_for_exit()`

        这是`set_exit_callback`的协程版本(堵塞函数`subprocess.Popen.wait`的替代)。

    - 类方法`initialize(io_loop=None)`

        初始化一个`SIGCHLD`处理器。

        这个信号处理器运行在IOLoop上面，防止锁的问题。注意，在信号处理中使用的`IOLoop`不需要和单独`Subprocess`对象使用的一样。

    - 类方法`uninitialize()`

        移除这个`SIGCHLD`处理器。

        