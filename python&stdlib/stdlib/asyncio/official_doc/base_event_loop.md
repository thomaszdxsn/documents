# Base Event Loop

源代码地址: [Lib/asyncio/events.py](https://github.com/python/cpython/tree/3.6/Lib/asyncio/events.py)

事件循环(event loop)是`asyncio`提供的中心执行设备(central execution device).它提供的能力包括:

- 注册，执行和取消延时的调用(超时).
- 为不同类型的通信方式创建client/server trasport
- 发动subprocess，以及和外部程序的通信
- 将开销高的函数调用委托给线程池

下面是定义的类:

- class`asyncio.BaseEventLoop`

    这个类是实现的细节。它是`AbstractEventLoop`的一个子类，是`asyncio`实现的主要的事件循环的基类。不应该直接使用它；而是使用`AbstractEventLoop`.`BaseEventLoop`不应该被第三方代码继承，因为它的内部结构还没有稳定下来。

- class`asyncio.AbstractEvnetLoop`

    事件循环的抽象基类。

    这个类**不是线程安全的**


## Run an event loop

- `AbstractEventLoop.run_forever()`

    运行事件循环，直到调用`.stop()`。如果`.stop()`在`.run_forever()`之前调用，这个I/O selector poll以超时为0开启，运行所有规划的callbacks，然后退出。如果在`.run_forever()`运行时调用了`.stop()`，会运行完毕当前这批callback然后退出。注意callback规划的callback不在此列.

- `AbstractEventLoop.run_until_complete(future)`

    运行事件循环，知道`Future`完毕.

    如果参数是一个协程对象，它会被`ensure_future()`封装为一个`Future`.

    返回这个Future的结果，或者抛出一个异常。

- `AbstractEventLoop.is_running()`

    返回事件循环的运行状态。

- `AbstractEventLoop.stop()`

    停止事件循环的运行。

- `AbstractEventLoop.is_closed()`

    如果事件循环已经结束，返回True。

- `AbstractEventLoop.close()`

    关闭这个事件循环。这个循环必须不在运行状态。待定的callback将会丢失。

    这个操作将会清除queue并关闭executor，并不会等待executor未完成的任务。

    这个方法是幂等(idempotent)的，不可逆的(irreversible)。在这个方法之后不应该调用其它方法。

- 协程`AbstractEventLoop.shutdown_asyncgens()`

    规划把所有目前开启的**asynchronous generator**<sup>[1]</sup>关闭.在调用这个方法之后，事件循环在异步生成器被迭代的时候都会发出警告。这个方法应该用于结束所有已规划的异步生成器。例如:

    ```python
    try:
        loop.run_forever()
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()
    ```

## Calls

多数`asyncio`函数不支持关键字参数。如果你想要为callback传入关键字参数，可以使用`functools.partial()`.例如，`loop.call_soon(functools.partial(print, "Hello", flush=True))`，等于调用`print("Hello", flush=True)`.

> 注意
>
> 使用`functools.partial()`比使用`lambda`更好。因为，`asyncio`可以在调试的时候查看`functools.partial()`对象的元数据信息，而`lambda`缺少这些信息。

- `AbstractEventLoop.call_soon(callback, *args)`

    让一个callback被尽快的调用。这个callback会在`call_soon()`返回之后，控制权交回的时候，被调用。

    这个操作是一个`FIFO`对列，callback按照它们注册的顺序被调用。每个callback都会被调用一次。

    任何callback之后的位置参数都会被在调用callback的时候传入。

    最后会返回一个`asyncio.Handle`实例，可以用它来取消这个callback。

- `AbstractEventLoop.call_soon_threadsafe(callback, *args)`

    像`call_soon()`一样，不过是线程安全的。


## Delayed calls

事件循环在它内部有一个时钟，使用它来计算超时。使用的时钟根据系统平台而不同。理论上使用的是monotonic clock。它基本上不同于`time.time()`的时钟。

> 注意：超时不应该超过1天

- `AbstractEventLoop.call_later(delay, callback, *args)`

    在给定的`delay`(秒)之后调用callback.

    callback会被调用一次。如果在同一个事件规划了两个callback，调用顺序是随机的。

    可选位置参数`args`将会在callback被调用的时候穿给它。如果你想传入关键字参数，请使用闭包`functools.partial()`.

- `AbstractEventLoop.call_at(when, callback, *args)`

    在一个给定的时间戳调用callback，时间戳基础为`AbstractEventLoop.time()`.

    这个方法的行为类似于`call_later()`

    然后会返回一个`asyncio.Handle()`实例，可以用它来取消callback.

- `AbstractEventLoop.time()`

    放回当前的时间戳，根据事件循环内部的时钟计算。

## Futures

- `AbstractEventLoop.create_future()`

    创建一个粘附于这个循环的`Future`.

    这是`asyncio`中创建future推荐的方式。

## Tasks

- `AbstractEventLoop.create_task(coro)`

    规划、执行一个**协程对象**：将它封装为一个`Future`对象，返回一个`Task`对象。

    第三方的事件循环可以使用它们自己的`Task`子类。

- `AbstractEventLoop.set_task_factory(factory)`

    设置一个task factory，将会被`AbstractEvent.create_task()`使用。

    如果传入`factory=None`，将会使用默认的task factory.

    如果factory是一个可调用对象，它的签名应该符合`(loop, coro)`，`loop`应该是当前事件循环的引用，`coro`是一个协程对象。这个可调用对象必须返回一个`asyncio.Future`.

- `AbstractEventLoop.get_task_factory()`

    返回一个task factory，如果使用默认的factory则返回None.


## Creating connections

- 协程`AbstractEventLoop.create_connection(protocol_factory, host=None, port=None, *, sll=None, family=0, proto=0, flags=0, sock=None, local_addr=None, server_hostname=None)`

    根据给定的host/port，创建一个stream transport connection.socket famil-`AF_INET`，`AF_INET6`基于host来定(或者根据指定的family)，socket type使用`SOCK_STREAM`.`protocol_factory`必须是一个可调用对象，返回一个protocol实例。

    这个方法式一个协程，它会试着在幕后创建一个连接。在成功之后，这个协程返回一个元组`(transport, protocol)`.

    底层操作按时间顺序的概要如下：

    1. 建立连接，创建一个`transport`来表达它。
    2. `protocol_factory`以无参数形式调用，必须返回一个`protocol`实例。
    3. `protocol`实例绑定了`transport`，然后调用了`connection_made()`方法.
    4. 协程调用成功后，会返回`(transport, protocol)`.

    创建的transport是一个独立实现的双向stream。

    > 注意: `protocol_factory`可以是任何类型的可调用对象，并不是说必须是一个类。例如，如果你想要使用一个预先定义的protocol实例，你可以传`lambda: my_protocol`

    在创建连接时可用的选项包括:

    - ssl

        如果给定了这个值并且非false，将会创建一个SSL/TLS transport(默认会创建一个普通的TCP transport)。如果ssl是一个`ssl.SSLContext`对象，会使用它来创建transport；如果`ssl=True`，将会使用一个默认值的context。

    - server_hostname

        pass

    - family

        pass

    - sock

        pass

    - local_addr

        pass


- 协程`AbstractEventLoop.createa_datagram_endpoint(protocol_facotry, local_addr=None, remote_addr=None, *, family=0, proto=0, flags=0, reuse_port=None, allow_broadcast=None, sock=None)`

    创建一个datagram连接。

    pass

- 协程`AbstractEventLoop.create_unix_connection(protocol_factory, path, *, ssl=None, sock=None)`

    创建Unix连接.

    pass

## Creating listening connections

- 协程`AbstractEventLoop.create_server(protocol_factory, host=None, port=None, *, family=socket.AF_UNSPEC, flags=socket.AI_PASSIVE, sock=None, backlog=100, ssl=None, reuse_address=None, reuse_port=None)`

    创建一个绑定host/port的TCP server.

    返回一个`Server`对象，它的`.sockets`属性包含创建的sockets。使用`Server.close()`方法可以关闭这个server。

    参数：

    ...


- 协程`AbstractEventLoop.create_unix_server(protocol_factory, path=None, *, sock=None, backlog=100, ssl=None)`

    和`AbstractEventLoop.create_server()`类似，不过指定socket family为`AF_UNIX`

    这个方法是一个协程.

- 协程`BaseEventLoop.connect_accpeted_socket(protocol_factory, sock, *, ssl=None)`

    处理一个接受的连接。

    pass


## Watch file descriptors

在Windows和`SelectorEventLoop`，只支持socket处理.

在Windows和`ProactorEventLoop`，这些方法都不支持.

- `AbstractEventLoop.add_reader(fd, callback, *args)`

    开始观察文件描述符，在可以读取的时候以args调用callback。

- `AbstractEventLoop.remove_reader(fd)`

    停止观察文件描述符的可读性。

- `AbstractEventLoop.add_writer(fd, callback, *args)`

    开始观察文件描述符的可写性，然后以args调用callback。

- `AbstractEventLoop.remove_writer(fd)`

    停止观察文件描述符的可写性。

## Low-level socket operations

- 协程`AbstractEventLoop.sock_recv(sock, nbytes)`

    从socket接受数据。

    返回的值是bytes对象，代表接受的数据。一次能接受的最大数量数据可以通过`nbytes`来指定。

    在`SelectorEventLoop`事件循环中，`sock`必须是非堵塞的。

    这个方法是一个协程。

- 协程`AbstractEventLoop.sock_sendall(sock, data)`

    将数据发送到socket。

    这个socket必须连接一个远程socket。这个方法将会持续发送数据，直到数据发送完毕或者有错误出现。在成功的时候会返回None。在错误的情况下，将会抛出exceptions。

    在`SelectorEventLoop`事件循环中，`sock`必须是非堵塞的。

    这个方法是协程。

- 协程`AbstractEventLoop.sock_connect(sock, address)`

    连接一个远程的socket。

    在`SelectorEventLoop`事件循环中，`sock`必须是非堵塞的。

    这个方法是协程。

- 协程`AbstractEventLoop.sock_accept(sock)`

    接受一个连接。

    这个socket必须绑定一个地址并对连接监听。返回的值是一对元组`(conn, address)`.

    `sock`必须是非堵塞的。

    这个方法是一个协程。

## Resolve host name

- 协程`AbstractEventLoop.getaddrinfo(host, port, *, family=0, type=0, proto=0, flags=0)`

    这个方法是一个协程，是非堵塞形式的`socket.getaddrinfo()`

- 协程`AbstractEventLoop.getnameinfo(sockaddr, flags=0)`

    这个方法是一个协程，是非堵塞形式的`socket.getnameinfo()`

## Connect pipes

Windows如果使用`SelectorEventLoop`，不支持这些方法。在Window只有使用`ProactorEventLoop`才支持pipe。

- 协程`AbstractEventLoop.connect_read_pipe(protocol_factory, pipe)`

    在事件循环中注册read pipe.

    `protocol_factory`应该是`Protocol`接口的实例化对象。`pipe`是一个类文件的对象。返回`(transport, protocol)`，transport支持`ReadTransport`接口。

    在事件循环`SelectotrEventLoop`中，pipe必须是非堵塞形式。

    这个方法是一个协程。

- 协程`AbstractEventLoop.connect_write_pipe(protocol_factory, pipe)`

    在事件循环中注册read pipe.

    `protocol_factory`应该是`BaseProtocol`接口的实例化对象。`pipe`是一个类文件对象.返回`(transport, protocol)`，transport支持`WriteTransport`接口。

    在事件循环`SelectotrEventLoop`中，pipe必须是非堵塞形式。

    这个方法是一个协程。

## UNIX signals

- `AbstractEventLoop.add_signal_handler(signum, callback, *args)`

    为信号加入一个handler.
    
    如果signal number是一个非法值，抛出`ValueError`.如果在建立handler时发送错误，抛出`RuntimeError`.

- `AbstractEventLoop.remove_signal_handler(sig)`

    移除一个信号的handler。

    如果handler被移除，返回True，否则返回False。

## Executor

在一个`Executor`(线程池或者进城池)中调用一个函数。默认情况下，事件循环会使用线程池executor。

- 协程`AbstractEventLoop.run_in_executor(executor, func, *args)`

    安排一个函数在指定的executor中运行。

    executor参数应该是一个`Executor`实例。如果传入None，将会使用默认的executor.

    这个方法是一个协程。

- `AbstractEventLoop.set_default_executor(executor)`

    设置一个默认的executor。

## Error Handling API

允许定义事件循环中异常如何处理。

- `AbstractEventLoop.set_exception_handler(handler)`

    设置一个handler，作为事件循环的exception handler。

    如果handler是None，将会使用默认的exception handler。

    如果handler是一个可调用对象，它的签名应该符合`(loop, context)`，`loop`代表当前的事件循环，`context`是一个字典对象(请看`call_exception_handler()`)

- `AbstractEventLoop.get_exception_handler()`

    返回一个exception handler，如果使用了默认handler则返回None。

- `AbstractEventLoop.default_exception_handler(context)`

    默认的exception handler。

    如果出现了一个错误，但是没有设置exception handler，将会调用这个方法。

- `AbstractEventLoop.call_exception_handler(context)`

    调用当前事件循环的exception handler.

    `context`是一个dict对象，包含以下的键：

    - `message`: 错误消息
    - `exception`(可选): Exception对象
    - `future`(可选): `asyncio.Future`实例
    - `handle`(可选): `asyncio.Handle`实例
    - `protocol`(可选): `Protocol`实例
    - `transport`(可选): `Transport`实例
    - `socket`(可选): `socket.socket`实例

    > 注意
    >
    >> 这个方法不应该被子类重写。

## Debug mode

- `AbstractEventLoop.get_debug()`

    获取事件循环的debug模式(bool)

    如果环境变量`PYTHONASYNCIODEBUG`设置为非空字符串，默认值为`True`。否则，默认值为`False`.

- `AbstractEventLoop.set_default(enabled: bool)`

    设置当前事件循环的debug模式。
    

## Server

- class`asyncio.Server`

    监听socket的服务器。

    这个对象使用`AbstractEventLoop.create_server()`方法或`start_server()`函数来创建。不要直接实例化这个类。

    - `close()`

        停止server：关闭监听的socket，设置`.sockets`属性为None。
        
        服务器是异步关闭的，使用协程`.wait_closed()`可以等待服务器关闭。

    - 协程`wait_closed()`

        等待，知道`close()`方法完成。

    - `sockets`

        这个server监听的所有`socket.socket`对象,如果服务器关闭则返回None。

## Handle

- class`asyncio.Handle`

    一个`AbstractEventLoop.call_sonn()`, `AbstractEventLoop.call_sonn_threadsafe()`, `AbstractEventLopp.call_later()`,
    `AbstractEventLoop.call_at()`返回的callback对象.

    - `cancel()`

        取消调用。如果callback已经取消或者被执行，这个方法没有效果。

## Event loop examples

### Hello World with call_soon()

下面这个例子使用`AbstactEventLoop.call_soon()`方法来规划一个callback。这个callback会显示"Hello World"然后停止事件循环：

```python
import asyncio


def hello_world(loop):
    print("Hello World")
    loop.stop()

loop = asyncio.get_event_loop()

# 规划一个打印"hello world"的callback
loop.call_soon(helloword, loop)

loop.run_forever()
loop.close()
```

### Display the current date with call_later()

下面例子中的callback会在每秒都打印当前的日期。这个callback使用`AbstractEventLoop.call_later()`：

```python
import asyncio
import datetime


def display_date(end_time, loop):
    print(datetime.datetime.now())
    if (loop.time() + 1.0) < endtime:
        loop.call_later(1, display_date, end_time, loop)
    else:
        loop.stop()

loop = asyncio.get_event_loop()

end_time = loop.time() + 5.0
loop.call_soon(display_date, end_time, loop)

loop.run_forever()
loop.close()
```

### Watch a file descriptor for read events

使用`AbstractEventLoop.add_reader()`方法来等待一个文件描述符已经可以读取，然后关闭事件循环：

```python
import asyncio
try:
    from socket import socketpair
except ImportError:
    from asyncio.windows_utils import socketpair


rsock, wsock = socketpair()
loop = asyncio.get_event_loop()


def reader():
    data = rsock.recv(100)
    print("Received:", data.decode())
    # 完成，解除文件描述符的注册
    loop.remove_reader(rsock)
    # 停止事件循环
    loop.stop()


# 为read事件注册给文件描述符
loop.add_reader(rsock, reader)

# 模仿从网络中获取数据
loop.call_soon(wsock.send, 'abc'.encode())

# 运行事件循环
loop.run_forever()

# 清理现场
rsock.close()
wsock.close()
loop.close()
```

### Set signal handlers for SIGINT and SIGTERM

使用`AbstractEventLoop.add_signal_handler()`方法为信号SIGINT和SIGTERM注册handlers：

```python
import asyncio
import functools
import os
import signal


def ask_exit(signame):
    print("got signal %s: exit" % signame)
    loop.stop()


loop = asyncio.get_event_loop()
for signame in ("SIGNAME", "SIGTERM"):
    loop.add_signal_handler(getattr(signal, signame),
                            functools.partial(ask_exit, signame))
                            

print("Event loop running forever, press Ctrl+C to interrupt.")
print("pid %s: send SIGINT or SIGTERM to exit." % os.getpid())
try:
    loop.run_forever()
finally:
    loop.close()
# 这里例子只能在Unix中运行
```



## 参考

-- | --
-- | --
[1] | [asynchronous generator](https://docs.python.org/3/glossary.html#term-asynchronous-generator)