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

## Scheduling Calls to Regular Functions

为了管理协程和I/O回调，`asyncio`事件循环可以基于循环中的时钟来规划调用常规函数。

### Scheduling a Callback "Soon"

如果callback运行时机不重要，`call_soon()`可以用来在循环的下一次迭代时调用该函数。任何在这个函数之后的额外参数都会在调用时当作函数参数传入。想要对callback传入关键字参数，请使用`functools.partial`.

#### asyncio_call_soon.py

```python
# asyncio_call_soon.py

import asyncio
import functools


def callbacks(arg, *, kwarg='default'):
    print('callback invoked with {} and {}'.format(arg, kwarg))


async def main(loop):
    print('registering callbacks')
    loop.call_soon(callback, 1)
    wrapped = functools.partial(callback, kwargs='not default')
    loop.call_soon(callback, 2)

    await asyncio.sleep(.1)


event_loop = asyncio.get_event_loop()
try:
    print('entering event loop')
    event_loop.run_until_complete(main(event_loop))
finally:
    print('closing event loop')
    event_loop.close()
```

`callback`将会按规划的顺序执行:

```shell
$ python3 asyncio_call_soon.py

entering event loop
registering callbacks
callback invoked with 1 and default
callback invoked with 2 and not default
closing event loop
```

### Scheduling a Callback with a Delay

想要推迟一个callback的执行时间，可以使用`call_later()`.第一个参数是延时时间，第二个参数即callback。

#### asyncio_call_later.py

```python
# asyncio_call_later.py

import asyncio


def callback(n):
    print('callback {} invoked'.format(n))


async def main(loop):
    print('regestring callbacks')
    loop.call_later(0.2, callback, 1)
    loop.call_later(0.1, callback, 2)
    loop.call_soon(callback, 3)

    await asyncio.sleep(.4)
    

event_loop = asyncio.get_event_loop()
try:
    print('entering event loop')
    event_loop.run_until_complete(main(event_loop))
finally:
    print('closing event loop')
    event_loop.close()
```

在这个例子中，同样一个`callback`函数被规划在不同的时间以不同的参数被调用。最后的实例，使用`call_soon()`，它的结果是最先出来的，以为着"soon"即没有延时.

```shell
$ python3 asyncio_call_later.py

entering event loop
registering callbacks
callback 3 invoked
callback 2 invoked
callback 1 invoked
closing event loop
```

### Scheduling a Callback for a Specific Time

可以在让一个callback在指定的时间运行。loop使用单一时钟(monotonic clock)，而不是挂钟时间，注意值"now"永远不会倒退。想要规划一个callback，需要使用`.time()`方法获取loop的时钟时间。

#### asyncio_call_at.py

```python
# asyncio_call_at.py

import asyncio
import time


def callback(n, loop):
    print('callback {} invoked at {}'.format(n, loop.time()))
    

async def main(loop):
    now = loop.time()
    print('clock time: {}'.format(time.time()))
    print('loop time: {}'.format(now))
    
    print('registering callbacks')
    loop.call_at(now + 0.2, callback, 1, loop)
    loop.call_at(now + 0.1, callback, 2, loop)
    loop.call_soon(callback, 3, loop)

    await asyncio.sleep(1)


event_loop = asyncio.get_event_loop()
try:
    print('entering event loop')
    event_loop.run_until_complete(main(event_loop))
finally:
    print('closing event loop')
    event_loop.close()
```

你可以看到，loop的时间和`time.time()`并不相符:

```shell
entering event loop
clock time: 1479050248.66192
loop  time: 1008846.13856885
registering callbacks
callback 3 invoked at 1008846.13867956
callback 2 invoked at 1008846.239931555
callback 1 invoked at 1008846.343480996
closing event loop
```

## Producing Results Asynchronously

`Future`代表一个还没有执行完成的任务结果。事件循环可以观察`Future`对象的状态直到它完成，利用这个特性可以允许一部分应用代码等待另一部完成。

### Waiting for a Future

`Future`扮演协程的角色，所以任何用于等待协程的技术也可以等待Future完成。下面这个例子把一个Future传入给了事件循环的`.run_until_complete()`方法.

#### asyncio_future_event_loop.py

```python
# asyncio_future_event_loop.py

import asyncio


def mark_done(future, result):
    print('setting future result to {!r}'.format(result))
    future.set_result(result)


event_loop = asyncio.get_event_loop()
try:
    all_done = asyncio.Future()
    
    print('scheduling mark_done')
    event_loop.call_soon(mark_done, all_done, 'the result')
    print('entering event loop')
    result = event_loop.run_until_complete(all_done)
    print('returned result: {!r}'.format(result))
finally:
    print('closing event loop')
    event_loop.close()

print('future result: {!r}'.format(all_done.result()))
```

`Future`可以通过`set_result()`把状态改为`done`，`Future`实例会保留给定的结果并在之后取回.


```shell
$ python3 asyncio_future_event_loop.py

scheduling mark_done
entering event loop
setting future result to 'the result'
returned result: 'the result'
closing event loop
future result: 'the result'
```

#### asyncio_future_await.py

`Future`也可以使用`await`关键字，例如:

```python
# asyncio_future_await.py

import asyncio


def mark_done(future, result):
    print('setting future result to {!r}'.format(result))
    future.set_result(result)


async def main(loop):
    all_done = asyncio.Future()

    print('scheduling mark_done`)
    loop.call_soon(mark_done, all_done, 'the result')
    
    result = await all_done
    print('returned result: {!r}'.format(result))
    

event_loop = asyncio.get_event_loop()
try:
    event_loop.run_until_complete(main(event_loop))
finally:
    event_loop.close()
```

`Future`的结果可以通过`await`返回，所以处理常规协程和Future的代码可以一样。

```shell
$ python3 asyncio_future_await.py

scheduling mark_done
setting future result to 'the result'
returned result: 'the result'
```

### Future Callbacks

为了像协程一样，`Future`可以在完成时调用一些回调函数。Callback按照注册时的顺序被调用。

#### asyncio_future_callback.py

```python
# asyncio_future_callback.py

import asyncio
import functools


def callback(future, n):
    print('{}: future done: {}'.format(n, future_result))


async def register_callbacks(all_done):
    print('registered callbacks on future')
    all_done.add_done_callback(functools.partial(callback, n=1))
    all_done.add_done_callback(functools.partial(callback, n=2))


async def main(all_done):
    await register_callbacks(all_done)
    print('setting result of future')
    all_done.set_result('the result')


event_loop = asyncio.get_event_loop()
try:
    all_done = asyncio.Future()
    event_loop.run_until_complete(main(all_done))
finally:
    event_loop.close()
```

callback首个位置参数应该接受`Future`实例。剩下的参数可以通过`functools.partial()`传入.

```shell
$ python3 asyncio_future_callback.py

registering callbacks on future
setting result of future
1: future done: the result
2: future done: the result
```

## Executing Tasks Concurrently

`Task`是和事件循环交互最主要的一种方式。`Task`封装了协程并在追踪它们知道完成。`Task`是`Future`的子类，所以其它的协程可以等待它完成，可以取回它的结果。

### Starting a Task

想要开启一个Task，可以使用`create_task()`来创建一个`Task`实例。返回的task将会作为并发操作的一部分运行。

#### asyncio_create_task.py

```python
# asyncio_create_task.py

import asyncio


async def task_func():
    print('in task_func')
    return 'the result'

    
async def main(loop):
    print('creating task')
    task = loop.create_task(task_func())
    print('waiting for {!r}'.format(task))
    return_value = await task
    print('task completed {!r}'.format(task))
    print('return value: {!r}'.format(return_value))


event_loop = asyncio.get_event_loop()
try:
    event_loop.run_until_complete(main(event_loop))
finally:
    event_loop.close()
```

这个例子会等待task执行完毕在结束main协程:

```shell
$ python3 asyncio_create_task.py

creating task
waiting for <Task pending coro=<task_func() running at
asyncio_create_task.py:12>>
in task_func
task completed <Task finished coro=<task_func() done, defined at
asyncio_create_task.py:12> result='the result'>
return value: 'the result'
```

### Canceling a Task

对于`create_task()`返回的`Task`对象，可以在它完成之前取消：

```python
# asyncio_cancel_task.py

