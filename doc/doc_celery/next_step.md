[TOC]

## Next Step

在`first step`中只介绍了Celery最基础的一部分用法。在这里我们介绍的更加详细，包括怎么让Celery来支持你的应用或者库。

## 在你的应用中使用Celery

### 我们的项目

项目布局：

```python
proj/__init__.py
    /celery.py
    /tasks.py
```


```python
# proj/celery.py
from __future__ import absolute_import, unicode_literals
from celery import Celery

app = Celery('proj', 
            broker='amqp://',
            backend='amqp://',
            include=['proj.tasks'])

# 可选的配置
app.conf.update(
    result_expires=3600
)


if __name__ == '__main__':
    app.start()
```

在这个模块中，我们创建了Celery实例(有时把它叫做app).想要在你的项目中使用Celery，通常只需要简单的import这个实例。

- `broker`参数指定想使用的broker之URI.

- `backend`参数指定想要使用的result backend

    Result可以在每个任务的基础上面来禁用，通过装饰器`@task(ignore_result=True)`

- `include`参数是当worker开启时要import的模块列表。你需要把任务模块加入到这里，所以worker就能找到它了。

```python
# proj/tasks.py
from __future__ import absolute_import, unicode_literals
from .celery import app

@app.task
def add(x, y):
    return x + y


@app.task
def mul(x, y):
    return x * y


@app.task
def xsum(numbers):
    return sum(numbers)
```

### 开启我们worker

`celery`程序可以通过worker来启动(你需要在`proj`的父级目录来运行这个worker):

`$ celery -A proj worker -l info`

当这个worker启动后，你将会看到一个banner和一些消息：

```python
-------------- celery@halcyon.local v4.0 (latentcall)
---- **** -----
--- * ***  * -- [Configuration]
-- * - **** --- . broker:      amqp://guest@localhost:5672//
- ** ---------- . app:         __main__:0x1012d8590
- ** ---------- . concurrency: 8 (processes)
- ** ---------- . events:      OFF (enable -E to monitor this worker)
- ** ----------
- *** --- * --- [Queues]
-- ******* ---- . celery:      exchange:celery(direct) binding:celery
--- ***** -----

[2012-06-08 16:23:51,078: WARNING/MainProcess] celery@halcyon.local has started.
```

- `broker`这个URI是你在`celery`模块指定的`broker`参数，你也可以在命令行通过`-b`选项选择另一个不同的broker.
- `concurrency`是指定用于处理你的任务并发的prefork worker进程数量，当所有这些进程都在忙的时候，碰到一个新的任务就需要等待一个进程空闲下来才行。

    默认的concurrency数字是这台机器的CPU数量，你可以通过`celery worker -c`选项指定一个数字。不推荐使用自定义的进程数量，比如如果你的任务大多是IO堵塞，你想增加处理的速度，有相关的实验证明了两倍于CPU数量的进程只能带来很少的性能提升，甚至于降低性能。

    除了默认的prefork池，Celery同样支持Eventlet, Gevent和运行于单线程。

- `events`是一个选项，激活后可以在worker发生动作时让Celery发送监视消息。可以使用监视程序如`celery events`和Flower - 一个实时的Celery监视器。

- `Queues`: 是一个queue列表，worker将会从中消费任务。worker可以一次性从若干队列消费，也可以用于将消息路由自特定的workers.详情请看**Routing Guide**.

### 停止worker

想要停止worker只需按下`Control-C`即可。另外也有一组信号可以处理worker的状态.

### 运行于后端

在生产环境中你想要把worker在后台运行，可以考虑使用supervisor...或者使用Celery的后台化功能。

后台化脚本使用`celery multi`命令在后台执行一个或多个wokers:

```python
$ celery multi start w1 -A proj -l info
celery multi v4.0.0 (latentcall)
>>> Starting nodes...
    > w1.halcyon.local: OK
```

你也可以重启它：

