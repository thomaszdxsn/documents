# concurrent.futures -- Lanuching parallel tasks

源代码: 

- [Lib/concurrent/futures/thread.py](https://github.com/python/cpython/tree/3.5/Lib/concurrent/futures/thread.py)
- [Lib/concurrent/futures/process.py](https://github.com/python/cpython/tree/3.5/Lib/concurrent/futures/process.py)

`concurrent.futures`模块提供了异步执行可调用对象的高级接口。

异步执行可以通过线程实现，使用`ThreadPoolExecutor`，或者使用单独的进程，通过`ProcessPoolExecutor`实现。它们都实现了相同的接口，都以一个抽象的`Executor`类定义。

## Executor Objects

- class`concurrent.futures.Executor`

    一个抽象类，可以提供一些方法用于代码的异步执行。不应该直接使用它，而应该继承它使用。

    - `submit(fn, *args, **kwargs)`

        规划一个callback，`fn`，这样来调用:`fn(*args, **kwargs)`，然后返回一个`Future`对象代表可调用对象的执行。

        ```python
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(pow, 323, 1235)
            print(future.result())
        ```

    - `map(func, *iterables, timeout=None, chunksize=1)`

        等同于调用`map(func, *iterables)`，除了`func`是异步并发执行的。如果超时的话会抛出`concurrent.futures.TimeoutError`.对于ProcessPoolExecutor，这个方法会把iterables分隔为若干部分，可以通过`chunksize`参数来指定chunks的大约大小。

    - `shutdown(wait=True)`

        通知executor在完成当前待定的任务之后释放自己所使用的资源。在shutdown以后再调用`.submit()`或`.map()`，会抛出`RuntimeError`.

        如果你使用上下文管理器，不需要显示的调用这个方法。

## ThreadPoolExecutor

`ThreadPoolExecutor`是一个`Executor`的子类，可以使用线程池来异步执行可调用对象。

如果一个`Future`等待另一个`Future`的结果，可能会造成死锁：

```python
import time


def wait_on_b():
    time.sleep(5)
    print(b.result())   # b永远不会完成，因为它等待a
    return 5


def wait_on_a():
    time.sleep(5)
    print(a.result())   # a永远不会完成，因为它等待b
    return 6


executor = ThreadPoolExecutor(max_workers=2)
a = executor.submit(wait_on_b)
b = executor.submit(wait_on_a)
```

另外:

```python
def wait_on_future():
    f = executor.submit(pow, 5, 2)
    # 这个函数永远不会执行，因为只有一个worker线程
    # 而这个线程正在执行这个函数
    print(f.result())


executor = ThreadPoolExecutor(max_workers=1)
executor.submit(wait_on_future)
```

- class`concurrent.futures.ThreadPoolExecutor(max_workers=None)`

    一个`Executor`的子类，使用`max_workers`个数量线程的一个pool来异步执行可调用对象。

### ThreadPoolExecutor Example

```python
import concurrent.futures
import urllib.request

URLS = [
    'http://www.foxnews.com/',
    'http://www.cnn.com/',
    'http://europe.wsj.com/',
    'http://www.bbc.co.uk/',
    'http://some-made-up-domain.com/'
]


# 根据url取回这个网页的内容
def load_url(url, timeout):
    with urllib.request.urlopen(url, timeout=timeout) as conn:
        return conn.read()


# 我们使用上下文管理器，可以保证正确的使用`.shutdown()`
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
    future_to_url = {executor.submit(load_url, url, 60): url for url in URLS}
    for future in concurrent.futures.as_completed(future_to_url):
        url = future_to_url[future]
        try:
            data = future.result()
        except Exception as exc:
            print("%r generated an exception: %s" % (url, exc))
        else:
            print("%r page is %d bytes" % (url, len(data)))
```

## ProcessPoolExecutor

`ProcessPoolExecutor`类是`Executor`的一个子类，它使用进程池来异步执行可调用对象。`ProcessPoolExecutor`使用`multiprocessing`模块，可以回避GIL的问题，不过也只可以执行pickable的对象并返回。

`__main__`模块必须可以被其它worker子进程可引用。这意味着`ProcessPoolExecutor`不可以用在REPL.

和线程池一样，重复调用有可能会造成死锁。

- class`concurrent.futures.ProcesPoolExecutor(max_workers=None)`

    `Executor`子类使用进程池并设定了最大`max_workers`个进程。如果`max_workers=None`，默认会使用本机器的核心数量作为worker数量。如果这个参数小于等于0，将会抛出`ValueErrro`.

    > 如果进程意外的中止，将会抛出`BrokenProcessPool`异常。

### ProcessPoolExecutor Exmaple

```python
import concurrent.futures
import math


PRIMES = [
    112272535095293,
    112582705942171,
    112272535095293,
    115280095190773,
    115797848077099,
    1099726899285419
]


def is_prime(n):
    if n % 2 == 0:
        return False

    sqrt_n = int(math.floor(math.sqrt(n)))
    for i in range(3, sqrt_n + 1, 2):
        if n % i == 0:
            return False
    return True


def main():
    with concurrent.futures.ProcessPoolExecutor() as executor:
        for number, prime in zip(PRIMES, executor.map(is_prime, PRIMES)):
            print("%d is prime: %s".format(number, prime))


if __name__ == '__main__':
    main()
```

## Future Objects

pass