import asyncio


async def task_func():
    print('in task_func')
    return 'the result'


async def main(loop):
    print('creating task')
    task = loop.create_task(task_func())

    print('canceling task')
    task.cancel()

    print('canceling task {!r}'.format(task))
    try:
        await task
    except asyncio.CancelledError:
        print('caught error from canceled task')
    else:
        print('task result: {!r}'.format(task.result()))


event_loop = asyncio.get_event_loop()
try:
    event_loop.run_until_complete(main(event_loop))
finally:
    event_loop.close()
```

这个例子中Task的创建和取消都是在启动事件循环之前进行。结果是`run_until_complete()`在碰到await一个已取消任务时会抛出`CancelledError`.

```shell
$ python3 asyncio_cancel_task.py

creating task
canceling task
canceled task <Task cancelling coro=<task_func() running at
asyncio_cancel_task.py:12>>
caught error from canceled task
```

#### asyncio_cancell_task2.py

如果一个task在等待另一个并发操作时取消，这个task将会以抛出一个`CancelledError`来通知.

```python
# asyncio_cancel_task2.py

import asyncio


async def task_func():
    print('in task_func, sleeping')
    try:
        await asyncio.sleep(1)
    except asyncio.CancelledError:
        print('task_func was canceled)
        raise
    return 'the result'


def task_canceller(t):
    print('in task_canceller')
    t.cancel()
    print('canceled the task')


async def main(loop):
    print('creating task')
    task = loop.create_task(task_func())
    loop.call_soon(task_canceller, task)
    try:
        await task
    except asyncio.CacelledError:
        print('main() also sees task as canceled')
        

event_loop = asyncio.get_event_loop()
try:
    event_loop.run_until_complete(main(event_loop))
finally:
    event_loop.close()
```

捕获这个异常可以让你有机会做一些清理工作。

```shell
$ python3 asyncio_cancel_task2.py

creating task
in task_func, sleeping
in task_canceller
canceled the task
task_func was canceled
main() also sees task as canceled
```

### Creating Tasks from Coroutines

`ensure_future()`函数返回绑定一个协程的Task。`Task`实例可以传给其它代码，其它的代码可以直接等待它不需要知道它是怎么构造的。

#### asyncio_ensure_future.py

```python
# asyncio_ensure_future.py

import asyncio


async def wrapped():
    print('wrapped')
    return 'result'


async def inner(task):
    print('inner: starting')
    print('inner: waitting for {!r}'.format(task))
    result = await task
    print('inner: task returned {!r}'.format(result))


async def starter():
    print('starter: creating task')
    task = asyncio.ensure_future(wrapped())
    print('starter: waiting for inner')
    await inner(task)
    print('starter: inner returned')


event_loop = asyncio.get_event_loop()
try:
    print('entering event loop')
    result = event_loop.run_until_complete(starter())
finally:
    event_loop.close()
```

注意传入`ensure_future()`的协程(即使被调用)不会被启动，直到有代码await它才会开始执行。

```shell
$ python3 asyncio_ensure_future.py

try:
    print('entering event loop')
    result = event_loop.run_until_complete(starter())
finally:
    event_loop.close()
```

## Composing Coroutines with Control Structure

一系列协程的线形控制流可以简单的通过`await`来管理。更复杂的结构比如并行执行，可以通过`asyncio`的一些工具来实现。

### Waiting for Multiple Coroutines

很常见的一个情况是把一个大任务拆分成若干小的任务分别执行。例如，下载多个远程资源或查询远程API。在这些情况下，执行的顺序不再重要。`wait()`可用来暂停一个协程，直到其它的背后操作完成。

#### asyncio_wait.py

```python
# asyncio_wait.py

import asyncio


async def phase(i):
    print('in phase {}'.format(i))
    await asyncio.sleep(.1 * i)
    print('done with phase {}'.format(i))
    return 'phase {} result'.format(i)


async def main(num_phases):
    print('starting main')
    phases = [
        phase(i)
        for i in range(num_phases)
    ]
    print('waiting for phases to complete')
    completed, pending = await asyncio.wait(phases)
    results = [t.result() for t in completed]
    print('results: {!r}'.format(results))
    

event_loop = asyncio.get_event_loop()
try:
    event_loop.run_until_complete(main(3))
finally:
    event_loop.close()
```

在内部,`wait()`使用一个`set`来保持它创建的Task实例。这些任务的结束顺序是不可预知的。`wait()`返回的值是一个元组，包含结束的任务和待定的任务。

```shell
$ python3 asyncio_wait.py
starting main
waiting for phases to complete
in phase 0
in phase 1
in phase 2
done with phase 0
done with phase 1
done with phase 2
results: ['phase 1 result', 'phase 0 result', 'phase 2 result']
```

#### asyncio_wait_timeout.py

如果我们传入了timeout参数，超时的任务将会是`pending`状态.

```python
# asyncio_wait_timeout.py

import asyncio


async def phase(i):
    print('in phase {}'.format(i))
    try:
        await asyncio.sleep(0.1 * i)
    except asyncio.CancelledError:
        print('phase {} canceled'.format(i))
        raise
    else:
        print("done with phase {}".format(i))
        return "phase {} result".format(i)


async def main(num_phases):
    print('starting main')
    phases = [
        phase(i)
        for i in range(num_phases)
    ]
    print('waiting 0.1 for phases to complete')
    completed, pending = await asyncio.wait(phases, timeout=0.1)
    print('{} completed and {} pending'.format(
        len(completed), len(pending)
    ))
    # 取消待定的任务，这样在我们退出的时候就不会报错
    if pending:
        print('canceling tasks')
        for t in pending:
            t.cancel()
    print('exiting main')


event_loop = asyncio.get_event_loop()
try:
    event_loop.run_until_complete(main(3))
finally:
    event_loop.close()
```

任务要么就完成，要么就取消。如果让任务保持待定状态那么是想要之后继续执行它们。否则退出时会报错.

```shell
$ python3 asyncio_wait_timeout.py

starting main
waiting 0.1 for phases to complete
in phase 1
in phase 0
in phase 2
done with phase 0
1 completed and 2 pending
cancelling tasks
exiting main
phase 1 cancelled
phase 2 cancelled
```

### Gathering Results from Coroutines

如果处理过程都定义好了，只有过程的结果重要，那么`gather()`可能更加适用于并行执行。

#### asyncio_gather.py

```python
# asyncio_gather.py

import asyncio


async def phase1():
    print('in phase1')
    await asyncio.sleep(2)
    print('done with phase1')
    return "phase1 result"


async def phase2():
    print("in phase2")
    await asyncio.sleep(1)
    print("done with phase2")
    return "phase2 result"


async def main():
    print('starting main')
    print('waiting for phases to complete')
    results = await asyncio.gather(
        phase1(),
        phase2()
    )
    print('results: {!r}'.format(results))


event_loop = asyncio.get_event_loop()
try:
    event_loop.run_until_complete(main())
finally:
    event_loop.close()
```

`gather()`创建的tasks没有暴露出来，所以不能取消它们。返回的值是一个result list，顺序和传入`gather()`时保持一致，不管并行操作是否真正完成。

```shell
$ python3 asyncio_gather.py

starting main
waiting for phases to complete
in phase2
in phase1
done with phase2
done with phase1
results: ['phase1 result', 'phase2 result']
```

### Handling Background Operatiosn as They Finish

`as_completed()`是一个生成器，管理给定它的协程list。和`wait()`一样，`as_completed()`并不保证顺序，但使用它不需等待所有的操作都执行完毕。

#### asyncio_as_completed.py

```python
# asyncio_as_completed.py

import asyncio


async def phase(i):
    print('in phase {}'.format(i))
    await asyncio.sleep(0.5 - (0.1 * i))
    print('done with phase {}'.format(i))
    return 'phase {} result'.format(i)


async def main(num_phases):
    print('starting main')
    phases = [
        phase(i)
        for i in range(num_phases)
    ]
    print('waiting for phases to complete')
    results = []
    for next_to_complete in asyncio.as_complete(phases):
        answer = await next_to_complete
        print('received answer {!r}'.format(answer))
        results.append(answer)
    print('results: {!r}'.format(results))
    return results


event_loop = asyncio.get_event_loop()
try:
    event_loop.run_until_complete(main(3))
finally:
    event_loop.close()
```

结果如下：

```shell
$ python3 asyncio_as_completed.py

starting main
waiting for phases to complete
in phase 0
in phase 2
in phase 1
done with phase 2
received answer 'phase 2 result'
done with phase 1
received answer 'phase 1 result'
done with phase 0
received answer 'phase 0 result'
results: ['phase 2 result', 'phase 1 result', 'phase 0 result']
```

## Synchronization Primitives

即使`asyncio`应用通常以单线程进程形式执行，但它仍然是一个并发应用。每个协程或task都会按不可预见的顺序被执行。为了保证安全的并发，`asyncio`加入了`threading`和`multiprocessing`模块的同步原语。

### Locks

`Lock`可以保证安全的对一个共享资源的访问。只有lock的持有者才可以访问资源。多个试图要求lock的请求将会堵塞，所有同时间只能有一个持有者。

#### asyncio_lock.py

```python
# asyncio_lock.py

import asyncio
import functools


def unlock(lock):
    print("callback releasing lock")
    lock.release()


async def coro1(lock):
    print("coro1 waiting for the lock")
    with await lock:
        print("coro1 acquired lock")
    print("coro1 released lock")


async def coro2(lock):
    print("coro2 waiting for the lock")
    await lock
    try:
        print("coro2 acquired lock")
    finally:
        print("coro2 released lock")
        lock.release()


async def main(loop):
    # 创建一个共享锁
    print("acquiring the lock before starting coroutines")
    await lock.acquire()
    print("lock acquired: {}".format(lock.locked()))
    
    # 规划一个callback来解锁lock
    loop.call_later(0.1, functools.partial(unlock, lock))

    # 运行使用lock的协程
    print("waiting for coroutines")
    await asyncio.wait([coro1(lock), coro2(lock)])


event_loop = asyncio.get_event_loop()
try:
    event_loop.run_until_complete(main(event_loop))
finally:
    event_loop.close()
```

lock可以直接调用，也可以使用`await`来请求它，然后使用`.release()`方法释放它，在`coro2()`函数中我们是这样做的。在`coro1()`中，我们使用了异步上下文管理器，使用了关键字`with await`.

```shell
$ python3 asyncio_lock.py

acquiring the lock before starting coroutines
lock acquired: True
waiting for coroutines
coro1 waiting for the lock
coro2 waiting for the lock
callback releasing lock
coro1 acquired lock
coro1 released lock
coro2 acquired lock
coro2 released lock
```

### Events

`asyncio.Event`基于`threading.Event`的概念实现，允许多个消费者等待事件发生(set/wait)。

#### asyncio_event.py

```python
# asyncio_event.py

import asyncio
import functools


def set_event(event):
    print("setting event in callback")
    event.set()


async def coro1(event):
    print("coro1 waitting for event")
    await event.wait()
    print("coro1 triggered")


async def coro2(event):
    print("coro2 waitting for event")
    await event.wait()
    print("coro2 triggered")  


async def main(loop):
    # 创建一个共享的event
    event = asyncio.Event()
    print("event start state: {}".format(event.is_set()))

    loop.call_later(
        0.1, functools.partial(set_event, event)
    )

    await asyncio.wait([coro1(event), coro2(event)])

    print("event end state: {}".format(event.is_set()))


event_loop = asyncio.get_event_loop()
try:
    event_loop.run_until_complete(main(event_loop))
finally:
    event_loop.close()
```

和`Lock`不同，现在`coro1()`和`coro2()`都同时等待event被set，并且它们不需要获取一个唯一的event对象。

```shell
$ python3 asyncio_event.py

event start state: False
coro2 waiting for event
coro1 waiting for event
setting event in callback
coro2 triggered
coro1 triggered
event end state: True
```

### Conditions

`Condition`和`Event`很像，除了它不会一次性唤醒所有的等候者，而是使用`.notify()`方法唤醒指定数量的等候者。

#### asyncio_condition.py

```python
# asyncio_condition.py

import asyncio


async def consumer(condition, n):
    with await condition:
        print("consumer {} is waiting".format(n))
        await condition.wait()
        print("consumer {} triggered".format(n))
    print("ending consumer {}".format(n))


async def manipulate_condition(condition):
    print("starting manipulate_condition")

    # 暂停，让consumers启动
    await asyncio.sleep(.1)

    for i in range(1, 3):
        with await condition:
            print("notifying {} consumers".format(i))
            condition.notify(n=1)
        await asyncio.sleep(.1)

    with await condition:
        print("notifying remaining consumers")
        condition.notify_all()

    print("ending manipulate_condition")


async def main(loop):
    # 创建一个condition
    condition = asyncio.Condition()

    # 设置等待condition的消费者
    consumers = [
        consumer(condition, i)
        for i in range(5)
    ]

    # 规划一个任务，让它来处理condition变量
    loop.create_task(manipulate_condition(condition))

    # 等待消费者完成
    await asyncio.wait(consumers)


event_loop = asyncio.get_event_loop()
try:
    result = event_loop.run_until_complete(main(event_loop))
finally:
    event_loop.close()
```

这个例子为`Condition`开启了5个消费者。每个消费者都使用`wait()`方法等待通知。`manipulate_condition()`依次通知一个消费者、两个消费者....

```shell
$ python3 asyncio_condition.py

starting manipulate_condition
consumer 3 is waiting
consumer 1 is waiting
consumer 2 is waiting
consumer 0 is waiting
consumer 4 is waiting
notifying 1 consumers
consumer 3 triggered
ending consumer 3
notifying 2 consumers
consumer 1 triggered
ending consumer 1
consumer 2 triggered
ending consumer 2
notifying remaining consumers
ending manipulate_condition
consumer 0 triggered
ending consumer 0
consumer 4 triggered
ending consumer 4
```

### Queues

`asyncio.Queue`提供了一个FIFO形式的数据结构，就像线程使用的`queue.Queue`或者进程使用的`multiprocessing.Queue`.

#### asyncio_queue.py

```python
# asyncio_queue.py

import asyncio


async def consumer(n, q):
    print("consumer {}: starting".format(n))
    while True:
        print("consumer {}: waiting for item".format(n))
        item = await q.get()
        print("consumer {}: has item {}".format(n, item))
        if item is None:
            # None是终止的信号
            q.task_done()
            break
        else:
            await asyncio.sleep(0.01 * item)
            q.task_done()
    print("consumer {}: ending".format(n))


async def producer(q, num_workers):
    print("producer: starting")
    # 将一些数字加入到队列中，模拟任务
    for i in range(num_workers * 3):
        await q.put(i)
        print("producer: add task {} to the queue".format(i))
    # 将None加入到队列中，通知消费者退出
    pritn("producer: adding stop signals to the queue")
    for i in range(num_workers):
        await q.put(None)
    print("producer: waiting for queue to empty")
    await q.join()
    print("producer: ending")


async def main(loop, num_consumers):
    # 创建一个固定大小的队列，所以producer也可能堵塞，直到队列空置才能继续
    q = asyncio.Queue(maxsize=num_consumers)

    # 规划consumer任务
    consumers = [
        loop.create_task(consumer(i, q))
        for i in range(num_consumers)
    ]

    # 规划producers任务
    prod = loop.create_task(producer(q, num_consumers))
    
    # 等待所有的协程结束
    await asyncio.wait(consumers + [prod])


event_loop = asyncio.get_event_loop()
try:
    event_loop.run_until_complete(main(event_loop, 2))
finally:
    event_loop.close()
```

使用`.put()`加入item，使用`.get()`移除item，它们都是异步操作(所以要使用await)，因为队列大小可能是固定的(put需要等待)或者为空(get需要等待).

```shell
$ python3 asyncio_queue.py

consumer 0: starting
consumer 0: waiting for item
consumer 1: starting
consumer 1: waiting for item
producer: starting
producer: added task 0 to the queue
producer: added task 1 to the queue
consumer 0: has item 0
consumer 1: has item 1
producer: added task 2 to the queue
producer: added task 3 to the queue
consumer 0: waiting for item
consumer 0: has item 2
producer: added task 4 to the queue
consumer 1: waiting for item
consumer 1: has item 3
producer: added task 5 to the queue
producer: adding stop signals to the queue
consumer 0: waiting for item
consumer 0: has item 4
consumer 1: waiting for item
consumer 1: has item 5
producer: waiting for queue to empty
consumer 0: waiting for item
consumer 0: has item None
consumer 0: ending
consumer 1: waiting for item
consumer 1: has item None
consumer 1: ending
producer: ending
```

## Asynchrounous I/O with Protocol Class Abstractions

直到目前，所有的例子都避免把并发和I/O混合在一起提出，主要是为了防止例子变复杂。不过，在I/O堵塞是上下文转换，是`asyncio`最主要的目的之一。基于已经介绍的并发概念，这个章节使用两个简单的程序实现一个简单的echo服务器/客户端。客户端可以连接到服务器，发送一些数据，然后在相应中收到相同的数据。每次初始化I/O操作时，执行代码都会把控制权交回给事件循环，在I/O堵塞完成前允许其它任务进行。

### Echo Server

#### asyncio_echo_server_protocol.py

```python
# asyncio_echo_server_protocol.py

import asyncio
import logging
import sys

SERVER_ADDRESS = ("localhost", 10000)

logging.basicConfig(
    level=logging.DEBUG,
    format='%(name)s: %(message)s',
    stream=sys.stderr
)
log = logging.getLogger('main')

event_loop = asyncio.get_event_loop()

# 然后继承`asyncio.Protocol`定义一个类，用来处理客户端通信
# 这个协议对象的方法会基于服务器socket中的事件而调用
class EchoServer(asyncio.Protocol):

    # 每个新的客户端连接都会触发调用`.connection_made()`.
    # `transport`参数是`asyncio.Transport`的一个实例,
    # 它提供了异步I/O访问socket的抽象实现。不同类型的通信会
    # 提供不同的transport实现，但是都具有相同的API。
    # 比如，有不同的transport类分别处理socket和subprocess的pipe,
    # 联入的客户端地址可以通过`.get_extra_info()`来获取
    def connection_made(self, transport):
        self.transport = transport
        self.address = transport.get_extra_info('peername')
        self.log = logging.getLogger(
            'EchoServer_{}_{}'.format(**self.address)
        )
        self.log.debug('connection accepted')

    # 在一个连接建立后，在客户端向服务器发送数据时，会调用
    # `data_received()`方法。数据以byte string的形式发送，
    # 由应用自行决定编码方式。下面我们把结果记录到日志，然后使用
    # `transport.write()`将数据立即写回给客户端
    def data_received(self, data):
        self.log.debug('received {!r}'.format(data))
        self.transport.write(data)
        self.log.debug('sent {!r}'.format(data))

    # 一些transport支持一种特殊的*end-of-file*(EOF).
    # 当遇到EOF时，会调用`.eof_received()`方法.
    # 在这种实现中，EOF会被发送给客户端代表它被接受
    # 因为不是所有的Transport都支持显式的EOF，
    # 这个协议首先会询问Transport是否能安全的发送EOF
    def eof_received(self):
        self.log.debug('received EOF')
        if self.transport.can_write_eof():
            self.transport.write_eof()

    # 在一个连接关闭后，不管是正常退出还是非正常退出，
    # 都会调用`connection_lost()`方法 如果有错误存在，
    # 参数`error`将会是一个异常对象，否则为None
    def connection_lost(self, error):
        if error:
            self.log.error('ERROR: {}'.format(error))
        else:
            self.log.debug('closing')
        super().connection_lost(error)


# 启动服务器有两个步骤。首先应用要告诉事件循环，
# 使用protocol类对象 + host + post创建一个server对象
# `.create_server()`方法是一个协程，它的结果应该传入给事件循环
# 完成上述步骤以后，一个`asyncio.Server`实例就绑定了事件循环
factory = event_loop.create_server(EchoServer, *SERVER_ADDRESS)
server = event_loop.run_until_complete(factory)
log.debug('starting up on {} port {}'.format(*SERVER_ADDRESS))

# 然后事件循环应该一直运行，以处理事件和客户端请求。
# 为了获取一个长时间运行的事件循环，可以使用`.run_forever()`方法
# 当事件循环关闭后，不管是在应用层面关闭还是通过信号关闭了进程,
# server应该在退出之前正确清理socket
try:
    event_loop.run_forever()
finally:
    log.debug('closing server')
    server.close()
    event_loop.run_until_complete(server.wait_closed())
    log.debug('closing event loop')
    event_loop.close()
```

### Echo Client

使用Protocol类创建Client的过程和创建Server时很像

#### asyncio_echo_client_protocol.py

```python
# asyncio_echo_client_protocol.py

import asyncio
import functools
import logging
import sys


MESSAGES = [
    b'This is the message. ',
    b'It will be sent ',
    b'in parts.',
]
SERVER_ADDRESS = ('localhost', 10000)

logging.basicConfig(
    level=logging.DEBUG,
    format='%(name)s: %(message)s',
    stream=sys.stderr
)

log = logging.getLogger('main')
event_loop = asyncio.get_event_loop()


class EchoClient(asyncio.Protocol):

    # 客户端的Protocol类和服务器的具有相同方法名，不过是不同的实现方式。
    # 类构造器接受两个参数，一个要发送的消息list，
    # 一个`Future`实例，用来通知客户端是否已经完成了一次消息循环
    def __init__(self, messages, future):
        super().__init__()
        self.messages = messages
        self.log = logging.getLogger('EchoClient')
        self.f = future

    # 当一个客户端和服务器成功连接时，它会立即开始通信。
    # 接下来的消息就会立即发送，虽然下面的传输层会组合多条消息再发送
    # 在所有消息发送完毕后，发送EOF
    
    # 虽然数据会被立即发送，不过transport会缓冲外流的数据,
    # 并设置一个callback。这些过程都是透明处理的
    def connection_made(self, transport):
        self.transport = transport
        self.address = transport.get_extra_info('perrname')
        self.log.debug(
            'connecting to {} port {}'.format(*self.address)
        )
        # 也可以使用`transport.writelines()`
        for msg in self.messages:
            transport.write(msg)
            self.log.debug('sending {!r}'.format(msg))
        if transport.can_write_eof():
            transport.write_eof()

    # 在服务器接受到客户端的数据后，将会记录日志
    def data_received(self, data):
        self.log.debug('received {!r}'.format(data))
        
    # 在碰到服务器端的EOF标记或者连接关闭信号时，
    # 本地的transport对象会关闭，
    # future对象会标记为完成并设置一个结果
    def eof_received(self):
        self.log.debug('received EOF')
        self.transport.close()
        if not self.f.done():
            self.f.set_result(True)
            

    def connection_lost(self, exc):
        self.log.debug("server closed connection")
        self.transport.close()
        if not self.f.done():
            self.f.set_result(True)
        super().connection_lost(exc)


# 通常需要把Protocol类传给事件循环来创建一个连接。
# 在这个例子中，因为事件循环不能为Protocol传入额外的参数,
# 我们必须使用`functools.partial`封装一个对象，
# 然后将它传入事件循环的`create_connection()`方法
client_completed = asyncio.Future()
client_factory = functools.partial(
    EchoClient,
    messages=MESSAGES,
    future=client_completed
)
factory_coroutine = event_loop.create_connection(
    client_factory,
    *SERVER_ADDRESS
)

# 向下面这样连续调用两个协程可以防止死循环
log.debug('waiting for client to complete')
try:
    event_loop.run_until_complete(factory_coroutine)
    event_loop.run_until_complete(client_completed)
finally:
    log.debug('closing event loop')
    event_loop.close()
```

### Output

分别运行上面两个程序:

```shell
$ python3 asyncio_echo_client_protocol.py
asyncio: Using selector: KqueueSelector
main: waiting for client to complete
EchoClient: connecting to ::1 port 10000
EchoClient: sending b'This is the message. '
EchoClient: sending b'It will be sent '
EchoClient: sending b'in parts.'
EchoClient: received b'This is the message. It will be sent in parts.'
EchoClient: received EOF
EchoClient: server closed connection
main: closing event loop

$ python3 asyncio_echo_client_protocol.py
asyncio: Using selector: KqueueSelector
main: waiting for client to complete
EchoClient: connecting to ::1 port 10000
EchoClient: sending b'This is the message. '
EchoClient: sending b'It will be sent '
EchoClient: sending b'in parts.'
EchoClient: received b'This is the message. It will be sent in parts.'
EchoClient: received EOF
EchoClient: server closed connection
main: closing event loop

$ python3 asyncio_echo_client_protocol.py
asyncio: Using selector: KqueueSelector
main: waiting for client to complete
EchoClient: connecting to ::1 port 10000
EchoClient: sending b'This is the message. '
EchoClient: sending b'It will be sent '
EchoClient: sending b'in parts.'
EchoClient: received b'This is the message. It will be sent in parts.'
EchoClient: received EOF
EchoClient: server closed connection
main: closing event loop
```

下面是server程序的日志输出:

```shell
$ python3 asyncio_echo_server_protocol.py
asyncio: Using selector: KqueueSelector
main: starting up on localhost port 10000
EchoServer_::1_63347: connection accepted
EchoServer_::1_63347: received b'This is the message. It will be sent in parts.'
EchoServer_::1_63347: sent b'This is the message. It will be sent in parts.'
EchoServer_::1_63347: received EOF
EchoServer_::1_63347: closing

EchoServer_::1_63387: connection accepted
EchoServer_::1_63387: received b'This is the message. '
EchoServer_::1_63387: sent b'This is the message. '
EchoServer_::1_63387: received b'It will be sent in parts.'
EchoServer_::1_63387: sent b'It will be sent in parts.'
EchoServer_::1_63387: received EOF
EchoServer_::1_63387: closing

EchoServer_::1_63389: connection accepted
EchoServer_::1_63389: received b'This is the message. It will be sent '
EchoServer_::1_63389: sent b'This is the message. It will be sent '
EchoServer_::1_63389: received b'in parts.'
EchoServer_::1_63389: sent b'in parts.'
EchoServer_::1_63389: received EOF
EchoServer_::1_63389: closing
```

## Asynchronous I/O Using Coroutines and Streams

这个章节使用另一种方式实现echo服务器/客户端，使用`asyncio` stream API的协程来替代Protocol和Transport抽象类。

### Echo Server

#### asyncio_echo_server_coroutine.py

```python
# asyncio_echo_server_coroutine.py

import asyncio
import logging
import sys

SERVER_ADDRESS = ('localhost', 10000)
logging.basicConfig(
    level=logging.DEBUG,
    format="%(name)s: %(message)s",
    stream=sys.stderr
)
log = logging.getLogger('main')

event_loop = asyncio.get_event_loop()


# 然后定义一个协程用来处理通讯。每次有客户端连接时,
# 一个新的协程实例将会被调用，所以协程函数的代码每次
# 都会只和一个客户端绑定。Python语言的运行时(runtime)
# 可以管理每个协程实例的状态，应用代码无需管这些

# 协程的参数分别是和新连接绑定的`StreamReader`和
# `StreamWriter`;和`Transport`一样，客户端的地址
# 可以通过`write.get_extra_info()`来获取
async def echo(reader, writer):
    address = writer.get_extra_info('peername')
    log = logging.getLogger('echo_{}_{}'.format(*address))
    log.debug('connection accepted')

    # 即使协程会在连接建立的时候被调用，但是当时可能
    # 仍然没有任何数据。为了避免堵塞式读取，
    # 协程使用`await reader.read()`来让事件循环控制
    while True:
        data = await reader.read(128)

    # 如果客户端发送了数据,它会返回给`await`
    # 多次调用`writer.write()`可以缓冲数据，
    # 然后使用`.drain()`把数据刷新.
    # 由于刷新(flush)网络I/O也可能堵塞，
    # 这里同样要使用`await`
    if data:
        log.debug('received {!r}'.format(data))
        writer.write(data)
        await writer.drain()
        log.debug('sent {!r}'.format(data))
    else:
        # 如果客户端没有发送数据，
        # `read()`返回一个空byte字符串代表连接关闭
        # server需要在写给client的时候关闭sockets
        log.debug('closing')
        writer.close()
        return


# 下面是启动服务器的两个步骤.
# 首先，应用告诉事件循环使用协程来创建一个新的server对象
# `.start_server()`返回一个协程，所以可以直接交给事件循环
factory = asyncio.start_server(echo, *SERVER_ADDRESSES)
server = event_loop.run_until_complete(factory)
log.debug('starting up on {} port {}'.format(**SERVER_ADDRESS))

# 然后使用`.run_forever()`方法来开启服务器
# 在关闭的时候需要使用`server.wait_close()`等待服务器正常关闭
try:
    event_loop.run_forever()
except KeyboardInterrupt:
    pass
finally:
    log.debug('closing server')
    server.close()
    event_loop.run_until_complete(server.wait_closed())
    log.debug('closing event loop')
    event_loop.close()
```

### Echo Client

#### asyncio_echo_client_coroutine.py

```python
# asyncio_echo_client_couroutine.py

import asyncio
import logging
import sys


MESSAGES = [
    b'This is the message ',
    b'It will be sent ',
    b'in parts.'
]

SERVER_ADDRESS = ("localhost", 10000)

logging.basicConfig(
    level=logging.DEBUG,
    format='%(name)s: %(message)s',
    stream=sys.stderr
)
log = logging.getLogger('main')

event_loop = asyncio.get_event_loop()


# echo_client协程接受两个参数
# 分别是服务器的地址，和要发送的消息
async def echo_client(address, messages):
    # 协程会在任务启动时被调用，但是本身并不会开启连接
    # 需要使用`.open_connection()`
    log = logging.getLogger('echo_client')
    log.debug('connecting to {} port {}'.format(*address))
    reader, writer = await asyncio.open_connection(*address)

    # `.open_connection()`协程会返回`(StreamReader, StreamWriter)`
    # 下一步是使用这个writer发送数据给server。
    # 和server代码一样，writer会缓冲数据直到socket准备好,
    # 或者使用`drain()`来刷新。由于刷新操作是网络堵塞I/O，
    # 这里也要使用`await`
    for msg in messages:
        writer.write(msg)
        log.debug('sending {!r}'.format(msg))
    if writer.can_write_eof():
        writer.write_eof()
    await writer.drain()

    # 然后客户端会等待服务器端的响应
    # 为了避免`.read()`堵塞，同样要使用`await`
    # 如果服务器端回复了数据，它会被记录到日志中，
    # 如果没有数据，则标记为连接关闭
    log.debug('waiting for response')
    while True:
        data = await reader.read(128)
        if data:
            log.debug('received {!r}'.format(data))
        else:
            log.debug('closing')
            writer.close()
            return


# 想要开启客户端，很简单
# 直接启动这个协程就好了
try:
    event_loop.run_until_complete(
        echo_client(SERVER_ADDRESS, MESSAGES)
    )
finally:
    log.debug('closing event loop')
    event_loop.close()
```

### Output

client程序的数据:

```shell
$ python3 asyncio_echo_client_coroutine.py
asyncio: Using selector: KqueueSelector
echo_client: connecting to localhost port 10000
echo_client: sending b'This is the message. '
echo_client: sending b'It will be sent '
echo_client: sending b'in parts.'
echo_client: waiting for response
echo_client: received b'This is the message. It will be sent in parts.'
echo_client: closing
main: closing event loop

$ python3 asyncio_echo_client_coroutine.py
asyncio: Using selector: KqueueSelector
echo_client: connecting to localhost port 10000
echo_client: sending b'This is the message. '
echo_client: sending b'It will be sent '
echo_client: sending b'in parts.'
echo_client: waiting for response
echo_client: received b'This is the message. It will be sent in parts.'
echo_client: closing
main: closing event loop

$ python3 asyncio_echo_client_coroutine.py
asyncio: Using selector: KqueueSelector
echo_client: connecting to localhost port 10000
echo_client: sending b'This is the message. '
echo_client: sending b'It will be sent '
echo_client: sending b'in parts.'
echo_client: waiting for response
echo_client: received b'This is the message. It will be sent '
echo_client: received b'in parts.'
echo_client: closing
main: closing event loop
```

server程序的输出:

```shell
$ python3 asyncio_echo_server_coroutine.py
asyncio: Using selector: KqueueSelector
main: starting up on localhost port 10000
echo_::1_64624: connection accepted
echo_::1_64624: received b'This is the message. It will be sent in parts.'
echo_::1_64624: sent b'This is the message. It will be sent in parts.'
echo_::1_64624: closing

echo_::1_64626: connection accepted
echo_::1_64626: received b'This is the message. It will be sent in parts.'
echo_::1_64626: sent b'This is the message. It will be sent in parts.'
echo_::1_64626: closing

echo_::1_64627: connection accepted
echo_::1_64627: received b'This is the message. It will be sent '
echo_::1_64627: sent b'This is the message. It will be sent '
echo_::1_64627: received b'in parts.'
echo_::1_64627: sent b'in parts.'
echo_::1_64627: closing
```

## Using SSL

`asyncio`内置支持对sockets激活SSL通信。传入`SSLContext`实例给协程来创建server/client，可以开启SSL协议。

第一步是创建证书和秘钥文件：

```shell
$ openssl req -newkey ras:2048 -nodes -keyout pymotw.key \ -x509 -days 365 -out pymotw.crt
```

之前例子中使用`start_server()`创建的是不安全socket：

```python
factory = asyncio.start_server(echo, *SERVER_ADDRESS)
server = event_loop.run_until_complete(factory)
```

想要加密，需要创建一个`SSLContext`:

```python
ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
ssl_context.check_hostname = False
ssl_context.load_cert_chain('pymotw.crt', 'pymotw.key')

factory = asyncio.start_server(echo, *SERVER_ADDRESS,
                               ssl=ssl_context)
```

同样的改动也要做用于client端，旧代码是这样的：

```python
reader, writer = await asyncio.open_connection(*address)
```

也要为它创建`SSLContext`对象:

```python
ssl_context = ssl.create_default_context(
    ssl.Purpose.SERVER_AUTH,
)
ssl_context.check_hostname = False
ssl_context.load_verify_locations('pymotw.crt')
reader, writer = await asyncio.open_connection(
    *server_address, ssl=ssl_context)
```

因为SSL连接不支持EOF，client需要使用NULL bytes来代替。

旧代码如下：

```python
for msg in messages:
    writer.write(msg)
    log.debug('sending {!r}'.format(msg))
if writer.can_write_eof():
    writer.write_eof()
await writer.drain()
```

应该改为发送一个zero byte(`b'\x00'`)

```python
for msg in messages:
    writer.write(msg)
    log.debug('sending {!r}'.format(msg))
# SSL does not support EOF, so send a null byte to indicate
# the end of the message.
writer.write(b'\x00')
await writer.drain()
```

`echo()`服务器协程代码必须查找NULL byte，然后再关闭连接。

```python
async def echo(reader, writer):
    address = writer.get_extra_info('peername')
    log = logging.getLogger('echo_{}_{}'.format(*address))
    log.debug('connection accepted')
    while True:
        data = await reader.read(128)
        terminate = data.endswith(b'\x00')
        data = data.rstrip(b'\x00')
        if data:
            log.debug('received {!r}'.format(data))
            writer.write(data)
            await writer.drain()
            log.debug('sent {!r}'.format(data))
        if not data or terminate:
            log.debug('message terminated, closing connection')
            writer.close()
            return
```

**运行结果**:

```shell
$ python3 asyncio_echo_server_ssl.py
asyncio: Using selector: KqueueSelector
main: starting up on localhost port 10000
echo_::1_53957: connection accepted
echo_::1_53957: received b'This is the message. '
echo_::1_53957: sent b'This is the message. '
echo_::1_53957: received b'It will be sent in parts.'
echo_::1_53957: sent b'It will be sent in parts.'
echo_::1_53957: message terminated, closing connection

$ python3 asyncio_echo_client_ssl.py
asyncio: Using selector: KqueueSelector
echo_client: connecting to localhost port 10000
echo_client: sending b'This is the message. '
echo_client: sending b'It will be sent '
echo_client: sending b'in parts.'
echo_client: waiting for response
echo_client: received b'This is the message. '
echo_client: received b'It will be sent in parts.'
echo_client: closing
main: closing event loop
```

## Interacting with Domain Name Services

网络应用通常要使用DNS，`asyncio`提供了一些方便的方法可以避免堵塞DNS查询。

### Address Lookup by Name

使用协程`getaddrinfo()`可以把一个hostname+port转换为IP/IPv6地址。就像`socket`模块的同名函数一样，返回的值是一个tuple list，包含5部分信息:

1. The address family
2. The address type
3. The protocol
4. The canonical name for the sever
5. A socket address tuple suitable for opening a connection to the server on the port originally specified

#### asyncio_getaddrinfo.py

查询可以通过协议过滤，在这个例子中，我们使用返回的TCP响应。

```python
# asyncio_getaddrinfo.py

import asyncio
import logging
import socket
import sys

TARGETS = [
    ('pymotw.com', 'https'),
    ('doughellmann.com', 'https'),
    ('python.org', 'https')
]


async def main(loop, targets):
    for target in targets:
        info = await asyncio.getaddrinfo(
            *target,
            proto=socket.IPPROTO_TCP
        )

        for host in info:
            print("{:20}: {}".format(target[0], host[4][0]))


event_loop = asyncio.get_event_loop()  
try:
    event_loop.run_until_complete(main(event_loop, TARGETS))
finally:
    event_loop.close()
```

这个例子会把一个域名+协议名转换为IP地址+端口号码.

```shell
$ python3 asyncio_getaddrinfo.py

pymotw.com          : 66.33.211.242
doughellmann.com    : 66.33.211.240
python.org          : 23.253.135.79
python.org          : 2001:4802:7901::e60a:1375:0:6
```

### Name Lookup by Address

#### asyncio_getnameinfo.py

协程`getnameinfo()`和之前的例子方向想法，给定它一对(IP地址, 端口)号会获取域名.

```python
# asyncio_getnameinfo.py

import asyncio
import logging
import socket
import sys

TARGETS = [
    ('66.33.211.242', 443),
    ('104.130.43.121', 443),
]

async def main(loop, targets):
    for target in targets:
        info = await loop.getnameinfo(target)
        print('{:15}: {} {}'.format(target[0], *info))


event_loop = asyncio.get_event_loop()
try:
    event_loop.run_until_complete(main(event_loop, TARGETS))
finally:
    event_loop.close()
```

结果如下:

```shell
$ python3 asyncio_getnameinfo.py

66.33.211.242  : apache2-echo.catalina.dreamhost.com https
104.130.43.121 : 104.130.43.121 https
```

## Working with Subprocesses

和其它程序/进程通信是很常见的情况，可以帮助我们利用现成的代码，而不是重复造轮子。和网络I/O一样，`asyncio`包含了可以和其它程序交互的方法.

### Using the Protocol Abstraction with Subprocesses

下面这个例子使用一个协程来运行Unix命令`df`，获取当前磁盘的可用空间。它使用`subprocess_exec()`来发布process，然后把它绑定到一个Protocol类，让我们可以知道如何读取`df`命令的输出。Protocol类会基于subprocess的事件自动调用它的方法。因为`stderr`, `stdin`参数设置为`None`，这些通信频道并不会连接到新的进程.

#### asyncio_subprocess_protocol.py

```python
# asyncio_subprocess_protocol.py

import asyncio
import functools


async def run_df(loop):
    print('in run_df')
    
    cmd_done = asyncio.Future(loop=loop)
    factory = functools.partial(DFProtocol, cmd_done)
    proc = loop.subprocess_exec(
        factory,
        "df", "-hl",
        stdin=None,
        stderr=None
    )
    try:
        print('lanuching process')
        transport, protocol = await proc
        print("waiting for process to complte")
        await cmd_done
    finally:
        transport.close()
    
    return cmd_done.result()


# `DFProtocol`衍生自`SubprocessProtocol`，
# 它定义了和其它进程使用pipeline通讯的API
# `done`参数应该是一个`Future`实例
class DFProtocol(asyncio.SubprocessProtocol):
    FD_NAMES = ['sdtin', 'stdout', 'stderr']

    def __init__(self, done_future):
        self.done = done_future
        self.buffer = bytearray()
        super().__init__()

    # 和socket通信相比，在对新的进程建立起输入频道以后调用
    # `.connection_made()`方法。`transport`参数是
    # `BaseSubprocessTransport`的一个实例。
    def connection_made(self, transport):
        print("process started {}".format(transport.get_pid()))
        self.transport = transport

    # 在process开始生成输出的时候，`pipe_data_received()`
    # 会被调用，并传入一个文件描述符以及pipe中的真实数据。
    def pipe_data_received(self, fd, data):
        print("read {} bytes from {}".format(len(data),
                                             self.FD_NAMES[fd]))
        if fd == 1:
            self.buffer.extend(data)

    # 在process结束以后，会调用`process_exited()`.
    # process的退出code可以通过`transport.get_returnceode()`获取
    def process_exited(self):
        print("process exited")
        return_code = self.transport.get_returncode()
        print("return code {}".format(return_code))
        if not return_code:
            cmd_output = bytes(self.buffer).decode()
            results = self._parse_results(cmd_output)
        else:
            results = []
        self.done.set_result((return_code, results))

    # 命令行输出被解析成一组字典
    def _parse_results(self, output):
        print("parsing results")
        if not output:
            return []
        lines = output.readlines()
        headers = lines[0].split()
        device = [1:]
        results = [
            dict(zip(headers, line.split()))
            for line in device
        ]
        return results


# 这个协程使用`.run_until_complte()`来调用，
# 然后打印各个设备的可用空间
event_loop = asyncio.get_event_loop()
try:
    return_code, results = event_loop.run_until_complte(
        run_df(event_loop)
    )
finally:
    event_loop.close()


if return_code:
    print("error exit {}".format(return_code))
else:
    print("\nFree space:")
    for r in results:
        print("{Mounted:25}: {Avail}".format(**r))
```

输出如下:

```shell
$ python3 asyncio_subprocess_protocol.py

in run_df
launching process
process started 49675
waiting for process to complete
read 332 bytes from stdout
process exited
return code 0
parsing results

Free space:
/                        : 233Gi
/Volumes/hubertinternal  : 157Gi
/Volumes/hubert-tm       : 2.3Ti
```

### Calling Subprocesses with Coroutines and Streams

想要让协程直接运行process，请调用`create_subprocess_exec()`并且指定`stdout`, `stderr`, `stdin`来连接pipe。这个协程的结果是衍生一个`Process`实例。

#### asyncio_subprocess_coroutine.py

```python
# asyncio_subprocess_coroutine.py

import asyncio
import asyncio.subprocess


async def run_df():
    print("in dun_df")

    buffer = bytearray()
    
    create = asyncio.create_subprocess_exec(
        'df', '-hl',
        stdout=asyncio.subprocess.PIPE
    )
    print("lanuching process")
    proc = await create
    print("process started {}".format(proc.pid))


    # 在这个例子中，`df`除了命令行参数以外并不需要任何输入，
    # 所有可以直接读取它的所有输出。
    # 这个例子使用`readline()`，但是和调用`read()`是一样的
    # 命令的输出被缓存了，所以和Protocol例子一样，它可以在之后被解析
    while True:
        line = await proc.stcout.readloine()
        print('read {!r}'.format(line))
        if not line:
            print("no more output from command")
            break
        buffer.extend(line)

    # `readline()`方法在没有输出的时候会返回一个空字符串，
    # 代表程序运行结束了，需要等到程序完整退出
    print("waiting for process to complete")
    await proc.wait()

    # 在这时，退出状态可以检查是否输出中有错误来决定
    # 解析逻辑和之前一样，但是在一个独立的函数中进行(假设有这个函数)
    # 在数据被解析完毕后，结果和退出码被一并返回
    return_code = proc.returncode
    print("return code {}".format(return_code))
    if not return_code:
        cmd_output = bytes(buffer).decode()
        results = _parse_results(cmd_output)
    else:
        results = []
    return return_code, results


# main程序就像之前Protocol例子一样
event_loop = asyncio.get_event_loop()
try:
    return_code, results = event_loop.run_until_complete(
        run_df()
    )
finally:
    event_loop.close()

if return_code:
    print("error exit {}".format(return_code))
else:
    print("\nFree space:")
    for r in results:
        print("{Mounted:25}: {Avail}".format(**results))
```

输出如下:

```shell
in run_df
launching process
process started 49678
read b'Filesystem     Size   Used  Avail Capacity   iused
ifree %iused  Mounted on\n'
read b'/dev/disk2s2  446Gi  213Gi  233Gi    48%  55955082
61015132   48%   /\n'
read b'/dev/disk1    465Gi  307Gi  157Gi    67%  80514922
41281172   66%   /Volumes/hubertinternal\n'
read b'/dev/disk3s2  3.6Ti  1.4Ti  2.3Ti    38% 181837749
306480579   37%   /Volumes/hubert-tm\n'
read b''
no more output from command
waiting for process to complete
return code 0
parsing results

Free space:
/                        : 233Gi
/Volumes/hubertinternal  : 157Gi
/Volumes/hubert-tm       : 2.3Ti
```

### Sending Data to Subprocess

上面的例子都是使用单个通讯频道来读取第二个process的数据。通常需要发送数据给命令来处理。下面这个例子使用Unix命令`tr`来把字符转义到它的输入流中。在这个例子中，`tr`用来把小写字母转换为大写字母。

#### asyncio_subprocess_coroutine_write.py

`to_upper()`协程接受的参数包括一个事件循环和一个输入字符串.它衍生一个子进程处理`tr [:lower:] [:upper:]`.

```python
# asyncio_subprocess_coroutine_write.py

import asyncio
import asyncio.subprocess


async def to_upper(input):
    print("in to_upper")

    create = asyncio.create_subprocess_exec(
        'tr', '[:lower:]', '[:upper:]',
        stdout=asyncio.subprocess.PIPE,
        stdin=asyncio.subprocess.PIPE
    )
    print("lanunching process")
    proc = await create
    print("pid {}".format(proc.pid))

    # 然后，使用Process的`.communicate()`方法来传入输入数据
    # 就像`Subprocess.Popen`版本的相同名称方法一样，
    # 这个方法返回的数据完全是byte strings。
    print("communicating with process")
    stdout, stderr = await proc.communicate(input.encode())
    
    # 在I/O完成以后，需要decode输出结果，然后返回
    return_code = proc.returncode
    print("return code {}".format(return_code))
    if not return_code:
        results = bytes(stdout).decode()
    else:
        results = ''
    return return_code, results


MESSAGE = """
This message will be converted
to all caps.
"""

event_loop = asyncio.get_event_loop()
try:
    return_code, results = event_loop.run_until_complete(
        to_upper(MESSAGE)
    )
finally:
    event_loop.close()

if return_code:
    print("error exit {}".format(return_code))
else:
    print("Original: {!r}".format(MESSAGE))
    print("Changed: {!r}".format(results))
```

输出如下:

```shell
$ python3 asyncio_subprocess_coroutine_write.py

in to_upper
launching process
pid 49684
communicating with process
waiting for process to complete
return code 0
Original: '\nThis message will be converted\nto all caps.\n'
Changed : '\nTHIS MESSAGE WILL BE CONVERTED\nTO ALL CAPS.\n'
```

## Receiving Unix Signals

Unix系统事件通知通常打断一个应用，处罚它的handler。在使用`asyncio`的时候，signal handler在事件循环的协程和回调之间交织。

### asyncio_signal.py

Signal handler必须是普通的callback，而不能是协程。

```python
# asnycio_signal.py

import asyncio
import functools
import os
import signals


def signal_handler(name):
    print("signal_handler({!r}".format(name))

# signal handler使用`.add_signal_handler()`来注册，
# 第一个参数是signal，第二个参数是callback，
# 如果函数需要参数，可以使用`functools.partial`
event_loop = asyncio.get_event_loop()

event_loop.add_signal_handler(
    signal.SIGHUP,
    functools.partial(signal_handler, name='SIGHUP'),
)
event_loop.add_signal_handler(
    signal.SIGUSR1,
    functools.partial(signal_handler, name='SIGUSR1')
)
event_loop.add_signal_handler(
    signal.SIGINT,
    functools.partial(signal_handler, name='SIGINT')   
)

# 这个例子使用一个协程，通过`os.kill()`来发送信号给它自己.
# 在信号发送以后，协程交出控制权，让handler运行.
# 在普通的应用中，可能有多个这样交出控制权的代码
async def send_signals():
    pid = os.getpid()
    print("starting send_signals for {}".format(pid))

    for name in ['SIGHUP', 'SIGHUP', 'SIGUSR1', 'SIGINT']:
        print("sending {}".format(name))
        os.kill(pid, getattr(signal, name))
        # 这里需要把控制权交回给事件循环
        # 否者信号并不会中止程序
        print("yielding control")
        await asyncio.sleep(.01)
    return


# main()会运行`send_singnals()`，直到发送完所有信号
try:
    event_loop.run_until_complete(send_signals())
finally:
    event_loop.close()
```

输出如下：

```shell
$ python3 asyncio_signal.py

starting send_signals for 21772
sending SIGHUP
yielding control
signal_handler('SIGHUP')
sending SIGHUP
yielding control
signal_handler('SIGHUP')
sending SIGUSR1
yielding control
signal_handler('SIGUSR1')
sending SIGINT
yielding control
signal_handler('SIGINT')
```

## Combining Coroutines with Threads and Processes

现存的很多库暂时并不打算支持`asyncio`。它们可能会堵塞，并不能获取asyncio的并发特性。想要异步执行这些代码，可以考虑使用`concurrent.futures`中的executor，开启一个独立的线程/进程。

### Threads

`.run_in_executor()`方法可以接受一个executor实例，一个普通的可调用对象，以及给这个可调用对象的参数。它会返回一个`Future`，可以等待这个函数执行完毕。如果没有传入executor，将会创建一个`ThreadPoolExecutor`.

#### asynio_executor_thread.py

`ThreadPoolExecutor`会开启它的worker线程然后在这个线程中调用这个函数。下面这个展示如何组合使用`run_in_executor()`和`wait()`.

```python
# asyncio_executor_thread.py

import asyncio
import concurrent.futures
import logging
import sys
import time


def blocks(n):
    log = logging.getLogger('blocks({}}'.format(n))
    log.info('running')
    time.sleep(.1)
    log.info('done')
    return n ** 2


async def run_blocking_tasks(executor):
    log = logging.getLogger('run_block_tasks')
    log.info('starting')

    log.info('creating executor tasks')
    loop = asyncio.get_event_loop()
    blocking_tasks = [
        loop.run_until_complete(executor, blocks, i)
        for i in range(6)
    ]
    log.info('waiting for executor tasks')
    completed, pending = await asyncio.wait(blocking_tasks)
    results = [t.result for t in completed]
    log.info('results: {!r}'.format(results))

    log.info('exiting')
    

if __name__ == '__main__':
    # configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(threadName)10s %(name)18s: %(message)s',
        stream=sys.stderr
    )

    # 创建一个有限数量的thread pool
    executor = concurrent.futures.ThreadPoolExecutor(
        max_workers=3
    )
    
    event_loop = asyncio.get_event_loop()
    try:
        event_loop.run_until_complete(
            run_blocking_tasks(executor)
        )
    finally:
        event_loop.close()
