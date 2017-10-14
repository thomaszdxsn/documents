[TOC]

文章原链接:[http://docs.sqlalchemy.org/en/rel_1_1/orm/mapper_config.html](http://docs.sqlalchemy.org/en/rel_1_1/orm/mapper_config.html)

## 映射类型

SQLAlchemy有两种完全不同风格的映射设置。两种风格是可以交织的，最后的结果都是一样的。一个用户定义类是通过`mapper()`函数映射成一个Table对象的。

### 声明式映射

`声明式映射(Declrative Mapping)`是SQLalchemy中的一种典型的映射方式。使用`Declarative`系统，用户定义类的Table元数据在映射时会立即定义。

```python
from sqlalchemy.ext.declrative import declrative_base
from sqlalchemy import Column, Integer, String, ForeignKey

Base = declrative_base()

class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    fullname = Column(String)
    password = Column(String)
```

上面例子中，是一个基础的还有4个列的表。附加属性，例如和其它映射类的关系，同样定义在映射类的属性中。

```python
class  User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    fullname = Column(String)
    password = Column(String)

    addresses = relationship("Address", backref='user', order_by='Address.id')


class Address(Base):
    __tablename__ = 'address'

    id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey('user.id'))
    email_address = Column(String)
```

### 经典映射

“经典映射”即使用`mapper()`函数来配置映射，而不用声明系统。这是SQLAlchemy原始的映射API，也仍然是ORM的基础映射系统。

在古典映射形式中，表元数据需要使用`Table`来独立创建，然后通过`mapper()`把它和User类联系起来。

```python
from sqlalchemy import Table, MetaData, Column, Integer, String, ForeignKey
from sqlalchemy.orm import mapper

metadata = MetaData()

user = Table('user', metadata,
            Column('id', Integer, primary_key=True),
            Column('name', String(50)),
            Column('fullname', String(50)),
            Column('password', String(12))
            )


class User(object):
    def __init__(self, name, fullname, password):
        self.name = name
        self.fullname = fullname
        self.password = password

mapper(User, user)
```

关于映射属性的信息，比如类的关系，通过`properties`字典提供。下面例子创建了第二个映射`Address`，通过`relationship()`来联系`User`。

```python
address = Table('address', metadata,
            Column('id', Integer, primary_key=True),
            Column('user_id', Integer, ForeignKey('user.id')),
            Column('email_address', String(50))
            )

mapper(User, user, properties={
    'addresses': relationship(Address, backref='addresses', order_by=address.c.id)
})
mapper(Address, address)
```

在使用古典映射时，访问列时的API类似Core系统，如`address.c.id`，而不是使用`address.id`。

### 映射、对象的运行时内省

任何类映射类都有一个`Mapper`对象。使用`inspect()`函数可以从映射类中获得一个Mapper对象。

```python
>>> from sqlalchemy import inspect
>>> insp = inspect(User)
```

详细信息可以通过类似语法`Mappler.columns`获得。

```python
>>> insp.columns
<sqlalchemy.util._collections.OrderedProperties object at 0x102f407f8>
```

这是一个命名空间，可以通过列表格式或通过单独的属性名看到。

```python
>>> list(insp.columns)
[Column('id', Integer(), table=<user>, primary_key=True, nullable=False), Column('name', String(length=50), table=<user>), Column('fullname', String(length=50), table=<user>), Column('password', String(length=12), table=<user>)]
>>> insp.columns.name
Column('name', String(length=50), table=<user>)
```

还有一些命名空间，包括`Mapper.all_orm_descriptors`，它包含所有的映射属性以及hybirds，连接代理(association proxies)。

```python
>>> insp.all_orm_descriptors
<sqlalchemy.util._collections.ImmutableProperties object at 0x1040e2c68>
>>> insp.all_orm_descriptors.keys()
['fullname', 'password', 'name', 'id']
```

以及还有`Mapper.column_attrs`:

```python
>>> list(insp.column_attrs)
[<ColumnProperty at 0x10403fde0; id>, <ColumnProperty at 0x10403fce8; name>, <ColumnProperty at 0x1040e9050; fullname>, <ColumnProperty at 0x1040e9148; password>]
>>> insp.column_attrs.name
<ColumnProperty at 0x10403fce8; name>
>>> insp.column_attrs.name.expression
Column('name', String(length=50), table=<user>)
```

## 映射列和SQL表达式

这章节讨论表的列和SQL表达式如何映射到独立的对象属性。

### 映射表列

`mapper()`默认的行为是它会组装Table中的所有列到映射对象的属性，这个行为是可以修改的。

#### 从属性名中区分命名列

映射中默认会把列名分享给被映射对象的属性。

赋值给Python属性的名称是可以修改的，我们马上要介绍这点，先创建声明式映射。

```python
class User(Base):
    __tablename__ = 'user'
    id = Column('user_id', Integer, primary_key=True)
    name = Column('user_name', String(50))
```

上面例子中，`User.id`联系到`user_id`列，`User.name`联系到`user_name`列。

当映射一个现存表时，可以直接引用Column对象

```python
class User(Base):
    __table__ = user_table
    id = user_table.c.user_id
    name = user_table.c.user_name
```

或者在古典映射中，在properties中放入应该的键值。

```python
mapper(User, user_table, properties={
    'id': user_table.c.user_id,
    'name': user_table.c.table_name
})
```

#### 从映射表中自动列名规划

在上一节中，我们展示了一个列如何在映射类中有不同名称的名称。但是我们并没有列出列清单，而是直接通过Table对象的放射自动生成。在这节中，我们使用`DDLEvents.column_reflect()`来拦截Column对象的生成用来作为Column.key的选择。

```python
@event.listen_for(Table, "column_reflect")
def column_reflect(inspector, table, column_info):
    # 设置 column.key = "attr_<小写名称>"
    column_info['key'] = "attr_{}".format(column_info['name'].lower)
```

```python
class MyClass(Base):
    __table__ = Table("some_table", Base.metadata,
                    autoreload=True, autoreload_with=some_engine)
```

```python
@event.listen_for(Table, 'column_reflect')
def column_reflect(inspector, table, column_info):
    if table.metadata is Base.metadata:
        column_info['key'] = "attr_%s" % column_info['name'].lower()
```

#### 为所有列加上前缀

一个快速为列名加上前缀的方法，就是在映射一个Table对象时，使用`column_prefix`。

```python
class User(Base):
    __table__ = user_table
    __mapper_args__ = {"column_prefix": "_"}
```

#### 对列级别选项使用column_property

可以使用`column_property()`函数。这个函数在mapper()时明确创建了`ColumnPeoperty`，用来跟踪那个Column。我们可以在使用`column_property()`时可以为Column传入额外的参数。在下面例子中，我么传入了一个选项`active_history`，它指出对一个列值的改变应该先返回之前的值。

```python
from sqlalchemy.orm import column_property


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = column_property(Column(String(50)), active_history=True)
```

`column_property()`可以用来把多个列映射到一个属性中。

```python
class User(Base):
    __table__ = user.join(address)

    # 把"user.id", address.user_id放入一个id属性
    id = column_property(user_table.c.id, address_table.c.user_id)
```

另一个使用`column_property()`的例子是为属性指定一个SQL表达式，比如下面的fullname属性是firstname和lastname两个属性的字符串串联结果。

```python
class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    firstname = Column(String(50))
    lastname = Column(String(50))
    fullname = column_property(firstname + ' ' + lastname)
```

`column_property()`的源码：

    `sqlalchemy.orm.column_property(*columns, *kwargs)

为映射类提供一个列级别的property。

参数：

* *cols - 映射列对象的列表

* active_history=False

    当设置为True时，指出在替换时之前的值也会载入。这个值可以通过`attributes.get_history()`或者`Session.is_modified()`来获得。

* comparator_factory

    一个继承自`ColumnProperty.Comparator`的类，为SQL中的比较操作符生成自定义SQL字句。

* group

    为这个property定义的组名，用在deferred

* deferred

    当设置为True时，这个列属性是延后的，以为着它不会立即读取，只有当属性第一次访问时才会被读取。

* doc

    可选的参数，用来作为描述符的文档字符串。

* expire_on_flush=True

* info

    可选的数据字典，它会构成这个对象的`MapperProperty.info`属性。

* extension

    传入一个`AttributeExtension`实例，或者一个实例列表。

#### 映射一个表列的子集

有时，一个`Table`对象可以用来反射数据库表结构。有时不一定要把表中的所有列都反射，使用`include_properties`或`exluce_properties`参数来指定映射列的子集。

```python
class User(Base):
    __table__ = user_table
    __mapper_args__ = {
        'include_properties': ['user_id', 'user_name']
    }
```

将会映射User类到user_table表，只会包含`user_id`和`user_name`两个列 - 剩下的不会引用。下面的例子也是一样。

```python
class Address(Base):
    __table__ = address_table
    __mapper_args__ = {
        'include_properties': ['street', 'city', 'state', 'zip']
    }
```

当这个映射被使用，在使用`Query`时不会返回没有包含在定义中的列。

有些情况下，多个列可以能有同样的名字，比如映射一到两张表的join结果，它们分享同样的列名。这是同样可以用这个方式来指定哪些列应该包含。

```python
class UserAddress(Base):
    __table__ = user_table.join(addresses_table)
    __mapper_args__ = {
        'exclude_properties': [address_table.c.id],
        'primary_key': [user_table.c.id]
    }
```

### 用映射类来当作SQL表达式

映射类的属性可以和SQL表达式绑定，可以用在查询中，很方便。

#### 使用Hybird

最简单的办法，适用于大多数用来绑定相对简单的SQL表达式到类属性，就是使用所谓的"hybird"属性，hybird属性提供了一个表达式同时作用于Python和SQL。

例如，下面有一个映射类User，包含属性`firstname`和`lastname`，并且包含一个"hybird"属性`fullname`，它是两个字符串的一个串联。

```python
from sqlalchemy.ext.hybird import hybird_property


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    first_name = Column(String(50))
    last_name = Column(String(50))

    @hybird_properties
    def fullname(self):
        return self.firstname + ' ' + self.lastname
```

`fullname`可以同时使用在实例和类级别中。

```python
some_user = session.query(User).first()
print(some_user.fullname)
```

并且可以用于查询。

```python
some_user = session.query(User).filter(User.fullname == 'John Smith').first()
```

这是个简单的例子。通常，SQL表达式和Python表达式的区分需要使用`hybird_properties.expression()`。下面例子我们解释hybird内部，使用`if`语句和`sql.expression.case()`来生成SQL表达式。

```python
from sqlalchemy.ext.hybird import hybird_property
from sqlalchemy.sql import case


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    firstname = Column(String(50))
    lastname = Column(String(50))

    @hybird_property
    def fullname(self):
        if self.firstname is not None:
            return self.firstname + ' ' + self.lastname
        else:
            return self.lastname

    @fullname.expression
    def fullname(cls):
        return case([
            (cls.firstname != None, cls.firstname + ' ' + cls.lastname),
        ], else_=cls.lastname)
```

#### 使用column_property

`orm.column_property()`函数用来映射一个SQL表达式，原理类似于常规的映射。使用这个技术，该属性会同其它属性一并读取。这在一些情况下比hybird更加有优势。

缺点是，使用`orm.column_property()`使用的SQL表达式必须兼容SELECT语句。

```python
from sqlalchemy.orm import column_property

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    firstname = Column(String(50))
    lastname = Column(String(50))
    fullname = column_property(firstname + " " + lastname)
```

想要使用相关子查询：

```python
from sqlalchemy.orm import column_property
from sqlalchemy import select, func
from sqlalchemy import Column, Integer, String, ForeignKey

from sqlalchemy.ext.declarative import declrative_base

Base = declrative_base()


class Address(Base):
    __tablename__ = 'address'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    address_count = column_property(
        select([func.count(Address.id)]).\
            where(Address.user_id == id).\
            correlate_except(Address)
    )
```

上面例子中，我们构建的`select()`是这样的。

```python
select([func.count(Address.id)]).\
    where(Address.user_id == id).\
    correlate_except(Address)
```

这条表达式的意义是，查询当`Address.user_id`等于`id`(在这个上下文中指类中的属性id，如果在另外的情况使用需要使用`User.id`)时，`Address.id`的计数值。

`select.correlate_except()`命令指出FROM字句的每个元素都应该被select忽略。这个方法不是严格必须的。

至于多对多关系，使用`and_()`来join关联的表，下面使用经典声明来解释。

```python
from sqlalchemy import and_


mapper(Author, authors, properties={
    'book_count': column_property(
                        select([func.count(book.c.id),
                            and_(
                                book_authors.c.author_id == authors.c.id,
                                book_authors.c.book_id == books.c.id
                            )))
})
```

#### 使用普通描述符

想要使用比`orm.column_property()`和`hybird_property()`更精密的SQL表达式。可以用Python的`@property`装饰器来标记为只读属性。在下面函数中，`object_session()`用来定位Session中相符的对象。

```python
from sqlalchemy.orm import object_session
from sqlalchemy improt select, func


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    firstname = Column(String(50))
    lastname = Column(String(50))

    @property
    def address_count(self):
        return object_session(self).\
                scalar(
                    select([func.count(Address.id)]).\
                        where(Address.user_id == self.id)
                )
```

### 改变属性行为

#### 简单的验证器

一个验证属性最快的方式就是使用`validates()`装饰器。一个属性装饰器可以抛出一个异常，暂停程序处理或改变属性的值。`Validators`(验证器)，就是所有属性的扩展，可以在用户范围的代码中调用。

```python
from sqlalchemy.orm import validates


class EmailAddress(Base):
    __tablename__ = 'address'

    id = Column(Integer, primary_key=True)
    email = Column(String)

    @validates('email')
    def validate_email(self, key, address):
        assert @ in address
        return address
```

验证器同样适合于集合增加事件，即数据加入到集合中的时候。

```python
from sqlalchemy.orm import validates


class User(Base):
    # ...

    addresses = relationship('Address')

    @validates('addresses')
    def validate_address(self, key, address):
        assert '@' in address.email
        return address
```

这个验证函数默认没有响应集合移除事件，因为一般情况下移除数据不需要验证。但是，`validates()`支持这个事件，只要标明`include_removing=True`。在装饰器中使用这个标识后，需要在被装饰函数加入一个新的布尔值参数`is_remove`。

```python
from sqlalchemy.orm import validates


class User(Base):
    # ...

    addresses = relationship("Address")

    @validates('addresses', include_removes=True)
    def validate_address(self, key, address, is_remove):
        if is_remove:
            return ValueError(
                'not allow to remove item from the collection'
            )
        else:
            assert '@' in address.email
            return address
```

因为backref，默认是互相依赖的验证器，使用`include_backrefs=False`。使用这个标识，我们设置False，来预防事件在backref时出现**不会**调用这个验证函数。

```python
from sqlalchemy.orm import validates


class User(Base):
    # ...

    addresses = relationship('Address', backref='user')

    @validates('addresses', include_backref=False)
    def validate_address(self, key, address):
        assert '@' in address
        return address
```

在上面例子中，如果我们为`Address.user`比如`some_address.user = some_user`，验证函数`validate_address()`不会调用 - 因为这个事件是通过backref发生的。

注意`validates()`装饰器是一个放在属性事件上面的简单函数。应用中可以更加细粒度的控制事件变动的行为，可以阅读[AttributeEvent](http://docs.sqlalchemy.org/en/rel_1_1/orm/events.html#sqlalchemy.orm.events.AttributeEvents)的描述。

函数分析：

    sqlalchemy.orm.validates(*names, **kwargs)

装饰一个方法，让它变为验证器。

指定一个方法为一个验证器，这个方法接受验证器中制定的属性名作为参数，也可以是一个集合。这个方法可以在验证失败时抛出异常(`ValueError`和`AssertError`是很好的选择)，或者在这个过程中修改或替换那个值，这个函数应该返回制定的值。


参数:

* *names - 应该被验证的属性列表

* include_removes

    如果值为True，‘移除’事件也会被发送到验证函数 - 被装饰函数必须接受一个额外的`is_remove`，这是一个bool参数。

* include_backrefs

    默认为True；如果设置为False，那么通过backref发生的事件则不会调用验证函数。如果向设置双边的验证器函数，可以这样设置。

#### 使用描述符和hybird

改变属性修改行为更复杂的方法是使用`descriptors`描述符。Python中最常用的描述符是`property()`函数。SQLAlchemy标准的描述符技术是创建一个普通的描述符，用它来为另一个不同名称的属性来读取映射属性。

```python
class EmailAddress(Base):
    __tablename__ = 'email_address'

    id = Column(Integer, primary_key=True)

    # 属性名包括一个下划线，和列名不同
    _email = Column('email', String)

    # 然后创建一个'.email'属性
    # 用来get/set '._email'
    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, email):
        self._email = email
```

上面的方法可以起作用，但是我们可以加入更多东西。

```python
from sqlalchemy.ext.hybird import hybird_propery


class EmailAddress(Base):
    __tablename__ = 'email_address'

    id = Column(Integer, primary_key=True)

    _email = Column('email', String)

    @hybird_propery
    def email(self):
        return self._email

    @email.setter
    def email(self, email):
        self._email = email
```

```python
from sqlalchemy.orm import Session

session = Session()

address = session.query(EmailAddress).\
                filter(EmailAddress.email == 'address@example.com').\
                one()

address.email = 'otheraddress@example.com'
session.commit()
```

`hybird_property`允许我们改变属性的行为。

```python
class EmailAddress(Base):
    __tablename__ = 'email_address'

    id = Column(Integer, primary_key=True)
    _email = Column("email", String)

    @hybird_property
    def email(self):
        """返回_email的值，直到倒数第十二个字符"""
        return self._email[:-12]

    @email.setter
    def email(self, email):
        """设置_email的值，
        最后12个字符加入@example.com
        """
        self._email = email + '@example.com'

    @email.expression
    def email(cls):
        """生成一个SQL表达式"""
        return func.substr(cls._email, 0, func.length(cls._email) - 12)
```

```
address = session.query(EmailAddress).filter(EmailAddress.email == 'address').one()

SELECT address.email AS address_email, address.id AS address_id
FROM address
WHERE substr(address.email, ?, length(address.email) - ?) = ?
(0, 12, 'address')
```

#### 同义(synonym)

同义是指映射类级别的构造器，让类中的任何属性可以称为另一个被映射属性的“镜像”。

在大多数基础的场景中，同义是一个让属性通过另一个名称访问的方法。

```python
class MyClass(Base):
    __tablename__ = 'my_table'

    id = Column(Integer, primary_key=True)
    job_status = Column(String(50))

    status = synonym('job_status')
```

上面的类有两个属性`.jog_status`和`status`的行为共享一个属性。下面是以SQL形式显示。

```python
>>> print(MyClass.job_status == 'some_status')
my_table.job_status = :job_status_1

>>> print(MyClass.status == 'some_status')
my_table.job_status = :job_status_1
```

在实例形式显示。

```python
>>> m1 = MyClass(status='x')
>>> m1.status, m1.job_status
('x', 'x')

>>> m1.job_status = 'y'
>>> m1.status, m1.job_status
('y', 'y')
```

`synonym()`也可以用于property --转换为 `MapperProperty`。

```python
class MyClass(Base):
    __tablename__ = 'my_table'

    id = Column(Integer, primary_key=True)
    status = Column(String(50))

    @property
    def job_status(self):
        return "Status: " + self.status

    job_status = synonym('status', descriptor=job_status)
```

当我们使用声明式系统时，我们可以使用装饰器`synonym_for()`。

```python
from sqlalchemy.ext.declrative import synonym_for


class MyClass(Base):
    __tablename__ = 'my_table'

    id = Column(Integer, primary_key=True)
    status = Column(String(50))

    @synonym_for("status")
    @property
    def job_status(self):
        return "Status: " + self.status
```

#### 自定义操作符

[重定义和创造新的操作符](http://docs.sqlalchemy.org/en/rel_1_1/core/custom_types.html#types-operators)


### 混合列类型

一组列可以和一个用户定义的数据类型联系起来。

```python
class Point(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __composite_values__(self):
        return self,x self.y

    def __repr__(self):
        return 'Point(x={}, y={})'.format(self.x, self.y)

    def __eq__(self, other):
        return isinstance(other, Point) and \
                other.x == self.x and \
                other.y == self.y

    def __ne__(self, other):
        return not self.__eq__(self, other)
```

这个自定义数据类型的构造器接受的参数符合它的列格式，并且提供了一个方法`__composite_values__()`它以元组或列表的方式返回对象状态。

我们创建一个表`vertices`，它表现坐标点的形式为`x1/y1`和`x2/y2`。列属性正常创建。然后，使用`composite()`赋予一个新值。

```python
from sqlalchemy import Column, Integer
from sqlalchemy.orm import composite
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Vertex(Base):
    __tablename__ = 'vertices'

    id = Column(Integer, primary_key=True)
    x1 = Column(Integer)
    y1 = Column(Integer)
    x2 = Column(Integer)
    y2 = Column(Integer)

    start = composite(Point, x1, y1)
    end = composite(Point, x2, y2)
```

古典映射的`composite`用法如下：

```python
mapper(Vertex, vertices_table, properties={
    'start': composite(Point, vertices.c.x1, vertices.c.y1),
    'end': composite(Point, vertices.c.x2, vertices.c.y2)
})
```

现在可以实例化`Vertex`，以及对它作查询。

```python
>>> v = Vertex(start=Point(3, 4), end=Point(5, 6))
>>> session.add(v)
>>> q = session.query(Vertex).filter(Vertex.start == Point(3, 4))
>>> print q.first().start
Point(x=3, y=4)
```

源码解释：

`sqlalchemy.orm.composite(class_, *args, **kwargs)`

使用Mapper创建一个混合列。

通过`composite()`返回的`MapperProperty`的是`CompositeProperty`。

参数：

* class_

    "混合类型"类

* *cols

    被映射的列列表。

* active_history=False

    如果设置为True，当值替换时之前一个值的标量属性也会被载入。

* group

    为属性设置的组名，用于deferred

* deferred

    当设置为True时，这个列属性是“延后”的，意味着不会立即被载入，在第一次访问该属性时才会访问。

* comparator_factory

    `CompositeProperty.Comparator`的子类，提供自定义的SQL子句比较符。

* doc

    可选的文档字符串，用于描述符。

* info

* extension

    一个`AttributeExtension`实例，或者一个扩展列表。

#### 混合列的原地修改

需要使用`MutableComposite`Mixin。

#### 为混合列重定义比较符

可以对`composite`传入`comparator_factory`来设置比较符，需要定一个一个自定义的`CompositeProperty.Comparator`类。

```python
from sqlalchemy.orm.properties import CompositeProperty
from sqlalchemy import sql


class PointComparator(CompositeProperty.Comparator):
    def __gt__(self, other):
        """重定义大于操作符"""
        return sql.and_(*[a>b for a, b in
                        zip(self.__clause_element__().cluases,
                            other.__composite_values__())])


class Vertex(Base):
    ___tablename__ = 'vertices'

    id = Column(Integer, primary_key=True)
    x1 = Column(Integer)
    y1 = Column(Integer)
    x2 = Column(Integer)
    y2 = Column(Integer)

    start = composite(Point, x1, y1,
                        comparator_factory=PointComparator)
    end = composite(Point, x2, y2,
                        comparator_factory=PointComparator)
```


## 映射类继承体系

SQLAlchemy支持三种类型的继承：

* 单表继承 - 一个表相当于多个类
* 实表继承 - 每种类都相当于独立的表来
* 联结表继承 - 类结构通过依赖表

最常见的继承类型是1和3，实表继承的配置相对更难。

当映射通过继承关系配置，SQLAlchemy可以载入元素`polymorphically`，意味着一个单独的查询可以返回多种类型的对象。

### 联结表继承

在联结表继承中，每个类通过有区别的表来表现层级结构。对一个层级的特定子类做查询，将会对它的继承结构所有的表做SQL JOIN - 如果这个类是基类，默认是只会在SELECT中包含基类。

基类在联结层级中通过额外的参数来配置，将会引用多态区分列(polymorphic discriminator column)以及基类的标志符。

```python
class Employee(Base):
    __tablename__ = 'employee'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    type = Column(String(50))

    __mapper_args__ = {
        'polymorphic_identity': 'employee',
        'polymorphic_on': type
    }
```

上面例子中，建立了一个附加列`type`，它起到了`discriminator`的作用，通过参数`polymorphic_on`来配置。这列将会存储一个行对象的类型的值。这个列可以是任何数据类型，但字符串和数字是最常用的。

多态区分符表达式并不是严格必须的，只有当多态载入时才是必须的。通过创建一个简单列的方式是最简单的，更复杂的方式是配置一个SQL表达式，比如CASE语句用来作为多态区分符。

> 注意
>> 目前，在整个层级中只支持一个区别符类或SQL表达式。级联多态区分符表达式尚未支持。


然后我们定义`Engineer`和`Manager`，它们都继承自`Employee`。每个表都包含主键，同样是一个连接父表的外键。

```python
class Engineer(Employee):
    __tablename__ = 'engineer'
    id = Column(Integer, ForeignKey('employee.id'), primary_key=True)
    engineer_name = Column(String(30))

    __mapper_args__ = {
        'polymorphic_identity': 'engineer'
    }


clsas Manager(Employee):
    __tablename__ = 'manager'
    id = Column(Integer, ForeignKey('employee.id'), primary_key=True)
    manager_name = Column(String(30))

    __mapper_args__ = {
        'polymorphic_identity': 'manager'
    }
```

多数情况下，外键和主键属于同一列。但也不是必须的。

对`Employee`的查询将会返回`Employee`、`Engineer`和`Manager`对象的组合。存储新的`Enginner`、`Manager`对象，`Employee`对象将会自动构成一个`employee.type`列。

#### 联结继承中的关系

联结继承中完全被支持。

```python
class Company(Base):
    __tablename__ = 'company'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    employees = relationship('Employee', back_populated='company')


class Employee(Base):
    __tabelname__ = 'employee'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    type = Column(String(50))
    company_id = Column(ForeignKey('company.id'))
    company = relationship('Company', back_populated="employees")

    __mapper_args__ = {
        'polymorphic_identity': 'employee',
        'polomorphic_on': type
    }

class Manager(Employee):
    # ...

class Engineer(Employee):
    # ...
```

如果一个表外键约束和子类对应，关系应该标向子类。在下面这个例子中，有一个`manager`到`company`的外键约束，所以应该在它们之间建立关系。

```python
class Company(Base):
    __tablename__ = 'company'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    managers = relationship("Manager", back_populates="company")


class Employee(Base):
    __tablename__ = 'employee'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    type = Column(String(50))

    __mapper_args__ = {
        'polymorphic_identity':'employee',
        'polymorphic_on':type
    }


class Manager(Employee):
    __tablename__ = 'manager'
    id = Column(Integer, ForeignKey('employee.id'), primary_key=True)
    manager_name = Column(String(30))

    company_id = Column(ForeignKey('company.id'))
    company = relationship('Company', back_populated='managers')

    __mapper_args__ = {
        'polymorphic_identity': 'manager'
    }


class Engineer(Employee):
    ...
```

上面例子中，`Manager`类有一个`Manager.company`属性；`Company`也会有一个`Company.managers`属性，它总是连带`manager`和`employee`一起载入。

#### 载入联结继承映射

看[载入继承层级](http://docs.sqlalchemy.org/en/rel_1_1/orm/inheritance_loading.html)和[载入对象和继承层级](http://docs.sqlalchemy.org/en/rel_1_1/orm/inheritance_loading.html#loading-joined-inheritance)

### 单表继承

单表继承等同于所有属性所有子类都在一张表里面。

对子类发出的查询将会针对基类发出一个SELECT，并会增加WHERE子句来限制特定的行。

单表继承在简便性方面优于联接表继承。

单表继承配置看起来很像联结表继承，除了只有基类定义了`__tablename__`。同样，基类必须有一个区别符，所以各个类才能有所区别。

即使子类分享基类的所有属性，当使用声明时映射时，Column对象也会在子类中指定，意味着这列只出现在子类中。

```python
class Employee(Base):
    __tablename__ = 'employee'

    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    type = Column(String(20))

    __mapper_args__ = {
        'polymorphic_on': type,
        'polymorphic_indentity': 'employee'
    }


class Manager(Employee):
    manager_data = Column(String(50))

    __mapper_args__ = {
        'polymorphic_identity': 'manager'
    }


class Engineer(Employee):
    engineer_info = Column(String(50))

    __mapper_args__ = {
        'polymorphic_identity': 'engineer'
    }
```

注意子类中都没有声明`__tablename__`属性，意思就是它们并没映射到属于它们自己的数据库表。

#### 单表继承中的关系

关系在单表继承中已经完全支持。对于它的配置和链接继承一样。

```python
class Company(Base):
    __classname__ = 'company'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    employees = relationship('Employee', back_populates='company')


class Employee(Base):
    __tablename__ = 'employee'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    type = Column(String(50))
    company_id = Column(Foreign_key('company.id'))
    company = relationship('Company', back_populates='employees')

    __mapper_args__ = {
        'polymorphic_identity': 'employee',
        'polymorphic_on': type
    }


class Manager(Employee):
    manager_data = Column(String(50))

    __mapper_args__ = {
        'polymorphic_identity': 'manager'
    }


class Engineer(Employee):
    engineer_info = Column(String(50))

    __mapper_args__ = {
        'polymorphic_identity': 'engineer'
    }
```

同样，想联结继承一样，我们可以为子类创建关系。当查询时，`SELECT`语句将会包含一个`WHERE`字句限定类的选择。

```python
class Company(Base):
    __tablename__ = 'company'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    managers = relationship("Manager", back_populates="company")


class Employee(Base):
    __tablename__ = 'employee'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    type = Column(String(50))

    __mapper_args__ = {
        'polymorphic_identity':'employee',
        'polymorphic_on':type
    }


class Manager(Employee):
    manager_name = Column(String(30))

    company_id = Column(ForeignKey('company.id'))
    company = relationship('Company', back_populates='managers')

    __mapper_args__ = {
        'polymorphic_identity': 'manager'
    }


class Engineer(Employee):
    engineer_info = Column(String(50))

    __mapper_args__ = {
        'polymorphic_identity': 'engineer'
    }
```

上面代码中，`Manager`类将会有一个`Manager.company`属性；`Company`会有一个`Company.managers`属性，它总是会在载入`employee`表时带上一个额外的`WHERE`子句，限定`type = 'manager'`。

#### 载入单表继承映射

单表继承的载入技术等同于联结继承，在高级层次提供一个两种映射的抽象。

### 实(concrete)表继承

```python
class Employee(Base):
    __tablename__ = 'employee'

    id = Column(Integer, primary_key=True)
    name = Column(String(50))


class Manager(Employee):
    __tablename__ = 'manager'

    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    manager_data = Column(String(50))

    __mapper_args__ = {
        'concrete': True
    }


class Engineer(Employee):
    __tablename__ = 'engineer'

    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    engineer_info = Column(String(50))

    __mapper_args__ = {
        'concrete': True
    }
```

需要留言两个关键点：

* 我们必须为每个子类显示定义所有的列，即使它们有同样的名称。一个列比如`Employee.name`不会拷贝到`Manager`和`Engineer`的表映射中。
* 当`Manager`和`Enginner`映射到`Employee`的层级关系中，它们仍然不会包含多态载入。意味着，我们对`Employee`查询，`manager`和`engineer`表不会一起被查询。

#### 实表多态载入配置

注意声明时需要使用`ConcretBase`和`AbstractConcreteBase`。

```python
from sqlalchemy.ext.declarative import ConcreteBase


class Employee(ConcreteBase, Base):
    __tablename__ = 'employee'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))

    __mapper_args__ = {
        'polymorphic_identity': 'employee',
        'concrete': True
    }


class Manager(Employee):
    __tablename__ = 'manager'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    manager_data = Column(String(40))

    __mapper_args__ = {
        'polymorphic_identity': 'manager',
        'concrete': True
    }


class Engineer(Employee):
    __tablename__ = 'engineer'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    engineer_info = Column(String(40))

    __mapper_args__ = {
        'polymorphic_identity': 'engineer',
        'concrete': True
    }
```

#### 抽象实类

```python
class Employee(Base):
    __abstract__ = True

class Manager(Employee):
    __tablename__ = 'manager'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    manager_data = Column(String(40))

    __mapper_args__ = {
        'polymorphic_identity': 'manager',
    }

class Engineer(Employee):
    __tablename__ = 'engineer'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    engineer_info = Column(String(40))

    __mapper_args__ = {
        'polymorphic_identity': 'engineer',
    }
```