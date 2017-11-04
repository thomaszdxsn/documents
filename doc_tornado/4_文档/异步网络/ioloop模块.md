## tornado.ioloop - 主要的事件循环

一个非堵塞socket的I/O事件循环。

一般的应用只要使用一个`IOLoop`对象就够了，即使用`.instalce`属性。`IOLoop.start()`这行代码一般在main函数的最后一行。非典型的应用可能使用多个`IOLoop`，比如每个线程一个`IOLoop`，或者每个`unittest`case使用一个`IOLoop`。

另外，对于I/O事件，`IOLoop`可以规划时间事件，`IOLoop.add_timeout`是`time.sleep`的非堵塞替代版本。

### IOLoop对象

- `tornado.ioloop.IOLoop`

一个条件触发(**level-triggered**)的I/O循环。

我们根据系统不同选择使用`epoll`(Linux)或者`kqueue`(BSD或者Mac OS X)，如果都没有也会降低标准使用`select()`。如果你想要实现同时处理上千条连接的应用，你应该使用一个支持`epoll`或者`kqueue`的系统。

一个简单TCP服务器的使用例子：

```python
import errno
import functools
import tornado.ioloop
import socket


def connection_ready(sock, fd, events):
    while True:
        try:
            connetion, address = sock.accept()
        except socket.error as e:
            if e.args[0] not in (errorno.EWOULDBLOCK, errono.EAGAIN):
                raise
            return
        connetion.setblocking(0)
        handle_connection(connection, address)


if __name__ == '__main__':
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setblocking(0)
    sock.bind(("", port))
    sock.listen(128)

    io_loop = tornado.ioloop.IOLoop.current()
    callback = functools.partial(connection_ready, sock)
    io_loop.add_handler(sock.fileno(), callback, io_loop.READ)
    io_loop.start()
```

默认情况下，除非已经存在一个当前的`IOLoop`，一个新构建的`IOLoop`将会变为线程当前的`IOLoop`。这个行为可以通过`IOLoop`构造器的`make_argument`参数来控制：如果`make_current=True`，新构造的`IOLoop`将会变为当前状态，如果已经存在一个当前状态的实例那么就会抛出一个错误。如果`make_current=False`，那么新构建的`IOLoop`不会尝试变为当前状态。


### 运行一个IOLoop

- 静态方法`IOLoop.current(instance=True)`

    返回当前线程的`IOLoop`.

    如果一个`IOLoop`已经运行或者已经通过`make_current`标记为当前循环，返回这个实例。如果当前没有`IOLoop`，如果参数为`instance=True`返回`IOLoop.instance()`(主线程必须创建一个IOLoop)。

    为了创建一个异步对象，一般情况你只需要使用`IOLoop.current`。如果想从其它线程和主线程通信的话，可以使用`IOLoop.instance`。

- `IOLoop.make_current()`

    将这个`IOLoop`变为当前线程。

    在线程启动时，其中的`IOLoop`都会自动变为当前状态。但是有时在启动`IOLoop`之前显式调用`make_current()`会很有用，所以在启动阶段的代码可以找到正确的`IOLoop`实例。

- 静态方法`IOLoop.instance()`

    返回一个全局`IOLoop`实例。

    多数应用在主线程只有一个单独的，全局的`IOLoop`。使用这个方法可以让其它线程获得这个实例。在其它情况下，使用`current()`来获取当前线程的`IOLoop`是一个更好的选择。

- 静态方法`IOLoop.initialized()`

    如果单个(singleton)实例已被创建，返回True。

- `IOLoop.install()`

    将这个`IOLoop`实例安置(install)为单个(singleton)实例。

    创建`IOLoop`并不要求一定要使用`instance()`，你可以使用`install()`来创建一个`IOLoop`的自定义子类。

    当使用一个`IOLoop`子类，在使用任何会隐式创建`IOLoop`的对象(如`tornado.httpclient.AsyncHTTPClient`)之前，应该优先调用这个方法。

- 静态方法`IOLoop.clear_instance()`

    清除全局的`IOLoop`实例。

- `IOLoop.start()`

    启动I/O循环。

    这个循环将会一直运行，直到一个callback调用`stop()`，它会让这个循环在**当前这次事件迭代完成后**停止循环。