```python
$ celery multi restart w1 -A proj -l info
celery multi v4.0.0 (latentcall)
> Stopping nodes...
    > w1.halcyon.local: TERM -> 64024
> Waiting for 1 node.....
    > w1.halcyon.local: OK
> Restarting node w1.halcyon.local: OK
celery multi v4.0.0 (latentcall)
> Stopping nodes...
    > w1.halcyon.local: TERM -> 64052
```

或者可以停止它：

`$ celery multi stop w1 -A proj -l info`

`stop`命令时异步的，所以你不要期待workers将会立即关闭。你可能想要使用`stopwait`命令，这个命令可以保证在退出前完成当前正在执行的任务：

`$ celery multi stopwait w1 -A proj -l info`

> 注意
>> `celery multi`并不存储workers有关的信息，所以你需要在重启的使用使用相同的命令行参数（`restart w1 -A proj -l info`）。在停止时只有相同的pidfile和logfile被使用。

默认会在当前的目录创建pid和log文件，为了防止多个workers覆盖，推荐你把它们放在一个专门的目录:

```python
$ mkdir -p /var/run/celery
$ mkdir -p /var/log/celery
$ celery multi start w1 -A proj -l info --pidfile=/var/run/celery/%n.pid\
                                        --logfile=/var/log/celery/%n%I.log
```

使用multi命令，你可以开启多个worker，下面是一个更加强力的命令语法，可以为不同的worker指定不同的参数，例如:

`$ celery multi start 10 -A proj -l info -Q:1-3 images, video -Q:4-5 data -Q default -L:4,5 debug`


### 关于--app参数

`--app`参数指定要使用的Celery app实例，必须传入`module.path:attribute`这种形式.

但是如果只指定了一个包的名称，也提供了一个更加简单的参数形式，我们搜索app实例的顺序如下：

对于`--app=proj`:

1. 一个命名为`proj.app`的属性(全局变量)，或者，
2. 一个命名为`proj.celery`的属性，或者，
3. 在proj模块中任意值是`Celery`实例的属性值，或者

如果在上面的步骤没有找到Celery实例，将会在proj.celery子模块查找：

4. 一个命名为`proj.celery.app`的属性，或者,
5. 一个命名为`proj.celery.celery`的属性，或者,
6. 在proj.celery模块中任意值是`Celery`实例的属性值


## 调用任务

你可以使用`delay()`方法来调用一个任务：

`>>> add.deley(2, 2)`

这个方法其实是`apply_async`的封装，讲位置参数打包进一个元祖传入：

`>>> add.apply_async((2, 2))`

下面参数的`countdown`是运行的倒计时，`queue`是要发送到的队列：

`>>> add.apply_async((2, 2), queue='lopri', countdonw=10)`

在上面例子中，我们的任务将会发送到一个名叫`lopri`的队列，任务最早会在消息发送10秒之后才会被发送。

直接调用任务将会在当前的进程直接运行，也就不会发送消息到broker:

```python
>>> add(2, 2)
4
```

这三个方法：`delay()`, `apply_async()`以及`__call__()`，代表Celery的调用API.

每个任务调用都会生成一个全局唯一标识符(UUID)，这就是任务id.

`delay()`和`apply_async()`方法都会返回一个`AsyncResult`实例，可以用于追踪任务执行的状态。但是想要达到这个目的，你需要激活一个**result backend**, 所以状态可以存储在某个地方。

`Result`默认被禁用，因为事实上没有一个result backend适用于所有的应用;而且为很多任务保持返回结果并没什么用。另外，result backend并不是用来监视任务和worker的，而是用于Celery专门的事件消息。

如果你有配置一个result backend，你可以取回一个任务的返回值：

```python
>>> res = add.delay(2, 2)
>>> res.get(timeout=1)
```

你可以通过`.id`属性来查看任务id:

```python
>>> res.id
d6b3aea2-fb9b-4ebc-8da4-848818db9114
```

如果任务抛出一个异常，你可以查看异常和traceback，事实上`get()`默认将会传播错误消息：

```python
>>> res = add.delay(2)
>>> res.get(timeout=1)

Traceback (most recent call last):
File "<stdin>", line 1, in <module>
File "/opt/devel/celery/celery/result.py", line 113, in get
    interval=interval)
File "/opt/devel/celery/celery/backends/rpc.py", line 138, in wait_for
    raise meta['result']
TypeError: add() takes exactly 2 arguments (1 given)
```

