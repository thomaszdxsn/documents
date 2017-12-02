## 通过事件追踪对象和sesion的改动

SQLAlchemy提供了一个拓展性的`Event Listening`系统，贯穿了Core和ORM。在ORM中，事件监听钩子很不一样，请查看[ORM Events文档](http://docs.sqlalchemy.org/en/latest/orm/extending.html).这些年中，不断地增加了一些新的，很有用的事件。这个章节将会介绍一些主要的事件钩子，并且会介绍该在何时使用它们。

### 持久化事件

可能使用最多的事件当属“持久化”事件，它和"flush process"相对应。flush是用来决定使用INSERT，UPDATE或DELETE中的一个来修改pending状态。

- `before_flush()`

    `SessionEvents.before_flush()`钩子是迄今为止差不多最有用的事件，用于当一个应用需要确保在flush proceeds中对数据库加上额外的持久化改动。这个事件可以安全的操纵Session状态，也就是说，一个新的对象可以attached到这个session，对象可以被删除，一个对象的独立属性可以自由修改，这些修改将会在事件钩子完成后推入到flush process中。

    一般`SessionEvents.before_flush()`钩子负责扫描集合如`Session.new`, `Session.dirty`以及`Session.delete`, 来看看对象中发生了哪些变化。

    想要看看使用的例子，请看[Versioning with a History Table](http://docs.sqlalchemy.org/en/latest/orm/examples.html#examples-versioned-history)和[Versioning using Temporal Rows](http://docs.sqlalchemy.org/en/latest/orm/examples.html#examples-versioned-rows)

- `after_flush()`

    `SessionEvents.after_flush()`钩子将会在一个flush process的SQL发出后被，但是在刷新的对象状态被修改**之前**被调用。也就是说，你仍然可以查看`Session.new`, `Session.dirty`和`Session.deleted`集合来看看哪些对象被刷新，你也可以使用`AttributeState`提供的历史追逐特性哪些改动被持久化。在`SessionEvents.after_flush()`事件中，可以通过观察数据库改动来发出额外的SQL。

- `after_flush_postexec()`

    `SessionEvents.after_flush_postexec()`将会在`SessionEvents.after_flush()`之后，以及对象状态改动**之后**被调用。`Session.new`, `Session.dirty`, `Session.deleted`集合在这时通常已经完全为空。使用`SessionEvents.after_flush_postexec()`来查看结束对象的identity map，也可以发送额外的SQL。在这个钩子中，可以对一个对象作出额外的改动，意味着Session可以再次进入`dirty`状态；

#### mapper事件

除了flush钩子，还有一套颗粒度更细的钩子，可以在单个对象的基础上，基于INSERT， UPDATE， DELETE语句来调用。这些钩子都属于mapper持久化钩子，这些钩子很流行，但是使用的时候需要更加小心，因为在执行时flush process已经存在；很多操作在这时执行比不安全。

这些事件包括:

- `MapperEvents.before_insert()`
- `MapperEvents.after_insert()`
- `MapperEvents.before_update()`
- `MapperEvents.after_update()`
- `MapperEvents.before_delete()`
- `MapperEvents.after_delete()`

每个事件都将会传入`Mapper`。

### 对象声明周期事件

另一个事件的使用案例是“追踪对象的声明周期“。

对象的所有状态都可以通过事件追踪。每个事件代表一个单独的过渡状态。下面的例子说明事件中可以指定关联一个Session：

```python
from sqlalchemy import event
from sqlalchemy.orm import Session

session = Session()

@event.listen_for(session, "transient_to_pending")
def object_is_pending(session, obj):
    print("new peding: %s" %obj)
```

也可以指定使用一个`sessionmaker`：

```python
from sqlalchemy import event
from sqlalchemy.orm import sessionmaker

maker = sessionmaker()

@event.listens_for(maker, "transient_to_pending")
def object_is_pending(session, obj):
    print("new pending: %s"% obj)
```

listener可以对单个函数堆叠使用：

```python
@event.listens_for(maker, "pending_to_persistent")
@event.listens_for(maker, "deleted_to_persistent")
@event.listens_for(maker, "detached_to_persistent")
@event.listens_for(maker, "loaded_as_persistent")
def detect_all_persistent(session, instance):
    print("object is now persistent: %s" %instance)
```

#### 短暂(Transistent)

所有映射对象构建的初始状态都是`transistent`.在这个状态中，这个对象处于独立存在状态，并不和任何Session关联。对于这个初始状态，没有特定的“transion"事件，因为它没有关联任何Session。但是如果想要拦截任何transient对象的创建时期，可能`InstanceEvents.init()`方法可能是最好的选择。这个事件需要应用于一个指定的类或者超类。例如，如果想要拦截一个特定declrative base基类的所有对象，可以这样做：

```python
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import event

Base = declarative_base()

@event.listen_for(Base, "init", propagate=True)
def intercept_init(instance, args, kwargs):
    print("new transient: %s" %instance)
```

#### 短暂到待定(transient to pending)

transient对象通过方法`Session.add()`或者`Session.add_all()`首次与Session关联后将会变为`pending`(待定)状态。一个对象也可以通过“cascade”变为Session的一部分。短暂(transient)到待定的过渡可以通过`SessionEvents.transient_to_pending()`事件来检测：

```python
@event.listens_for(sessionmaker, "transient_to_pending")
def intercerpt_transient_to_pending(session, object_):
    print("transient to pending: %s"%object_)
```

#### 待定到持久化(pending to persistent)

pending对象在flush process对一个实例执行INSERT语句后变为persistent对象。这个对象现在具有一个识别key。最终pending到persistent的过渡可以通过`SessionEvents.pending_to_persistent()`事件里检测：

```python
@event.listens_for(sessionmaker, "pending_to_persistent")
def intercerpt_pending_to_persistent(session, object_):
    print("pending to persistent: %s" %object_)
```

#### 待定到短暂(pending to transient)

如果调用了`Session.callback()`或者`Session.expunge()`，pending状态对象可以转回到transient状态.可以通过事件`SessionEvents.pending_to_transient()`来追踪：

```python
@events.listens_for(sessionmaker, "pending_to_transient")
def intercerpt_pending_to_transient(session, object_):
    print("transient to pending: %s" %object_)
```

#### 读取后直接变为持久化(loaded as persistent)

如果对象是从数据库读取，那么可以直接在Session中以`persistent`状态呈现。追踪这个状态的过渡和追踪对象是否读取是同一个意思，也和使用`InstanceEvents.load()`实例级事件是同一个意思。但是，`SessionEvents.loaded_as_persistent()`事件提供了一个以session为中心的钩子来拦截通过特定场景进入persistent持久化状态的对象：

```python
@events.listen_for(sessionmaker, "loaded_as_persistent")
def intercept_loaded_as_persistent(session, object_):
    print("object loaded into persistent state: %s" % object_)
```

#### 持久化到短暂(persistent to transient)

通过调用`Session.callback()`，persistent对象可以转回transient状态。可以使用钩子`SessionEvents.persistent_to_transient()`来追踪这个钩子：

```python
@event.listens_for(sessionmaker, "persistent_to_transient")
def intercept_persistent_to_transient(session, object_):
    print("persistent to transient: %s" % object_)
```

#### 持久化到删除(persistent to deleted)

一个对象被标记为删除并且在flush process时将它从数据库删除后，这个persistent对象将会变为deleted状态。注意这和对一个目标使用`Session.delete()`**不一样**。`Session.delete()`方法只会讲对象标记删除，DELETE语句还没有通过flush process发出。

在deleted状态中，对象只是和Session略微沾边。它不会出现在identity map也不会出现在`Session.deleted`集合中。

对于deleted状态，可以在事务提交后进一步变为detached状态，抑或事务回滚后变回persistent状态。

可以通过事件钩子`SessionEvents.persistent_to_deleted()`来追踪：

```python
@event.listens_for(sessionmaker, "persistent_to_deleted")
def intercept_persistent_to_deleted(session, object_):
    print("object was DELETEd, is now in deleted state: %s" % object_)
```

#### 删除到分离(deleted to detached)

如果事务提交后，deleted对象将会变为detached。在调用`Session.commit()`之后，数据库事务将会结束，并且Session中的对象将会通通丢弃。可以通过`SessionEvents.deleted_to_detached`这个事件钩子来追踪：

```python
@event.listens_for(sessionmaker, "deleted_to_detached")
def intercept_deleted_to_detached(session, object_):
    print("deleted to detached: %s" % object_)
```

#### 持久化到分离(persistent to detached)

一个对象通过`Session.expunge()`, `Session.expunge_all()`或者`Session.close()`方法来解除和Session的关联后，persistent对象将会变为detached状态。

> 对象也可能会在垃圾回收阶段变为detached状态。

可以通过事件钩子`SessionEvents.persistent_to_detached()`来追踪：

```python
@event.listens_for(sessionmaker, "persistent_to_detached")
def intecept_persistent_to_detached(session, object_):
    print("object became detached: %s" % object_)
```

#### 分离到持久化(detached to persistent)

detached对象可以通过`session.add()`或者类似方法将之和session重新关联，再次变为persistent状态。可以通过事件钩子`SessionEvents.detached_to_persistent()`来追踪：

```python
@event.listens_for(sessionmaker, "detached_to_persistent")
def intecept_detached_to_persistent(session, object_):
    print("object became persistent again: %s" % object_)
```

#### 删除变为持久化(deleted to persistent)

在调用`Session.rollback()`以后，deleted对象将可能会变回persistent状态。可以通过事件钩子`SessionEvents.deleted_to_persistent()`来追踪：

```python
@event.listens_for(sessionmaker, "transient_to_pending")
def intercept_transient_to_pending(session, object_):
    print("transient to pending: %s" % object_)
```

### 事务事件

事务事件允许一个应用在事务边界出现时, 在Connection对象中的Session事务状态变动时被提醒：

- `SessionEvents.after_transaction_create()`, `SessionEvents.after_transaction_end()`: 这些事务将会追踪Session的域。
- `SessionEvents.before_commit()`, `SessionEvents.after_commit()`, `SessionEvents.after_begin()`, `SessionEvents.after_rollback()`, `SessionEvents.after_soft_rollback()`

### 属性修改事件

属性修改事件可以允许拦截对象特定属性的改动。这些事件包括：

- `AttributeEvents.set()`
- `AttributeEvents.append()`
- `AttribuetEvents.remove()`


