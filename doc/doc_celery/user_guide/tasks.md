## 任务

任务是Celery应用的构件块。

任务是一个类，可以通过任何可调用对象来创建。它执行的是拨号的工作，在一个任务被调用后(发送了消息)它定义了将会发生什么事情，或者一个worker收到消息后会发生什么。

每个任务类都有个独一的名称，这个名称在消息中被引用，所以worker能够找到正确的函数并执行。

一个任务消息直到被worker知晓才会从队列中移除。一个worker可以提前保留很多消息，甚至这个worker已经被杀死 - 比如停电或者其它原因导致 - 这个消息将会重新递送给其它worker。

理想情况下，任务应该是幂等(idempotent)的:**意思就是即使函数以同样参数被调用多次，它应该不会造成不同的结果,不会造成意想不到的后果**.如果你的任务是幂等的，默认的行为是在(任务)执行前提前告知消息，所以在一个任务被调用后不会再次被执行。

如果你的任务是幂等的，你就可以设置`acks_late`选项，就可以在任务返回后再让worker知晓。

注意即使在设置了`acks_late`之后，在子进程执行任务被终结后(调用`sys.exit()`，或者通过信号终止)，这个worker将会知晓。这个行为是为了:

1. 我们不想返回的任务强制核心发送一个`SIGSEGV`(segmentation fault)或者进程中其它类似的信号.
2. 我们假设系统管理员是有意杀死任务，而不让它自动重启
3. 一个任务被分配了太多内存是很危险的，容易处罚系统内核的OOM杀手，同样的事情可能会再次发生。
4. 在重新递送时一个任务总是失败的话，将会造成一个高频率的消息循环，让系统奔溃。

如果你真的希望任务在这种场景下面重新递送，你应该考虑使用`task_reject_on_worker_lost`设置。


> 警告
>> 一个任务无线堵塞下去的话，最终会导致worker实例终止
>> 
>> 如果你的任务做一些I/O，需要确认你对这些操作加上了timeout，比如使用requests库进行web请求加上了timeout一样:
>>
>> ```python
>> connect_timeout, read_timeout = 5.0, 30.0
>> response = request.get(URL, timeout=(connect_timeout, read_timeout))
>> ```
>>
>> 时间限制(`get(timeout=?)`)是一个很便利的习惯，让你的所有任务都具有一个超时行为，但是这个时间限制系统将会强制杀死进程，所以只有在你没有设置超时的任务上再使用这个系统才好.
>>
>> 默认的prefork池调度器对长时间运行的任务并不友好.所以，如果你有任务运行时间以数十分钟/小时计数，那么你应该确保对*celery worker*激活了`-Ofair`命令行参数
>>
>> 如果你的任务挂起，请在Github提交issue前检查哪个任务在运行，大多数挂起的任务都是因为任务在进行网络操作.

### 基础

你可以使用`@task`装饰器很轻松的让任何可调用对象变为一个任务：

```python
from .models import User


@app.task
def create_user(username, password):
    User.objects.create(username=username, password=password)
```

`@task`装饰器还可以设置很多options：

```python
@app.task(serializer='json')
def create_user(username, password):
    User.objects.create(username=username, password=password)
```

> 多个装饰器
>>
>> 当使用多个装饰器时，你必须确保`@task`在最后面应用
>>
>> ```python
>> @app.task
>> @decorator2
>> @decorator1
>> def add(x, y):
>>     return x + y
>> ```


### 绑定(bouding)任务

一个绑定的任务意味着任务的第一个参数总是它自己(self)，就像Python的绑定方法一样:

```python
logger = get_task_logger(__name__)

@task(bind=True)
def add(self, x, y):
    logger.info(self.request_id)
```

在retry的时候需要绑定任务，可以用来访问当前任务请求的信息，可以使用你自定义的任务方法.


### 任务继承

`@task`装饰器的`base`参数指定任务的基类:

```python
import celery


class MyTask(celery.Task):

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        print('{0!r} failed: {1!r}'.format(task_id, exc))


@task(base=MyTask)
def add(x, y):
    raise KeyError()
```

### 命名

每个任务必须有一个独一的名称。

如果没有显式的为`@task`装饰器提供`name`参数，那么装饰器会自动为你生成一个任务名称，它会依据1)任务定义的模块名称，2)任务函数的名称.

显式设置任务名称的例子:

```python
>>> @app.task(name='sum-of-two-numbers')
>>> def add(x, y):
...     return x + y

>>> add.name
'sum-of-two-numbers'
```

有一个最佳实践就是使用模块名作为命名空间，使用这种方式就不会发送其它模块定义了同样名称任务的冲突问题：

```python
>>> @app.task(name='tasks.add')
>>> def add(x, y):
...     return x + y
```

你可以通过任务的`.name`属性来查看任务的名称:

```python
>>> add.name
'tasks.add'
```

即使你不设置名称，`@task`的默认名称生成规范也是这样:

```python
@app.task
def add(x, y):
    return x + y
```

```python
>>> from tasks import add
>>> add.name
'tasks.add'
```

