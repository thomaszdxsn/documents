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

`__table__`的方法可以把注意力放在建立表的metadata上面，但是同时又能兼具declarative的优势。下面是一个反射类的例子：

```python
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()
Base.metadata.reflect(some_engine)


class User(Base):
    __table__ = metadata.tables['user']
    

class Address(Base):
    __table__ = metadata.tables['address']
```

注意在使用`__table__`方法时，这个对象是可以直接拿来使用的：

```python
class MyClass(Base):
    __table__ = Table('my_table', Base.metadata,
                    Column('id', Integer, primary_key=True),
                    Column('name', String(50)))

    widgets = relationship(Widet,
                    primaryjoin=Widget.my_class_id==__table__.c.id)
```

另外可以对table对象的属性生成同义词(synonym):

```python
from sqlalchemy.ext.declarative import synonym_for


class MyClass(Base):
    __table__ = Table('my_table', Base.metadata,
        Column('id', Integer, primary_key=True),
        Column('name', String(50))
    )

    _name = __table__.c.name

    @synonym_for('_name')
    def name(self):
        return "Name: %s" %_name
```

### 使用Declarative和反射

可以通过建立一个`Table`然后使用`autoload=True`来轻松的建立映射类：

```python
class MyClass(Base):
    __table__ = Table('mytable', Base.metadata,
                    autoload=True, autoload_with=some_engine)
```

有一种方式可以无需声明engine。即使用Mixin`DeferredReflection`，只有当调用`prepare()`之后才会进行真正的反射：

```python
from sqlalchemy.ext.declarative import declarative_base, DeferredReflection

Base = declarative_base(engine=DeferredReflection)


class Foo(Base):
    __tablename__ = 'foo'
    bars = relationship('Bar')


class Bar(Base):
    __tablename__ = 'bar'
    foo_id = Column(Integer, ForeignKey('foo.id'))
    

Base.prepare(e)
```

## 继承配置

declarative支持三种形式继承方式。

### Joined Table Inheritance

Joined Table继承通过子类继承并且定义了它们自己的表：

```python
class Person(Base):
    __tablename__ = 'people'
    id = Column(Integer, primary_key=True)
    discriminator = Column('type', String(50))
    __mapper_args__ = {'polymorphic_on': discriminator}


class Engineer(Person):
    __tablename__ = 'engineers'
    __mapper_args__ = {'polymorphic_on': 'engineer'}
    id = Column(Integer, ForeignKey("people.id") primary_key=True)
    primary_language = Column(String(50))
```

注意上面的`Engineer.id`属性，由于它和`People.id`属性具有相同的属性名，将会同时表现于`people.id`和`engineers.id`列，如果直接查询将会首先查询`Engineer.id`列：

```python
class Engineer(Person):
    __tablename__ = 'engineers'
    __mapper_args__ = {'polymorhpic_identity': 'engineer'}
    engineer_id = Column('id', Integer, ForeignKey('people.id'),
                    primary_key=True)
    primary_language = Column(String(50))
```

### Single Table Inheritance

Single Table继承通过子类定义，并且没有它自己的表；你可以不用输入`__table__`和`__tablename__`属性:

```python
class Person(Base):
    __tablename__ = 'people'
    id = Column(Integer, primary_key=True)
    discriminator = Column('type', String(50))
    __mapper_args__ = {'polymorhpic': discriminator}

    
class Engineer(Person):
    __mapper_args__ = {"polymorphic_identity": "enginerr"}
    primary_language = Column(String(50))
```

#### 解决列冲突

```python
class Person(Base):
    __tablename__ = 'people'
    id = Column(Integer, primary_key=True)
    discriminator = Column('type', String(50))
    __mapper_args__ = {"polymorhpic_on": discriminator}

    
class Engineer(Person):
    __mapper_args__ = {'polymorphic_identity": "engineer"}
    start_data = Column(DateTime)


class Manager(Person):
    __mapper_args__ = {'polymorhpic_identity': "manager"}
    start_date = Column(DateTime)
```