如果你不想让错误向上传播：

```python
>>> res.get(propagate=False)
TypeError('add() takes exactly 2 arguments (1 given)',)
```

在这个例子中，将会返回`Exception`实例，这时想要检查任务成功或失败，你可以使用相符的方法来查看：

```python
>>> res.failed()
True

>>> res.successful()
False
```

所以如何知道任务失败与否？可以通过查看任务状态来查看：

```python
>>> res.state
'FAILURE'
```

一个任务一次只能具有一个状态，但是它可以在运行时通过若干状态。典型的任务过渡为：

`PENDING -> STARTED -> SUCCESS`

`started`状态是一个特殊的状态，只有在`task_track_started`设置开启时，或者在一个任务中传入了参数`@task(track_started=True)`才会被记录.

`pending`状态不是一个被记录状态，而是一个任务的默认状态：

```python
>>> from proj.celery import app

>>> res = app.AsyncResult('this-id-does-not-exist')
>>> res.state
'PENDING'
```

如果任务被重启，状态阶段可能会变得更加复杂。为了展示这些，假设一个任务被重启了两次，它的状态阶段将会变成这样:

`PENDING -> STARTED -> RETRY -> STARTED -> RETRY -> STARTED -> SUCCESS`


## Canvas: 设计工作流

你只学会了如何使用`delay()`方法调用一个任务，通常你也只需要明白这个就行了，但是有时你也会想在一个任务中调用另一个任务，或者把签名传入其它函数。

你可以对`add()`创建一个签名：

```python
>>> add.signature((2, 2), countdonw=10)
tasks.add(2, 2)
```

也可以使用一个快捷方式：

```python
>>> add.s(2, 2)
tasks.add(2, 2)
```

### 然后它们再次调用API

Signature实例同样支持调用API:意味着它们也拥有`delay`和`apply_async`方法。

但是有一个不同之处在于，签名中可能已经存在一个指定的参数.比如`add()`接受两个参数，一个包含两个参数的签名意味着它是一个完整签名:

```python
>>> s1 = add.s(2, 2)
>>> res = s1.delay()
>>> res.get()
4
```

但是，你也可以像`functools.partial`一样创建一个不完成的签名：

```python
# 不完成的签名: add(?, 2)
>>> s2 = add.s(2)
```

s2是一个partial签名，需要另一个参数才能使他完整：

```python
# 解决partial: add(8, 2)
>>> res = s2.delay(8)
>>> res.get()
10
```

这里我们加入的参数8将会往前追加(prepend)到签名，所以现在存在了两个参数，构成了一个完整的签名`add(8, 2)`.

关键字参数可以同样在之后加入，它们将会和存在的关键字参数合并，但是新的参数将会更优先：

```python
>>> s3 = add.s(2, 2, debug=True)
>>> s3.delay(debug=False)       # debug现在是False
```

一个有状态的签名支持这些调用API：

- `sig.apply_async(args=(), kwargs={}, **options)`

    调用这个签名已经partial位置参数，关键字参数。同样支持partial options。

- `sig.delay(*args, **kwargs)`

    `apply_async`的unpack参数版本。所有的参数都会prepend到签名中，关键字参数将会覆盖存在的参数。

看起来很有用，但是我们到底能用它们来做些啥？在说明它们的作用之前，我必须介绍一些画布原语(canvas primitives).


### The primitives

这些primitives都是签名对象本身，所以它们可以任意拼接组合来构成一个复杂的工作流。

> 注意
>> 这些例子取回了任务结果，所以需要配置一个result backend.

让我们看一些例子。

#### Groups

一个`group`调用并行(parallel)调用一个任务列表，它会返回一个特殊的result实例让我们查看一个group的结果，并且能够按顺序取回它们的返回值：

```python
>>> from celery import group
>>> from proj.tasks import add

>>> group(add.s(i, i) for i in range(10))().get()
[0, 2, 4, 6, 8, 10, 12, 14, 16, 18]
```

