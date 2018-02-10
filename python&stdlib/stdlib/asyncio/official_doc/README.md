官方文档地址:

    https://docs.python.org/3/library/asyncio.html

源代码地址:

    https://github.com/python/cpython/tree/3.6/Lib/asyncio/

这个模块提供了使用协程编写单线程并发代码的底层基础设施代码，可以用于大量的I/O访问，运行网络server/client，以及其它相关的场景。下面是这个模块的一些细节内容清单：

- 一个可插拔的**事件循环**，以及根据不同系统平台的多种实现.
- `transport`和`protocol`抽象类(类似于`Twisted`中的同名类).
- 支持TCP,UDP,SSL,subprocess pipes,延时调用，等等.
- `Future`类，模仿`concurrent.futures`，可以被事件循环使用.
- 可以基于`yield from`(PEP380)使用的协程和task，可以编写类同步风格的并发代码.
- 支持`Future`和协程的取消.
- 可以在单个线程的协程中使用同步原语，模仿自`threading`模块
- 提供一个接口，可以让你把堵塞的可调用对象传给线程池调用

异步编程比以前的同步编程(连续编程)更加复杂，请仔细看Develop with asyncio章节，它涵盖了常见的坑以及如何避免遇到它们。