```

下面是输出结果:

```shell
$ python3 asyncio_executor_thread.py

MainThread run_blocking_tasks: starting
MainThread run_blocking_tasks: creating executor tasks
  Thread-1          blocks(0): running
  Thread-2          blocks(1): running
  Thread-3          blocks(2): running
MainThread run_blocking_tasks: waiting for executor tasks
  Thread-1          blocks(0): done
  Thread-3          blocks(2): done
  Thread-1          blocks(3): running
  Thread-2          blocks(1): done
  Thread-3          blocks(4): running
  Thread-2          blocks(5): running
  Thread-1          blocks(3): done
  Thread-2          blocks(5): done
  Thread-3          blocks(4): done
MainThread run_blocking_tasks: results: [16, 4, 1, 0, 25, 9]
MainThread run_blocking_tasks: exiting
```

### Processes

`ProcessPoolExecutor`使用方式一样，不过是创建一组worker进程来替代线程。使用独立的进程需要更多的系统资源，但是对于计算密集型任务，这可以利用到每个CPU核心。

#### asyncio_executor_process.py

```python
# asyncio_executor_process.py

# 上面代码和asyncio_executor_thread.py一样

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG,
        format='PID %(process)5s %(name)18s: %(message)s',
        stream=sys.stderr
    )

    # 创建一个有限数量的进程池
    executor = concurrent.futures.ProcessPollExecutor(
        max_workers=3
    )

    event_loop = asyncio.get_event_loop()
    try:
        event_loop.run_until_complete(
            run_blocking_tasks(executor)
        )
    finally:
        event_loop.close()
