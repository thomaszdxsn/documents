## Concurrency

### Concurrency with Evenlet

#### Introduce

[Eventlet](http://eventlet.net/)首页是这么描述它的；Python的一个网络并发库，可以改变你代码的运行方式，而不是改变你编写代码的方式。

- 它使用`epoll`或者`libevent`来进行高伸缩性非堵塞I/O
- 协程让用户可以以同步的方式来编写代码，和threading很类似，但是提供了非堵塞I/O
- 事件分发是隐式的：你可以很简单的使用Evenlet，或者对一个大应用中的一部分代码使用

Celery支持Eventlet作为执行池的替代方案。有些方面它优于prefork，但是你需要确保你的任务没有执行堵塞的操作，
堵塞的操作将会影响到worker中的其它操作，直到堵塞操作返回值。

prefork pool可以利用多个进程，但是进程数受CPU数量的限制。Eventlet可以让你创建成百上千个绿色线程。在一个feed系统中，Eventlet池可以每秒提取和处理上百个feeds。注意这是异步I/O擅长的地方(异步HTTP请求)。你可以混合使用Eventlet和prefork workers，根据任务的类型来将它路由至合适的worker。

#### Enabling Eventlet

你可以使用命令`celery worker -P`来开启Eventlet pool:

```python
$ celery -A proj worker -P eventlet -c 1000
```

#### 例子

请看Celery官方发布版的[Eventlet examples](https://github.com/celery/celery/tree/master/examples/eventlet)文件夹.