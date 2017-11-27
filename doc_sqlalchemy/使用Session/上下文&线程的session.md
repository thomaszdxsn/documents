## 上下文/线程(contextual/thread-local)Session

在问题"当我构建一个Session时，需要在什么时候关闭它？”中引入了一个“session scope”的概念，使用了一个Web app的例子，一个Session的域和一个web request关联。多数现代web框架包含了集成工具，可以自动管理“session scope”。

SQLAlchemy包含它本身的helper对象，可以用来帮助建立用户定义的session域。同样可以使用第三方的集成系统来帮助构建session域。

这个对象即`scoped_session`对象，它代表`Session`对象的一个注册工厂。如果你不熟悉注册模式，推荐看一下[链接](https://martinfowler.com/eaaCatalog/registry.html)。

> 注意
>> `scoped_session`在SQLAlchemy应用中很受欢迎。然而，需要明白的是它仅仅是Session管理的方法之一。如果你刚刚开始使用SQLAlchemy，如果对术语"thread-local"很陌生，如果有可能的话我们推荐你先使用类似`Flask-SQLAlchemy`或者`zope.sqlalchemy`这类集成系统。

一个`scoped_session`通过调用来构建，传入一个**Factory**可以生成一个新的Session对象。对于session来说，最常见的**factory**即`sessionmaker`。下面是用法：

```python
>>> from sqlalchemy.orm import scoped_session
>>> from sqlalchemy.orm import sessionmaker

>>> session_factory = sessionmaker(bind=some_engine)
>>> Session = scoped_session(session_factory)
```

现在我们调用`Session`将会调用这个registry：

```python
>>> some_session = Session()
```

上面代码中，`some_session`是`Session`的一个实例，我们将会使用它来和数据库交互。如果我们再次调用`Session`这个registry，将会返回同样的`Session`:

```python
>>> some_other_session = Session()
>>> some_session is some_other_session
True
```

这个模式可以让应用中的不同模块调用全局的`scoped_session`，在这些区域中可以分享同一个session而不需要显示传入。通过registry建立的`Session`将会保持，除非显示让registry使用`scoped_session.remove()`来废弃它。

```python
Session.remove()
```

`scoped_session.remove()`方法将会首先访问当前`Session`的`Session.close()`，它将会释放Session拥有的连接/事务资源，然后丢弃`Session`本身。这里的"释放“意思是将(数据库)连接返回给连接池，并将事务回滚，最后会调用底层DBAPI连接的`rollback()`方法。

此时，`scoped_session`对象为“空”，如果再次调用又回创建一个新的`Session`。这时的对象和之前并不一样：

```python
>>> new_session = scoped_session()
>>> new_session is some_session
False
```

上面的一系列步骤简单的阐释了"registry"模式。这个模式是一个基础概念，接下来我们可以讨论一些模式处理的细节。

### 隐式方法访问

`scope_session`的原理很简单；保持一个Session，接收所有查询。`scoped_session`同样包含**"proxy behavior"**，意思就是这个registry本身可以以Session对象来对待。当这个对象的方法被调用，它会**代理(proxy)**至这个registry维持的Session：

```python
Session = scoped_session(some_factory)

# 等同于:
#
# session = Session()
# print(session.query(MyClass).all())
print(Session.query(MyClass).all())
```

### Thread-Local Session

熟悉多线程的编程者都知道使用全局变量是一个很糟的想法，它暗含这个全局变量可以被多个线程并发访问。`Session`对象完全被设计与使用在**非并发**风格，用多线程中的话来说即“一次只能存在于一个线程中“。所以我们以上的`scoped_session`用法在多线程中并不好用。需要使用Python提供的`threading.local()`.

`scoped_session`提供了一个快速，相对简单的方式来供给一个单独的，全局对象，以供应用中的多线程安全的调用。

### 在Web APP中使用Thread-Local Scope

之前有提到过，一个web应用是围绕一个**web请求**来构建的，将这样一个App和Session集成，通常意味着Session和这个请求有关联。话说回来，多数Web框架，除了一些异步框架如Tornado和Twisted，通过一个简单的方式使用线程，比如web请求的接收，处理和完成都在一个worker线程中完成。当这个请求结束后，这个worker线程将会释放到worker线程池，让它可以处理其它请求。

下面的实例图解释了web框架和session的集成：

```python
Web Server          Web Framework           SQLAlchemy ORM Code
----------          -------------           -------------------
startup      ->     Web framework           # 建立了Session registry
                    initialize              Session = scoped_session(sessionmaker())

incoming     ->     web request       ->    # registry可选直接对本身调用
web request         starts                  # 或者显示创建一个local Session
                                            Session()

                                            # Session registry现在可以用于其它地方
                                            Session.query(MyClass)
                                            Session.add(some_object)

                                            # 如果数据修改完成，提交这个事务
                                            Session.commit()

                    web request ends  ->    # registry被命令移除Session

                    sends output      <-
 outgoing web   <-
 response
```

使用上面的控制流，处理web应用和Session的集成有两个必须要求：

1. 在web应用首次开启时创建单个`scoped_session`registry，确保这个对象可以在接下来的代码中可访问。
2. 确保在web请求结束时调用`scoped_session.remove()`，通常集成web框架的事件系统，建立一个“request end”事件。

上面的方法只是Session集成web框架的**方法之一**，而且一个重要的假定即这个web框架的每个web请求关联一个web线程。强烈推荐使用使用web框架提供的集成工具而不是直接使用`scoped_session`。

### 使用自定义创建的Scope

pass