[TOC]

## Session可以干什么？

广义来说，Session在数据库和Python对象间建立会话。它提供了一个入口点，使用Session对象当前
的数据库连接来发送数据库查询，组成结果行并且存入Session中，Session中的这个数据结构叫做
`Identity Map` - 这个数据结构维持每个对象的唯一标识符，"唯一"意思就是"一个特定的主键只
对应一个对象"。

Session本质上是无状态的形式。一旦通过它发起一个查询，它会从一个Engine请求连接资源。这个连接
代表一个持续存在的事务，它会保持状态直到Session发出commit或者rollback指令。

在数据库再次查询之前或者当前的事务提交后，Session中一个对象所有的更改都会被追踪，然后所有待定
的修改都会被刷新到数据库。这就是所谓的`Unit of Work`模式。

当使用一个Session时，值得注意的是这个对象关联的对象叫做"代理对象(proxy object)" - 有
很多种情况会重新访问数据库来保持同步。也许可以从一个Session中"detach"一个对象，然后继续
使用它，虽然这个行为需要小心使用。

## 获取一个Session

`Session`是一个常规的Python类，可以直接实例化它。但是，想要标准化session的配置，可以使用
`sessionmaker()`类来创建顶级的`Session`配置，可以在整个app项目中使用，无需重复的配置参数。

`sessionmaker`的使用方法：

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 一个Engine，Session使用它作为连接资源
some_engine = create_engine("postgresql://scott:tiger@localhost/")

# 创建一个配置过的"Session"类
Session = sessionmaker(bind=some_engine)

# 创建一个session
session = Session()

# 使用session
myobject = MyObject('foo', 'bar')
session.add(myobject)
session.commit()
```

上面例子中，`sessionmaker`为我们创建类一个session工厂，我们为它赋值为名称`Session`。
这个session工厂，我们调用后，我们将会使用给定到这个工厂的配置函数来创建一个新的`Session`对象。
在这种情况下，我们配置session工厂时一般设置一个特定的`Engine`作为连接资源。

典型的起步工作是关联`sessionmaker`和一个`Engine`，所以每个生成的Session对象都会使用这个
Engine作为连接资源。

当你写自己的app时，将这个`sessionmaker`工厂函数放在顶层结构上。这个工厂可以在app的剩余
部分作为生成新Session的来源。

`sessionmaker`工厂可以关联其它的辅助函数，可以通过自定义的sessionmaker来实现。

### 增加额外的配置到一个现存的sessionmaker()

一个常见的场景就是在import的时候调用`sessionmaker`，但是要关联这个`sessionmaker`的一个
或多个`Engine`实例可能还没有处理。对于这种情况，可以使用`sessionmaker`提供的
`sessionmaker.configure()`方法，它会为现存的sessionmaker直接增加额外的配置，在这个
对象调用时生效：

```python
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

# 配置Session类和一些想要的选项
Session = sessionmaker()

# 然后，我们创建engine
engine = create_engine('postgresql://...')

# 将它与我们自定义的Session类关联
Session.configure(bind=engine)

# 使用这个Session
session = Session()
```

### 通过可替代参数来创建一个专门的Session对象

在一个app中某些情况可能需要创建一个配置特殊参数的新Session，它和app中一般使用的Session
不一样，比如这个Session会绑定另外一个连接资源，或者这个Session需要在配置一些其它的参数
如`expire_on_commit`，特殊的参数可以传入`sessionmaker`工厂的`sessionmaker.__call__()`
方法。下面例子中，一个新的Session配置了一个特定的`Connection`:

```python
# 在模块级别，全局的sessionmaker绑定了一个特定的Engine
Session = sessionmaker(bind=engine)