```

唯一改动就是把executor从thread改为process.

```shell
$ python3 asyncio_executor_process.py

PID 16429 run_blocking_tasks: starting
PID 16429 run_blocking_tasks: creating executor tasks
PID 16429 run_blocking_tasks: waiting for executor tasks
PID 16430          blocks(0): running
PID 16431          blocks(1): running
PID 16432          blocks(2): running
PID 16430          blocks(0): done
PID 16432          blocks(2): done
PID 16431          blocks(1): done
PID 16430          blocks(3): running
PID 16432          blocks(4): running
PID 16431          blocks(5): running
PID 16431          blocks(5): done
PID 16432          blocks(4): done
PID 16430          blocks(3): done
PID 16429 run_blocking_tasks: results: [4, 0, 16, 1, 9, 25]
PID 16429 run_blocking_tasks: exiting
```

## Debugging with asyncio

`asyncio`包含若干实用的调试特性。

首先，事件循环使用`logging`发出运行时状态信息。可以调用`.set_debug()`,传入一个布尔值参数，指出是否应该开启调试。

`asyncio`的应用主要是发现运行失败的协程和事件循环上面运行缓慢的callback.可以设置`slow_callback_duration`property来设定callback运行多久后该给出警告。

最后，如果一个`asyncio`应用退出但没有清理现场，可能会造成一些逻辑错误。开启`ResourceWarning`可以获得这些警告消息.

### asnycio_debug.py

```python
# asyncio_debug.py

