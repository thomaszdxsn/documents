# concurrent.futures -- Manage Pools of Conccurent Tasks

*用途:简单的管理并发和并行任务*

`concurrent.futures`模块提供了接口使用线程/进程池来运行任务。API是相同的，所以应用可以极小改动的情况下在线程和进程之间转换。

这个模块提供了两种类型的类来和pool交互。`executor`可以用来管理pool和worker，`future`可以用来管理worker的计算结果。想要使用worker池，应用需要创建一个适当的executor类，并把任务提交给它让它运行。在每个task启动时，都会返回一个`Future`实例。当需要task的结果时，应用可以使用`Future`来堵塞知道获取了结果。提供了不同的API，可以等待task的完成，所以不需要直接管理`Future`对象。

## Using map() with Basic Thread Pool

`ThreadPoolExecutor`管理了一组worker线程，将任务传给它们可以更加高效的完成。下面这个例子使用`map()`来并发的执行一组任务。这个任务使用`time.sleep()`，暂停不同的时间来模拟任务的耗时，不管并发任务的执行顺序，`map()`总是返回的顺序总是和输入的顺序一致。

### futures_thread_pool_map.py

```python
# futures_thread_pool_map.py

from concurrent import futures
import threading
import time


def task(n):
    print("{}: sleeping {}".format(
        threading.current_thread().name,
        n
    ))
    time.sleep(n / 10)
    print("{}: done with {}".format(
        threading.current_thread().name,
        n
    ))
    return n / 10


ex = futures.ThreadPoolExecutor(max_workers=2)
print("main: starting")
results = ex.map(task, range(5, 0, -1))
print('main: unprocessed results {}'.format(results))
print('main: waiting for real results')
real_results = list(results)
print('main: results: {}'.format(real_results))
```

输出如下：

```shell
$ python3 futures_thread_pool_map.py

main: starting
Thread-1: sleeping 5
Thread-2: sleeping 4
main: unprocessed results <generator object
Executor.map.<locals>.result_iterator at 0x1013c80a0>
main: waiting for real results
Thread-2: done with 4
Thread-2: sleeping 3
Thread-1: done with 5
Thread-1: sleeping 2
Thread-1: done with 2
Thread-1: sleeping 1
Thread-2: done with 3
Thread-1: done with 1
main: results: [0.5, 0.4, 0.3, 0.2, 0.1]
```

## Scheduling Individual Tasks

除了使用`map()`，也可以使用`submit()`提交一个单独的任务，并使用返回的`Future`对象来等待一个任务的结果.

### futures_thread_pool_submit.py

```python
# futures_thread_pool_submit.py

from concurrent import futures
import threading
import time


def task(n):
    print('{}: sleeping {}'.format(
        threading.current_thread().name,
        n)
    )
    time.sleep(n / 10)
    print('{}: done with {}'.format(
        threading.current_thread().name,
        n)
    )
    return n / 10


ex = futures.ThreadPoolExecutor(max_workers=2)
print("main: starting")
f = ex.submit(task, 5)
print("main: future: {}".format(f))
print("main: waiting for results")
result = f.result()
print('main: result: {}'.format(result))
print('main: future after result: {}'.format(f))
```

输出如下：

```shell
$ python3 futures_thread_pool_submit.py

main: starting
Thread-1: sleeping 5
main: future: <Future at 0x1010e6080 state=running>
main: waiting for results
Thread-1: done with 5
main: result: 0.5
main: future after result: <Future at 0x1010e6080 state=finished
 returned float>
```

## Waiting for Tasks in Any Order

调用`Future`对象的`.result()`方法会堵塞直到任务完成(返回一个结果或者抛出异常)，或者可以取消。任务的结果可以使用`.order()`来按顺序获取。如果顺序不是那么重要，可以使用`.as_completed()`来处理它们。

### futures_as_completed.py

```python
# futures_as_completed.py

from concurrent import futures
import random
import time


def task(n):
    time.sleep(random.random())
    return n, n / 10


ex = futures.ThreadPoolExecutor(max_workers=5)
print("main: starting")

wait_for = [
    ex.submit(task, i)
    for i in range(5, 0, -1)
]

for f in futures.as_completed(wait_for):
    print("main: result: {}".format(f.result()))
```

因为池的workers数量和task数量一样，所有的task都可以一同启动。task结束的任务时随机的，所以每次调用的结果都不同。

```shell
$ python3 futures_as_completed.py

main: starting
main: result: (3, 0.3)
main: result: (5, 0.5)
main: result: (4, 0.4)
main: result: (2, 0.2)
main: result: (1, 0.1)
```

## Future Callbacks

想要在一个task完成以后作一些事情，而不用显示的等待结果出现后在手动处理，可以使用`add_done_callback()`来指定一个`Future`完成以后调用的函数。这个callback以单参数`Future`调用.

### futures_future_callback.py

```python
# futures_future_callback.py

from concurrent import futures
import time


def task(n):
    print("{}: sleeping".format(n))
    time.sleep(0.5)
    print("{}: done".format(n))
    return n / 10


def done(fn):
    if fn.cancelled():
        print("{}: canceled".format(fn.arg))
    elif fn.done():
        error = fn.exception()
        if error:
            print("{}: error returned: {}".format(
                fn.arg, error
            ))
        else:
            result = fn.result()
            print("{}: value returned: {}".format(
                fn.arg, result
            ))
            

if __name__ == '__main__':
    ex = futures.ThreadPoolExecutor(max_workers=2)
    print("main: starting")
    f = fx.submit(task, 5)
    f.arg = 5
    f.add_done_back(done)
    result = f.result()
```