# 然后，一些代码块需要创建一个绑定特别Connection的Session
conn = engine.connect()
session = Session(bind=conn)
```


## Session FAQ(最常见问题)

在这个时候，很多用户已经对session有疑问了。这个章节提供了一个使用Session的迷你的FAQ。

### 我要在何时使用sessionmaker？

只需要使用一次，在你应用app的全局部分。它应该查询你应用的一部分配置。如果你的应用在一个包里面
有3个`.py`文件，那么也许你可以把`sessionmaker`放在`__init__.py`文件中；

如果你的应用启动，做了import，但是还不知道它要如何连接哪个数据库，你可以在一个类的代码层面上
绑定一个Session和engine，使用方法`sessionmaker.configure()`来实现。

在这个章节的例子中，我们通常在调用Session的时候之前使用sessionmaker。但是这只是例子的缘故！
在现实情况下，`sessionmaker`可能在模块级别使用。`Session`的实例化可能放在想要连接
数据库的代码部分之前进行。

### 我应该何时构建一个Session，何时commit，何时close？

> 1. 作为一般的规则，保持一个函数和对象访问／操纵数据库数据使用的session生命周期**分离和外部化**，
    这将会帮助达成一个可预见性和一致性的事务型域。
> 2. 确信你自己对事务的开启和结束位置有一个清晰的概念，保持事务**短**，意味着需要在一系列
    操作后停止，而不是保持无止尽的开启状态。

一个`Session()`通常在一个潜在可能数据库访问的逻辑操作开始部分构建。

无论何时使用`Session`来与数据库对话，在开始沟通时会马上开启一个事务。假定`autocommint`
标志让它保持默认(推荐)的设置`False`，这个事务会持续进行直到Session的rollback，commit
和close操作。如果再次使用，这个`Session`会开启一个新的连接，紧随之前事务的结束；Session
能够在多个事务之间保持一个生命周期，尽管一次只能有一个。我们将这两个概念称为：**事务域**和
**session域**。

SQLAlchemy ORM鼓励开发者在它们的应用中是建立这两个域，包括不仅是域的开始和结束，以及这些
域的延伸部分。比如我们应该在一个函数或方法的执行流中使用一个Session实例，应该在整个应用使用
一个全局对象，或者在两个函数／方法之间创建。

开发者的负担部分是需要决定这个域放在哪个位置。`unit of work`模式用来随着事件累计修改并且
周期性的更新它们，保持内存状态的同步性并且知道哪些出现在当地事务中。这个模式在事务域中有效。

通常并不难决定Session域的开始和结束的最佳位置，虽然不同的应用架构可能会引用很难处理的情况。

一个常见的选择是在事务结束时关闭一个Session，意味着事务域和session域同时进行。

但是没有万全的法则来决定事务域。尤其是如果撰写一个web应用。

**不应该**这样做：

```python
# 这是一个"坏方式"

class ThingOne(object):
    def go(self):
        session = Session()
        try:
            session.query(FooBar).update({'x': 5})
            session.commit()
        except:
            session.rollback()
            raise


class ThingTwo(object):
    def go(self):
        session = Session()
        try:
            session.query(Widget).update({"q": 18})
            session.commit()
        except:
            session.rollback()
            raise


def run_my_program():
    ThingOne().go()
    ThingTwo().go()
```

保持session的生命周期（通常事务的周期也一样）**分离和外部化**：

```python
# 这是一个更好的方式

class ThingOne(object):
    def go(self, session):
        session.query(FooBar).update({"x": 5})

class ThingTwo(object):
    def go(self, session):
        session.query(Widget).update({"q": 18})


def run_my_program():
    session = Session()
    try:
        ThingOne().go(session)
        ThingTwo().go(session)

        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()
```

进阶的开发者会试着保持session的细节，我们可以使用`上下文管理器（context manager）`进一步分离概念：

```python
# 另一种方式(不只是唯一的方式)

from contextlib import contextmanager


@contextmanager
def session_scope():
    """提供一个事务域来进行一系列操作。"""
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


def run_my_program():
    with session_scope() as session:
        ThingOne().go(session)
        ThingTwo().go(session)
```

### Session是一个缓存吗？

是也不是...它在某种程度可以看作是一个缓存，因为它实现了`identity map`模式，将对象的主键
作为键来存储对象。但是它**并不会作任何查询缓存**。这意味着，如果你调用
`session.query(Foo).filter_by(name='bar')`，即使`Foo(name='bar')`正处于identity map中，
session并不明白怎么查询到它。它会对数据库发起一个查询，取回结果行，然后查看行中的主键，然后
在本地的identity map中可以看到这个对象已经存在于那里了。只有当你使用`query.get({主键})`
的时候，`Session`可以不必发出查询。

另外，Session默认使用弱引用来存储对象实例。这同样打消了使用Session作为缓存的想法。

Session并不是设计来作为一个全局对象让每个人将它作为对象的"注册器"使用。这些工作都是
**二级缓存**来完成。SQLAlchemy提供了`dogpile.cache`模式来实现二级缓存。

### 我怎么获得一个确定对象的Session？

使用Session中的类方法`object_session()`:

`session = Session.object_session(someobject)`

或者可以使用更新的`inspect`系统：

```python
from sqlalchemy import inspect

session = inspect(someobject).session
```

### Session是线程安全的吗？

`Session`有意使用**非并发**模式，意味着一次存在一个线程中。

。。。


## Session的基础用法

### 查询

`query()`方法接受一个或多个实体并返回一个新的`Query`对象。实体可以指一个映射类，一个Mapper对象，
一个orm描述符，或者一个`AliasedClass`对象：

```python
# 查询一个类
session.query(User).filter_by(name='ed').all()

# 查询多个类，返回一个元组
session.query(User, Address).join("addresses").filter_by(name='ed').all()

# 使用ORM描述符查询
session.query(User.name, User.fullname).all()

# 查询一个mapper
user_mapper = class_mapper(User)
session.query(user_mapper)
```

当`Query`返回结果后，每个实例化后的对象都会存储进identity map，当一个行匹配的对象已经存在，
同样的对象将会被返回。实际例子中，行是否由现存的对象组成取决于这个实例的属性是否过期。一个默认
配置的Session在事务边界自动过期所有实例。

### 增加新的或现存的数据项

`add()`用来为session放入实例。对于过渡的实例，在事务下次刷新时会发出INSERT语句：

```python
user1 = User(name='user1')
user2 = User(name='user2')
session.add(user1)
session.add(user2)

