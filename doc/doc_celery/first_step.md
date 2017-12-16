[TOC]

## 简介

Celery是一个基于分布式消息传递的异步**任务队列**/**job队列**。它聚焦于实时操作，但是同样也支持任务规划。

## 开始学习Celery

Celery是一个电池内置的任务队列。它可以很简单的使用，所以你不需要学会解决异步任务的复杂性就能简单的使用它。它根据最佳实践来设计的，可以轻松整合到你的项目中。

在这篇tutorial中，你将会学会Celery的基础使用：

- 选择和安装一个消息传输工具(broker)
- 安装Celery并创建你的首个任务
- 开启woker并调用task
- 通过不同状态间的过渡来追踪任务，并返回值

Celery初看起来很难－但是不要害怕－这篇tutorial很短时间技能让你入门。它被有意地设计为简单使用，所以高级特性也不会让你困惑。在阅读这篇tutorial以后，最好也阅览一遍剩下的文档.

## 选择一个Broker

Celery需要一个方案来发送和接受消息；通常把这个服务称为"message broker".

有以下的选择可供挑选：

### RabbitMQ

`RabbitMQ`是一个成熟的，稳定，易安装的应用。在生产环境中，这是最好的选择。

如果你使用Ubuntu或者Debian，可以直接输入以下命令下载:

`$ sudo apt-get install rabbitmq-server`

当这个命令完成后，broker将会自动在后台运行，并且会返回一条信息提示你:"Starting rabbitmq-server: SUCCESS".

### Redis

Redis同样是一个成熟的应用。但是在一些down机的情况可能会造成数据的丢失。

### 其它Brokers

请看[broker overview](http://docs.celeryproject.org/en/latest/getting-started/brokers/index.html#broker-overview)


## 安装Celery

Celery已经挂上了PYPI，所以可以通过pip和easy_install来快速安装：

```python
$ pip install celery
```

## 应用

你首先需要的就是一个Celery实例。我们把它叫做`Celery application`，或者更简化的可以称为`app`.这个实例是一个入口点，你所有想要让Celery完成的事情都需要它来实现，比如创建task和管理worker，一般都会通过其它模块来import它。

在这篇tutorial中，我们把一切都放入了单个模块中，但是对于大型项目来说，你需要创建一个[专门的模块](http://docs.celeryproject.org/en/latest/getting-started/next-steps.html#project-layout)

让我们创建文件-`task.py`:

```python
from celery import Celery

app = Celery('tasks', broker='pyamqp://guest@localhost//')

@app.task
def add(x, y):
    return x + y
```

传入`Celery`的第一个参数是当前模块的名称。所以这个参数可以使用`__name__`这个模块变量。

第二个参数是一个`broker`关键字参数，制定你想使用的消息broker的URI，这里使用了RabbitMQ.

你定义了一个简单的task, 叫做`called`,返回两个数字的总和。

## 运行Celery worker服务器

你可以通过`worker`参数来运行woker, 执行我们的程序：

`$ celery -A tasks woker --loglevel=info`

## 调用task

想要调用我们的任务，你可以使用`delay()`方法.

这个方法是`apply_async()`方法的一个缩写，可以让你更加细粒度的控制任务执行：

```python
>>> from tasks import add
>>> add.delay(4, 4)
```

这个任务现在会被你之前开启的worker处理。你可以看看控制台的worker来验证这一点。

结果默认不会被保存。想要在数据库中保持异步任务的执行结果。你需要配置Celery使用一个结果后端(result backend).

## 保持结果

如果你想要保持对任务状态的追踪，Celery需要一个地方来存储/发送状态。这里有若干种result backend可供选择：`SQALchemy/DjangoORM`, `Memcached`, `Redis`, `RPC(RabbitMQ/AMQP)`，或者你可以定义你自己的后端。

在这篇tutorial中，我们使用rpc作为result backend，然后把状态以transient消息来发送。这个后端可以通过`Celery`的关键字参数`backend`来指定(或者如果你使用一个可配置的模块，可以通过`result_backend`配置来设定):

`app = Celery('tasks', backend='rpc://', broker='pyampq://')`

或者你想使用`Redis`作为结果后端，但是仍然选择RabbitMQ作为消息broker(一个很受欢迎的选择):

`app = Celery('tasks', backend='redis://localhost', broker='pyamqp://')`

现在我们配置了result backend，让我们再次调用task.现在在你调用一个task以后，将会返回一个`AsyncResult`实例：

`>>> result = add.delay(4, 4)`

`ready()`方法将会根据任务是否结束而返回布尔值：

```python
>>> result.ready()
False
```

你可以等待结果完成，但是这种用法很奇怪，你把一个异步的调用变为了一个同步的调用：

```python
>>> result.get(timeout=1)
8
```

万一task抛出了异常，`get()`会继续抛出这个异常，但是你可以通过关键字参数`propagate=False`来抑制这个异常：

`>>> result.get(propagate=False)`

如果异常抛出一个异常，你还是可以访问它的traceback:

```python
>>> result.traceback
?
```

## 配置

Celery，像一个消费者应用一样，不需要很多配置。它包含输入和输出。输入必须连接一个broker，输出必须连接一个result backend.

默认的配置可以应用于大多数使用场景，但是有很多选项可以配置让Celery的运行更符合规则。请阅读[Configuration API](http://docs.celeryproject.org/en/latest/userguide/configuration.html#configuration)

配置可以直接用于app，或者使用一个专门的配置模块。比如，你可以通过`task_serializer`配置改变默认的序列化转化器来转换任务payload:

`app.conf.task_serialier = 'json'`

如果你需要一次性更新多个配置，你可以使用方法`update`:

```python
app.conf.update(
    task_serializer='json',
    accept_content['json'],
    result_serializer='json',
    timezone='Europe/Oslo',
    enable_utc=True
)
```

对于大型项目，推荐使用一个专门的配置模块。不推荐使用硬编码的*周期任务间隔*和*任务routing options*.最好把这些东西都集中放在一起。对于项目来说尤其如此，可以让用户控制它们的任务行为.一个集中的配置也允许系统管理员可以修复事件系统的故障。

你可以通过调用`app.config_from_object_('celeryconfig')`方法来告诉一个Celery使用配置模块。

这个模块通常叫做`celeryconfig`，但是你也可以任意为它取名。

在上面的例子中，必须在当前Python路径的目录下面可以读取一个命名为`celeryconfig.py`的模块。看起来像这样：

```python
# celeryconfig.py
broke_url = 'pyamqp://'
result_backend = 'rpc://'

task_serializer = 'json'
result_serializer = 'json'
accept_content = ['json']
timezone = 'Europe/Oslo'
enable_utf = True
```

想要验证配置是否正确，想要确证其中没有语法错误，可以输入：

`$ python -m celeryconfig`


## 为什么result backend没有起作用

自己跟着tutorial碰到的坑就是加上了result backend,但是调用`Result.get()`之后没有返回结果。

原因是因为：意外开启了多个woker, 正巧使用的worker是老的(没有设置过result backend)。所以使用`ps aux | grep "worker"`之后肯定能够发现多个woker进程。

推荐使用supervisor来管理进程.
