## Debugging

### Debugging Tasks Remotely(using pdb)

#### Basics

`celery.contrib.rdb`是`pdb`的一个扩展版本，可用来远程调试。

使用例子:

```python
from celery import task
from celery.contrib import rdb


@task()
def add(x, y):
    result = x + y
    rdb.set_trace()     # <- 设置断点
    return result
```

`set_trace()`可以在原地设置一个断点，并创建了一个socket让你可以远程调试。

debugger可能会同时开启多个，所以不要使用固定的端口，而是从一个端口范围内搜索，开始于6900(默认).可以通过环境变量`CELERY_RDB_PORT`来修改这个基础端口.

默认情况下，debugger只能被本地host访问，如果想要设置让其它host访问，需要修改环境变量`CELERY_RDB_HOST`.

当一个worker碰到你的断点时，它会输出如下信息:

```python
[INFO/MainProcess] Received task:
    tasks.add[d7261c71-4962-47e5-b342-2448bedd20e8]
[WARNING/PoolWorker-1] Remote Debugger:6900:
    please telnet 127.0.0.1 6900. Type `exit` in session to continue.
[2011-01-18 14:25:44,119: WARNING/PoolWorker-1] Remote Debugger:6900:
    Waiting for client...
```

如果你使用telnet连接指定端口，将会进入一个pdb shell:

```python
$ telnet localhost 6900
Connected to localhost.
Escape character is '^]'.
> /opt/devel/demoapp/tasks.app(128)add()
-> return result
(Pdb)
```

输入help获取可用命令.

为了阐释说明，我们读取`result`变量的值，修改它并继续任务的执行:

```python
(Pdb) result
4
(Pdb) result = 'hello from rdb'
(Pdb) continue
Connection closed by foreign host.
```

可以在worker日志中找到执行结果：

```python
[2011-01-18 14:35:36,599: INFO/MainProcess] Task
    tasks.add[d7261c71-4962-47e5-b342-2448bedd20e8] succeeded
    in 61.481s: 'hello from rdb'
```

#### Tips

##### Enabling the break-point signal

如果设置了环境变量`CELERY_RDBSIG`，那么只要接受到`SIGUSR2`信号，worker就会开启一个pdb shell.

例如：

```python
$ CELERY_RDBSIG=1 celery worker -l info
```

你可以通过执行如下命令来开启一个rdb shell:

```python
$ kill -USR2 <pid>
```

