# User guide

## Installing APScheduler

`pip install apscheduler`

## Code examples

源代码中有一个文件夹`examples`，包含各种使用场景的例子.

## Basic concepts

APScheduler包含以下4种部分:

- triggers

    `triggers`包含了规划逻辑。每个job都有它自己的trigger，它可以决定何时执行下一次job。除了初始化时的配置，trigger是完全无状态的。

- job stores

    `job stores`存储了规划的job。默认的`job stores`将job存储在内存中，不过也可以存在在各种数据库中。在job存储到一个持久化的`job stores`的时候，它的数据会被序列化，然后在把数据读取回来的时候会反序列化。`job stores`不应该被`schedulers`共享。

- executors

    `executors`用来处理运行的job。一般会将callable提交给一个线程/进程池来执行。在job完成的时候，`executor`会通知`scheduler`然后发出一个适当的event。

- schedulers

    `schedulers`会把上面这些绑定在一起。一般在你的应用中只应该有一个`scheduler`。应用开发者一般也不需要直接处理`triggers`, `job stores`或者`executors`。而是通过`scheduler`的接口来处理这些东西。可以通过`scheduler`来配置`job stores`和`executors`，以及可以使用`scheduler`来增加、修改和移除jobs。

## Choosing the right scheduler, job store(s), executor(s) and trigger(s)   

大多数时候应该根据你的编程环境来选择scheduler。

下面是选择scheduler的快速教程：

- `BlockingScheduler`

    如果你的进程只运行这个scheduler，可以选择这个。

- `BackgroundScheduler`

    如果你不使用以下的框架，但想让scheduler在后台运行，可以选择这个。

- `AsyncIOScheduler`

    如果你的应用使用`asyncio`，可以选择这个。

- `GeventScheduler`

    如果你的应用使用`gevent`，可以选择这个。

- `TornadoScheduler`

    如果你的应用使用`Tornado`，可以选择这个。

- `TwistedScheduler`

    如果你的应用使用`Twisted`，可以选择这个。

- `QtScheduler`

    如果你想创建一个`Qt`应用，可以选择这个。

很简单，是吗？

要想选择一个合适的`job store`，你首先需要决定你的job是否需要持久化。如果你在启动你的应用的时候需要重新创建job，那么使用默认的(`MemoryJobStore`)就行了。不过如果你希望你的job持久化，即使应用重启或者崩溃仍然存在，那么你可以根据你的编程环境来选择一个合适的持久化`job store`.

同样的，`executor`的选择也基于你自己。默认会使用`ThreadPoolExecutor`，它足够太多数场景。如果你需要进行CPU密集计算，你应该考虑使用`ProcessPoolExecutor`.并且你可以同时使用它们，在适当的时候切换即可。

在你规划一个job的时候，你应该为它选择一个`trigger`.`trigger`可以决定何时(date/time)来运行job。APScheduler有三种内置的trigger类型：

- `date`: 如果你想让job在一个确定的时间运行
- `interval`: 如果你想让job在一个固定间隔的时间后运行
- `cron`: 如果你想让job在周期内运行

也可以将多个trigger组合。

## Configuring the scheduler

APScheduler提供了不同的方式来配置scheduler。你可以使用configure字典，或者以关键字参数的形式传入option。首先你需要实例话scheduler，加入job以及配置scheduler。这种方式可以为任何环境提供最大的弹性。

scheduler级别的配置可以在`BaseScheduler`类的API reference中看到。Scheduler子类可以拥有它们自己额外的一些options。job store和executor的配置选项都可以在它们的API reference中看到。

让我们假设你想要在自己的应用中运行一个`BackgroundScheduler`，并且使用默认的`job store`和默认的`executor`:

```python
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()
```

然后你或获得一个`BackgroundScheduler`，以及一个名为"default"的`MemoryJobStore`，以及一个名为"default"的`ThreadPoolExecutor`(默认开启10个worker线程)。

现在，假定你想要更多的东东。你需要两个`job store`，使用两个`executor`，你想要把修改新job的默认值，并且设置一个时区。下面三个方式效果是一样的，完成以后你会获得：

- 一个名为"mongo"的`MongoDBJobStore`
- 一个名为"default"的`SQLAlchemyJobStore`(使用SQLite)
- 一个名为"default"的`ThreadPoolExecutor`(默认开启20个worker)
- 一个名为"processpool"的`ProcessPoolExecutor`(默认开启5个worker)
- 使用UTC作为scheduler的时区
- 默认关闭新job的合并(coalescing)
- 默认一个新job最多有3个实例

### Method-1

```python
from pytz import utc

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.mongodb import MongoDBJobStore
from apscheduler.jobsotres.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor

jobstores = {
    'mongo': MongoDBJobStore(),
    'default': SQLAlchemyJobStore(url='sqlite:///jobs.sqlite'),
}
executors = {
    'defaults': ThreadingPoolExecutor(20),
    'processpool': ProcessPoolExecutor(5),
}
job_defaults = {
    'coalesce': False,
    'max_instances': 3
}
scheduler = BackgroundScheduler(jobstores=jobstores, executors=executors, job_defaults=job_defaults, timezone=utc)
```

### Method-2

```python
from apscheduler.schduler.background import BackgroundScheduler

# "apscheduler."是硬编码
sheduler = BackgroundScheduler({
    "apscheduler.jobstores.mongo": {
        'type': 'mongodb'
    },
    'apscheduler.jobstores.default': {
        'type': 'sqlalchemy',
        'url': 'sqlite:///jobs.sqlite'  
    },
    'apscheduler.executors.default': {
        'class': 'apscheduler.executors.pool:ThreadPoolExecutor',
        'max_workers': '20'
    },
    'apscheduler.executors.processpool': {
        'type': 'processpool',
        'max_workers': '5'
    },
    'apscheduler.job_defaults.coalesce': 'false',
    'apscheduler.job_defaults.max_instances': '3',
    'apscheduler.timezone': 'UTC'
})
```

