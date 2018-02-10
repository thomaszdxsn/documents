# Event loops

源代码：[Lib/asyncio/events.py](https://github.com/python/cpython/tree/3.6/Lib/asyncio/events.py)

## Event loop functions

下面的函数是一些快捷方式，用来快速访问global policy的方法。注意这些方法都是提供用来访问默认policy的，除非在这之前使用`set_event_loop_policy()`切换了policy.

- `asyncio.get_event_loop()`

    等同于调用`.get_event_loop_policy().get_event_loop()`.

- `asyncio.set_event_loop(loop)`

    等同于调用`.get_event_loop_policy().set_event_loop(loop)`.

- `asyncio.new_event_loop()`

    等同于`get_event_loop_policy().new_event_loop()`.

## Available event loops

asyncio目前支持两种事件循环的实现：`SelectorEventLoop`和`ProactorEventLoop`

- class`asyncio.SelectorEventLoop`

    基于`selector`模块的事件循环。`AbstractEventLoop`的子类。

    基于系统平台来选择最高效的selector。

- class`asyncio.ProactorEventLoop`

    Windows使用的Proactor事件循环。

Windows使用`ProactorEventLoop`的例子:

```python
import asyncio, sys


if sys.platform == 'win32':
    loop = asyncio.ProactorEventLoop()
    asyncio.set_event_loop(loop)
```

## Platform support

`asyncio`设计于实现可以跨平台移植的，但是每个平台还是有些微妙的差别，可能并不能支持所有的`asyncio`特性。

### Windows

Windows事件循环的一些限制：

- 不支持使用`create_unix_connection()`和`create_unix_server()`
- 不支持使用`add_signal_handler()`和`remove_signal_handler()`
- 不支持`EventLoopPolicy.set_child_watcher()`.`ProactorEventLoop`支持Subprocess.

`SelectorEventLoop`特定的限制:

- `SelectSelector`只支持socket，限制为512sockets。
- `add_reader()`和`add_writer()`只接受socket的文件描述符。
- 不支持Pipe
- 不支持`Subprocesses`

`ProactorEventLoop`特定的限制：

- `create_datagram_endpoint()`(UDP)暂不支持。
- `add_reader()`和`add_writer()`并不支持。

Windows支持的monotonic clock大约是15.6 mesc.最爱方案是0.5 mesc.

### Mac OS X

在Mac OS中，默认的事件循环是`SelectorEventLoop`，它使用`selectors.KqueueSelector`.

### Event loop policies and the default policy

事件循环使用一个*policy*模式来抽象。

对于`asyncio`的大多数用户来说，都不需要直接和policy打交道，默认的global policy已经够用了。

### Event loop policy interface

事件循环policy必须实现下面的接口：

- class`asyncio.AbstractEventLoopPolicy`

    Event loop policy.

    - `get_event_loop()`

        获取当前上下文的事件循环。

        返回一个实现了`AbstractEventLoop`接口的事件循环对象。

        如果当前上下文没有设置事件循环，抛出一个异常。

    - `set_event_loop(loop)`

        将当前上下文的事件循环设为`loop`.

    - `new_event_loop()`

        根据policy规则创建并返回一个新的事件循环对象。

默认的policy会在当前线程定义policy。如果当前线程还没有关联一个事件循环，使用`get_event_loop()`时会在主线程创建默认的policy，否则抛出`RuntimeError`。

### Access to the global loop policy

- `asyncio.get_event_loop_policy()`

    获取当前事件循环的policy.

- `asyncio.set_event_loop_policy(policy)`

    设置当前事件循环的policy。如果`policy`为None，恢复使用默认的policy.

### Customizing the event loop policy

想要实现一个新的事件循环policy，推荐你继承默认事件循环policy`DefaultEventLoopPolicy`，然后重写那些你想要重写的方法，例如：

```python
class MyEventLoopPolicy(asyncio.DefaultEventLoopPolicy):
    
    def get_event_loop(self):
        """Get the event loop.

        This may be None or an instance of EventLoop.
        """
        loop = super().get_event_loop()
        # Do something with loop...
        return loop

asyncio.set_event_loop_policy(MyEventLoopPolicy())
```

