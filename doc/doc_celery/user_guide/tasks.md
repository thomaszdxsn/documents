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

logger = get_task_logger

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