import argparse
import asyncio
import logging
import sys
import time
import warnings

parser = argparse.ArgumentParse('debugging asyncio')
parser.add_argument(
    '-v',
    dest='verbose',
    default=False,
    action='store_true'
)
args = parser_args()


logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)7s: %(message)s',
    stream=sys.stderr
)
LOG = logging.getLogger('')


async def inner():
    LOG.info('inner starting')
    # 使用堵塞函数sleep()来模拟一个函数的运行
    time.sleep(.1)
    LOG.info('inner completed')


async outer(loop):
    LOG.info('outer starting')
    await asyncio.ensure_future(loop.create_task(inner()))
    LOG.info('outer completed')


event_loop = asyncio.get_event_loop()
if args.verbose:
    LOG.info('enabling debugging')

    # 激活调试
    event_loop.set_debug(True)

    # 修改slow_callback运行时长警告，
    # 默认值是0.1，即100毫秒
    event_loop.slow_callback_duration = 0.001

    # 报告所有错误管理的异步资源
    warnning.simplefilter('always', ResourceWarning)

LOG.info('entering event loop')
event_loop.run_until_complete(outer(event_loop))
```

在为开启debug模式的时候，看起来还不错:

```shell
$ python3 asyncio_debug.py
  DEBUG: Using selector: KqueueSelector
   INFO: entering event loop
   INFO: outer starting
   INFO: inner starting
   INFO: inner completed
   INFO: outer completed
```

开启debug模式后，可以发现存在一些问题。包括`inner()`的运行时长超标，程序结束后没有正确的关闭事件循环。

```shell
$ python3 asyncio_debug.py -v

  DEBUG: Using selector: KqueueSelector
   INFO: enabling debugging
   INFO: entering event loop
   INFO: outer starting
   INFO: inner starting
   INFO: inner completed
WARNING: Executing <Task finished coro=<inner() done, defined at
asyncio_debug.py:34> result=None created at asyncio_debug.py:44>
took 0.102 seconds
   INFO: outer completed
.../lib/python3.5/asyncio/base_events.py:429: ResourceWarning:
unclosed event loop <_UnixSelectorEventLoop running=False
closed=False debug=True>
  DEBUG: Close <_UnixSelectorEventLoop running=False
closed=False debug=True>
```