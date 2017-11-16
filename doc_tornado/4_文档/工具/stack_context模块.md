## tornado.stack_context -- 异步回调中的错误处理

`StackContext`可以让应用维持一个**类线程锁(threadlock-like)**的状态，它会跟随代码执行到其它的执行上下文中。

主要的好处是可以移除显式的`async_callback`封装，让一些追加的上下文可以记录日志。

这个行为有一些黑魔法，但是它确实扩展了思维(错误处理)，比如一个错误处理器是一种局部栈状态，当这个栈被暂停并重启一个新的上下文时，之前的状态需要保持。`StackContext`过滤了每次调用站点时存储状态的负担(比如：将每个`AsyncHTTPClient`封装到一个`async_callback`中)，将控制由一个上下文移交给下一个(比如`AsyncHTTPClient`本身，`IOLoop`, 线程池，等等).

使用例子：

```python
@contextlib.contextmanager
def die_on_error():
    try:
        yield
    except Exception:
        logging.error("exception in asynchronous opeartion", exc_info=True)
        sys.exit(1)

with StackContext(die_on_error):
    # 一个异常在这里，*或者*在一个callback中抛出
    # 它的出现会让进程结束，而不是在ioloop中反反复复出现
    http_client.fetch(url, callback)
ioloop.start()
```

多数应用不需要直接使用`StackContext`。下面有一套何时使用`StackContext`的规则：

- pass