### Method-3

```python
from pytz import utc

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ProcessPoolExecutor

jobstores = {
    'mongo': {'type': 'mongodb'},
    'default': SQLAlchemyJobStore(url='sqlite:///job.sqlite')
}
executors = {
    'default': {'type': 'threadpool', 'max_workers': 20},
    'processpool': ProcessPoolExecutor(max_workers=5)
}
job_defaults = {
    'coalesce': False,
    'max_instances': 3
}
scheduler = BackgroundScheduler()

# ...做一些其它的事情
scheduler.configure(
    jobsotres=jobstores,
    executors=executors,
    job_defaults=job_defaults,
    timezone=utc
)
```

## Starting the scheduler

可以调用scheduler的`.start()`即可以开启一个scheduler。

在开启scheduler以后，你不可以再修改它的配置。

## Adding jobs

有两种方式可以把一个job加入到scheduler中。

1. 调用`add_job()`
2. 使用`scheduled_job()`装饰一个函数

第一种方式是最常用的方式。第二种方式更加方便来声明一个job。`add_job()`方法会返回一个`apscheduler.job.Job`实例，你可以使用这个实例来修改或移除job。

你可以在任何时候使用schduler规划一个job。如果job加入的时候scheduler还没有运行，这个job将会被暂时性的scheduled，它会在schedulers开启的时候被运行。

如果你使用的exectutor和job store需要存储序列化的job，它会为你的job加入一些必要条件：

1. callable必须全局可访问
2. callable的参数必须是可序列化的

对于内置`job stores`来说，只有`MemoryJobStore`不会序列化job。对于内置`executors`来说，只有`ProcessPoolExecutor`会序列化job。

> 如果想要直接运行一个job，那么在添加这个job的时候不要传入`trigger`参数。

## Removing jobs

当你从scheduler中移除一个job的时候，将会把它从`job store`中移除并且不会再被执行。有两种方式可以移除job：

1. 通过传入job的ID和`job store alias`到`remove_job()`
2. 通过把`add_job()`返回的`Job`实例，调用它的`.remove()`

第二种方法更加的方便，但是它要求你把job存在在某个地方。如果job是通过`scheduled_job()`来规划的，只可以使用第一种方法。

如果job的规划结束(比如，trigger不会在未来任何时间内生产)，它会被自动移除。

例子：

```python
job = scheduler.add_job(myfunc, 'interval', minutes=2)
job.remove()
```

也可以使用job ID：

```python
scheduler.add_job(myfunc, 'interval', minutes=2, id='my_job_id')
scheduler.remove_job('my_job_id')
```

## Pausing and resuming jobs

你可以通过`Job`实例或者scheduler来停止和重启job。在一个job停止的时候，它的下次运行时间也会被清空，直到这个job重启。

想要停止一个job，可以:

- `apscheduler.job.Job.pause()`
- `apscheduler.schedulers.base.BaseScheduler.pause_job()`

重启，可以：

- `apscheduler.job.Job.resume()`
- `apscheduler.schedulers.base.BaseScheduler.resume_job()`

## Getting a list of scheduled jobs

想要获取一个机器被规划的job，你可以通过`get_jobs()`来获得它们。它会返回一个`Job`实例的list。如果你只对某个特定`job store`中的job感兴趣，可以将这个`job store`的alias作为参数传入。

处于方便的语言，你可以使用`.print_jobs()`方法来打印格式化的job列表(包括triggers，下次运行时间)。

## Modifying jobs

可以通过`apscheduler.job.Job.modify()`或者`modify_job()`来修改任何job的属性(除了`id`属性都可以修改).

例子:

```python
job.modify(max_instances=6, name='Alternate name')
```

如果你想要重新规划一个job - 比如说修改它的trigger，你可以使用`apscheduler.job.Job.reschedule()`或者`reschedule_job()`。

例子:

```python
scheduler.reschedule_job('my_job_id', trigger='cron', minute='*/5')
```

## Shutting down the scheduler

关闭一个scheduler:

```python
scheduler.shutdown()
```

默认情况下，sheduler会关闭executor和job store之后再退出。如果你不想等待：

```python
scheduler.shutdown(wait=False)
```

## Pausing/resuming job processing

可以暂停一个scheduler：

```python
scheduler.pause()
```

然后可以重启它：

```python
scheduler.resume()
```

也可以在从`pause`状态开启一个scheduler：

```python
scheduler.start(paused=True)
```

## Limiting the number of concurrently executing instances of a job

默认情况下，同一时间每个job只有一个实例会被运行。这意味着，如果一个job要运行的时候之前的一次运行还没有完成，之后的一次运行将会被认为是一个misfire。不过可以设定一个job可以并发执行的最大数量，通过关键字参数`.max_instances`.

## Missed job executions and coalescing

有时scheduler可能不能在规定的时间运行一个job。

pass...

## Scheduler events

情况`.event`模块的文档.

例子：

```python
def my_listener(event):
    if event.exception:
        print('The job crashed :(')
    else:
        print('The job worked :)')

scheduler.add_listener(my_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
```

## Troubleshooting

你可以重设logging登记，看到更多的日志信息.

```python
import logging

logging.basicConfig()
logging.getLogger('apscheduler').setLevel(logging.DEBUG)
```

## Reporting bugs

Github [bug tracker](https://github.com/agronholm/apscheduler/issues)

## Getting help

pass...


