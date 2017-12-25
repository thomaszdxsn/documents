## Routing Tasks

### Basic

#### Automatic routing

使用routing最简单的方式就是直接配置`task_create_missing_queues`.

在开启这个配置以后，一个没有定义在`task_queues`settings中的命名队列将会被自动创建。可以很轻松的执行routing任务.

比如说你有两个服务器x和y，用来处理常规任务。另有一个服务器z，用来处理feed相关任务。你可以这样配置:

```python
task_routes = {'feed.tasks.import_feed': {'queue': 'feeds'}}
```

这个route设置将会把`import_feed`任务routed到`"feeds"`队列，其它的所有任务都将会routed至默认队列("celery").

另外，你可以使用`glob pattern`来匹配，或者正则表达式。匹配`feed.tasks`中的所有任务任务可以这样写：

```python
app.confo.task_routes = {'feed.tasks.*': {'queue': 'feeds'}}
```

如果匹配模式的顺序很重要：

```python
task_routes = ([
    ('feeds.tasks.*', {'queue': 'feeds'}),
    ('web.tasks.*', {'queue': 'web'}),
    (re.compile(r'(video|image)\.tasks\..*'), {"queue": "media"}),
],)
```

`task_routes`设置可以是一个字典，如果有多个route设置那么可以传入一个列表，列表中的元素以元祖表示(`(task_pattern, queue_dict)`)

在设置好route以后，你可以开启服务器z，让它只负责处理feeds队列:

```python
user@z:/$ celery -A proj worker -Q feeds
```

如果你想的话，也可以设置多个队列，只需要逗号分割即可：

```python
user@z:$ celery -A proj worker -Q feeds.celery
```

##### Changing the name of default queue

你可以使用如下配置修改默认队列的名称:

```python
app.conf.task_default_queue = 'default'
```

##### How the queues are defined

比如一个"video"队列可以通过如下设置来创建:

```python
{
    'exchange': 'video',
    'exchange_type': 'direct',
    'routing_key': 'video'
}
```

非AMQP的后端(如Redis,SQS)不支持exchanges，所以需要讲exchange和队列名保持一致.

#### Manual routing

比如说你有两个服务器x和y，用来处理常规任务。另有一个服务器z，用来处理feed相关任务。你可以这样手动配置:

```python
from komku import Queue

app.conf.task_default_queue = 'default'
app.conf.task_queues = (
    Queue('default', routing_key='task.#'),
    Queue('feed_tasks', routing_key='feed.#')
)
task_default_exchange = 'tasks'
task_default_exchange_type = 'topic'
task_default_routing_key = 'task.default'
```

`task_queues`是一个`Queue`实例的列表。如果你没有指定exchange或者exchange_type，它们会从设置中拿取`task_default_exchange`, `task_default_exchange_type`使用.

想要将一个任务route至`feed_tasks`队列，你可以在`task_routes`加入:

```python
task_routes = {
    'feeds.tasks.import_feed': {
        'queue': 'feed_tasks',
        'routing_key': 'feed.import'
    }
}
```

你可以在使用`Task.apply_async()`或者`send_task()`时通过传入参数`routing_key`来覆盖这个设置:

```python
>>> from feeds.tasks import import_feed
>>> import_feed.apply_async(args=['http://cnn.com/rss'],
...                         queue='feed_tasks',
...                         routing_key='feed.import')
```

想要让服务器z单独的消费队列feeds:

```python
user@z:/$ celery -A proj worker -Q feed_tasks --hostname=z@%h
```

服务器x和y必须配置消费default队列：

```python
user@x:/$ celery -A proj worker -Q default --hostname=x@%h
user@y:/$ celery -A proj worker -Q default --hostname=y@%h
```

如果你愿意，z服务器也可以处理默认队列中的任务:

```python
user@z:/$ celery -A proj worker -Q feed_tasks,default --hostname=z@%h
```

如果你有另外一个队列但是需要加入额外的exchange:

```python
from kombu import Exchange, Queue

app.conf.task_queues = (
    Queue('feed_tasks',    routing_key='feed.#'),
    Queue('regular_tasks', routing_key='task.#'),
    Queue('image_tasks',   exchange=Exchange('mediatasks', type='direct'),
                           routing_key='image.compress'),
)
```

如果这些术语把你搞糊涂了，建议阅读AMQP.

### Special Routing Options

#### RabbitMQ Message Priorities

可以通过参数`x-max-priority`来支持队列优先级:

```python
from kombu import Exchange, Queue

app.conf.task_queues = [
    Queue('tasks', Exchange('tasks'), routing_key='tasks',
          queue_arguments={'x-max-priority': 10})
]
```

所有队列的默认优先级可以通过`task_queue_max_priority`来设置:

```python
app.conf.task_queue_max_priority = 10
```

### AMQP Primer

#### Message