`start_date`列在`Engineer`和`Manager`同时定义将会引发一个错误:

```python
sqlalchemy.exc.ArgumentError: Column 'start_date' on class
<class '__main__.Manager'> conflicts with existing
column 'people.start_date'
```

```python
from sqlalchemy.ext.declarative import declared_attr


class Person(Base):
    __tablename__ = 'people'
    id = Column(Integer, primary_key=True)
    discriminator = Column("type", String(50))
    __mapper_args__ = {"polymorhpic_on": discriminator}


class Engineer(Person):
    __mapper_args__ = {'polymorhpic_identity': 'engineer'}

    @declared_attr
    def start_date(cls):
        "Start date column, if not presen already"
        return Person.__table__.c.get("start_date", Column(DateTime))


class Manager(Person):
    __mapper_args__ = {'polymorphic_identity': 'manager'}

    @declared_attr
    def start_date(cls):
        "Start date column, if not present already."
        return Person.__table__.c.get('start_date', Column(DateTime))
```

另外也可以使用mixin：

```python
class Person(Base):
    __tablename__ = 'people'
    id = Column(Integer, primary_key=True)
    discriminator = Column('type', String(50))
    __mapper_args__ = {'polymorphic_on': discriminator}

class HasStartDate(object):
    @declared_attr
    def start_date(cls):
        return cls.__table__.c.get('start_date', Column(DateTime))

class Engineer(HasStartDate, Person):
    __mapper_args__ = {'polymorphic_identity': 'engineer'}

class Manager(HasStartDate, Person):
    __mapper_args__ = {'polymorphic_identity': 'manager'}
```

### Concrete Table Inheritance

需要在继承类中加入`concret=True`:

```python
class Person(Base):
    __tablename__ = 'people'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))

class Engineer(Person):
    __tablename__ = 'engineers'
    __mapper_args__ = {'concrete':True}
    id = Column(Integer, primary_key=True)
    primary_language = Column(String(50))
    name = Column(String(50))
```

## Mixin&Base Class

使用`declarative`的一个常见情况是需要共享一些功能，比如设置一个通用类，一些通用的表选项，或者其它映射属性。

```python
from sqlalchemy.ext.declarative import declared_attr


class MyMixin(object):

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    __table_args__ = {"mysql_engine": 'InnoDB'}
    __mapper_args__ = {"always_refresh": True}

    id = Column(Integer, primary_key=True)


class MyModel(MyMixin, Base):
    name = Column(String(1000))
```

上面例子中，`MyModel`会包含一个"id"列作为主键，`__tablename__`属性将会衍生自类本身的名称，已经会继承`MyMixin`里面的`__table_args__`和`__mapper_args__`.


### Argumenting the Base

除了使用纯mixin，这章节使用的技术大多应用于base class本身。可以通过`declarative_base()`的`cls`属性来指定：

```python
from sqlalchemy.ext.declarative import declared_attr


class Base(object):
    @declared_attr
    def __tablename__(cls):
        return cls.__table__.lower()

    __table_args__ = {"mysql_engine": 'InnoDB'}

    id = Column(Integer, primary_key=True)


from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base(cls=Base)


class MyModel(Base):
    name = Column(String(1000))
```

### Mixin in Columns

在一个列中指定一个mixin的常用方式是：

```python
class TimestampMixin(object):
    created_at = Column(DateTime, default=datetime.now())


class MyModel(TiemstampMixin, Base):
    __tablename__ = 'test'

    id = Column(Integer, primary_key=True)
    name = Column(String(1000))
```

```python
from sqlalchemy.ext.declarative import declared_attr


class ReferrenceAddressMixin(object):
    @declared_attr
    def address_id(cls):
        return Column(Integer, ForeignKey('address.id'))


class User(ReferenceAddressMixin, Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
```

### Mixin in Relationships

