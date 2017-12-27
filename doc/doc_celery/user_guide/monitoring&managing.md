## Monitoring and Management Guide

### Introduce

有几个工具可以在监控和管理Celery cluster时使用。

这篇文档描述了其中的几种，以及关于监控的特性，比如事件和broadcast命令.

### Workers

#### Management Command Utilities(inspect/control)

`celery`(命令)可以用来监控和管理worker node(以及一些degree任务).

想要获取所有命令的清单:

```python
$ celery help
```

或者某个指定命令的帮助:

```python
$ celery <command> help
```

##### Commands

- `shell`

    进入一个Python shell.

    shell的locals(本地域)中将包含一个celery变量：也就是当前的app.所有已知的任务将会自动加入到这个locals.

    如果使用其它的`Python`实现，可以通过参数指定进入该实现的shell，比如`--bpython`, `ipython`.

- `status`

    将cluster中所有激活node列出清单：

    ```python
    $ celery -A proj status
    ```

- `result`

    展示一个任务的结果

    ```python
    $ celery -A proj result -t tasks.add 4e196aa4-0141-4601-8138-7aa33db0f577
    ```

    注意只要不是使用自定义的result backend。你可以省略掉任务名称，celery可以根据task-id找到它。

- `purge`

    将所有已配置的任务队列清除。

    这个命令将会移除`CELERY_QUQUES`settings中的所有消息.

    > 警告
    >
    >> 这个命令不能撤销，消息会被永久性删除

    ```python
    $ celery -A proj purge
    ```

    可以使用`-Q`来指定要清除的队列：

    ```python
    $ celery -A proj purge -Q celery,foo,bar
    ```

    可以使用`-X`来指定排除出清除范围的队列:

    ```python
    $ celery -A proj purge -X celery
    ```

- `inspect active`

    列出所有激活任务的清单.

    ```python
    $ celery -A proj inspect active
    ```

- `inspect scheduled`

    列出所有被规划ETA任务.

    ```python
    $ celery -A proj inspect scheduled
    ```

    当任务带有`eta`或者`countdown`参数时被worker保留.

- `inspect reserved`

    保存中的任务清单。

    ```python
    $ celery -A proj inspect reserved
    ```

- `inespect revoked`

    被取消任务的历史清单.

    ```python
    $ celery -A proj inspect revoked
    ```

- `inspect registered`

    已注册任务的清单。

    ```python
    $ celery -A proj inspect registered
    ```

- `insepect stats`

    展示worker的统计信息。

    ```python
    $ celery -A proj inspect statas
    ```

- `inspect query_task`

    通过任务ID来展示任务的信息

    任何包含这个任务ID的worker都会回复:

    ```python
    $ celery -A proj inspect query_task e9f6c8f0-fec9-4ae8-a8c6-cf8c8451d4f8
    ```

    你可以查询多个任务的信息:

    ```python
    $ celery -A proj inspect query_task id1 id2 ... idN
    ```

- `control enable_events`

    激活事件

    ```python
    $ celery -A proj control enable_events
    ```

- `control disable_events`

    禁用事件

    ```python
    $ celery -A proj control disable_events
    ```

- `migrate`

    将任务从一个broker迁移到另一个.

    ```python
    $ celery -A proj migrate redis://localhost amqp://localhost
    ```

> Note
>
>> `inspect`和`command`都支持`--timeout`参数。

##### Specifying destination nodes

默认`inspect`和`control`操作会应用到所有worker中。你可以使用`--destination`指定workers:

```python
$ celery -A proj inspect -d w1@e.com,w2@e.com reserved

$ celery -A proj control -d w2@e.com,w2@e.com enable_events
```

#### Flower: Real-time Celery Web-monitor

Flower是一个基于web的，针对Celery的，实时的监控工具。它仍然在开发中，但是已经是一个成熟的工具了。

##### Features

- 使用Celery事件实时监控

    - 任务进度和历史
    - 可以展示任务的细节(arguments, start time, run-time等)
    - 图表和统计

- Remote Control

    - 查看任务状态和统计信息
    - 关闭和重启worker实例
    - 控制worker池的大小
    - 查看和修改一个worker消费的队列
    - 查看当前运行任务
    - 查看规划中的任务(countdown/ETA)
    - 采用time和rate-limit
    - 查看配置
    - 取消或终结任务

- HTTP API

    - worker清单
    - 关闭一个worker
    - 重启worker池
    - 扩展worker池
    - 缩减worker池
    - 自动伸缩worker池
    - 开始从一个队列消费
    - 停止从一个队列消费
    - 任务清单
    - 任务类型清单
    - 获取一个任务的信息
    - 执行一个任务
    - 通过名称执行一个任务
    - 获取一个任务结果
    - 修改一个任务的soft/hard time limit
    - 修改一个任务的rate limit
    - 取消一个任务

- OpenID验证

##### Usage

使用pip来下载安装：

```python
pip install flower
```

使用`flower`命令即可开启一个web服务器:

```python
$ celery -A proj flower
```

默认端口为`http://localhost:5555`，你可以使用`--port`来修改端口：

```python
$ celery -A proj flower --port=5555
```

也可以通过参数`--broker`传入一个broker URL:

```python
$ celery -A proj flower --broker=amqp://guest:guest@localhost:5672//

$ celery -A proj flower --broker=redis://guest:guest@localhost:6379/0
```

