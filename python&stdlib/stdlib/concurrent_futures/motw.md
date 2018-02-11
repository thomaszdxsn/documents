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

pass