- `partial group`

```python
>>> g = group(add.s(i) for i in range(10))
>>> g(10).get()
[10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
```

#### Chains

任务可以链接(linked)在一起，可以在一个任务完成后调用另一个，这里重载了管道操作符:

```python
>>> from celery import chain
>>> from proj.tasks import add, mul

# (4 + 4) * 8
>>> chain(add.s(4, 4) | mul.s(8))().get()
64
```

或者一个`partial chain`:

```python
>>> # (? + 4) * 8
>>> g = chain(add.s(4) | mul.s(8))
>>> g(4).get()
64
```

Chains也可以写成下面这样(不需要使用`chain`):

```python
>>> (add.s(4, 4) | mul.s(8))().get()
64
```

#### Chord

chord是一个group和一个callback：

```python
>>> from celery import chord
>>> from proj.tasks import add, xsum

>>> chord((add.s(i, i) for i in range(10)), xsum.s())().get()
90
```

由于这些原语(primitives)都是签名(signature)类型，你可以将它任意组合使用，例如：

```python
>>> upload_document.s(file) | group(apply_filter.s() for filter in filters)
```

## Routing

Celery支持AMQP支持的所有routing能力，但是它通用支持一个简单的routing，即把消息发送给一个命名队列。

`task_routes`设置能够让你将任务以名称来路由，并且让一切都集中在一个地方配置：

```python
app.conf.update(
    task_routes = {
        'proj.tasks.add': {"queue": "hipri"}
    },
)
```

你也可以在运行时使用参数`apply_async.queue`为任务指定队列：

```python
>>> from proj.tasks import add
>>> add.apply_async((2, 2), queue='hipri')
```

现在你可以设定一个worker来消费这个队列，可以通过命令行`celery worker -Q`来实现：

```python
$ celery -A proj worker -Q hipri
```

你可以通过逗号分割来指定多个队列。比如你想让一个worker消费默认队列以及`hipri`队列，默认队列因为历史原因名称叫做`celery`: 

```python
$ celery -A proj worker -Q hipri,celery
```

队列名称的顺序不重要，worker会将它们相等对待。

## 远程控制

如果你使用RabbitMQ(AMQP)，Redis，或者Qpid作为broker，那么你可以在运行时控制和监测worker。

例如，你可以查看当前worker在进行哪个任务：

`$ celery -A proj inspect active`

这个系统通过广播消息来实现，所以cluster中所有的worker都将收到控制命令。

你也可以使用命令行选项`--destination`来指定一个或多个worker作为被请求对象：

`$ celery -A proj inspect active --destination=celery@example.com`

如果没有提供destination，那么每个worker都会作为被请求对象。

`celery inspect`命令不会改变worker的任何东西，它只会返回根据worker内部情况返回信息和统计数据。

`celery control`命令可以在运行时修改worker。

例如，你可以让worker激活事件消息(用来监听任务和worker)：

`$ celery -A proj control enable_events`

当事件激活后，你可以使用event dumper来查看哪个woker在工作：

`$ celery -A proj events --dump`

或者你可以开启curse接口：

`$ celery -A proj events`

当你结束监听以后，你可以再次禁用事件：

`$ celery -A proj control disable_events`

`celery status`命令同样用于远程控制，可以展示cluster中的一组在线worker：

`$ celery -A proj status`

## 时区

所有的时间，日期和内部消息都是使用UTC时区。

当一个worker收到一个消息后，例如收到一个countdown以后将会吧UTC时间转换为本地时间。如果你想使用和系统不一样的时区，可以通过`timezone`设置来完成：

`app.conf.timezone = 'Europe/London'`

## 优化

默认的配置并没有为吞吐量(throughput)优化，它会试图在众多短任务和少部分长任务之间作平衡，在公平调度和吞吐量之间协商。

如果你有严格的调度要求，或者需要优化吞吐量，那么你需要阅读`Optimizing Guide`.

如果你在使用RabbitMQ，那么你可以安装`librabbitmq`模块：这是一个C实现的AMQP客户端。

`$ pip install librabbitmq`