```python
class RefTargetMixin(object):
    @declared_attr
    def target_id(cls):
        return Column('target_id', ForeignKey('target.id'))

    @declared_attr
    def target(cls):
        return relationship('Target')


class Foo(RefTargetMixin, Base):
    __tablename__ = 'foo'
    id = Column(Integer, primary_key=True)

class Bar(RefTargetMixin, Base):
    __tablename__ = 'bar'
    id = Column(Integer, primary_key=True)

class Target(Base):
    __tablename__ = 'target'
    id = Column(Integer, primary_key=True)
```

#### Using Advanced Relationship Argument

```python
class RefTargetMixin(object):
    @declared_attr
    def target_id(cls):
        return Column('target_id', ForeignKey('target.id'))


    @declared_attr
    def target(cls):
        return relationship(Target,
                    primaryjoin=Target.id==cls.target.id) # 这种用法不对
```

使用上面的类作为mixin，将会获得错误:

```python
sqlalchemy.exc.InvalidRequestError: this ForeignKey's parent column is not yet associated with a Table.
```

上面的情况可以使用lambda来解决：

```python
class RefTargetMixin(object):
    @declared_attr
    def target_id(cls):
        return Column('target_id', ForeignKey('target.id'))

    @declared_attr
    def target(cls):
        return relationship(Target,
                primaryjoin=lambda: Target.id == cls.target_id)
```

或者也可以使用字符串形式:

```python
class RefTargetMixin(object):
    @declared_attr
    def target_id(cls):
        return Column('target_id', ForeignKey('target.id'))

    @declared_attr
    def target(cls):
        return relationship('Target',
                primaryjoin="Target.id==%s.target_id" %cls.__name__)
```


### Mixin in deferred(), column_property(), and other MapperProperty classes

```python
class SomethingMixin(object):
    @declared_attr
    def dprop(cls):
        return deferred(Column(Integer))

        
class Something(SomethingMixin, Base):
    __tablename__ = 'something'
```

```python
class SomethingMixin(object):
    x = Column(Integer)
    y = Column(Integer)

    @declared_attr
    def x_plus_y(cls):
        return column_property(cls.x + cls.y)
```

### Mixin in Association Proxy and Other Attributes

```python
from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import relationship
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.declarative import declarative_base, declared_attr

Base = declarative_base()


class HasStringCollection(object):
    @declared_attr
    def _strings(cls):
        class StringAttribute(Base):
            __tablename__ = cls.stinrg_table_name
            id = Column(Integer, primary_key=True)
            value = Column(String(50), nullable=False)
            parent_id = Column(Integer,
                            ForeignKey('%s.id' %cls.__tablename__),
                            nullable=False)

            def __init__(self, value):
                self.value = value

        return relationship(StringAttribute)

    @declared_attr
    def strings(cls):
        return association_proxy('_strings', 'value')


class TypeA(HasStringCollection, Base):
    __tablename__ = 'type_a'
    string_table_name = 'type_a_strings'
    id = Column(Integer(), primary_key=True)


class TypeB(HasStringCollection, Base):
    __tablename__ = 'type_b'
    string_table_name = 'type_b_strings'
    id = Column(Integer(), primary_key=True)
```

### Controlling table inheritance with mixins

```python
from sqlalchemy.ext.declarative import declared_attr


class Tablename:
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()


class Person(Tablename, Base):
    id = Column(Integer, primary_key=True)
    discriminator = Column('type', String(50))
    __mapper_args__ = {'polymorphic_on': discriminator}


class Engineer(Person):
    __tablename__ = None
    __mapper_args__ = {'polymorhpic_on': 'engineer'}
    primary_language = Column(String(50))
```


```python
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.declarative import has_inherited_table


class Tablename(object):
    @declared_attr
    def __tablename__(cls):
        if has_inherited_table(cls):
            return None
        return cls.__name__.lower()


class Person(Tablename, Base):
    id = Column(Integer, primary_key=True)
    discriminator = Column('type', String(50))
    __mapper_args__ = {'polymorhic_on': discriminator}


class Engineer(Person):
    primary_language = Column(String(50))
    __mapper_args__ = {'polymorhpic_identity': 'engineer'}
```

### Mixing in Columns in Inheritance Scenarios

pass