message通过一个header和body组成。Celery使用header存储消息的内容类型以及内容编码。内容类型通常是消息的序列化格式。body包含：要执行任务的名称，任务id(UUID)，执行任务要传入的参数以及一些额外的元数据(比如ETA的重试次数).

下面是一个任务消息的Python字典表达形式:

```python
{
    'task': 'myapp.tasks.add',
    'id': '54086c5e-6193-4575-8308-dbab76798756',
    'args': [4, 4],
    'kwargs': {}
}
```

#### Producers, Consumers, and brokers

`client`负责发送消息，一般也把它叫做*发布者(publisher)*，或者*生产者(producer)*，接受消息的实体一般叫做*消费者(consumer)*.

`broker`是消息服务器，在生成者和消费者之间负责传递消息.

#### Exchanges, queues, and routing keys

1. 消息被发送至exchanges
2. 一个exchange会将消息路由至一个或多个队列。如果有不同的exchange类型存在，就提供了不同的路由方式，或者实现了不同的消息场景.
3. 消息将会存在于队列中，知道被某人消费
4. 在消息被ackownledged后，将会从队列中删除

发送和接受消息必要的几个步骤：

1. 创建一个exchange
2. 创建一个队列
3. 将队列绑定到exchange

Celery自动创建`task_queues`配置中需要的实体(除非设置了`auto_declare=False`).

下面是一个例子，关于三个队列的配置；一个用于Video，一个用于Image，另一个默认队列用于一切任务：

```python
from komku import Exchange, Queue

app.conf.task_queues = (
    Queue('default', Exchange('default'), routing_key='default'),
    Queue('Video', Exchange('media'), routing_key='media.video'),
    Queue('Image', Exchange('media'), routing_key='media.image')
)
app.conf.task_default_queue = 'default'
app.conf.task_default_exchange_type = 'direct'
app.conf.task_default_routing_key = 'default'
```

#### Exchange types

exchange type定义了消息如何通过exchange来路由。已经定义的exchange type标准有:`direct`, `topic`, `fanout`以及`headers`.非标准的exchange type可以当做是RabbitMQ的插件获取。比如LRU插件。

##### Direct exchanges

direct类型精确匹配routing key.所以在一个队列绑定了一个routing key以后，只会收到这个routing key的消息.

##### Topic echanges

topic类型使用逗号分割字符来匹配，并且支持通配符:`*`(代表单个字符), `#`(代表零或多个字符)

比如routing key为`usa.news, usa.weather, norway.news, norway.weather`。可以使用`*.news`(所有的news)，`usa.#`(USA所有的东西),或者`usa.weather`(只包含USA的weather)来绑定.

#### Related API commands

- `exchange.declare(exchange_name, type, passive, durable, auto_delete, internal)`

    通过名称声明一个exchange.

    关键字参数：

    - `passive`: passive意味着exchange不会被创建，但是你可以使用它来检查是否exchange已存在.
    - `durable`: Durable exchanges are presistent.
    - `auto_delete`: 如果没有queue使用它，broker可以自动删除这个exchange.

- `queue.declare(queue_name, passive, durable, exclusive, auto_delete)`

    通过名称声明一个队列。

    exclusive队列可以只被当前连接消费。exclusive同样隐含了`auto_delete`.

- `queue.bind(queue_name, exchange_name, routing_key)`

    透过一个routing key，讲队列和exchange绑定。

    解除一个队列的绑定不会收到消息.

- `queue.delete(name, if_unused=False, if_empty=False)`

    删除一个队列和它的绑定。

- `exchange.delete(name, if_unused=False)`

    删除一个exchange.


#### Hands-on with the API

Celery有一个叫做`celery amqp`的工具，可以用来在命令行访问AMQP API，可以用来管理任务，创建/删除队列和exchange，清除队列或者发送消息。它也可以用于非AMQP broker，但是可能并不包含所有的命令。

你可以直接在`celery amqp`后面以参数形式加入命令，或者可以直接无参数启动shell:

```python
$ celery -A proj amqp
-> connecting to amqp://guest@localhost:5672/.
-> connected.
1>
```

这里`1>`是提示，数字1是你已经执行的命令。

让我们来创建一个可以让你发消息的队列:

```python
$ celery -A proj amqp
1> exchange.declare testexchange direct
ok.
2> queue.declare testqueue
ok. queue:testqueue messages:0 consumer:0.
3> queue.bind testqueue testexchange testkey
ok.
```

这些命令分别创建了一个叫做"testexchange"的exchange，一个叫做“testqueue"的queue，以及使"testkey"将两者绑定在一起.

从此所有目标为`testexchange`，以routing key`testkey`发送的消息，都会路由至`testqueue`.你可以使用`basic.publish`命令发送一个消息:

```python
4> basic.publish 'This is a message!' testexchange testkey
ok.
```

然后可以使用`basic.get`来取回消息:

```python
5> basic.get testqueue
{'body': 'This is a message!',
 'delivery_info': {'delivery_tag': 1,
                   'exchange': u'testexchange',
                   'message_count': 0,
                   'redelivered': False,
                   'routing_key': u'testkey'},
 'properties': {}}
```

AMQP使用ackownledgment来标记这个消息已经被收到并且成功处理。如果消息没有被acknowledged并且消息频道已经关闭，这个消息将会分发给其它消费者。

注意上面信息中的`dlivery_tag`没有？在一个连接频道中，每个收到的消息都有一个唯一的`dlivery_tag`.这个tag用于ack。同样注意，`delivery_tag`在跨连接的情况并不是保持唯一的，在其它频道完全有可能有相同的tag值。

你可以使用`basic.ack`来讲这个消息ackownledge.

```python
6> basic.ack 1
ok.
```

在测试完成后，你应该清除你创建的这些实体：

```python
7> queue.delete testqueue
ok. 0 messages deleted.
8> exchange.delete testexchange
ok.
```

### Routing Tasks

#### Defining queues

在Celery中，可以获取的任务队列都定义于`task_queues`设置中。

下面是一个配置的例子:

```python
from komku import Exchange, Queue

app.conf.task_queues = (
    Queue('default', Exchange('default'), routing_key='default'),
    Queue('Video', Exchange('media'), routing_key='media.video'),
    Queue('Image', Exchange('media'), routing_key='media.image')
)
app.conf.task_default_queue = 'default'
app.conf.task_default_exchange_type = 'direct'
app.conf.task_default_routing_key = 'default'
```

这里的`task_default_queue`用于路由没有显示设置路由的任务。(即默认队列)

默认的exchange, exchange type和routing key都将应用于默认队列。

支持单个队列多个绑定：

```python
from kombu import Exchange, Queue, binding

media_exchange = Exchange('media', type='direct')

CELERY_QUEUES = (
    Queue('media', [
        binding(media_exchange, routing_key='media.video'),
        binding(media_exchange, routing_key='media.image')
    ])
)
```

#### Specifying task destination 

一个任务的终点根据如下方法决定(按顺序):

1. 定义于`task_routes`中的`Route`
2. `Task.apply_async()`中的`routing`参数
3. Task对象本身的routing相关属性

最佳实践是不要对这些值硬编码，最好使用Router并且加上配置选项。

####　Routers

router是一个函数，可以确定一个任务的路由选项。

如果你想要定义一个router，只需要定义一个接受参数签名为`(name, args, kwargs, options, task=None, **kw)`的函数：

```python
def route_task(name, args, kwargs, options, task=None, **kw):
    if name == 'myapp.tasks.compress_video':
        return {
            'exchange': 'video',
            "exchange_type": "topic",
            "routing_key": "video.compress"
        }
```

如果你返回queue键，它将会扩展settings`task_queues`中的队列:

```python
{'queues': 'video', 'routing_key': 'video.compress'}
```

变为 -->

```python
{
    'queue': 'video',
    'exchange': "video",
    "exchange_type": "topic",
    "routing_key": "video.compress"
}
```

你需要安装这个`route`函数：

```python
task_routes = (route_task,)
```

也可以以字符串名称形式追加:

```python
task_routes = ('myapp.routers.route_task',)
```

对于上面例子中这种简单的name->route映射，你可以这样做:

```python
task_routes = {
    'myapp.tasks.compress_video': {
        'queue': 'video',
        "routing_key": "video.compress"
    }
}
```

路由可以按顺序遍历，在找到第一个符合的router时停下，并将它作为任务的最终路由。

你可以在序列中使用不同的声明方式:

```pyhton
task_routes = [
    route_task,
    {
        'myapp.tasks.compress_video': {
            'queue': 'video',
            'routing_key': 'video.compress',
    },
]
```

#### Broadcast

Celery支持broadcast路由。下面是一个例子,`broadcast_tasks`分发所有任务的拷贝到已连接的所有worker中:

```python
from kombu.common import Broadcast

app.conf.task_queues = (Broadcast('broadcast_tasks'),)
app.conf.task_routes = {
    'tasks.reload_cache': {
        'queue': 'broadcast_tasks',
        'exchange': "broadcast_tasks"
    }
}
```

现在, `task.reload_cache`任务将会发送到每个消费这个队列的worker中。

下面是另一个例子，使用的是`celery beat`:

```python
from kombu.common import Broadcast
from celery.schedules import crontab

app.conf.task_queues = (Broadcast('broadcast_tasks'),)

app.conf.beat_schedule = {
    'test-task': {
        'task': 'task.reload_cache',
        'schedule': crontab(minute=0, hour='*/3'),
        'options': {'exchange': 'broadcast_tasks'}
    }
}
```

##### Broadcast & Results

如果两个任务具有相同id,celery result不会被定义.如果同样的任务被分配给多个worker，那么状态历史也不会保留。

在这种情况下，最好设置`task.ignore_result`