然后你可以通过浏览器查看flower了:

```python
$ open http://localhost:5555
```

#### celery events: Curses Monitor

`celery events`是一个简单的curses监控系统，可以查看任务和worker的历史记录。你可以通过inspect result来获得任务的回溯信息，它也支持一些管理命令比如rate-limit, shutdown worker等。

开始:

```python
$ celery -A proj events
```

你将会开到类似`top`的屏幕显示.

`celery events`通常用来开启快照:

```python
$ celery -A proj events --camera=<camera-class> --frequency=1.0
```

另外有一个dump参数，可以将事件导出至`stdout`:

```python
$ celery -A proj events --dump
```

完整的选项列表请使用`--help`查看。


### RabiitMQ

想要管理Celery的话,更重要的是要明白RabbitMQ是如何被监控的。

### Redis

可以通过查看列表长度来观察redis队列.

### Mulin

### Events

无论何时，某个事件发生后,worker就可以发送一条消息.这些事件被flower和events命令利用来监控cluster.

#### Snapshots

即使一个worker可以生成大量的events，将所有任务的历史都存储在硬盘中开销也是很大的.

通过*快照*你可以看到所有状态的任务，但是只需要周期性地将它们写入到硬盘.

想要使用*快照*,你需要一个`Camera`类.在每次快照发生时，你可以将记录信息写入数据库,发送邮件等等...

`celery`然后可以使用这个`Camera`进行快照,比如你想每2秒捕获一次状态：

```python
$ celery -A proj events -c myapp.Camera --frequency=2.0
```

#### Custom Camera

下面是一个`Camera`的例子，它讲快照打印到屏幕上:

```python
from pprint import pformat
from celery.events.snapshot import Polaroid


class DumpCam(Polaroid):
    # clear after flush
    clear_after = True

    def on_shutter(self, state):
        if not state.event_count:
            # No new events since last snapshot
            return
        print('Workers: {0}'.format(pformat(state.workers, indent=4)))
        print('Tasks: {0}'.format(pformat(state.tasks, indent=4)))
        print('Total: {0.event_count} events, {0.task_count} tasks'.format(
            state))
```

可以直接使用这个Camera了:

```python
$ celery -A proj events -c myapp.DumpCam --frequency=2.0
```

或者可以在程序中使用它：

```python
from celery import Celery
from myapp import DumpCam

def main(app, freq=1.0):
    state = app.events.State()
    with app.connection() as conn:
        recv = app.events.Receiver(conn, handlers={"*": state.event})
        with DumpCam(state, freq=freq):
            recv.capture(limit=None, timeout=None)


if __name__ == "__main__":
    app = Celery(broker='amqp://guest@localhost//')
    main(app)
```

#### Real-time processing

处理事件如果是实时的，你需要遵循:

- 一个事件接受者(Receiver)
- 一组handler，在事件发生时调用

    可以设置多个的handler,或者使用通配符*来让一个handler适配多个事件。

- State(可选)

```python
from celery import Celery


def my_monitor(app):
    state = app.events.State()

    def announce_failed_tasks(event):
        state.event(event)
        task = state.tasks.get(event['uuid'])

        print('TASK FAILED: %s[%s] %s' % (
            task.name, task.uuid, task.info(),))

    with app.connection() as connection:
        recv = app.events.Receiver(connection, handlers={
                'task-failed': announce_failed_tasks,
                '*': state.event,
        })
        recv.capture(limit=None, timeout=None, wakeup=True)

if __name__ == '__main__':
    app = Celery(broker='amqp://guest@localhost//')
    my_monitor(app)
```

### Event Reference

#### Task Events

- `task-sent`

    签名: `task-sent(uuid, name, args, kwargs, retries, eta, expires, queue, exchange, routing_key, root_id, parent_id)`

    当`task_send_sent_event`setting激活，并且任务消息已经published后发送这个事件.

- `task-received`

    签名: `task-received(uuid, name, args, kwargs, retries, eta, hostname, timestamp, root_id, parent_id)`

    等worker接受到这个任务时发送这个事件。

- `task-started`

    签名: `task-started(uuid, hostname, timestamp, pid)`

    在worker执行任务之前发送这个事件。

- `task-succeeded`

    签名: `task-succeeded(uuid, result, runtime, hostname, timestamp)`

    如果任务执行成功，发送这个事件。

- `task-failed`

    签名: `task-failed(uuid, exception, traceback, hostname, timestamp)`

    如果任务执行失败，发送这个事件.

- `task-rejected`

    签名: `task-rejected(uuid, requeued)`

    任务被worker拒绝后发送这个事件。可能是重新入列(re-queued)或者移到一个死字队列.

- `task-revoked`

    签名: `task-revoked(uuid, terminated, signum, expired)`

    在任务被取消后发送这个事件。

- `task-retried`

    签名: `task-retried(uuid, exception, traceback, hostname, timestamp)`

    如果任务失败，等待之后retry时,发生这个事件.


#### Worker Events

- `worker-online`

    worker连接到broker并且保持在线。

- `worker-heartbeat`

    每分钟发送一次该事件，如果２分钟都没有收到心跳，那么就可能已经离线.

- `worker-offline`

    worker和broker失去连接后发送这个事件.

    