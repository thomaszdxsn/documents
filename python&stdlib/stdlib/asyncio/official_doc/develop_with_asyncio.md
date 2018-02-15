# Develop with asyncio

异步编程和“顺序”编程有所不同。这篇文档列出常见的陷阱，以及如何避免它们。

## Debug mode of asyncio

`asyncio`实现的一大目的就是为了获取更好的性能。为了更简单的开发异步代码，你可能想要开启debug模式。

想要开启一个应用的debug检查:

- 通过设置环境变量`PYTHONASYNCIODEBUG`为1来开启全局的asyncio debug模式，或者可以调用`AbstractEventLoop.set_debug()`.
- 将`asyncio.logger`的日志等级设为`DEBUG`.
- 配置`warnings`模块，让它显示`ResourceWarning`。

debug检查的例子:

- 记录**定义了但从不“yield from”的协程**
- 如果在一个错误的线程调用`call_soon()`和`call_at()`方法，将会抛出一个异常。
- 记录selector的执行时间。
- 记录执行时间超过100ms的callback。`AbstractEventLoop.slow_callback_duration`属性可以设置这个阈值。
- 如果transport和事件循环没有显式地关闭，将会发出`ResourceWarning`警告.

## Cancellation

在以前的编程中，一般不会碰到要把任务取消的情况。在异步编程中，它仍然不常见，但是你可以处理这种情况。

Future和Task都可以显式地取消(通过`.cancel()`方法)。`wait_for()`在超时的时候会取消掉仍在等待的task。以及很多其它情况，task都会被间接地取消。

如果future被取消了，不要对它调用`set_result()`和`set_exception()`:

```python
if not fut.cancelled():
    fut.set_result('done')
```

如果你等待一个future，你应该先检查它是否已经取消，已避免无效操作:

```python
@coroutine
def slow_operation(fut):
    if fut.cancelled():
        return
    # ... slow computation ...
    yield from fut
    # ...
```

`shield()`函数可以用来忽略cancellation.

## Concurrency and multithreading

一个事件循环运行在一个线程中，所有的callback和task都在同一个线程中被执行。在事件循环运行一个task的时候，不会在同线程中再运行其它的task。但是当task使用`yield from`的时候，这个task会被暂停，事件循环会执行下一个task。

想要规划另一个线程的callback，应该使用`AbstractEventLoop.call_soon_threadsafe()`:

```python
loop.call_soon_threadsafe(callback, *args)
```

大多数asyncio的对象都不是线程安全的。你只需要担心访问事件循环之外对象的情况。例如，如果想要取消一个future，不要直接调用它的`Future.cancel()`:

```python
python.call_soon_threadsafe(fut.cancel)
```

想要处理信号和执行subprocess，事件循环必须运行在主线程。

想要运行另一个线程中的一个协程，可以使用`run_coroutine_threadsafe()`函数。它会返回一个`concurrent.futures.Future`对象：

```python
future = asyncio.run_coroutine_threadsafe(coro_func(), loop)
result = future.result(timeout)
```

`AbstractEventLoop.run_in_executor()`方法可以使用一个线程池来非堵塞的执行一个callback。

## Handle blocking functions correctly

堵塞函数不应该直接调用。例如，如果一个函数堵塞1秒钟，其它所有的task都会被延时1秒钟，这会对灵活性产生重大影响。

对于网络和subprocess，asyncio提供了高级的API如`protocols`来解决这些问题。

Executor可以把任务在一个独立的线程/进程中执行，不会堵塞事件循环所在的线程。

## Logging

`asyncio`使用名为"asyncio”的logger来记录日志。

asyncio模块默认的日志级别为INFO，可以这样更改:

```python
logging.getLogger('asyncio').setLevel(logging.WARNING)
```

## Detect coroutine object never scheduled

在一个协程函数被调用，但是它的结果没有传入`ensure_future()`或者`.create_task()`，那么这个协程对象永远不会被scheduled，它可能就是个BUG。

下面是bug的例子:

```python
import asyncio

@asyncio.coroutine
def test():
    print("never scheduled")

test()
```

debug模式会输出如下：

```python
Coroutine test() at test.py:3 was never yielded from
Coroutine object created at (most recent call last):
  File "test.py", line 7, in <module>
    test()
```

## Detect exceptions never consumed¶

Python对于未捕获的错误通常会调用`sys.excepthook()`.如果调用了`Future.set_exception()`，但是这个exception永远不被消费，就不会调用`sys.excepthook()`.在这个future被垃圾回收的时候会记录下一条日志，并记录下异常的traceback。

下面是一个未处理异常的例子:

