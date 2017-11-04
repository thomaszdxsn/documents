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

```