### Combining Table/Mapper Arguments from Multiple Mixins

pass

### Creating Indexes with Mixins

```python
class MyMixin(object):
    a = Column(Integer)
    b = Column(Integer)

    @declared_attr
    def __table_args__(cls):
        return (Index('test_idx_%s' %cls.__tablename__, 'a', 'b'),)


class MyModel(MyMixin, Base):
    __tablename__ = 'atable'
    c = Column(Integer, primary_key=True)
```


## Declarative API

### API Reference

- `sqlalchemy.ext.declarative.declarative_base(bind=None, metadata=None, mapper=None, cls=<type 'object'>, name='Base', constructor=<function__init__>, class_registry=None, metaclass=<class 'sqlalchemy.ext.declarative.api.DeclarativeMeta'>)`

    构建一个declarative定义的基类。

    新的类会给定一个metadata，它会生成适当的`Table`对象，根据类中定义的信息生成合适的`mapper()`对象。

    参数:

    - `bind`: 一个可选的`Connectable`，将会把这个bind参数赋值给MetaData实例

    - `metadata`: 一个可选的`MetaData`实例。所以继承这个base的子类都会默认共享这个MetaData.如果没有传入实例这默认会生成一个新的MetaData实例。MetaData实例可以通过`.metadata`属性来访问。

    - `mapper`: 一个可选的可调用对象，默认为`mapper()`.将用来映射子类和它的Table.

    - `cls`: 默认为`object`.一个用于生成基类的类型。可以是一个类或者一个类元祖(多个类).

    - `name`: 默认为`Base`.生成类的显示名称。多数情况自定义这个选项没什么意义，但是可以在调试和回溯时显得更加清晰。

    - `constructor`: 默认为`_declarative_constructor()`.

    - `class_registry`: 可选的字典，将会用来作为类名的registry.

    - `metaclass`: 默认为`DeclarativeMeta`.


- `sqlalchemy.ext.declarative.as_declarative(**kw)`

    `declrative_base()`的类装饰器.

    为发送到`declarative_base()`的`cls`提供了一个快捷方式，可以允许一个基类原地转换为declarative base:

    ```python
    from sqlalchemy.ext.declarative import as_declarative

    
    @as_declarative()
    class Base(object):
        @declared_attr
        def __tablename__(cls):
            return cls.__name__.lower()

        id = Column(Integer, primary_key=True)


    class MyMappedClass(Base):
        # ...
    ```

    所有传入到`@as_declarative()`的关键字参数都将传入到`declarative_base()`中。


- `sqlalchemy.ext.declarative.declared_attr(fget, cacading=False)`

    基类： `sqlalchemy.orm.base._MappedAttribute, __builtin__.property`

    标记一个类级别的方法，让它代表一个映射属性或者一个特殊的declarative成员名称.

    可用于mixin:

    ```python
    class ProvidesUser(object):
        """一个Mixin, 为类增加一个'user'关系 """

        @declared_attr
        def user(self):
            return relationship('User')
    ```

    也可以用于映射类，比如提供一个"polymorphic"继承参数：

    ```python
    class Employee(Base):
        id = Column(Integer, primary_key=True)
        type = Column(String(50), nullable=False)

        @declared_attr
        def __tablename__(cls):
            return cls.__name__.lower()

        @declared_attr
        def __mapper_args__(cls):
            if cls.__name__ == 'Employee':
                return {
                    "polymorphic_on: cls.type,
                    "polymorphic_identity": "Employee"
                }
            else:
                return {"polymorphic_identity": cls.__name__}
    ```

    - `cascading`

        标记一个`declared_attr`为cascading.

        这是一个用于特殊情况的修饰符，它指出在一个mapped继承的场景下，一个column或者MapperProperty属性应该在每个子类中区分声明。

        比如下面的例子中，MyClass和MySubClass都会建立一个单独的`id`列：

        ```python
        class HasIdMixin(object):
            @declared_attr.cascading
            def id(cls):
                if has_inherited_table(cls):
                    return Column(ForeignKey('myclass.id'), primary_key=True)
                else:
                    return Column(Integer, primary_key=True)


        class MyClass(HasIdMixin Base):
            __tablename__ = 'myclass'
            # ...


        class MySubClass(MyClass):
            # ...
        ```

