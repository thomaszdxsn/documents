    ## Optimizing

    ### Introduce

    默认配置做了很多折中方案。这些方案针对某些具体情况时并不是最优解，但是对大多数情况来说也够了。

    下面是一些针对特殊场景下的优化方法。

    ### Ensuring Operations

    有本书提了一个问题:

    *密西西比河每天流出多少水？*

    在编程领域就是指一个系统能在单位时间内处理多少数据。

    在Celery中，如果一个任务需要10分钟来完成，但是每分钟队列中会加入10个新的任务，那么队列永远不会执行完毕。这也是监控队列长度为什么重要的原因。

    有一个办法是使用`Mulin`，它会在队列过长时通知你。

    ### General Settings

    #### librabbitmq

    如果你使用RabbitMQ，那么你可以使用它的一个用C来实现的客户端：`librabbitmq`.

    #### Broker Connection Pool

    在v2.5以后，broker连接池默认开启。

    你可以通过`broker_pool_limit`设置连接池的最小大小。

    #### Using Transient Queues

    Celery创建的队列默认会被持久化。这意味着broker将会把消息写入硬盘以确保在broker重启后，那些消息仍然找得到。

    但是有些情况下，消息丢失了无所谓。你可以创建一个`transient queue`来改进性能:

    ```python
    from komku import Exchange, Queue

    task_queues = (
        Queue('celery', routing_key='celery'),
        Queue('Transient', Exchange('transient', delivery_mode=1),
            routing_key='transient', durable=False)
    )
    ```

    或者通过`task_routes`:

    ```python
    task_routes = {
        'proj.tasks.add': {'queue': 'celery', 'delivery_mode': "transient"}
    }
    ```

    `delivery_mode`可以队列消息的递送方式。值为1代表消息不会被写入到硬盘，值为2（默认）代表消息会被写入到硬盘。

    想要讲一个任务路由自你新定义的队列，可以使用`queue`参数(或者使用设置`task_routes`):

    ```python
    task.apply_async(args, queue='transient')
    ```

    ### Worker Settings

    #### Prefetch Limits

    *Prefetch*是一个源自AMQP的术语，经常被人误解。

    `prefetch limit`是一个worker本身能保留任务/消息数量的限制。如果值为0，这个worker会持续消费消息，不管是否其它worker node是否马上就要消费这个消息，或者消息已经不在内存中。

    worker的默认`prefetch limit`在`worker_prefetch_multiplier`设置中指定。

    这个值的大小和任务的处理时间有关，如果有任务大多需要长时间来处理，那么将这个值设小一点。否则这个值应该设置大一些，不然吞吐量/通信回转的延时会因此而累计增加。

    #### Reserve one task at a time

    [Should I use retry or acks_late?](http://docs.celeryproject.org/en/latest/faq.html#faq-acks-late-vs-retry)

    #### Prefork pool prefetch settings

    prefork pool可以异步发送消息，也就是说它可以影响prefetching task.

    这个行为可以提升性能，但是可以任务会堵塞等待一个长时间运行任务的完成:

    ```python
    -> send task T1 to process A
    # A executes T1
    -> send task T2 to process B
    # B executes T2
    <- T2 complete sent by process B

    -> send task T3 to process A
    # A 仍然在处理T1, T3会在缓存区中等待直到T1完成，另外其它的队列任务不会被发送至闲散的process
    <- T1 complete sent by process A
    # A executes T3 
    ```

    这些等待的任务将会停驻在pipe buffer中。

    你可以使用`-Ofair`选项来禁用这个prefetching行为:

    ```python
    $ celery -A proj worker -l info -Ofair
    ```

    结果:

    ```python
    -> send task T1 to process A
    # A executes T1
    -> send task T2 to process B
    # B executes T2
    <- T2 complete sent by process B

    -> send T3 to process B
    # B executes T3

    <- T3 complete sent by process B
    <- T1 complete sent by process A
    ```