输出如下:

```shell
$ python3 futures_future_callback.py

main: starting
5: sleeping
5: done
5: value returned: 0.5
```

## Cancelling Tasks

`Future`可以被取消，如果已经被提交但是还没有启动，可以调用`.cancel()`方法来取消。

### futures_future_callback_cancel.py

```python
# futures_future_callback_cancel.py

from concurrent import futures
import time


def task(n):
    print('{}: sleeping'.format(n))
    time.sleep(0.5)
    print('{}: done'.format(n))
    return n / 10


def done(fn):
    if fn.cancelled():
        print('{}: canceled'.format(fn.arg))
    elif fn.done():
        print('{}: not canceled'.format(fn.arg))


if __name__ == '__main__':
    ex = futures.ThreadPoolExecutor(max_workers=2)
    print("main: starting")
    tasks = []

    for i in range(10, 0, -1):
        print("main: submitting {}".format(i))
        f = ex.submit(task, i)
        f.arg = i
        f.add_done_callback(done)
        tasks.append((i, f))

    for i, t in reversed(tasks):
        if not t.cancel():
            print('main: did not cancel {}'.format(i))
    
    ex.shutdown()
```

`cancel()`返回一个布尔值，代表任务是否成功被取消。

```shell
$ python3 futures_future_callback_cancel.py

main: starting
main: submitting 10
10: sleeping
main: submitting 9
9: sleeping
main: submitting 8
main: submitting 7
main: submitting 6
main: submitting 5
main: submitting 4
main: submitting 3
main: submitting 2
main: submitting 1
1: canceled
2: canceled
3: canceled
4: canceled
5: canceled
6: canceled
7: canceled
8: canceled
main: did not cancel 9
main: did not cancel 10
10: done
10: not canceled
9: done
9: not canceled
```

## Exceptions in Tasks

如果一个task抛出一个未被处理的exception，它会被保存到Future对象中，通过`result()`或者`exception()`来获取它。

### futures_future_exception.py

```python
# futures_future_exception.py

from concurrent import futures


def task(n):
    print("{}: starting".format(n))
    raise ValueError("the value {} is no good".format(n))


ex = futures.ThreadPoolExecutor(max_workers=2)
print("main: starting")
f = ex.submit(task, 5)

error = f.exception()
print("main: error: {}".format(error))

try:
    result = f.result()
except ValueError as e:
    print('main: saw error "{}" when accessing result'.format(e))
```

如果调用`.result()`的时候抛出一个未捕获的异常，这个异常会在当前的上下文中再次抛出。

```shell
$ python3 futures_future_exception.py

main: starting
5: starting
main: error: the value 5 is no good
main: saw error "the value 5 is no good" when accessing result
```

## Context Manager

Executor可以以上下文管理器的方式运行，可以并发的运行task并等待它们完成。在上下文管理器退出的时候，会调用executor的`.shutdown()`方法。

### futures_context_manager.py

```python
# futures_context_manager.py

from concurrent import futures


def task(n):
    print(n)


with futures.ThreadPoolExecutor(max_workers=2) as ex:
    print("main: starting")
    ex.submit(task, 1)
    ex.submit(task, 2)
    ex.submit(task, 3)
    ex.submit(task, 4)

print("main: done")
```

输出如下:

```shell
$ python3 futures_context_manager.py

main: starting
1
2
3
4
main: done
```

## Process Pools

`ProcessPoolExecutor`和`ThreadPoolExecutor`类似，但是使用进程来代替线程。使用进程可以利用多核CPU来进行CPU密集型操作，不会受限于CPython的GIL。

### futures_process_pool_map.py

```python
# futures_process_pool_map.py

from concurrent import futures
import os


def task(n):
    return n, os.getpid()


ex = futures.ProcessPoolExecutor(max_workers=2)
results = ex.map(task, range(5, 0, -1))
for n, pid in results:
    print("ran task {} in process {}".format(n, pid))
```

和线程池一样，单独的worker进程可以用在多个task：

```shell
$ python3 futures_process_pool_map.py

ran task 5 in process 60245
ran task 4 in process 60246
ran task 3 in process 60245
ran task 2 in process 60245
ran task 1 in process 60245
```

### futures_process_pool_broken.py

如果在worker进程运行的时候发生了一些意料之外的事情，`ProcessPoolExecutor`会被认为是“broken”并不再进行任务的规划。

```python
# futures_process_pool_broken.py

from concurrent import futures
import os
import signal


with futures.ProcessPoolExecutor(max_workers=2) as ex:
    print("getting the pid for one worker")
    f1 = ex.submit(os.getpid)
    pid1 = f1.result()

    print("killing process {}".format(pid1))
    os.kill(pid1, signal.SIGHUP)

    print("submitting another task")
    f2 = ex.submit(os.getpid)
    try:
        pid2 = r2.result()
    except futures.process.BrokenProcessPool as e:
        print("could not start new tasks: {}".format(e))
```

异常`BrokenProcessPool`会在结果被处理的时候抛出，而不是任务被提交的时候。

```shell
$ python3 futures_process_pool_broken.py

getting the pid for one worker
killing process 62059
submitting another task
could not start new tasks: A process in the process pool was
terminated abruptly while the future was running or pending.
```