#### 自动命名和相对引用

> 绝对引用
>>
>> Python2开发者的最佳实践就是在每个模块的顶部加上:
>>
>> `from __future__ import absolute_import`

相对应用和自动命名不相融洽，所以在你使用相对引用时你需要显式的设置名称。

例如，如果客户端以`.tasks`的方式import模块`myapp.tasks`，生成的名称不会匹配并且会抛出一个`NotRegisterd`错误。

#### 改变自动命名的行为

有些情况下自动命名行为并不太合适。考虑你在很多不同的模块包含很多任务：

```python
project/
    /__init__.py
    /celery.py
    /moduleA/
            /__init__.py
            /tasks.py
    /moduleB/
            /__init__.py
            /tasks.py
```

使用默认的命名行为，每个生成的名称都会类似`moduleA.tasks.taskA`, `moduleA.tasks.taskB`, `moduleB.tasks.test`等等...你可能想移除所有任务名称中的`tasks`.解决方案是，你可以使用显式的任务名称，或者你可以覆盖`app.gen_task_name()`来改变自动命名行为。继续之前的例子，`celery.py`可以这样改：

```python
from celery import Celery


class MyCelery(Celery):

    def gen_task_name(self, name, module):
        if module.endswith('tasks'):
            module = module[:-6]
        return super(MyCelery, self).gen_task_name(name, module)

app = MyCelery('main')
```

所以，现在每个任务的名称看起来会像`moduleA.taskA`, `moduleA.taskB`...

> 警告
>>
>> 确保你的`gen_task_name()`是一个纯函数: **同样的输入必须返回同样的输出**


### 任务请求

`app.Task.request`包含当前执行任务的信息和状态。

request定义了如下的属性：

- `id`: 执行任务的唯一id
- `group`: 如果任务是group的一个成员，返回任务group的唯一id
- `chord`: 这个任务所属chord的唯一id(如果这个任务是chord的一部分)
- `correlation_id`: 自定义id，用于解决想解除重复之类的事情
- `args`: 位置参数
- `kwargs`: 关键字参数
- `origin`: 这个任务发送的host名称
- `retries`: 这个任务重试的次数，一个最小为0的整数
- `is_eager`: 如果任务被本地执行而不是被worker执行，返回True
- `eta`: 任务的初始ETA(如果有的话)。这是一个UTC时间(依据`enable_utc`设置)
- `expires`: 任务的初始过期时间(如果有的话)。这是一个UTC时间
- `hostname`: 执行任务的worker实例之node名称
- `delivery_info`: 额外的消息传递信息。这是一个映射，包含用于任务传递的改动和routing key。
- `reply-to`: 回复的队列名称(默认使用RPC result backend)
- `called_directlly`: 如果任务不是由worker执行，这个flag返回True
- `timelimit`: 一个时间元组(soft, hard)，这个任务的时间限制
- `callbacks`: 如果任务返回成功,将会被调用的一组签名（signature）
- `errbacks`: 如果任务失败时，将会被调用的一组签名(signature)
- `utc`: 如果调用者激活了`UTC`，返回True
- `headers`: 这个任务消息发送的头部映射(可以是None)
- `reply_to`: 回复的队列名称(默认使用RPC result backend)
- `root_id`: 这个任务所属工作流第一个任务的独立id(如果任务是工作流的一部分的话)
- `parent_id`: 如果这个任务是被另一个任务调用的，返回调用者任务的独立id
- `chain`: 保留任务chain列表(如果有的话).

#### 例子

下面是一个访问任务信息的例子：

```python
@app.task(bind=True)
def dump_context(self, x, y):
    print("Executing task id {0.id}, args: {0.args!r} kwargs: {0.kwargs!r}".format(self.request))
```

`bind`参数意味着这个函数是一个"bound method"，所以你可以使用self访问任务对象的信息.


### 日志

worker可以自动为你记录日志，或者你也可以手动配置日志。

一个特殊的logger名叫`celery.task`可以获取使用，你可以继承这个logger，在日志中自动获取任务名称和unique id。

最佳实践是在一个模块的顶部为你的任务创建一个通用的logger：

```python
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

@app.task
def add(x, y):
    logger.info('Adding {0} + {1}'.format(x, y))
    return x + y
```

#### 参数检查

但你调用一个任务后，Celery将会验证传入的参数，就像Python调用常规函数一样:

```python
>>> @app.task
... def add(x, y):
...     return x + y

# 使用两个参数来调用任务
>>> add.delay(8, 8)
<AsyncResult: f59d71ca-1549-43e0-be41-4e8821a83c0c>

# 只用一个参数来调用参数将会发生错误
>>> add.dealy(8)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "celery/app/task.py", line 376, in delay
    return self.apply_async(args, kwargs)
  File "celery/app/task.py", line 485, in apply_async
    check_arguments(*(args or ()), **(kwargs or {}))
TypeError: add() takes exactly 2 arguments (1 given)
```

可以对单个任务通过`typing`属性来禁用参数检查：

