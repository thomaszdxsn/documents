[TOC]

## Starting the worker

你可以通过下面的命令在前台执行worker:

`$ celery -A proj worker -l info`

你可以在同一个机器运行多个worker，但是要确保每个单独的worker都指定一个唯一的node名称，node名称通过`--hostname`(-n)参数指定：

```python
$ celery -A proj worker --loglevel=INFO --concurrency=10 -n worker1@%h
$ celery -A proj worker --loglevel=INFO --concurrency=10 -n worker2@%h
$ celery -A proj worker --loglevel=INFO --concurrency=10 -n worker3@%h
```

`hostname`参数可以通过以下的变量来扩展：

- `%h`: hostname, 包含domain
- `%n`: 只包含hostname
- `%d`: 只包含domain

比如，如果当前的hostname是`george.example.com`, 可以这样扩展:

变量 | 模版 | 结果
-- | -- | --
%h | worker1@%h | worker1@george.exmaple.com
%n | worker1@%n | worker1@george
%d | worker1@%d | worker1@example.com

> supervisor用户的注意事项
>
>> `%`符号需要转义，比如: `%%h`.

## Stopping the worker

worker的shutdown应该符合`TERM`信号。

当worker在初始化一个shutdown时，它会在真正的关闭前结束所有执行中的任务。如果这些任务很重要，你应该等待它执行完毕再强行结束，比如发送一个`KILL`信号。

如果worker不在一个等的急的时间内关闭，或者在一个类似于死循环中堵塞，你可以使用`KILL`信号来强行终止worker：但是要明白正在执行的任务会丢失(除非任务设置了`acks.late`).

另外进程不能覆盖`KILL`信号，worker不能够reap它的children。请手动完成它。下面这个命令可以实现：

`$ pkill -9 -f 'celery worker'`

如果你的系统没有`pkill`命令，你可以使用稍长一些的命令:

`$ ps auxww | grep 'celery worker' | awk '{print $2}' | xargs kill -9`

## Restarting the worker

想要重启woker，你需要发送`TERM`信号来开启一个新的实例。在开发时想要轻松的管理worker，可以使用`celery multi`:

```python
$ celery multi start 1 -A proj -l info -c4 --pidfile=/var/run/celery/%n.pid
$ celery multi restart 1 --pidfile=/var/run/celery/%n.pid
```

至于生产环境，你可能需要一个进程监视系统.

另外你可以通过`HUP`信号来重启一个worker。注意，这个方法让worker自己负责重启所以不推荐使用在生产环境:

`$ kill -HUP $pid`

## Process Signals

worker主要靠覆盖如下的信号来处理进程：

信号 | 功能
-- | -- 
TERM | 热关闭，等待所有的任务完成
QUIT | 冷关闭，终结ASAP
USR1 | 讲所有激活线程的traceback导出
USR2 | 远程DEBUG


## Variable in file paths

文件路径参数`--logfile`, `--pidfile`以及`--statedb`可以包含变量:

### Node name replacements

- `%p`: 完整Node名称
- `%h`: hostname, 包含domain名称
- `%n`: 只包含hostname
- `%d`: 只包含domain名称
- `%i`: Prefork进程池索引，如果是主进程则索引为0
- `%I`: 通过分隔符分割的Prefork进程池索引

例如，如果当前的hostname为**george@foo.exmaple.com**:

- `--logfile=%p.log` --> `george@foo.exmaple.com.log`
- `--logfile=%h.log` --> `foo.example.com.log`
- `--logfile=%n.log` --> `george.log`
- `--logfile=%d` --> `example.com.log`

### Prefork pool process index

prefork池进程索引说明符将会扩充到不同的文件中。

可以让每个进程用一个单独的日志文件。

记住这个文件数量将会保持和进程限制数量一样，不管后来进程退出或者自动伸缩。也就是说，是process index的数量，而不是进程计数或者pid.

- `%i` - pool process index，如果是主进程则为0

    比如,`-n worker1@example.com -c2 -f -%n-%i.log`将会生成三个日志文件：

    - `worker1-0log`(主进程)
    - `worker1-1log`(pool process 1)
    - `worker1-2log`(pool process 2)

- `%I`- pool process index，并且带有分隔符

    比如,`-n worker1@example.com -c2 -f -%n%i.log`将会生成三个日志文件：

    - `worker1.log`(main process)
    - `worker1-1.log`(pool process 1) (`-`是分隔符)
    - `worker1-2.log`(pool process 2)


## Concurrency

默认使用multiprocessing来并发执行任务，但是你也可以使用`Evenlet`.进程/线程的数量可以通过参数`--concurrency`, `-c`参数来指定，默认使用机器中的核心数量.

> 进程数量(multiprocess/prefork pool)
>
>> 更多的pool proceesses通常会认为更好，但是增加pool proceesses的时候有一个分割点(cut-off point)，如果超出这个点之后继续增加process，性能反而会变遭.即使证明显示有时多个worker实例运行时，可能比单个worker的性能更好。你需要经验，经验可以帮助你找到最适合你的process数量，这个数量根据应用，工作负载，运行时长，以及其它的一些因素而不同。

## Remote control

-- | -- 
-- | --
pool | prefork, eventlet, gevent
support | blocking:solo
broker | amqp, redis
support | 


Worker可以通过使用高级的广播消息队列被远程控制。也就是说命令可以导向所有的worker，或者指定的worker列表.

命令也可以有回复。客户端可以等待并收集这些回复。由于没有一个中心系统可以知道在cluster中有多少个可获取的worker，也就不能估算多少个worker可以发送回复，所以客户端可以设置一个timeout -- reply抵达时间的超时限制。这个timeout默认为1s.如果worker在达到timeout的时候也没有发送回复，可能是worker已亡，或者仅仅是网络延时。

除了timeout，客户端可以指定要等待回复的最大数量。如果设定指定目标，这个限制就是目标hosts的数量。

> 注意
>
>> `solo`池支持远程控制命名，但是任务执行时将会堵塞控制命令的执行，所以如果worker很忙的时候不要太频繁的使用控制命令。在这种情况下你也必须增加超时时间来等待worker的回复.

### broadcast()函数

这是一个客户端函数，用来发送消息给workers.一些远程控制的命令通常在后台使用`broadcast()`返程了一些高级接口，比如`rate_limit()`, `ping()`.

发送`rate_limit`命令以及关键字参数:

```python
>>> app.control.broadcast('rate_limit',
...                         arguments={'task_name': 'myapp.mytask',
...                                    'rate_limit': '200/m'})
```

这个函数可以异步发送命令，不需要等待回复。想要请求回复，你需要使用`reply`参数：

```python
>>> app.control.broadcase('rate_limit', {
...             'task_name': 'myapp.mytask', 'rate_limit': '200/m'}, reply=True)
[{'worker1.example.com': 'New rate limit set successfully'},
 {'worker2.example.com': 'New rate limit set successfully'},
 {'worker3.example.com': 'New rate limit set successfully'}]
})
```

使用`destination`参数你可以指定接受命令的workers列表：

```python
>>> app.control.broadcase('rate_limit', {
...     'task_name': "myapp.mytask",
...     'rate_limit': "200m"}, reply=True,
...                            destination=['worker1@example.com'])
[{'worker1.example.com': 'New rate limit set successfully'}]
```

使用高阶接口如`rate_limit`显然更加方便。但是有些命令只可以使用`broadcast()`.

