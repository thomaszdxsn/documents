## Extensions and Bootsteps

### Custom Message Consumers(自定义消息消费者)

你可以嵌入自定义的Kombu消费者来手动处理你的消息.

假定存在一个特殊的`ConsumerStep`bootstep存在，你只需要定义`get_consumers`方法，在连接建立时这个方法需要返回一个`kombu.Consumer`对象的列表:

```python
from celery import Celery
from celery import bootsteps
from kombu import Consumer, Exchange, Queue

my_queue = Queue('custom', Exchange('custom'), 'routing_key')

app = Celery(broker='amqp://')


class MyConsumerStep(bootsteps.ConsumerStep):

    def get_consumers(self, channel):
        return [Consumer(channel,
                         queues=[my_queue],
                         callbacks=[self.handle_message],
                         accept=['json'])]
    
    def handle_message(self, body, message):
        print("Received message: {0!r}".format(body))
        message.ack()

app.steps['consumer'].add(MyConsumerStep)


def send_me_a_message(who, producer=None):
    with app.producer_or_acquire(producer) as producer:
        producer.publish(
            {'hello': who},
            serializer='json',
            exchange=my_queue.exchange,
            routing_key='routing_key',
            declare=[my_queue],
            retry=True,
        )

if __name__ == '__main__':
    send_me_a_message('world!')
```

> 注意
>
>> Kombu Consumers有两种不同的回调分发机制。上面例子中是一个`callbacks`参数，接受一个回调list，每个回调的签名都是`(body, message)`.
>>
>> 第二种回调机制是使用`on_message`参数，只接受单个回调，回调的签名是`(message,)`.第二种方式不会自动的对payload解码和反序列化。
>>
>> ```python
>> def get_consumers(self, channel):
>>     return [Consumer(channel, queues=[my_queue],
>>                      on_message=self.on_message)]
>>
>>
>> def on_message(self, message):
>>     payload = message.decode()
>>     print(
>>           'Received message: {0!r} {props!r} rawlen={s}'.format(
>>              payload, props=message.properties, s=len(message.body)    
>> ))
>>     message.ack()
>> ```

### Blueprints

Bootsteps是一种为workers增加功能的技术.bootsteps是一个自定义类，它为worker不同阶段中的钩子都定义了自定义的动作/行为。每个bootstep都属于一个blueprint，worker当前定义了两个blueprint: `Worker`和`Consumer`.

> 图1
>
>> `Worker`和`Consumer`这两个blueprint中的bootstep.`worker`蓝本从最下面的Timer开始，它的最后一步是开启`Consumer`蓝本，然后建立broker连接，开始对消息的消费。

![图1](http://docs.celeryproject.org/en/latest/_images/worker_graph_full.png)


#### Worker

Worker是第一个开启的蓝本，然后它启动最主要的组件，如事件循环，进程池，作为timer的ETA任务和其它计时任务.

当Worker启动完成，会进入于与Consumer蓝本的交互，它决定任务如何被执行，连接到broker，开始对消息的消费。

`WorkerController`是核心的worker蓝本实现，它包含的若干方法和属性你都可以在你自己的蓝本中使用.

属性:

- `app`

    当前的app实例.

- `hostname`

    这个worker节点的名称.

- `blueprint`

    这是worker的蓝本BluePrint.

- `hub`

    事件循环对象(`Hub`).你可以使用它为事件循环注册回调。

    它只支持异步I/O的传输(amqp, redis)，如果开启异步以后，`worker.use_eventloop`应该为True.

    你的worker bootstep如果要求必须有`Hub bootstep`:

    ```python
    class WorkerStep(bootsteps.StartStopStep):
        requires = {'celery.worker.components:Hub'}
    ```

- `pool`

    当前的process/eventlet/gevent/thread 池。

    你的worker bootstep如果要求必须有`pool bootstep`:

    ```python
    class WorkerStep(bootsteps.StartStopStep):
        requires = {'celery.worker.components:Pool'}
    ```

- `timer`

    用户规划函数的`Timer`.

    你的worker bootstep如果要求必须有`timer bootstep`:

    ```python
    class WorkerStep(bootsteps.StartStopStep):
        requires = {'celery.worker.components:Timer'}
    ``


- `statedb`

    在worker重启之间维持状态的`Database <celery.worker.state.Persistent>`

    只有在激活`statedb`时才会被定义。

    你的worker bootstep如果要求必须有`statedb bootstep`:

    ```python
    class WorkerStep(bootsteps.StartStopStep):
        requires = {'celery.worker.components:Statedb'}
    ``

- `autoscaler`

    `Autoscaler`用于自动增长和收缩进程池中进程的数量.

    # ...

- `autoreloader`

    在文件系统更改时，`Autoreloader`用来自动进行重启.
    
    # ...

##### Example worker bootstep

```python
from celery import bootsteps


class ExampleWorkerStep(bootsteps.StartStopStep):
    requires = {"celery.worker.compnents:Pool"}

    def __init__(self, worker, **kwargs):
        print('Called when the WorkController instance is constructed')
        print('Arguments to WorkController: {0!r}'.format(kwargs))

    def create(self, worker):
        # this method can be used to delegate the action methods
        # to another object that implements ``start`` and ``stop``.
        return self

    def start(self, worker):
        print('Called when the worker is started.')

    def stop(self, worker):
        print('Called when the worker shuts down.')

    def terminate(self, worker):
        print('Called when the worker terminates')
```

每个方法都会将当前的`WorkerController`实例当做第一个参数。

另一个例子是，使用timer，在有规律的间隔后被唤醒:

```python
from celery import bootsteps


class DeadlockDetection(bootsteps.StartStopStep):
    requires = {'celery.worker.components:Timer'}

    def __init__(self, worker, deadlock_timeout=3600):
        self.timeout = deadlock_timeout
        self.requests = []
        self.tref = None

    def start(self, worker):
        # run every 30 seconds.
        self.tref = worker.timer.call_repeatedly(
            30.0, self.detect, (worker,), priority=10,
        )

    def stop(self, worker):
        if self.tref:
            self.tref.cancel()
            self.tref = None

    def detect(self, worker):
        # update active requests
        for req in worker.active_requests:
            if req.time_start and time() - req.time_start > self.timeout:
                raise SystemExit()
```

#### Consumer

`Consumer`蓝本建立了对broker的连接，如果连接丢失了会自动重连。`Consumer`bootstep包含worker 心跳(heart beat)，远程控制consumer，以及任务消费者.

当你创建`Consumer`bootstep的时候，你必须考虑到它是有可能会重启的。它额外定义了一个`shutdown`bootstep方法,这个方法在worker关闭时被调用.

属性:

- app

- controller

    创建这个consumer的`WorkerController`.

- hostname

- blueprint

- hub

- connection

- event_dispatch

    一个`app.events.Dispatcher`对象.

- gossip

    用于worker和worker之间的广播通信.

- pool

- timer

- heart

- task_consumer

- strategies

- task_buckets

- qos

方法:

- `consumer.reset_rate_limits()`

#...这章主要介绍扩展bootstep，暂时没有这种深度定制的需求，略