- `sqlalchemy.ext.declarative.api._declarative_constructor(self, **kwargs)`

    一个简单的构造器，允许通过kwargs来初始化。

    使用`kwargs`中的名称和值来构建实例的属性。

    只有键名出现在实例的类的属性中才允许。可以是任何映射列或者关系。

- `sqlalchemy.ext.declarative.has_inherited_table(cls)`

    给定一个类，如果有任何类继承自这个类则返回True，否则返回False.


- `sqlalchemy.ext.declarative.synonym_for(name, map_column=False)`

    装饰器，让Python`property`可以查询一个同义词的列。

    ```python
    @synonym_for('col')
    @property
    def prop(self):
        return "special sauce"
    ```

    常规的`synonym()`是这么用的:

    `prop = synonym('col', descriptor=property(_read_prop, _write_prop))`

- `sqlalchemy.ext.declarative.comparable_using(comparator_factory)`

    装饰器，允许一个Python`property`可以用于查询标准（criteria）.

    ```python
    @comparable_using(MyComparatorType)
    @property
    def prop(self):
        return "special sauce"
    ```

- `sqlalchemy.ext.declarative.instrument_declarative(cls, registry, metadata)`

    给定一个类，让这个类declaratively, 使用给定的registry，可以是一个字典或者一个`MetaData`对象。

- `sqlalchemy.ext.declarative.AbstractConcreteBase`

    基类：`sqlalchemy.ext.declartive.api.ConcreteBase`

    "concrete"声明式映射的helper类。

    pass...

- `sqlalchemy.ext.declarative.ConcreteBase`

    "concrete"声明式映射的helper类。

    pass...


- `sqlalchemy.ext.declarative.DeferredReflection`

    一个帮助类，用于映射构建的`deferred`反射步骤。

    ```python
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.ext.declarative import DeferredReflection
    
    Base = declarative_base()

    class MyClass(DeferredReflection, Base):
        __tablename__ = 'mytable'
    ```

    上面例子中, `MyClass`还没有被映射。在另外一系列的类都安装上面的风格被定义之后，所有的table都可以通过`prepare()`来映射：

    ```python
    engine = create_engine("someengine://...")
    DeferredReflection.prepare(engine)
    ```

### Special Directives

- `__declare_last__()`

    这个钩子允许类级函数的定义中自动调用`MapperEvents.after_configured()`事件:

    ```python
    class MyClass(Base):
        @classmethod
        def __declare_last__(cls):
            # ...
            # do something with mappings
    ```

- `__declare_first__()`

    很像`__declare_last__()`，但是它会在mapper配置前映射，通过事件`MapperEvents.before_configured()`.

    ```python
    class MyClass(Base):
        @classmethod
        def __declare_first__(cls):
            # ...
            # do something before mappings are configured
    ```

- `__abstract__`

    `__abstract__`可以让这个类跳过table或mapper的生成过程。但是可用于继承或者Mixin：

    ```python
    class SomeAbstractBase(Base):
        __abstract__ = True

        def some_helpful_method(self):
            # ...

        @declared_attr
        def __mapper_args__(cls):
            return {"helpful mapper arguments": True}


    class MyMappedClass(SomeAbstractBase):
        # ...
    ```

    有一种使用`__abstract__`的场景是，不同的Base具有不同的MetaData:

    ```python
    Base = declarative_base()

    class DefaultBase(Base):
        __abstract__ = True
        metadata = MetaData()


    class OtherBase(Base):
        __abstract__ = True
        metadata = MetaData()
    ```

- `__table_cls__`

    允许callable/class用来自定义Table的生成:

    ```python
    class MyMixin(object):
        @classmethod
        def __table_cls__(cls, name, metadata, *arg **kw):
            return Table(
                "my_" + name,
                metadata, *arg, **kw
            )
    ```

    