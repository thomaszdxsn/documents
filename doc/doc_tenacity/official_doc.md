# Tenacity

Tenacity是一个Apache2.0许可的通用retrying库，使用Python编写。这个项目最开始是[retrying](https://github.com/rholder/retrying/issues/65)的一个分支。

最简单的使用例子，让一个有瑕疵的函数出现任何Exceptions都会重试，直到函数正确返回值为止：

```python
import random
from tenacity import retry


@retry
def do_something_unreliable():
    if random.randin(0, 10) > 1:
        raise IOError('Broken sauce, everything is hosted!!!111one')
    else:
        return 'Awesome sauce!'

print(do_something_unreliable())
```

## Feature

- 通用的装饰器API
- 可以设定停止的条件(限制尝试次数)
- 可以设定等待的时间(每次尝试之间指数型的间隔)
- 自定义碰到哪种异常再retry
- 自定义要碰到什么样的返回值才停止
- 协程中的retry

## Installation

`$ pip install tenacity`

## Examples

我们之间说到过，默认的行为是无限等待重试，直到函数返回：

```python
@retry
def never_give_up_nerver_surrender():
    print("Retry forever ignoring Exceptions, don't wait between retries")
    raise Exception
```

让我们给定一些条件，比如尝试retry的总次数:

```python
@retry(stop=stop_after_attempt(7))
def stop_after_attempts():
    print("Stopping after 7 attempts")
    raise Exception
```

再设置一个等待的时间：

```python
@retry(stop=stop_after_delay(10))
def stop_after_10_s():
    print("Stopping after 10 seconds")
    raise Exception
```

你可以使用管道操作符`|`，让多个条件组合起来:

```python
@retry(stop=(stop_after_delay(10) | stop_after_attempt(5)))
def stop_after_10_s_or_5_retries():
    print("Stopping after 10 seconds or 5 retries")
    raise Exception
```

多数情况你不想让retry立即执行，让我们设定2秒钟的间隔:

```python
@retry(wait=wait_fixed(2))
def wait_2_s():
    print("Wait 2 second between retries")
    raise Exception    
```

有时最好等待一个随机的时间：

```python
@retry(wait=wait_random(min=1, max=2))
def wait_random_1_to_2_s():
    print("Randomly wait 1 to 2 seconds between retries")
    raise Exception
```

如果是分布式服务，有必要设定一个指数级的间隔：

```python
@retry(wait=wait_exponential(multiplier=1, max=10))
def wait_exponential_1():
    print("Wait 2^x * 1 second between each retry, up to 10 seconds, then 10 seconds afterwards")
    raise Exception
```

另外可以组合fixed时间和random时间:

```python
@retry(wait=wait_fixed(3) + wait_random(0, 2))
def wait_fixed_jitter():
    print("等待最少3秒，再加上0到2秒的随机间隔")
    raise Exception
```

在碰到多进程使用共享资源时，指数级增长的间隔可以帮助减少冲突:

```python
@retry(wait=wait_random_exponential(multiplier=1, max=60))
def wait_exponential_jitter():
    print("Randomly wait up to 2^x * 1 seconds between each retry until the range reaches 60 seconds, then randomly up to 60 seconds afterwards")
    raise Exception
```

有时有必要构件一个间隔的链条:

```python
@retry(wait=wait_unchain(*[wait_fixed(3) for i in range(3)] +
                          [wait_fixed(7) for i in range(2)] +
                          [wait_fixed(9)]))
def wait_fixed_chained():
    print("Wait 3s for 3 attempts, 7s for the next 2 attempts and 9s for all attempts thereafter")
    raise Exception
```

我们可以指定在特定的异常才retry：

```javascript
@retry(retry=retry_if_exception_type(IOError))
def might_io_error():
    print("Retry forever with no wait if an IOError occurs, raise any other errors")
    raise Exception
```

我们可以使用函数的结构来修改retry的行为:

```python
def is_none_p(value):
    """Return True if value is None"""
    return value is None


@retry(retry=retry_if_result(is_none_p))
def might_return_none():
    print("Retry with no wait if return value is None")
```

我们也可以组合多个条件：

```python
def is_none_p(value):
    """如果值是None，返回True."""
    return value is None

@retry(retry=(retry_if_result(is_none_p) | retry_if_exception_type()))
def might_return_none():
    print('Retry forever ignoring Exceptions with no wait if return value is None')
```

可以在任何时候通过抛出`TryAgain`异常来显式retry：

```python
@retry
def do_something():
    result = something_else()
    if result == 23:
        raise TryAgain
```

如果是“timeout“抛出的`RetryError`，我们可以重新抛出最后一个碰到的异常：

```python
@retry(reraise=True, stop=stop_after_attempt(3))
def raise_my_exception():
    raise MyException('Fail')


try:
    raise_my_exception()
except MyException:
    pass
```

也可以通过`before`，指定在一个重新尝试之前执行一个callback：

```python
logger = logging.getLogger(__name__)

@retry(stop=stop_after_attempt(3), before=before_log(logger, logging.DEBUG))
def raise_my_exception():
    raise MyException('Fail')
```

同样的道理，也可以在retry之后执行一次:

```python
logger = logging.getLogger(__name__)

@retry(stop=stop_after_attempt(3), after=after_log(logger, logging.DEBUG))
def raise_my_exception():
    raise MyException('Fail')
```

你可以通过被装饰函数的`retry`属性访问统计数据:

```python
@retry(stop=stop_after_attempt(3))
def raise_my_exception():
    raise MyException('Fail')

try:
    raise_my_exception()
except Exception:
    pass

print(raise_my_excpetion.retry.statistics)
```

你可以修改被装饰函数的`retry_with`，重新指定retry handler：

```python
@retry(stop=stop_after_attempt(3))
def raise_my_exception():
    raise MyException('Fail')

try:
    raise_my_exception.retry_with(stop=stop_after_attempt(4))()
except Exception:
    pass

print(raise_my_exception.retry.statistics)
```

最后，`retry`同样可以装饰`asyncio`和`tornado`的协程。sleep是异步完成的.

```python
@retry
async def my_async_function(loop):
    await loop.getaddrinfo('8.8.8.8', 53)
```

```python
@retry
@tornado.gen.coroutine
def my_async_function(http_client, url):
    yield http_client.fetch(url)
```