```python
import asyncio

@asyncio.coroutine
def bug():
    raise Exception("not consumed")

loop = asyncio.get_event_loop()
asyncio.ensure_future(bug())
loop.run_forever()
loop.close()
```

输出:

```python
Task exception was never retrieved
future: <Task finished coro=<coro() done, defined at asyncio/coroutines.py:139> exception=Exception('not consumed',)>
Traceback (most recent call last):
  File "asyncio/tasks.py", line 237, in _step
    result = next(coro)
  File "asyncio/coroutines.py", line 141, in coro
    res = func(*args, **kw)
  File "test.py", line 5, in bug
    raise Exception("not consumed")
Exception: not consumed
```

开启debug模式以后的输出:

```python
Task exception was never retrieved
future: <Task finished coro=<bug() done, defined at test.py:3> exception=Exception('not consumed',) created at test.py:8>
source_traceback: Object created at (most recent call last):
  File "test.py", line 8, in <module>
    asyncio.ensure_future(bug())
Traceback (most recent call last):
  File "asyncio/tasks.py", line 237, in _step
    result = next(coro)
  File "asyncio/coroutines.py", line 79, in __next__
    return next(self.gen)
  File "asyncio/coroutines.py", line 141, in coro
    res = func(*args, **kw)
  File "test.py", line 5, in bug
    raise Exception("not consumed")
Exception: not consumed
```

修复这个问题有很多方法。比如将协程chain起来并使用传统的try/except：

```python
@asyncio.coroutine
def handle_exception():
    try:
        yield from bug()
    except Exception:
        print("exception consumed")

loop = asyncio.get_event_loop()
asyncio.ensure_future(handle_exception())
loop.run_forever()
loop.close()
```

或者使用`.run_until_complete()`函数：

```python
task = asyncio.ensure_future(bug())
try:
    loop.run_until_complete(task)
except Exception:
    print("exception consumed")
```

## Chain coroutines correctly

在一个协程函数调用另一个协程函数或者task的时候，应该使用`yield from`把它们链接起来。

下面是一个有bug的用法:

```python
import asyncio

@asyncio.coroutine
def create():
    yield from asyncio.sleep(3.0)
    print("(1) create file")

@asyncio.coroutine
def write():
    yield from asyncio.sleep(1.0)
    print("(2) write into file")

@asyncio.coroutine
def close():
    print("(3) close file")

@asyncio.coroutine
def test():
    asyncio.ensure_future(create())
    asyncio.ensure_future(write())
    asyncio.ensure_future(close())
    yield from asyncio.sleep(2.0)
    loop.stop()

loop = asyncio.get_event_loop()
asyncio.ensure_future(test())
loop.run_forever()
print("Pending tasks at exit: %s" % asyncio.Task.all_tasks(loop))
loop.close()
```

期待的输入为:

```python
(1) create file
(2) write into file
(3) close file
Pending tasks at exit: set()
```

实际输出为:

```python
(3) close file
(2) write into file
Pending tasks at exit: {<Task pending create() at test.py:7 wait_for=<Future pending cb=[Task._wakeup()]>>}
Task was destroyed but it is pending!
task: <Task pending create() done at test.py:5 wait_for=<Future pending cb=[Task._wakeup()]>>
```

事件循环在`create()`结束前就停止了，`close()`在`write()`之前就被调用，因此完全没有按照顺序来。

想要解决这个问题，必须使用`yield from`语法:

```python
@asyncio.coroutine
def test():
    yield from asyncio.ensure_future(create())
    yield from asyncio.ensure_future(write())
    yield from asyncio.ensure_future(close())
    yield from asyncio.sleep(2.0)
    loop.stop()
```

不用`ensure_future()`也是可以的:

```python
@asyncio.coroutine
def test():
    yield from create()
    yield from write()
    yield from close()
    yield from asyncio.sleep(2.0)
    loop.stop()
```

## Pending task destroyed¶

如果一个pending的任务被销毁了，它封装的协程也就不会执行完毕。这可能是个bug，所以记录到了日志中。

日志：

```python
Task was destroyed but it is pending!
task: <Task pending coro=<kill_me() done, defined at test.py:5> wait_for=<Future pending cb=[Task._wakeup()]>>
```

debug模式的日志:

```python
Task was destroyed but it is pending!
source_traceback: Object created at (most recent call last):
  File "test.py", line 15, in <module>
    task = asyncio.ensure_future(coro, loop=loop)
task: <Task pending coro=<kill_me() done, defined at test.py:5> wait_for=<Future pending cb=[Task._wakeup()] created at test.py:7> created at test.py:15>
```

## Close transports and event loop

在一个transport不需要的时候，应该调用它的`.close()`方法来释放它的资源。

事件循环必须显式地关闭。

否则都会发出警告`ResourceWarning`.