```python
>>> @app.task(typing=False)
... def add(x, y):
...     return x + y

# 可以正常调用，但是worker收到任务后将会抛出错误
>>> add.delay(8)
<AsyncResult: f59d71ca-1549-43e0-be41-4e8821a83c0c>
```

#### 在参数中隐藏敏感信息

当使用**task_protocol 2(任务协议2)**或者更高级别，你可以自定义日志和监视中位置参数和关键字参数如何展现，通过`argsrepr`和`kwargsrepr`来实现：

```python
>>> add.apply_async((2, 3), argsrepr='(<secret-x>, <secret-y)')

>>> charge.s(account, card='1234 5678 1234 5678').set(
...     kwargsrepr=repr({'card': '***** **** **** 5678'})    
... ).delay()
```

### 重试(retrying)

`app.Task.retry()`可以用于任务的再执行，比如碰到可恢复性错误的事件。

当你调用`retry`以后将会发送一个新的消息，使用同样的task-id.

当一个任务被retry以后，任务状态也会被记录，所以你可以使用result实例来追踪任务的进度。

下面是使用`retry`的例子：

```python
@app.task(bind=True)
def send_twitter_status(self, oauth, tweet):
    try:
        twtter = Twitter(oauth)
        twitter.update_status(tweet)
    except (Twitter.FailWhaleError, Twitter.LoginError) as exc:
        raise self.retry(exc=exc)           # 通过raise来调用self.retry
```

> 注意
>> 
>> `app.Task.retry()`将会抛出一个异常，所以在retry之后的代码不会执行。这是一个`Retry`异常，它不会被当做错误处理，而是对worker被标记为**半谓语(semi-predicate)**，指明这个任务需要retry，所以可以在激活result backend的时候存储正确的状态.
>>
>> 这是一个总是会发生的一般操作，除非retry的`throw`参数设置为False.

`@task`的`bind`参数可以让你访问`self`(task类型实例).

`exc`参数(?patch)用于传递异常信息，之后可以在存储任务结果时用于记录日志。任务状态中可以获得异常和traceback(如果result backend激活).

如果task包含一个`max_retries`值，那么在retry达到最大值的时候将会向上传播当前的异常，但是在下面的情况不会发生：

- 没有给定`exc`参数

    在这种情况下，将会抛出`MaxRetriesExceededError`异常。

- 当前没有异常

#### 使用自定义的retry delay

当一个任务要retry时，它可以在执行前等待一个给定的时间，默认的delay时间通过`default_retry_dealy`属性来设置。默认情况下，这个值是3分钟。注意这个属性值的单位是秒(整数或浮点数).

你可以为`retry()`提供一个`countdown`参数来覆盖默认的行为：

```python
@app.task(bind=True, default_retry_delay=30 * 60)   # 30分钟后重试
def add(self, x, y):
    try:
        something_raising()
    except Exception as exc:
        # 覆盖默认的delay时间，设置为1分钟
        raise self.retry(exc=exc, countdown=60)
```

#### 对于已知的异常自动retry

有时你只想无论何时一个特定的异常抛出后你都想将它retry。

幸运的是，Celery提供了一个选项`autoretry_for`可以完成这个想法：

```python
from twitter.exceptions import FailWhaleError


@app.task(autoretry_for=(FailWhaleError,))
def refresh_timeline(user):
    return twitter.refresh_timeline(user)
```

如果你想为内部的`@Task.retry`调用提供自定义的参数，可以为`@Task`传入`retry_kwargs`参数：

```python
@app.task(autoretry_for=(FailWhaleError,),
          retry_kwargs={'max_retries': 5})
def refresh_timeline(user):
    return twitter.refresh_timeline(user)
```

这是一个手动处理异常的代替方式，上面的例子等同于下面的代码：

```python
@app.task
def refresh_timeline(user):
    try:
        twitter.refresh_timeline(user)
    except FailWhaleError as exc:
        raise div.retry(exc=exc, max_retries=5)
```

如果你想在任何错误的情况下都retry, 只需要简单的这样使用即可:

```python
@app.task(autoretry_for=(Exception,))
def x():
    ...
```

如果你的任务依赖其它的服务，比如对一个API进行请求，最好使用`exponential backoff`来避免让你的任务对服务进行淹没式的请求。只需要指定`retry_backoff`参数即可：

```python
from requests.exceptions import RequestException


@app.task(autoretry_for(RequestException,), retry_backoff=True)
def x():
    ...
```

