## tornado.concurrent -- 线程和futures

组合线程和Future的工具函数。

`Future`是Python3.2以后引入的一个并发编程的模式，在`concurrent.futures`包中引入。这个包定义了具备高度兼容性的`Future`类，用于协程的使用。

- `tornado.concurrent.Future`

    一个异步结果的占位符。

    `Future`封装了一个异步操作的结果。在同步应用中，`Futures`用来等待线程／进程池的结果；在Tornado中通常使用`IOLoop.add_future`或者在一个`@gen.coroutine`协程函数中yield这个Future。

    `tornado.concurrent.Future`类似于`concurrent.futures.Future`，但不是线程安全的(因此速度快于单线程事件循环)。

    除了`exception`和`set_exception`，在Python2中方法`exc_info`和`set_exc_info`可以支持捕获回溯信息。在Python3中可以自动获取回溯信息。


### 消费者方法

- `Future.result(timeout=None)`

    如果一个操作成功，返回它的结果。如果失败，重新抛出它的异常。

    这个方法可以接受一个`timeout`参数，用来兼容`concurrent.futures.Future`，但是错误会在Future完成之前被抛出，所有timeout从来没有被调用。

- `Future.exception(timeout=None)`

    如果操作抛出一个异常，返回这个对象，否则返回None。

    这个方法可以接受一个`timeout`参数，用来兼容`concurrent.futures.Future`，但是错误会在Future完成之前被抛出，所有timeout从来没有被调用。

- `Future.exc_info()`

    返回一个元组，格式和`sys.exc_info`一样。或者返回None.

- `Future.add_done_callback(fn)`

    将给定的callback关联到Future中。

    这个callback将会在Future结束后，将Future.result作为参数来调用。在`Tornado`中，考虑使用`IOLoop.add_future()`，而不是直接使用`add_done_callback()`。

- `Future.done()`

    如果Future结束运行，返回True。

- `Future.running()`

    如果这个操作当前还在运行，返回True。

- `Future.cancel()`

    如果可能，取消这个操作。

    Tornado的`Future`不支持取消。所以这个方法总是返回False。

- `Tornado.cancelled()`

    如果这个操作已经取消，返回True。

    Tornado的`Future`不支持取消。所以这个方法总是返回False。

### 生产者方法

- `Future.set_result(result)`

    设置一个Future的结果。

    不能对同一个对象调用多次
    set方法。

- `Future.set_exception(exception)`

    设置一个Future的异常。

- `Future.set_exc_info(exc_info)`

    设置一个Future的异常信息。

    在Python2中保存回溯信息。

- `tornado.concurrent.run_on_executor(*args, **kwargs)`

    一个装饰器，可以让一个同步方法在一个executor中异步执行。

    被装饰的方法可以接受一个callback关键字参数，并返回一个Future。

    使用的`IOLoop`和executor，通过self的属性`self.io_loop`和`self.executor`来决定。想用使用不同的属性，将关键字参数传入到这个装饰器中：

    ```python
    @run_on_executor(executor='_thread_pool')
    def foo(self):
        pass
    ```

- `tornado.concurrent.return_future(f)`

    一个装饰器，让函数可以返回callback返回的一个`Future`。

    被封装的函数应该接受一个`callback`关键字参数，在它结束时通过一个参数来调用这个callback。对于信号失败，这个函数只会简单的抛出一个异常(它会被`StackContext`捕获并传入到Future中)。

    从调用者的角度来说，callback参数是可选的。如果给定了这个参数，将在函数结束时以`Future.result()`作为参数来调用。如果这个函数失败，callback不会被调用，异常将会抛出到`StackContext`环境中。

    如果没有给定callback，调用者需要使用`Future`来等待函数完成(可能在一个`gen.engine`函数中yield它，或者传入到`IOLoop.add_future`)。

    用法：

    ```python
    @return_future
    def future_func(arg1, arg2, callback):
        # 做一些事情(可能是异步的)
        callback(result)

    @gen.engine
    def caller(callback):
        yield future_func(arg1, arg2)
        callback()
    ```

    注意`@return_future`和`@gen.engine`可以应用在同个函数中，`@return_future`应该出现在顺序的前面。不过，还是推荐使用`@coroutine`来代替这个组合。

- `tornado.concurrent.chain_future(a, b)`

    将两个future链接在一起，所以在一个完成后，开始进行另一个。

    `a`的结果(成功或失败)将会拷贝到`b`，除非`b`在`a`结束的时候已经完成或者取消。