- `IOLoop.stop()`

    停止I/O循环。

    如果时间循环当前并没有开始运行，下一次调用`start()`将会立即返回。

    想要在一些同步代码中使用异步方法(比如单元测试)，你可以像下面这样启动和停止事件循环：

    ```python
    ioloop = IOLoop()
    async_method(ioloo=ioloop, callback=ioloop.stop)
    ioloop.start()
    ```

    在`async_method()`调用它的callback时，`ioloop.start()`即会返回。

    注意及时在`stop()`被调用以后，`IOLoop`并不会完全停止，因为它需要等待`IOLoop.start()`返回。在`stop()`之前规划的任务将会继续运行，完成之后才会将`IOLoop`关闭。

- `IOLoop.run_sync(func, timeout=None)`

    开启`IOLoop`，运行给定的函数，然后停止循环。

    这个函数必须返回一个`yieldable`对象或者`None`。如果这个函数返回一个`yieldable`对象，`IOLoop`将会运行直到这个`yieldable`完成(`run_sync()`将会返回这个`yieldable`的结果)。如果它抛出一个异常，`IOLoop`将会停止，异常将会再次抛出给调用者。

    **仅关键字(keyword only)参数**`timeout`可以用来设定函数运行的最大时间。如果达到超时时间，将会抛出一个`TimeoutError`错误。

    这个方法非常适合与`tornado.gen.coroutine`组合使用，可以让main函数进行异步调用：

    ```python
    @gen.coroutine
    def main():
        # 做一些异步调用

    if __name__ == '__main__':
        IOLoop.current().run_sync(main)
    ```

- `IOLoop.close(all_fds=False)`

    关闭这个`IOLoop`，释放它使用的资源。

    如果`all_fsd=True`，所有这个IOLoop注册的文件描述符都会关闭(不一定都是这个IOLoop创建的)。

    多数应用在整个进程的生命周期内只使用一个`IOLoop`。这种情况下关闭`IOLoop`是多余的，因为在进程结束后所有的东西都会清理干净。`IOLoop.close`支持的使用场景如单元测试，它会创建并摧毁大规模数量的`IOLoop`。

    一个`IOLoop`关闭之前必须完全停止。意思就是在调用`IOLoop.close()`之前调用了`IOLoop.start()`的话，那么就必须调用`IOLoop.stop()`

### I/O事件

- `IOLoop.add_handler(fd, handler, events)`

    注册给定的handler，让它来接受对fd给定的事件。

    `fd`参数要么是一个整数型的文件描述符，或者一个带有`fileno()`方法的类文件对象(这个对象可选带有一个`close()`方法，这个方法将会在`IOLoop`关闭时调用)。

    `events`参数是一个常量按位值(bitwise)，这些常量包括`IOLoop.READ`, `IOLoop.WRITE`以及`IOLoop.ERROR`。

    当一个事件出现，将会运行`handler(fd, events)`。

- `IOLoop.update_handler(fd, events)`

    修改我们对`fd`监听的事件。

- `IOLoop.remove_handler(fd)`

    停止监听`fd`的事件。


### callback和timeout

- `IOLoop.add_callback(callback, *args, **kwargs)`

    在下次I/O循环迭代时调用给定的callback。

    除了信号handler以外，在任何时间的任何线程都可以自由调用这个方法。注意这个方法是`IOLoop`中**唯一**保证线程安全的方法；其它与`IOLoop`的交互叶必须在这个`IOLoop`的线程内完成。`add_callback()`可以用来讲控制权从其它线程转交到`IOLoop`的线程。

    想要从一个信号handler添加callback，可以使用`add_callback_from_signal`。

- `IOLoop.add_callback_from_signal(callback, *args, **kwargs)`

    在下次I/O循环迭代时调用给定的callback。

    可以在Python信号handler中安全的使用这个方法；不应该用在其它地方。

    传入到这个方法的callback将会不带`stack_context`的运行，主要是为了防止上下文中的函数将会干扰到信号。

- `IOLoop.add_future(future, callback)`

    通过`IOLoop`规划一个callback, 将会在futures完成后调用。

    这个callback只有一个参数，即`future`(Future对象)。

- `IOLoop.add_timeout(deadline, callback, *args, **kwargs)`

    pass