默认情况下，exponential backoff将会引入一个随机的[jitter](https://en.wikipedia.org/wiki/Jitter)来避免所有的任务在同时运行。

- `Task.autoretry_for`

    一个异常类的列表/元祖。如果在任务执行阶段抛出了其中的异常，这个异常将会自动retry.默认情况下，不会假设任何异常可以autoretry.

- `Task.retry_kwargs`

    一个字典。使用这个字典来定义如何执行autoretry.注意如果你使用了exponential backoff options，任务的countdown将会由Celery的autoretry系统来决定，这个字典中的countdown将会被忽略.

- `Task.retry_backoff`

    一个布尔值，或者一个数值。如果值为True，autoretry将会使用exponential backoff来计算delay时间。首次retry将会delay1秒，第二次retry将会delay2秒，第三次retry将会delay4秒...（delay的值可以根据`retry_jitter`来指定）。如果这个值是一个数字，将会作为第一个retry的时间，随后继续使用指数级增长.

- `Task.retry_backoff_max`

    一个数字。如果`retry_bakcoff`已经设定，这个选项可以设置任务retry的最大秒数。默认情况，这个选项设置为600，即10分钟。

- `Task.retry_jitter`

    一个布尔值。Jitter用于引入一个随机的指数backoff delay.预防队列中所有的任务都同时执行。


### Options

`@task`装饰器可以接受若干选项，用来改变任务的行为，比如你可以通过`rate_limit`选项来设置一个任务的频率。

任何传入`@task`装饰器的关键字参数都会被设置为最终task类的一个属性。

#### General

- `Task.name`

    任务注册的名称。

    你可以手动设置这个name，或者可以根据模块和函数名称自动生成这个属性。

- `Task.request`

    如果这个任务被执行，可以通过这个属性查看当前请求的信息。使用Thread local存储。

- `Task.max_retries`

    只有在任务调用`self.retry`或者装饰器加上了参数`autoretry_for`以后才会应用。

    在放弃之前最大的retry试图次数。如果超出了这个数值将会抛出`MaxRetriesExceededError`.

    如果值设置为None, 那么就不会限制retry的次数，直到任务成功以后才会停止。

- `Task.throws`

    可选的错误类元祖，这些类不应该被当做真实的错误来处理。

    在这个列表/元祖中的错误将会在result backend报告为失败，但是worker并不会将它记录为日志，也不会包含traceback.

    例子：

    ```python
    @task(throws=(KeyError, HttpNotFound))(:patch?)
    def get_foo():
        something()
    ```

    错误类型：

    - 已期待的错误(Tasks.throws)

        被记录为INFO日志，不会包含traceback.

    - 未期待的错误

        记录为ERROR日志，包含traceback.

- `Task.default_retry_delay`

    任务执行retry的delay时间。可以是int或者float.默认为180(三分钟)

- `Task.rate_limit`

    设置这个任务类型的频率限制(rate limit).

    如果值为None，意味着没有限制。如果是一个int或者float，将会被解释为"每秒的任务数"

    可以通过后缀"/s", "/m", "/h"来指定时间单位。

    例子："100/m"(每分钟100个任务)。这将会转换为同样的两个相同任务设置600ms间隔。

    注意这是一个worker级别的设置，而不是全局设置。想要设置全局限制，你必须限制给定的队列。

- `Task.time_limit`

    任务的硬(hard)时间限制，单位为秒。

- `Task.soft_time_limit`

    任务的软(soft)时间限制，单位为秒。

- `Task.ignore_result`

    不存储任务状态。注意这以为着你不可以使用`AsyncResult`来检查任务是否准备好了，也不能获得它的返回值。

- `Task.store_errors_even_if_ignored`

    如果设置为True，即使设置了`ignore_result`，错误也会被存储。

- `Task.serializer`

    一个字符串标识，代表要使用的默认序列化方法。默认使用`task_serializer`设置。可以是**pickle, json, yaml, 或者任何自定义序列化方法(通过kombu.serialization.registry注册过)**

- `Task.compression`

    一个字符串标识，代表要默认使用的压缩方式。

    默认使用`task_compression`设置。可以是**gzip, bzip2或者任何自定义压缩方法(已经通过komku.compression注册)**.

- `Task.backend`

    这个任务使用的result backend.必须选择`celery.backends`中的一种类的实例。默认使用`app.backend`,设置为`result_backend`.

- `Task.acks_late`

    如果设置为True, 这个任务的消息将会在执行后再被ack(ackownledged)，而不是在任务执行前就被ack。

    注意：意味着你的任务如果在执行过程中终止的话，将会被执行多次。请确保你的任务是幂等的(idempotent).

    全局设置可以通过`task_acks_late`设置来覆盖。

- `Task.track_started`

    如果这个值为True.在一个任务被worker执行后，这个任务将会被记录为"started"状态。默认值为False,即通常不会报告这个细粒度的状态。


### State

Celery可以追踪当前任务的状态。状态可以包含成功任务的记过，也可以包含失败任务的异常和traceback。

可以选择若干不同的result backend.它们各有不同的优劣。

在一个任务的生命周期内，它可能会通过若干可能的状态，每个状态会有一些任意的元数据。当一个任务过渡到新的状态后，之前的状态将会被遗弃。

同样有若干组状态，如FAIULURE_STATUS组，READY_STATUS组。

客户端使用一个状态组(PROPAGATE_STATES)类决定是否异常应该向上传播，或者可以决定状态是否应该缓存。

#### Result Backends

如果你想要追踪任务的状态，或者想要任务返回值，那么Celery需要一个地方来存储或者发送状态，并且在晚些时候取回它。可以有若干内置的result backends可供选择：`SQLAlchemy/Django ORM`, `Memcached`, `RabbitMQ/QPid(rpc)`, `Redis` -- 或者你可以自定义你自己的result backend。

没有backend可以在每个场景都适用。你可以了解每个backend的优势和劣势，并选择最适合你的那一种。

##### RPC Result Backend(RabbitMQ/QPid)

RPC result backend(`rpc://`)是一个特殊的请看，它并不会真正的存储状态，而是将它们作为消息发送。一个巨大的差异之处在于一个结果只能被取回一次，在客户端初始化任务的时候。两个不同的程序不能等待同一个结果。

即使有这个限制，如果你只是想实时接受状态的改动，这也是个极好的选择。使用消息意味着客户端不需要为新状态poll.

消息默认是转瞬即逝(transient)的，所以如果broker重启后结果将会消失。可以通过`result_persistent`设置来发送持久化消息。

##### Database Result Backend

把状态存储在数据库是一个很方便的方式，尤其是对于web应用，因为数据库资源随手可得，但是它也有自身的限制：

- 新状态poll到数据的操作开销太大，你可能需要增加poll操作的间隔，比如`result.get()`

- 一些数据库使用默认的事务隔离等级，并不适用于poll操作

    在MySQL中，默认的事务隔离等级是`REPEATABLE-RAED`: 意味着两个事务同时进行时，直到一个事务提交前，一个事务是看不到另一个事务中的修改的。

    **推荐修改为`READ-COMMITTED`隔离等级**

#### 内置状态

##### PENDING

Task正在等待执行，或者处于未知状态。任何没有任务id的任务都是pending状态。

##### STARTED

任务已经启动。默认不会报告这个状态，除非你开启了`app.Task.trace_started`设置。

- `meta-data`: 执行这个任务的子进程的`pid`和`hostname`

##### SUCCESS

任务已经成功执行。

- `meta-data`: 结果中包含这个任务的返回值。
- `propagates`: YES
- `ready`: YES

##### FAILURE

失败情况的任务执行结果。

- `meta-data`: `result`包含出现的异常，`traceback`包含异常的追溯信息.
- `propagates`: YES

##### RETRY

任务已经retried.

- `meta-data`: 任务包含retry出现的异常，`traceback`包含异常的追溯信息。
- `propagates`: NO

##### REVOKED

任务已经被取消。

- `propagates`: YES

#### 自定义状态

你可以很轻松的定义你自己要的状态，只需要想一个unique的名称即可。状态名称通常是一个大写字符串。

可以使用`update_state()`来更新任务状态：

```python
@app.task(bind=True)
def upload_files(self, filenames):
    for i, file in enumerate(filenames):
        if not self.request.called_directly:
            self.update_state(state='PROGRESS',
                    meta={'current': i, 'total': len(filenames)})
```

在这个例子中，我创建了一个**PROGRESS**状态，可以告诉应用这个任务正在进行中，并且定义了元数据`meta`，可以获取任务的current和total数据。

#### 创建pickable异常

很少人直到Python的异常必须支持pickle模块。

如果使用pickle作为serialzer，并且异常不能够被pickle，那么任务就不能正常工作。

想要确保你的异常是pickeable的，这个异常**必须**调用内置异常的初始化方法。


```python
# 正确
class HTTPError(Exception):
    pass

# 错误
class HTTPError(Exception):

    def __init__(self, status_code):
        self.status_code = status_code

# 正确
class HTTPError(Exception):

    def __init__(self, status_code):
        self.status_code = status_code
        Exception.__init__(self, status_code)   # 这一行是必须的(也可使用super()函数)
```

原则就是：任何自定义异常如果支持参数`*args`, 必须调用`Exception.__init__(self, *args)`

对于关键字参数并没有特殊的支持方式，所以如果你想要保留关键字参数你需要将它们以位置参数的形式传入`Exception.__init__()`

```python
class HttpError(Exception):
    
    def __init__(self, status_code, headers=None, body=None):
        self.status_code = status_code
        self.headers = headers
        self.body = body

        super(HttpError, self).__init__(status_code, headers, body)
```


### Semepredicates(半谓词?)

worker将会把任务封装到以个tracing函数，可以记录任务的最终状态。

有若干异常可以当作信号使用，让函数可以决定如果对待任务的返回。

#### Ignore

任务可以抛出`Ignore`让worker忽略这个任务。这意味着不会记录这个任务的状态，但是它的消息还是可以被ack(从队列中移除)的.

可以将它做什么用呢？可以使用它来实现你的自定义取消功能，或者手动存储一个任务的状态。

下面是一个例子，如果任务在redis集合中则直接取消：

```python
from celery.exceptions import Ignore


@app.task(bind=True)
def some_task(self):
    if redis.ismember('tasks.revoked', self.request.id):
        raise Ignore()
```

```python
from celery import states
from celery.exceptions import Ignore


@app.task(bind=True)
def get_twttes(self, user):
    timeline = twitter.get_timeline(user)
    if not self.request.call_redirectly:
        self.update.state(state=states.SUCCESS, meta=timeline)
    raise Ignore()
```

#### Reject

任务抛出`Reject`将会使用诸如`AMQP.basic_reject()`的方法来拒绝一个任务消息。除非激活了配置`Task.acks_late`，否者这个异常不会有效果。

reject一个消息和ack一个消息是同样的效果，但是一些broker可能实现了一些额外的功能。比如RabbitMQ支持一种[Dead Letter Exchanges](http://www.rabbitmq.com/dlx.html)概念，当一个队列配置为DLE，那么被拒绝的消息将会被再次递送。

Reject同样可以用于re-queue消息，但是请小心使用，因为这很容易造成死消息循环。

下面是一个例子，在碰到无内存可用的请看下拒绝一个消息：

```python
import errono
from celery.exceptions import Reject


@app.task(bind=True, acks_late=True)
def render_scene(self, path):
    file = get_file(path)
    try:
        renderer.render_scene(file)
    
    # 如果这个文件太大，导致内存不够用
    # 我们就会拒绝它，让它以Dead Letter Exchanges来重新递送
    # 我们可以手动监测这个情形
    except MemoryError as exc:
        raise Reject(exc, requeue=False)
    except OSError as exc:
        if exc.errorno = errno.ENOMEM:
            raise Reject(exc, requeue=False)

    # 在其它错误情况下，我们在10秒后retry
    except Exception as exc:
        raise self.retry(exc, countdonw=10)
```

下面是一个将消息re-queueing的例子：

```python
from celery.exceptions import Reject


@app.task(bind=True, acks_late=True)
def requeues(self):
    if not self.request.delivery_info['redelivered']:
        raise Reject('no reason', requeue=True)
    print('received two times')
```

#### Retry

`Retry`异常由`Task.retry()`方法抛出，告诉worker这个任务要被retry。


### 自定义任务类

所以继承自`app.Task`类的任务。`run()`方法都会变成任务的body.

作为一个例子，考虑下面这些代码：

```python
@app.task
def add(x, y):
    return x + y
```

差不多在幕后做了下面这些事情：

```python
class _AddTask(app.Task):

    def run(self, x, y):
        return x + y
    
add = app.tasks[_AddTask.name]
```

#### Instantiation

任务并**不会**在每次请求时都实例化，而是将这个任务注册到`task registry`，作为一个全局实例。

这意味着，每个进程中每个`task.__init__()`都不会被调用两次，所以这个task类在语义上等同于`Actor`模型。

如果你有下面这样一个任务：

```python
from celery import Task


class NativeAuthenticateServer(Task):

    def __init__(self):
        self.users = {'george': 'password'}

    def run(self, username, password):
        try:
            return self.users[username] == password
        except KeyError:
            return False
```

然后你在相同进程中路由(route)每个请求时，将会保持每个请求的状态。

这个模式也可以用于缓存资源，例如，一个Task类可以缓存一个数据库链接：

```python
from celery import Task


class DatabaseTask(Task)
    _db = None

    @property
    def db(self):
        if self._db is None:
            self._db = Database.connection()
        return self._db
```

然后可以这样增加任务：

```python
@app.task(base=DatabaseTask)
def process_rows():
    for row in process_rows.db.table.all():
        process_row(row)
```

现在在每个进程中，`process_rows`任务的`db`属性总是保留。


#### Handlers(Task的方法)


- `after_return(self, status, retval, task_id, args, kwargs, einfo)`

    在任务返回后调用的handler.

    参数:

    - `status`: 当前的任务状态
    - `retval`: 任务返回的值/异常
    - `task_id`: 独一的任务ID
    - `args`: 返回的任务的初始位置参数
    - `kwargs`: 返回任务的初始关键字参数
    - `einfo`: 关键字参数，`ExceptionInfo`实例，包含traceback（如果有的话）

- `on_failure(self, exc, task_id, args, kwargs, einfo)`

    如果任务失败将会被woker调用的handler.

    参数:

    - `exc`: 这个任务抛出的异常
    - `task_id`: 独一的任务ID
    - `args`: 返回的任务的初始位置参数
    - `kwargs`: 返回任务的初始关键字参数
    - `einfo`: 关键字参数，`ExceptionInfo`实例，包含traceback（如果有的话）

- `on_retry(self, exc, task_id, args, kwargs, einfo)`

    当任务retry时将会被worker调用的handler.

    参数:

    - `exc`: 这个任务抛出的异常
    - `task_id`: 独一的任务ID
    - `args`: 返回的任务的初始位置参数
    - `kwargs`: 返回任务的初始关键字参数
    - `einfo`: 关键字参数，`ExceptionInfo`实例，包含traceback（如果有的话）

- `on_success(self, retval, task_id, args, kwargs)`

    - `retval`: 任务返回的值/异常
    - `task_id`: 独一的任务ID
    - `args`: 返回的任务的初始位置参数
    - `kwargs`: 返回任务的初始关键字参数


### How it works?

这里介绍一些技术细节。这部分内容不是你必须知道的，但是你可能会有兴趣。

所有定义的任务都会列入`registry`清单。registry包含一组任务名称和它们的任务类。你可以手动查看这个registry:

```python
>>> from projc.celery import app
>>> app.tasks
{'celery.chord_unlock':
    <@task: celery.chord_unlock>,
 'celery.backend_cleanup':
    <@task: celery.backend_cleanup>,
 'celery.chord':
    <@task: celery.chord>}

```

这是Celery的内置任务清单。注意只有任务的模块被imported以后才会讲任务注册到registry.

`@app.task`装饰器负责将你的任务注册到应用的任务registry中。

当任务发送后，并没有把函数代码发送，只是发送了要执行的任务名称。在worker接受到消息后，它会在自己的任务registry中搜索这个任务名称，最后找到要执行的代码。

这意味着你的worker应该总是和客户端的代码同步。这是一个设计上的缺点，热更新的技术正在想办法解决中。

### Tips and Best Practices

#### 如果你不是真的需要，那就忽略任务的执行结果

如果你不在乎任务的结果，确保设置了`ignore_result`选项，毕竟存储结果将会浪费时间和资源.

```python
@app.task(ignore_result=False)
def mytask():
    something()
```

结果可以全局禁用，通过设置`task_ignore_result`.

#### 更多优化tips

请看官方文档的[Optimizing Guide](http://docs.celeryproject.org/en/latest/userguide/optimizing.html#guide-optimizing)


#### 避免调用同步的子任务

如果一个任务需要等待另一个任务的结果，这种任务的效率是很低的，甚至可能会导致worker池耗尽而死锁.

请确保代码的异步设计，比如使用`callback`:

```python
# bad_example.py
@app.task
def update_page_info(url):
    page = fetch_page.delay(url).get()
    info = parse_page.delay(url, page).get()
    store_page_info.delay(url, info)


@app.task
def fetch_page(url):
    return myhttplib.get(url)


@app.task
def parse_page(url, page):
    return myparser.parse_document(page)


@app.task
def store_page_info(url, info):
    return PageInfo.objects.create(url, info)
```

```python
# good_example.py

def update_page_info(url):
    # fetch_page -> parse_page -> store_page
    chain = fetch_page.s(url) | parse_page.s(url) | store_page_info.s(url)
    chain()


@app.task()
def fetch_page(url):
    return myhttplib.get(url)


@app.task()
def parse_page(page):
    return myparser.parse_document(page)


@app.task(ignore_result=True)
def store_page_info(info, url):
    PageInfo.objects.create(url=url, info=info)
```

在下面的例子中，我们使用签名特性实现的`chain()`方法。

默认情况下, celery并不会让你在任务中同步运行另一个任务(所以上面的`bad_example.py`并不能运行)，除非一些极端罕见的情况。**警告**: 不推荐同步运行子任务：

```python
@app.task
def update_page_info(url):
    page = fetch_page.delay(url).get(disable_sync_subtasks=False)
    info = parse_page.delay(url, page).get(disable_sync_subtasks=False)
    store_page_info.delay(url, info)

    
@app.task
def fetch_page(url):
    return myhttplib.get(url)


@app.task
def parse_page(url, page):
    return myparser.parse_document(page)


@app.task
def store_page_info(url, info):
    return PageInfo.objects.create(url, info)
```


### 性能和策略(performance and strategies)

#### 细粒度（Granularity）

任务细粒度是指每个子任务的计算重量。一般情况下，最好是将任务分解成多个小任务，避免运行一个耗时很长的任务。

对于小一些的任务，你可以并行处理很多这种任务，不会导致worker堵塞。

不过，将任务分割会带来额外的开销：需要传递消息，数据需要存储等等。

所以这中间的权衡需要仔细把握。

推荐书目: [Art of Concurrency](http://oreilly.com/catalog/9780596521547)

#### Data locality

worker处理的任务应该尽可能的接近数据。最好的情况是在内存中有一份拷贝，最坏的情况是从另一个大陆讲数据传输过来。

如果数据离你很远，你可能需要运行另一个worker将它拿过来。

在不同的worker之间分享数据的一个最简单的方式就是使用*分布式缓存系统*，如`memcached`.

推荐书目: [Distributed Computing Economics](http://research.microsoft.com/pubs/70001/tr-2003-24.pdf)

#### 状态(State)

由于Celert是一个**分布式系统**，你不可能直到任务被哪个进程或者哪台机器在处理。

古老的`async`谚语告诉我们"asserting the world is the responsibility of the task".因为任务被请求后它的世界观就已经改变了，所以任务应该用来确认将世界变成它应该变成的那样；如果你有一个任务对一个搜索引擎re-index工作，搜索引擎应该最多每5分钟re-index一次，必须让任务来负责这件事，而不是调用者。

另一个gotcha是Django model对象。它们不应该作为参数传入到任务中。最好在任务启动时从数据库重新获取对象，使用旧对象的数据很可能造成竟态(race conditon).

想象一下下面的场景，你有一篇文章和一个任务，任务可为文章自动扩充一些缩略语：

```python
class Article(models.Model):
    title = models.CharField()
    body = models.TextField()


@app.task
def expand_abbreviations(article):
    article.body.replace('MyCorp', 'My Corporation')
    article.save()
```

首先，一个作者创建了一篇文章并保存了它，然后作者点击了一个按钮初始化这个缩略语任务：

```python
>>> article = Article.objects.get(id=102)
>>> expand_abbreviation.delay(article)
```

现在，碰巧队列很忙，任务在两分钟后以后才会被运行。与此同时另一个作者改动了这篇文章，所以在任务最终被运行时，文章的body将会变回第一个作者创建时的样子，因为在任务初始化时传入的参数即是这样。

修复race condition是很简单的，只需使用article_id代替article_obj即可：

```python
@app.task
def expand_abbreviations(article_id):
    article = Article.objects.get(id=article_id)
    article.body.replace('MyCorp', 'My Corporation')
    article.save()
```

```python
>>> expand_abbreviations.delay(article_id)
```

使用这个方法同样具有性能上面的好处，因为发送数据量大的消息也是有开销的。

#### 数据库事务(database transactions)

让我们看一下另一个例子：

```python
from django.db import transaction


@transaction.commit_on_success
def create_article(request):
    article = Article.objects.create()
    expand_abbreviations.delay(article.pk)
```

这是一个Django的view，首先在数据库中创建了一个article对象，然后将它的主键传入到任务中。它使用了`commit_on_success`装饰器，这个装饰器会在view返回时提交这个事务，或者会在view抛出错误时将事务回滚。

这里存在一个race condition，即任务开始执行前事务还没有提交的这种情况；也就是数据库对象这时候还不存在。

解决方案是使用`on_commit`回调，这个回调会在事务成功提交后再执行。

```python
from django.db.transaction import on_commit


def create_article(request):
    article = Article.objects.create()
    on_commit(lambda: expand_abbreviations.delay(article.pk))
```

### 例子

让我们考虑一个现实世界的例子：一个博客的comment发布需要筛选一些spam。当这个comment创建后，spam筛选会在后台运行，所以用户不需要等待这个任务的结束。

```python
# blog/models.py

from django.db import models
from django.utils.translation import ugettext_lazy as _


class Comment(models.Model):
    name = models.CharField(_('name'), max_length=64)
    email_address = models.EmailField(_("email_address"))
    homepage = models.URLField(_('home_page'),
                              blank=True, verify_exists=False)
    comment = models.TextField(_('comment'))
    pub_date = models.DateTimeField(_("Published date"),
                                    editable=False, auto_add_now=True)
    is_spam = models.BooleanField(_('spam?'),
                                 default=False, editable=False)


    class Meta:
        verbose_name = _("comment")
        verbose_name_plurl = _("comments")
```

在view中我们首先将comment在数据库中创建，然后在后台运行一个spam筛选的任务。

```python
from django import forms
from django.http import HttpResponseRedirect
from django.template.context import RequestContext
from django.shortcuts import get_object_or_404, render_to_response

from blog import tasks
from blog.models import Comment


class CommentForm(forms.ModelForm):
    
    class Meta:
        model = Comment


def add_comment(request, slug, template_name='comments/create.html'):
    post = get_object_or_404(Entry, slug=slug)
    remote_addr = request.META.get('REMOTE_ADDR')
    
    if request.method == 'POST':
        form = CommentForm(request.POST, request.FILES)
        if form.is_valid():
            comment.save()
            # 异步检查spam comment
            tasks.spam_filter.delay(comment_id=comment.id,
                                    remote_addr=remote_addr)
            return HttpResponseRedirect(post.get_absolute_url())
    else:
        form = CommentForm()

    context = RequestContext(request, {'form': form})
    return render_to_response(template_name, 
                    context_instance=context)
```

筛选spam comment我选择使用Akismet的服务。

```python
from celery import Celery

from akismet import Akismet

from django.core.exceptions import ImproperlyConfigured
from django.contrib.sites.models import Site

from blog.models import Comment

app = Celery(broker='ampq://')


@app.task
def spam_filter(comment_id, remote_addr=None):
    logger = spam_filter.get_logger()       # 获取logger(这么方便?)
    logger.info('Running spam filter for comment %s', comment_id)
    
    comment = Comment.objects.get(pk=comment_id)
    current_domain = Site.objects.get_current().domain
    akismet = Akismet(settings.AKISMET_KEY, 
                    'http://{0}'.format(domain))
    if not akismet.verify_key():
        raise ImproperlyConfigured('Invalid AKISMET_KEY')

    is_spam = akismet.comment_check(user_ip=remote_addr,
                        comment_content=comment.comment,
                        comment_author=comment.name,
                        comment_author_email=comment.email_address)
    if is_spam:
        comment.is_spam = True
        comment.save()

    return is_spam
```



