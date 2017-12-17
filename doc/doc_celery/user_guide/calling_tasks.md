## 基础

这篇文档介绍了Celery的"Calling API"风格，用于任务实例和Canvas中。

这个API定义了一套执行的选项，包含以下三个方法：

- `apply_asnyc(args[, kwargs[, ...]])`

    发送一个任务消息

- `delay(*args, **kwargs)`

    发送一个任务消息的快捷方式。但是不支持额外的任务执行选项。

- 直接(同步)调用(`__call__`)

    直接调用一个任务意味着这个任务不会由worker执行，而是由当前进程直接同步执行(也就不会发送任务消息了)。

> 速查表
> - `T.delay(arg, kwargs=value)`
>   
>   `T.apply_async()`的快捷方式.
>
> - `T.apply_async((arg,), {'kwarg': value})`
>   
> - `T.apply_async(countdown10)`
>   
>   在１０秒以后开始执行这个任务
>
> - `T.apply_async(countdown=60, expires=120)`
> 
>   在1分钟以后开始执行，但是在设定了2分钟以后任务过期.
> 
> - `T.apply_async(expires=now + timedealta(days=2))`
>
>   在两天以后过期.

### 例子

`delay()`方法是一个方便的用法，因为看起来就像调用一个普通函数一样：

`task.delay(arg1, arg2, kwarg1='x', kwarg2='y')`

如果使用`apply_async()`，你需要这么来写:

`task.apply_async((arg1, arg2), {"kwarg1": "x", "kwarg2": "y"})`

所以`delay()`是更加清晰易读的，但是如果你想要加入额外的执行选项，那么你不得不使用`apply_async`.

这篇文档的剩余部分会详细的探讨执行选项。所有的例子都是用一个`add()`的任务：

```python
@app.task
def add(x, y):
    return x + y
```

### Linking(callbacks/errbacks)

Celery支持讲任务链接在一起，所以可以让一个任务紧随着另一个任务执行。callback任务将会把父任务的返回结果当做自己的一个partial参数.

`add.apply_async((2, 3), link=add.s(16))`

