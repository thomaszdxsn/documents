# asyncio -- Asynchronous I/O, event loop, and concurrency tools

*用途:一个异步I/O和并发框架*

`asyncio`模块可以让你使用协程来编写并发应用。`threading`使用应用线程(application threads)来实现并发，`multiprocessing`使用系统进程来实现并发，`asyncio`使用单线程、单进程的方式，不过在任务等候I/O的时候可以切换到其它任务的执行。大多数时候，上下文转换在程序等待读取/写入的堵塞时间发生，不过`asyncio`可以规划代码，让它在一个预定时间运行，让一个协程等待另一个协程完成，或者处理系统信号，或者识别一些事件的发送。

## Asynchronous Concurrency Concepts

多数程序写的并发模型都是线性的，依靠底层的线程/进程管理，在适当的时候切换上下文。基于`asyncio`的应用要求应用代码显式的处理上下文改动。

`asyncio`提供的框架紧紧围绕一个概念 -- 事件循环(event loop)，这个对象负责高效的处理I/O事件，系统事件和应用上下文改动。根据操作系统，提供了若干种不同的事件循环实现。

应用和事件循环的交互是为了代码执行显式的进行注册，资源可用时事件循环进行调用。例如，一个网络服务器开启sockets，然后注册这些sockets，在输入事件出现时告诉它。事件循环在建立新的网络连接或数据读取时通知服务器。应用代码会在I/O堵塞时交出控制权。例如，如果暂时socket没有数据可以读取，服务器应该将控制权交回给事件循环。

这个**把控制权交回给事件循环**的机制是依靠Python的协程来实现的，这是一种特殊的函数，可以将控制权暂时放弃但是不会丢失当前的状态。协程和生成器函数类似，事实上在Python3.5没有原生协程之前，就是使用生成器函数来实现协程的。`asyncio`同样提供了类级别的抽象层，可以编写回调式的异步代码。

`Future`是一种数据结构，代表一个数据的结果还没有完成。事件循环可以观察`Future`对象是否完成，允许应用的一部分代码等待另一部分代码完成。除了`Future`，`asyncio`包含另外一些并发原语，包括locks, semaphores.

`Task`是`Future`是一个子类，它知道如何封装和管理一个协程的执行。Task可以被事件循环规划执行，可以生成一个结果供其它协程使用。

## Cooperative Multitasking with Coroutines

协程是一种(编程)语言结构，设计于用来并发操作。协程函数会在调用时创建一个协程对象，调用者可以使用协程的`.send()`方法来运行它的代码。协程可以使用`await`关键字让另一个协程暂停。当它暂停的时候，协程的状态会保持，在下一次被唤醒时接着使用。

### Starting a Coroutine

`asyncio`有若干种方法可以运行一个协程。最简单地即使用`run_until_complete()`，直接传入一个协程。

#### asyncio_coroutine.py

```python
# asyncio_coroutine.py

import asyncio


async def coroutine():
    print('incoroutine')


event_loop = asyncio.get_event_loop()
try:
    print('starting coroutine')
    coro = coroutine()
    print('entering event loop')
    event_loop.run_until_complete(coro)
finally:
    print('closing event loop')
    event_loop.close()
```

首先是要获取一个事件循环。可以使用默认的循环，或者指定一个事件循环。在这里例子中，我们使用默认的事件循环。`.run_until_complete()`方法使用协程开启了这个循环，在协程退出返回时关闭了循环。

```shell
$ python3 asyncio_coroutine.py

starting coroutine
entering event loop
in coroutine
closing event loop
```

### Returing Values from Coroutines

协程返回的值会发送给它的调用者

#### asyncio_coroutine_return.py

```python
# asyncio_coroutine_return.py
import asyncio


async def coroutine():
    print('in coroutine')
    return 'result'


event_loop = asyncio.get_event_loop()
try:
    return_value = event_loop.run_until_complete(
        coroutine()
    )
    print('it returned {!r}'.format(return_value))
finally:
    event_loop.close()
```

在这个例子中，`.run_until_complete()`会返回协程的结果:

```shell
$ python3 asyncio_coroutine_return.py

in coroutine
it returned: 'result'
```

### Chaining Coroutines

一个协程可以等待另一个协程的结果再执行。这种特性可以让代码分解成更多可重用的部分。下面例子中的两个阶段必须按顺序执行，但是可以并发执行其它操作.

#### asyncio_coroutine_chain.py

```python
# asyncio_coroutine_chain.py

import asyncio


async def outer():
    print('in outer')
    print('waiting for result1')
    result1 = await phase1()
    print('waiting for result2')
    result2 = await phase2(result1)
    return (result1, result2)


async def phase1():
    print('in phase1')
    return 'result1'


async def phase2(arg):
    print('in phase2')
    return "result2 derived from {}".format(arg)


event_loop = asyncio.get_event_loop()
try:
    return_value = event_loop.run_until_complete(outer())
    print('return value: {!r}'.format(return_value))
finally:
    event_loop.close()
```

`await`关键字可以用来代替为事件循环显式地加入新协程，因为控制流已经处于一个事件循环管理的协程里面了，所以不需要再告诉它管理新的协程。

```shell
$ python3 asyncio_coroutine_chain.py

in outer
waiting for result1
in phase1
waiting for result2
in phase2
return value: ('result1', 'result2 derived from result1')
```

### Generators instead of Coroutines

协程函数是`asyncio`设计的一个核心组件。它提供了一个语言层面的构造可以暂停程序一部分的执行，保留调用的状态，在之后可以重新获取这个状态，它们都是并发框架所需的重要能力。

Python3.5引入了新的语言特性来定义原生协程(`async def`)，可以使用`await`来交出控制权，上面`asnycio`的例子都利用了这个新特性。在Python3以前可以使用生成器+`asyncio.coroutine`装饰器+`yield from`来达到相同的效果。

#### asyncio_generator.py

```python
# asyncio_generator.py

import asyncio


@asyncio.generator
def outer():
    print('in outer')
    print('waiting for result1')
    result1 = yield from phase1()
    print('waiting for result2')
    result2 = yield from phase2()
    return (result1, result2)


@asyncio.coroutine
def phase1():
    print('in phase1')
    return 'result1'


@asyncio.coroutine
def phase2(arg):
    print('in phase2')
    return 'result2 derived from {}'.format(arg)


event_loop = asyncio.get_event_loop()
try:
    return_value = event_loop.run_until_complete(outer())
    print('return value: {!r}'.format(return_value))
finally:
    event_loop.close()
```

上面的代码和`asyncio_coroutine_chain.py`结果一样:

```shell
$ python3 asyncio_generator.py

in outer
waiting for result1
in phase1
waiting for result2
in phase2
return value: ('result1', 'result2 derived from result1')
```