session.commit()        # 把改动写入数据库
```

想一次性对session增加一个items列表，可以使用`add_all()`：

`session.add_all([item1, item2, item3])`

`add()`操作具有**级联**选项，与`save-update`关联。

### 删除

`delete()`方法将一个实例放入Session并标记为删除：

```python
# 标记两个对象为已删除
session.delete(obj1)
session.delete(obj2)

# 提交（或刷新)
session.commit()
```

#### 集合中的删除

在对集合中的成员使用`delete()`删除时会引发一个常见的混淆。当这个集合成员被标记为已删除，
并不影响它在集合内存中的状态，直到这个集合过期。下面例子中，我们阐释即使`Address`对象被
标记为删除，它仍然会存在于User的关联集合中，即使刷新后也一样：

```python
>>> address = user.addresses[1]
>>> session.delete(address)
>>> sesssion.flush()
>>> address in user.addresses
True
```

当上面的session提交后，所有的属性都被过期。下次访问`user.addresses`将会重新读取这个集合，
展示应该的状态：

```python
>>> session.commit()
>>> address in usre.addresses
False
```

通常删除集合中的成员是放弃直接使用`delete()`，而是使用级联行为来自动化调用删除行为。可以使用
`delete-orphan`级联：

```python
mapper(User, user_table, properties={
    "addresses": relationship(Address, cascade="all, delete, delete-orphan"
})

del user.addresses[1]
session.flush()
```

上面例子中，一旦从`User.addresses`集合中移除`Address`对象，`delete-orphan`级联将会
生效，把移除的Address对象传入`delete()`。

#### 筛选标准下的删除

`Session.delete()`的注意事项是你需要一个对象就在手边以方便删除。`Query`对象包含了一个
`delete()`方法基于筛选标准来删除：

`session.query(User).filter(User.id == 7).delete()`

`Query.delete()`方法包含把匹配标准的对象（并且存在于session）过期的功能。但是它也有一些
注意事项，包括"delete"和"delete-orphan"都不会生效。


### 刷新

当`Session`使用默认配置时，刷新步骤通常总是透明执行的。特别是，刷新会出现在任何单独的`Query`
发出之前，会出现在调用`commit()`之前，同样会出现在savepoint(使用`begin_nested()`)之前。

不管用没用自动刷新配置，总是可以使用`flush()`方法来强制刷新：

`session.flush()`

"查询时刷新"的行为可以禁用，通过`sessionmaker`的标志参数`autoflush=False`来实现：

`Sesssion = sessionmaker(autoflush=False)`

另外，autoflush是可以临时关闭的，在任何适合设置`autoflush`属性即可：

```python
mysession = Session()
mysession.autoflush = False
```

刷新步骤**总是**出现在事务中，即使Session配置了`autoflush=True`。如果没有事务，`flush()`
会自动创建它自己的事务并提交。任何刷新时出现的失败/错误都会导致事务回滚(rollback)。如果
没有配置`autoflush=True`模式，需要在刷新失败时手动显式调用`callback()`，即使下层的事务
已经回滚了 - 这叫做所谓的"子事务"。

### 提交

`commit()`用来提交当前的事务。它总是会预先发出`flush()`来把剩余的状态刷新到数据库；这个
特性独立于"autoflush"配置。如果没有事务，将会抛出错误。注意Session的默认行为是总是会有
一个"事务"出现；这个行为可以通过`autocommit=True`来禁用。在自动刷新模式下，一个事务可以
通过调用`begin()`方法来初始化。

> 注意
>> 这里的术语"事务"引用了`Session`本身的事务构造，它可能会维持零到多个真实数据库事务。
    一个独立的DBAPI连接在它首次执行一个SQL表达式时开始参加到一个事务中，剩下的会直到
    session级事务完成。

`commit()`的另一种行为是在提交完成后将所有实例的状态都设置为过期。想要禁用这种行为，
可以配置`sessionmaker`，使用`expire_on_commit=False`。

一般来说，读取到Session的实例永远不会在随后的查询中修改；假定当前的事务被隔离所以只要事务
继续那么状态总是最近的状态。

### 回滚

`rollback()`回滚当前事务。对于一个默认的session配置，session的回滚后状态为：

- 所有的事务都会回滚并且所有的连接都会返回到连接池。除非Session直接绑定到一个连接，这种
情况连接会继续维持(仍然会回滚)
- 对象在session中初始化为pending状态，符合INSERT的语句将会回滚，它们的属性状态仍然保持未变
- 标记为已删除的对象将会转为持久化状态，符合DELETE的居于将会回滚
- 所有未被清除的对象都会被过期

### 关闭

`close()`方法将会发出一个`expunge_all()`，并且解除多个事务／连接资源。当连接返回给连接
池时，事务状态也会回滚。




