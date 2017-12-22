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

## Commands

### revoke:Revoking tasks

-- | --
-- | --
pool | all, terminate only support by prefork
broker | amqp, redis
command | celery -A proj control revoke <task_id>

所有的worker node都保持了一份已撤销任务的id的内存，或者保存在内存中或者持久化到硬盘里.

当一个worker接受到一个revoke情况，它会跳过任务的执行，但是除非在设置了terminate选项的前提下，它不会终止当前正在执行的任务。

> 注意：
>
>> 当一个任务卡住后，terminate选项是管理员的最后一个手段。它不是终止任务，而是终止执行任务的进程。进程可能在信号发送的时候已经开始处理其它的任务，所以你不应该在程序上面调用这个terminate.

如果设置了terminate，worker中处理任务的子进程将会被终结。默认发送的信号是TERM，但是你可以通过`signal`参数来另外指定。Signal可以是大写的名称或者任何定义于Python标准库`signal`模块的常量.

terminate一个任务也意味着会revoke它.

例子:

```python
>>> result.revoke()

>>> AsyncResult(id).revoke()

>>> app.control.revoke('d9078da5-9915-40a0-bfa1-392c7bde42ed')

>>> app.control.revoke('d9078da5-9915-40a0-bfa1-392c7bde42ed',
                       terminate=True)

>>> app.control.revoke('d9078da5-9915-40a0-bfa1-392c7bde42ed',
                       terminate=True, signal='SIGKILL')
```

### Revoking multiple tasks

revoke方法同样接受列表参数，它会一次性撤销多个任务。

例子:

```python
>>> app.control.revoke([
...    '7993b0aa-1f0b-4780-9af0-c47c0858b3f2',
...    'f565793e-b041-4b2b-9ca4-dca22762a55d',
...    'd9d35e03-2997-42d0-a13e-64a66b88a618',    
])
```

### Persistent revokes

撤销任务是通过发送一个广播消息到所有的worker而生效的，然后worker会在内存中保持一份撤销任务的列表。当一个worker启动后，将会与cluster中的其它worker同步这份列表.

撤销任务列表存储在内存中，所有一旦所有的worker都重启，那么这份列表就会销毁。如果你想要持久化这份列表，那么你需要对`celery worker`使用`--statedb`参数:

`$ celery -A proj worker -l info --statedb=/var/run/celery/worker.state`

或者如果你使用`celery multi`的时候想要为每个worker创建一个文件,那么你可以使用`%n`格式符：

`$ celery multi start 2 -l info --statedb=/var/run/celery/%n.state`

注意，远程控制命令当前只支持RabbitMQ和Redis.

## Time Limits

-- | --
-- | --
pool | prefork/gevent

> Sort, or hard?
>
>> time limit有两种值,soft和hard。soft time limit可以允许任务被杀死前捕获一个任务并清除。hard time limit并不能缓存，它会强制终止任务.

一个任务有可能永远的运行下去，比如你有些任务在等待一些永远不会发生的事件导致进入死循环。解决这个问题的最好办法就是设置time limit.

time limit是定义一个任务可以运行的最大时长：

```python
from myapp import app
from celery.exceptions import SoftTimeLimitExceeded


@app.task
def mytask():
    try:
        do_work()
    except SoftTimeLimitExceeded:
        clean_up_in_hurry()
```

### Changing time limits at run-time

-- | --
-- | --
broker | amqp, redis

有一个远程控制命令可以修改soft和hard的time limit.

```python
>>> app.control.time_limit('tasks.crawl_the_web',
                    soft=60, hard=120, reply=True)
[{'worker1.example.com': {'ok': 'time limits set successfully'}}]
```

## Rate Limits

### Changing rate-limits at run-time

下面是一个例子，修改`myapp.mytask`的rate-limit，让它每分钟只能运行最多２００个任务：

```python
>>> app.control.rate_limit('myapp.mytask', '200/m)
```

上面的例子并没有指定destination,所以会影响到cluster中的所有worker实例。如果你只想影响一个指定的worker列表，可以使用`destination`参数：

```python
>>> app.control.rate_limit('myapp.mytask', '200/m',
...                         destination=['celery@worker1.example.com'])
```

## Max tasks per child setting

-- | --
-- | --
pool | prefork

用这个option，你可以设置一个worker可执行的最大任务数量。

在你有内存泄漏的问题是这个配置很有用。

这个option可以通过worker的命令参数`--max-tasks-per-child`来设定，或者直接使用`worker_max_tasks_per_child`设置。

## Max memory per child setting

你可以选择设置一个worker中常驻内存的最大值。

在你有内存泄漏的问题是这个配置很有用。

这个option可以通过worker的命令参数`--max-memory-per-child`来设定，或者直接使用`worker_max_memory_per_child`设置。

## Autoscaling

-- | --
-- | --
pool | prefork,gevent

autoscaler组件可以依据负载动态地调整pool的大小。

- 在有很多事情要做的时候，autoscaler会自动增加新的pool process
- 在负载很低的时候，autoscaler会自动移除process

可以通过选项`--autoscale`来激活，这个选项需要两个值：pool的最大值和最小值：

```python
--autoscale=AUTOSCALE
    Enable autoscaling by providing
    max_concurrency,min_concurrency. Example:
        --autoscale=10,3(always keep 3 processes, but grow to 10 if necessary).
```

你可以通过继承`Autoscaler`来设定自己的autoscaler规则。一些好的经验是将可用的内存平分。

## Queues

一个worker实例可以从任意数量的队列中消费。默认它会消费定义在`task_queues`设置中的所有队列(如果没有指定，将会使用默认队列`celery`).

你可以在开启阶段指定从哪个队列消费，通过为`Q`选项传入以逗号分隔的队列名称即可：

`$ celery -A proj worker -l info -Q foo,bar,baz`

你同样可以在运行时使用远程控制命令开启和停止对一个队列的消费：`add_consumer`和`cancel_consumer`.

### Queues: Adding consumers

`add_consumer`控制命令可以让一个或多个worker来开启对一个队列的消费。这个操作是幂等的。

