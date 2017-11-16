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

- 如果你正在写一个异步库，但是没有依赖任何的`stack_context`库，如`tornado.ioloop`或者`tornado.iostream`(比如你在编写一个线程池)，在任何异步操作捕获操作起始时的stack上下文之前，使用`stack_context.wrap`。

- 如果你编写的异步库有一些共享资源(比如连接池)，在`with stack_context.NullContext()`上下文块中创建共享资源。这将会防止一个请求到另一个之间的`StackContexts`泄漏问题。

- 如果你想要编写一些通过异步调用构成的异常handler，需要创建一个新的`StackContext`(或者`ExceptionStackContext`)，让你的异步调用在`with`代码块中引用`StackContext`。


**类:**

- `tornado.stack_context.StackContext(context_factory)`

    建立给定的上下文，当作`StackContext`形式转移。

    注意这个参数是一个上下文管理器返回的可调用对象，而不是上下文本身。也就是说，如果是一个不可转移的上下文，将会像下面这样：

    `with my_context():`

    StackContext接收函数本身，而不是它的结果：

    `with StackContext(my_context):`

    `with StackContext() as cb:`的结果是一个deactivation的回调，在StackContext不需要继续传播时，调用这个回调。这是一个高级特性，在大多数应用中不需要直接使用。

- `tornado.stack_context.ExceptionStackContext(exception_handler)`

    专门用于StackContext的异常处理。

    `exception_handler`将会在上下文中出现一个非捕获异常时被调用。这个类的语法非常类似于`try/finally`子句，一般用于记录错误日志，关闭socket，或者其它清理工作。`exc_info`三位元组(type, value, traceback)将会传入到exception_handler函数中。

    如果这个异常handler返回True，这个异常将会被消费，不会继续向上传播。

- `tornado.stack_context.NullConetxt`

    重置`StackContext`。

    创建一个共享资源时很有用(比如`AsyncHTTPClient`)。

- `tornado.stack_context.wrap(fn)`

    返回一个可调用对象，在执行时会回复当前的`StackContext`。

    使用这个对象保存一个callback，之后在另外一个执行上下文中被执行(可以在另一个线程，或者在同线程中异步执行)。

- `tornado.stack_context.run_with_stack_context(context, func)`

    在给定`StackContext`中运行一个协程函数func。

    在`with StackContext`代码块中使用`yiled`语句并不安全，所以将`@gen.coroutine`和stack context一起使用很困难。这个帮助函数将会让`yield`和`with`语句语法分离。

    ```python
    @gen.coroutine
    def incorrect():
        with StackContext(ctx):
            # 错误: 将会抛出StackContextInconsistentError
            yield other_coroutine()
    

    @gen.coroutine
    def correct():
        yield run_with_stack_context(StackContext(ctx), other_coroutine)
    ```
    
    