第一个任务的结果是**4**，这个结果将会发送给新任务(`link`参数）,上面的表达式形式为`(2+2)+16 = 20`.

如果任务抛出一个异常你也可以调用一个callback(errback)，但是这个场景的处理方式稍有不同。

下面是一个使用errback的例子:

```python
@app.task
def error_handler(uuid):
    result = AsyncResult(uuid)
    exc = result.get(propagate=False)
    print("Task {0} raise exception: {1!r}\n{2!r}".format(uuid, exc, result.traceback))
```

可以使用`link_error`这个选项加入到一个任务的执行中：

`add.apply_async((2, 2), link_error=error.handler.s())`

另外，`link`和`link_error`可以以列表形式传入多个：

`add.apply_async((2, 2), link=[add.s(16), other_task.s()])`

callback/errbacks将会按顺序调用，所有的callback都将会把父对象的返回值当做一个partial参数来执行。

### On message

Celery支持设置一个`on_message`callback来捕获所有状态的更改。

比如，对于一个长时间运行的任务你可以以下面这样的方式来发送任务的进度：

```python
@app.task(bind=True)
def hello(self, a, b):
    time.sleep(1)
    self.update_state(state="PROGRESS", meta={"progress": 50})
    time.sleep(1)
    self.update_state(state="PROGRESS", meta={"progress": 90})
    time.sleep(1)
    return "Hello World: %i" (a + b)
```

```python
def on_raw_message(body):
    print(body)


r = hello.apply_async()
print(r.get(on_message=on_raw_message, propagate=False))
```

将会生成类似如下的输出：

```python
{
    "task_id": '5660d3a3-92b8-40df-8ccc-33a5d1d680d7',
    "result": {"progress": 50},
    "children": [],
    "status": "PROGRESS",
    "traceback": None
}
{
    "task_id": '5660d3a3-92b8-40df-8ccc-33a5d1d680d7',
    "result": {"progress": 90},
    "children": [],
    "status": "PROGRESS",
    "traceback": None
}
{
    'task_id': '5660d3a3-92b8-40df-8ccc-33a5d1d680d7',
    'result': 'hello world: 10',
    'children': [],
    'status': 'SUCCESS',
    'traceback': None
}
hello world: 10
```

### ETA和Countdown

ETA(估算抵达的时间)可以让你设置任务执行的最早时间。`countdown`是一个设置ETA的快捷方式，可以很方便的设置一个倒计时：

```python
>>> result = add.apply_async((2, 2), countdonw=3)
>>> result.get()        # 这个任务最少会在3秒以后才执行
4
```

这个任务会确保在指定时间/日期之后被执行，但**并不能**保证一个精确的时间。比如可能会因为队列中太忙而堵塞，或者因为高网络延迟的原因。想要确保任务按时执行，你需要监控队列的拥堵情况。

`countdown`是一个整数，`eta`必须是一个`datetime`对象，指定一个精确的时间和日期(包含毫秒级精度，以及时区信息):

```python
>>> from datetime import datetime, timedelta

>>> tomorrow = datetime.utcnow() + timedelta(days=1)
>>> add.apply_async((2, 2), eta=tomorrow)
```

### 过期

`expires`参数定义了一个可选的过期时间，可以是任务发布后的秒数，或者可以是一个指定的时间/日期(datetime对象):

```python
>>> # 任务将会在现在开始的一分钟过后过期
>>> add.apply_async((10, 10), expires=60)

>>> # 同样支持datetime
>>> from datetime import datetime, timedelta
>>> add.apply_async((10, 10), kwargs, 
                expires=datetime.now() + timedelta(days=1))
```

当一个worker接受到一个过期的任务时，将会把这个任务标记为`REVOKED`.


### 消息发送的retry

Celery支持在链接失败时自动retry发送消息这一行为，retry行为也可以通过配置来实现 -- 比如何时retry，或者设置一个retry的最大数值 - 或者将它们都禁用。

想要禁用`retry`，只需要在调用API中将它设置为False即可：

`add.apply_async((2, 2), retry=False)`

#### Retry策略

`retry policy`是一个映射，可以控制retry的行为，这个映射包含以下的键：

- `max_retries`

    retry的最大尝试次数，如果达到最大值以后将会抛出异常。

    如果这个键设置为None，意味着可以无限尝试retry。

    默认为retry3次。

- `interval_start`

    定义retry之间的间隔时间。默认为0

- `interval_step`

    每个接下来的retry的间隔，默认为0.2

- `interval_max`

    retry之间的间隔时间最大值。默认为0.2

例如，默认的policy为：

```python
add.apply_async((2, 2), retry=True, retry_policy={
    'max_retries": 3,
    "interval_start": 0,
    "interval_step": 0.2,
    "interval_max": 0,2
})
```

### 链接错误处理

当你发送一个任务而消息传输时链接断了，或者链接不能初始化，将会抛出一个`OperationError`:

```python
>>> from proj.tasks import add
>>> add.delay(2, 2)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "celery/app/task.py", line 388, in delay
        return self.apply_async(args, kwargs)
  File "celery/app/task.py", line 503, in apply_async
    **options
  File "celery/app/base.py", line 662, in send_task
    amqp.send_task_message(P, name, message, **options)
  File "celery/backends/rpc.py", line 275, in on_task_call
    maybe_declare(self.binding(producer.channel), retry=True)
  File "/opt/celery/kombu/kombu/messaging.py", line 204, in _get_channel
    channel = self._channel = channel()
  File "/opt/celery/py-amqp/amqp/connection.py", line 272, in connect
    self.transport.connect()
  File "/opt/celery/py-amqp/amqp/transport.py", line 100, in connect
    self._connect(self.host, self.port, self.connect_timeout)
  File "/opt/celery/py-amqp/amqp/transport.py", line 141, in _connect
    self.sock.connect(sa)
  kombu.exceptions.OperationalError: [Errno 61] Connection refused
```

如果你对这个任务设置了retry，那么这个异常直到retry耗尽以后才会被抛出。

你也可以处理这个错误：

```python
>>> from celery.utils.log import get_logger
>>> logger = get_logger(__name__)

>>> try:
...     add.delay(2, 2)
... except add.OperationalError as exc:
...     logger.exception('Sending task raised: %r", exc)
```

### Serializers

客户端和worker之间的数据传输需要序列化，所以Celery中的每个消息都会有一个`content_type`头部，描述自己使用的是哪种序列化方法。

默认的serializer是JSON, 但是你可以通过`task_serializer`设置来更改，或者对每个任务，每个消息来单独设置。

默认支持的序列化方式为JSON, pickle, YAML, 和msgpack.你也可以创建你自己的serializer，需要通过Kombu serialzer registry将它注册。

每种方式都有它的优劣势：

- `json`

- `pickle`

- `yaml`

- `msgpack`

### 压缩

Celery可以使用诸如*gzip*, *bzip2*来压缩消息。你也可以创建你自己的压缩方式，最后通过Kombu compression registry来注册。

### 连接

你可以通过创建一个publisher来手动处理连接：

```python
result = []
with add.app.pool.acqure(block=True) as connection:
    with add.get_publisher(connection) as publisher:
        try:
            for args in numbers:
                res = add.apply_async((2, 2), publisher=publisher)
                results.append(res)
print([res.get() for res in results])
```

虽然使用group的话明显更好：

```python
>>> from celery import group

>>> numbers = [(2, 2), (4, 4), (8, 8), (16, 16)]
>>> res = group(add.s(i, j) for i, j in numbers).apply_async()

>>> res.get()
[4, 8, 16, 32]
```

### Routing options

Celery可以将任务route到不同的队列。

简单的routing可以通过`queue`选项实现：

`add.apply_async(queue='priority.high')`

也可以使用命令行形式：

`$ celery -A proj worker -l info -Q celery,priority.high`


#### 高级options


下面是一些AMQP的高级routing选项：

- `exchange`

- `routing_key`

- `priority`

    0 - 255的数字，255为最高。

    支持：RabbitMQ, Redis(在redis里面相反，0为最高).


