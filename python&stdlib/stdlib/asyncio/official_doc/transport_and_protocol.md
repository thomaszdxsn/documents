# Transports and Protocols(callback based API)

源代码: [Lib/asyncio/transport.py](https://github.com/python/cpython/tree/3.6/Lib/asyncio/transports.py)

源代码: [Lib/asyncio/protocol.py](https://github.com/python/cpython/tree/3.6/Lib/asyncio/protocols.py)

## Transports

`Transport`是`asyncio`提供的一个类，可以提供为不同种类通讯频道(communication channel)的抽象类。你一般不会直接实例化一个transport；相反，你应该调用`AbstractEventLoop`的方法来创建一个transport并试图实例化底层的通讯频道，在成功以后会通知你。

一旦通讯频道建立之后，transport通常和`protocol`实例成对出现。protocol可以以各种用途来调用transport的方法。

`asyncio`目前支持TCP，UDP，SSL和subprocess pipe的transport。根据transport种类的不同，它的方法也不同。

### BaseTransport

- class`asyncio.BaseTransport`

    transport的积累。

    - `close()`

        关闭transport。