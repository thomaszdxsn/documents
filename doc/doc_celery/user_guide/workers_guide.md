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

..
