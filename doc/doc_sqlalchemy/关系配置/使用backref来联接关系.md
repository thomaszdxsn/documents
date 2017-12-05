[toc]

## 通过backref来联接关系

`backref`关键字参数在ORM教程中已经介绍过了，并且在很多的例子中也提到过。它到底做了什么？让我们从经典的User和Address场景开始：

```python
from sqlalchemy import Integer, ForeignKey, String, Column
from sqlalchemy.ext.declarative import declrative_base
from sqlalchemy.orm import relathionship


Base = declarate_base()


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String)

    addresses = relationship("Address", backref='user')


class Address(Base):
    __tablename__ = 'address'
    id = Column(Integer, primary_key=True)
    email = Column(String)
    user_id = Column(Integer, ForeignKey('user.id'))
```

上面配置为User建立了一个Address对象集合，可以通过`User.addresses`调用。并且在Address中建立一个`.user`属性，可以引用它的父级User对象。

事实上，`backref`关键字参数只是一个在Address映射中放入第二个`relationship()`的快捷方式，并且包含在每一边都建立对镜像属性操作的事件监听。

上面的配置等同于：

```python
from sqlalchemy import Integer, ForeignKey, String, Column
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relathionship

Base = declrative_base()


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String)

    addresses = relationship("Address", back_populates='user')


class Address(Base):
    __tablename__ = 'address'
    id = Column(Integer, primary_key=True)
    email = Column(String)
    user_id = Column(Integer, ForeignKey("user.id"))

    user = relationship("User", back_populates="addresses")
```

上面例子中，我们为`Address`显式加入一个`.user`关系。在所有关系中，`back_populates`直接告诉每个关系另外一个的信息，告诉它们应该建立双向关系。主要的影响就是，这个关系配置为每个属性增加了一个事件处理程序，具备“但一个集合发生追加时，使用特定的属性名设置待定的属性".这个行为在下面的例子中解释，在开始阶段，`.addresses`集合为空，以及`.user`属性为`None`:

```python
>>> u1 = User()
>>> a1 = Address()
>>> u1.addresses
[]
>>> print(a1.user)
None
```

然而，一旦`Address`追加到`u1.addresses`及和，集合以及标量属性都将构建而成：

```python
>>> u1.addresses.append(a1)
>>> u1.addresses
[<__main__.Address object at 0x12a6ed0]
>>> a1.user
<__main__.User object at 0x12a6590>
```

这个行为在相反的操作(删除)中同样奏效，在两侧的操作是想等的。比如当`.user`设置为None，在`User.addresses`集合中同样也会被移除：

```python
>>> a1.user = None
>>> u1.addresses
[]
```

对`.addresses`集合以及`.user`属性的操作完全发生在Python，没有对数据库有任何操作。没有这个行为，将会发送多余的数据库查询操作。

记住，当`backref`关键字用于一个单独的关系，完全等同与对两个关系分别使用`back_populates`。

### Backref参数

我们建立的`backref`关键字仅仅是在建立双侧关系的一种快捷方式。这个快捷方式的部分行为是可以将本来可以通过`relationship()`设定的若干参数应用到另一个方向。通常的用法是多对多关系中的`secondary`参数，或者一对多/多对一关系中的`primaryjoin`参数。

我们想要限制Address对象的集合，必须起始为"tony":

```python
from sqlalchemy import Integer, ForeignKey, String, Column
from sqlalchemy.ext.declarative import declrative_base
from sqlalchemy.orm import relathionship

Base = declrative_base()


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String)

    addresses = relathionship("Addresses",
                            primaryjoin="and_(User.id == Address.user_id, ",
                                    "Address.email.startswith('tony'))",
                            backref="user")


class Address(Base):
    __tablename__ = 'address'
    id = Column(Integer, primary_key=True)
    email = Column(String)
    user_id = Column(Integer, ForeignKey('user.id'))
```

我们可以观察到，当检查结果属性时，关系中的每一侧都应用了join条件：

```python
>>> print(User.addresses.property.primaryjoin)
"user".id = address.user_id AND address.email LIKE : email_1 || '%%'
>>> print(Address.user.property.primaryjoin)
"user".id = address.user_id AND address.email LIKE : email_1 || '%%'
```

另一个经常使用的场景时，我们通过backref建立双侧关系时同样可以传入一些关系中的参数，如`lazy`, `remote_side`, `cascade`和`cascade_backrefs`。这些时候我们需要使用`backref()`函数来代替字符串：

```python
# 其它import
from sqlalchemy.orm improt backref


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String)

    addresses = relathionship("Address",
                    backref=backref("user", lazy='joined'))
```

上面例子中，我们直接在`Address.user`端放入可一个`lazy="joined"`，表明在对一个Address对象查询时，将会自动发出一个join联接到User的查询。`backref()`函数的格式以及接受的参数等同于`relationship()`。

### 单向backref

一个不常见的例子是“单向backref”，意思是"back-populating"行为只在一个方向生效。一个例子是一个集合必须包含筛选`primaryjoin`的条件。我们可以按需为这个集合追加数据，并对待定对象构成父对象。然而，我们可能也想item不是及和的一部分，但是同样具有parent关联 - 这些item应该永远不出现在集合中。

继续上面的例子，当建立一个`primaryjoin`的限制，只有邮箱地址以"tony"起始的Address对象会出现在集合中，一般的backref行为是在两侧都建立item。我们不想要如下这种行为：

```python
>>> u1 = User()
>>> a1 = Address(email='many')
>>> a1.user = u1
>>> u1.addresses
[<__main__.Address object at 0x1411910>]
```

上面例子中，Address对象不匹配“起始为tony”的标准但是同样出现在`u1.addresses`集合中。当这些对象刷新后，这个事务提交，它们的属性过期并重载，下次访问`addresses`及和时将不会再出现Address对象（由于筛选条件）。但是我们可以通过两个relationship()来实现另一种行为：

```python
from sqlalchemy import Integer, ForeignKey, String, Column
from sqlalchemy.ext.declarative import declrative_base
from sqlalchemy.orm import relathionship

Base = declrative_base()


Class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    addresses = relationship("Address",
                        primaryjoin="and_(User.id == Address.user_id, "
                                    "Address.email.startswith('tony'))",
                        back_populates="user")


class Address(Base):
    __tablename__ = 'address'
    id = Column(Integer, primary_key=True)
    email = Column(String)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship("User")
```

上面的场景下，对`User.addresses`的追加将会总是对`Address`对象建立一个`.user`属性：

```python
>>> u1 = User()
>>> a1 = Address(email='tony')
>>> u1.addresses.append(a1)
>>> a1.user
<__main__.User objectat 0x1411850>
```

然而，把一个User对象设置为Address的`.user`属性，并不会把这个Address追加到集合中：

```python
>>> a2 = Address(email='mary')
>>> a2.user = u1
>>> a2 in u1.addresses
False
```

