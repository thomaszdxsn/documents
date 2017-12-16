# Declrative

Declarative系统一般用于提供SQLAlchemy的ORM的定义类和数据库表之间的映射。Declarative相比SQLAlchemy的`mapper()`增加了若干扩展。

## Basic Use(基础用法)

SQLAlchemy的对象-关系配置牵涉到了`Table`和`mapper()`以及映射类的组合。`declartive`允许允许这三种方式都可以通过类声明的形式来表达。

下面是一个简单的例子：

```python
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class SomeClass(Base):
    __tablename__ = 'some_table'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
```

上面例子中，`declarative_base()`返回一个新的base类，所有的映射类都应该继承它。当类的定义完成后，将会生成一个新的`Table`以及`mapper()`.

生成的table和mapper可以通过属性`__table__`和`__mapper__`来访问:

```python
# 访问映射表
SomeClass.__table__

# 访问Mapper
SomeClass.__mapper__
```

### 定义属性

在之前的例子中，`Column`对象的将会自动以属性名称来命名。

想要显式的设置一个列名，只需要对第一个参数传入字符串作为列名即可：

```python
class SomeClass(Base):
    __tablename__ = 'some_table'
    id = Column('some_table_id', Integer, primary_key=True)
```

属性也可以在构建完毕之后再加入到类中，它们会以合适的方式加入到底层的`Table`和`mapper()`中：

```python
SomeClass.data = Column('data', Unicode)
SomeClass.releted = relationship(RelatedInfo)
```

### 访问metadata

`declarative_bae()`基类包含一个`MetaData`对象，其中收集了新定义的Table对象。这个对象适用于对`MetaData`特定操作的访问。比如，对所有表发出`CREATE`语句：

```python
engine = create_engine("sqlite://")
Base.metadata.create_all(engine)
```

`declarative_base()`也可以接受一个预先定义的`MetaData`对象：

```python
mymetadata = MetaData()
Base = declarative_bae(metadata=mymetadata)
```

### 类构造器

有一个可供便于方便使用的特性，`declarative_base`为类设置了一个默认的构造器，这个构造器可以接受关键字参数，然后将关键字参数赋予给同名属性。

`e = Engineer(primary_language='Python')`

### Mapper配置

Declarative在创建一个声明类的映射时，将会在内部使用`mapper()`函数。对于`mapper()`的参数可以通过类属性`__mapper_args__`来传递:

```python
from datetime import datetime


class Widget(Base):
    __tablename__ = 'widgets'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, nullable=False)

    __mapper_args__ = {
        'version_id_col': timestamp,
        'version_id_generator': lambda v:datetime.now()
    }
```

### 定义SQL表达式

pass

## 配置关系

配置与其它类的关系可以通过一般的方式完成，可以在`relationship()`指定字符串名称：

```python
class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    addresses = relationship('Address', backref='user')


class Address(Base):
    __tablename__ = 'addresses'

    id = Column(Integer, primary_key=True)
    email = Column(String(50))
    user_id = Column(Integer, ForeignKey('users.id'))
```

下面我们使用primary join条件来设定一个关系：

```python
class Address(Base):
    __tablename__ = 'addresses'

    id = Column(Integer, primary_key=True)
    email = Column(String(50))
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship(User, primaryjoin=user_id == User.id)
```

在relationship中可以以字符串形式使用sqlalchemy的函数，如`desc()`或者`func`:

```python
class User(Base):
    # ...
    addresses = relationship("Address",
                        order_by="desc(Address.email)",
                        primaryjoin="Address.user.id==User.id")
```

有时可能有多个模块具有相同的一个类名：

```python
class User(Base):
    # ...
    addresses = relationship("myapp.model.address.Address",
                        order_by="desc(myapp.model.address.Address.email)",
                        primaryjoin="myapp.model.address.Address.user_id==myapp.model.address.User.id")
```

也可以使用callble，比如使用lambda返回最终的对象：

```python
class User(Base):
    # ...
    addresses = relationship(lambda: Address,
                        order_by=lambda: desc(Address.email),
                        primaryjoin=lambda: Address.user_id==User.id)
```

或者可以直接将类本身传入:

```python
User.addresses = relationship(Address,
                    primaryjoin=Address.user_id==User.id)
```

### 配置多对多关系

多对多关系一般要传入`secondary`参数，通常传入一个`Table`对象。`Table`通常分享同一个MetaData对象：

```python
keywords = Table(
    'keywords', Base.metadata,
    Column('author_id', Integer, ForeignKey('authors.id')),
    Column('keyword_id', Integer, ForeignKey('keywords.id'))
)


class Author(Base):
    __tablename__ = 'authors'
    id = Column(Integer, primary_key=True)
    keywords = relationship("Keyword", secondary=keywords)
```

就像`relationship()`的其它参数一样，同样可以对secondary传入一个字符串，它代表中间表的名称(必须存在于`Base.metadata.tables`)：

```python
class Author(Base):
    __tablename__ = 'authors'
    id = Column(Integer, primary_key=True)
    keywords = relationship("Keyword", secondary="keywords")
```

## 表配置

表参数都可以使用`__table_args__`类属性来定义。这个属性可以接受和`Table`构造器相同的位置参数和关键字参数。这个属性可以设定为两种形式，一种是字典：

```python
class MyClass(Base):
    __tablename__ = 'sometable'
    __table_args__ = {"mysql_engine": 'InnoDB'}
```

或者可以使用元组(里面的参数都以位置参数形式传入`Table()`):

```python
class MyClass(Base):
    __tablename__ = 'sometable'
    __table_args__ = (
        ForeignKeyConstraint(['id'], ['remote_table.id']),
        UniqueConstraint('foo')
    )
```

使用元组形式也可以传入关键字参数，即把最后一个参数传入为字典：

```python
class MyClass(Base):
    __tablename__ = 'sometable'
    __table_args__ = (
        ForeignKeyConstraint(['id'], ['remote_table.id']),
        UniqueConstraint('foo'),
        {'autoload': True}
    )
```

### hybird形式使用__table__

除了使用`__tablename__`，也可以直接传入`Table`构造。这时`Column`对象要求必须要有一个列名：

```python
class MyClass(Base):
    __table__ = Table('my_table', Base.metadata,
            Column('id', Integer, primary_key=True),
            Column('name', String(50))
            )
```

