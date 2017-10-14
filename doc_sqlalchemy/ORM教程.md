[TOC]



SQLAlchemy的ORM使用的方法是联合用户定义的Python类和数据库表，这些类的实例（对象）映射相对应数据库表中的行。它包含一个透明的同步系统，叫做**unit of work**。



ORM和SQLAlchemy表达式语言是相对应的。SQL表达式语言提供了原始构建关系型数据库的方法，ORM是更高等级、更抽象的用法。



## 版本检查



```python

>>> import sqlalchemy

>>> sqlalchemy.__version__

```



## 连接



在这个教程中，我们使用SQLite数据库。使用`create_engine()`函数来链接。



```python

>>> from sqlalchemy import create_engine

>>> engine = create_engine("sqlite:///:memory:", echo=True)

```

`echo`标示是SQLAlchemy日志功能的简称，它通过Python标准库`logging`来实现。如果应用了这个标识，我们能看到所有生成的SQL输出。如果你照着教程敲的代码但是输出明显和教程不一样，那么应该是这个标识没有设置。



`create_engine()`返回的值是一个`Engine`实例，它代表数据库的核心接口，并且适配了方言系统和特定数据库的DBAPI。在这个例子中使用的SQLite数据库，通过Python内置的`sqlite3`模块来解释使用。



当首次调用`Engine.execute()`或者`Engine.connect()`方法时，`Engine`对象将会建立一条真的DBAPI链接到数据库，它用来发出SQL语句。但使用ORM时，通常不需要直接使用创立的`Engine`对象，我们很快就能看到如何把它置于ORM的幕后工作了。



> 惰性链接

>

> `Engine`对象，当它一开始由`create_engine()`返回时，并没有真正的尝试连接数据库；直到对数据库执行任务命令时才真正第一次连接。



## 声明一个映射

当使用ORM时，通常先要描述我们将要打交道的数据库表是怎样的，然后再定义自己的类来映射这些数据库表。在SQLAlchemy中，两个步骤通常使用一个名为`Decalrative`的系统来同时进行，它允许我们创建一个类并包含想要映射数据库表的直接描述。



使用声明系统的映射类通常叫做`declarative base class`。在一个程序中通常只要一个base实例。通过`declarative_base()`函数来创建base类。



```python

>>> from sqlalchemy.ext.declarative import declarative_base

>>> Base = declarative_base()

```

现在我们有一个`base`了，我们可以通过继承它来创建任意多个映射类。我们先从一个表开始，它称为`users`。创建一个User的映射类，在这个类中我们定义了关于表的细节，比如字段、主键和表名，列名，列数据类型。



```python

>>> from sqlalchemy import Column, Integer, String

>>> class User(Base):

...         __tablename__ = 'users'

...

...         id = Column(Integer, primary_key=True)

...         name = Column(String)

...         fullname = Column(String)

...         password = Column(String)

...

...         def __repr__(self):

...             return '<User(name="{}", fullname="{}", password="{}">'.format(self.name, self.fullname, self.password)

```



一个叫做声明类的类最少也需要定一个`__tablename__`属性，在列中最少要有一个列定义为主键。SQALchemy本身不会作任何假设，不会有任何自动创建的列、数据类型和约束。但这样不是说一定让你写刻板代码；相反，鼓励创建自己的自动化函数或Mixin类。

当我们类创建成功后，声明类将会把所有的Column对象通过Python描述符来替换；这个过程被称为`instrumentation`。



## 创建模式



在通过功能系统构建User类时，我们定义了一些表的信息，被称为表元数据。用来表示表元数据的对象是`Table`，声明类中它自动为我们创建了这个对象，我们可以通过`__table__`属性来访问它。



```python

>>> User.__table__

Table('users', MetaData(bind=None),

            Column('id', Integer(), table=<user>, primary_key=True, nullable=False),

            Column('name', String(), table=<user>),

            Column('fullname', String(), table=<user>),

            Column('password', String(), table=<user>), schema=None)

```

当我们声明我们的类时，Decalartive使用一个Python元类来执行元数据的添加；在这个阶段，创建了一个`Table`对象，构建了一个`Mapper`对象来与相应的数据库表关联。这个过程来幕后完成，一般不需要我们直接处理。



`Table`对象是`MetaData`的成员之一。当使用`Declarative`，这个对象可以通过访问`.metadata`属性来获得。



`MetaData`是一个注册器，可以通过它对数据库发送模式创建的命令。



```python

>>> Base.metadata.create_all(engine)

SELECT ...

PRAGMA table_info("user")

()

CREATE TABLE users (

    id INTEGER NOT NULL, name VARCHAR,

    fullname VARCHAR,

    password VARCHAR,

    PRIMARY KEY (id)

)

()

COMMIT

```



### Minimum Table Description vs. Full Description



熟悉SQL语法的用户可能会发现VARCHAR没有长度，在SQLite和PostgreSQL中，这是个合法的数据类型，其它的数据库就不是这样了。如果不支持这样，那么就应该在String中传入一个length值。



```python

Column(String(50))

```



另外，在`Firebird`和`Oracle`中需要为主键字段设立sequence类型。



```python

from sqlalchemy import Sequence

Column(Integer, Sequence('user_id_seq"), primary_key=True)

```



一个完整的、简单明了的映射类应该这样写：



```python

class User(Base):

    __tablename__ = 'users'

    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)

    name = Column(String(50))

    fullname = Column(String(50))

    password = Column(String(12))



    def __repr__(self):

        return "<User(name='%s', fullname='%s', password='%s')>" % (

                                self.name, self.fullname, self.password)

```



## 创建一个映射类的实例



当映射完成后，让我们来使用`User`对象。



```python

>>> ed_user = User(name='ed', fullname='Ed Jones', password='edspassword')

>>> ed_user.name

'ed'

>>> ed_user.password

'edspassword'

>>> str(ed_user.id)

None

```

应为我们在构建对象时没有传入值，现在`id`的值还是None。其它的值将会作为`INSERT`是插入的值。



## 创建Session

现在准备开始讲一下数据库。ROM通过Session来处理数据库。当我们创建应用时，在`create_engine()`声明的同级别处，我们需要定义一个`Session`类。

```python
>>> from sqlalchemy.orm import sessionmaker
>>> Session = sessionmaker(bind=engine)
```

万一你写下这些代码的时候还不存在engine对象，那么只要这么鞋就够了。

```python
>>> Session = sessionmaker()
```

然后，当你使用`create_engine`创建engine后，想要连接Session的话可以使用`configure()`。

```python
>>> Session.configure(bind=engine)
```

自定义的Session类将会创建新的Session对象，这些在之后的章节将会讨论。然后，想要对数据库进行操作，需要实例化Session。

```python
>>> session = Session()
```

上面的`Session`和我们的SQLite后端`Engine`相联合，但这个时候对数据库的连接还没有打开。当第一次使用时，它将会从`Engine`维护的连接池取出一条连接，保持这条连接知道我们提交所有的改动。

## 增加和更新对象

想要把User对象持久化，需要使用`Session`的`add()`方法。

```python
>>> ed_user = User(name='ed', fullname='Ed Jones', password='edspassword')
>>> session.add(en_user)
```

在这个时间点，我们说这个对象处于`pending(待定)`状态；还没有SQL被发送，对象还不是数据库的一条记录。当session刷新后，session会发出SQL来在数据库构成这条Ed Jones数据。如果我们对数据库查询这条Ed Jones，所有的待定信息将会首次刷新(flushed)，然后才会对数据库作出查询。

比如，下面我们创建了一个`Query`对象，载入了`User`对象。我们通过`name`属性为`ed`的表达式来过滤。

```python
>>> our_user = session.query(User).filter_by(name='ed').first()
>>> our_user
<User(name='ed', fullname='Ed Jones', password='edspassword')>
```

事实上，`Session`可以识别出结果的这行数据和最开始的一行相同。

```python
>>> ed_user is our_user
True
```

这个处理过程在ORM中叫做[identity map](http://docs.sqlalchemy.org/en/rel_1_1/glossary.html#term-identity-map)。如果一个对象的主键存在于Session中，所有对于相同特定主键的SQL查询，Session都会反对相同的Python对象。

我们可以使用`add_all()`方法来一次增加多个对象。

```python
>>> session.add_all([
...     User(name='wendy', fullname='Wendy Williams', password='foobar'),
...     User(name='mary', fullname='Mary Contrary', password='xxg527'),
...     User(name='fred', fullname='Fred Flinstone', password='blah')])
```

而且，我们给ed设置的密码不够安全，修改一下。

```python
>>> ed_user.password = 'f8s7ccs'
```

`Session`一直在保持注意力。例如，它知道`Ed Jones`已经被修改了。

```python
>>> session.dirty
IdentitySet([<User(name='ed', fullname='Ed Jones', password='f8s7ccs')>])
```

新加入的User对象处于待定状态。

```python
>>> session.new
IdentitySet([<User(name='wendy', fullname='Wendy Williams', password='foobar')>,
<User(name='mary', fullname='Mary Contrary', password='xxg527')>,
<User(name='fred', fullname='Fred Flinstone', password='blah')>])
```

我们想要告诉Session发出所有修改命令，需要使用`commit()`。

```python
>>> session.commit()
```

如果我们注意ed的id属性，他开始是None，而现在有了一个值。

```python
>>> ed_user.id
1
```

> session对象状态
>> User对象在session中的移动过程，它包含3个“对象状态” - 'transient', 'pending', 'persistent'。理解这几个状态肯定有好处，推荐阅读[快速介绍对象状态](http://docs.sqlalchemy.org/en/rel_1_1/orm/session_state_management.html#session-object-states)

## 回滚

由于Session的原理类似于事务，我们可以回滚来改变作出的修改。

```python
>>> ed_user.name = 'Edwardo'
>>> fake_user = User(name='fakeuser', fullname='Invalid', password='12345')
>>> session.add(fake_user)
```

对session作出查询，我们可以看到当前的事务已经刷新。

```python
>>> session.query(User).filter(User.name.in_(['Edwardo', 'fakeuser'])).all()
[<User(name='Edwardo', fullname='Ed Jones', password='f8s7ccs')>, <User(name='fakeuser', fullname='Invalid', password='12345')>]
```

回滚后，我们可以看到`ed_user`的名称已经修改回`ed`，`fake_user`被踢出了session。

```python
>>> session.rollback()

>>> ed_user.name
ed
>>> fake_user in session
False
```

使用`SELECT`来解释数据库的改动。

```python
>>> session.query(User).filter(User.name.in_(['ed', 'fakeuser'])).all()
[<User(name='ed', fullname='Ed Jones', password='f8s7ccs')>]
```

## 查询

`Query`对象通过`Session`的`query`方法来创建。这个函数接受若干参数，这些参数可以是任何映射类和映射类的描述符属性。

```python
>>> for instance in session.query(User).order_by(User.id):
...     print(instance.name, instance.fullname)
ed Ed Jones
wendy Wendy Williams
mary Mary Contrary
fred Fred Flinstone
```

也可以接受描述符属性作为参数，将它映射的列数据作为返回结果。

```python
>>> for name, fullname in session.query(User.name, User.fullname):
...     print(name, fullname)
ed Ed Jones
wendy Wendy Williams
mary Mary Contrary
fred Fred Flinstone
```

Query返回的元组是命名元组，继承自`KeyedTuple`类，可以将它当作普通的Python对象，它的属性名来自于query中的类名和属性名。

```python
>>> for row in session.query(User, User.name).all():
...    print(row.User, row.name)
<User(name='ed', fullname='Ed Jones', password='f8s7ccs')> ed
<User(name='wendy', fullname='Wendy Williams', password='foobar')> wendy
<User(name='mary', fullname='Mary Contrary', password='xxg527')> mary
<User(name='fred', fullname='Fred Flinstone', password='blah')> fred
```

可以对描述符使用`label`来改变返回命名元组的名称，继承来自于`ColumnElement`

```python
>>> for row in session.query(User.name.lable('name_label')).all():
...     print(row.name_label)
ed
wendy
mary
fred
```

结果集的名称来自于类名，如果相同类多次出现在query()中，可以使用`aliased()`函数。

```python
>>> from sqlalchemy.orm import aliased
>>> user_alias = aliased(User, name='user_aliase')

>>> for row in session.query(user_alias, user_alias.name).all():
...    print(row.user_alias)
<User(name='ed', fullname='Ed Jones', password='f8s7ccs')>
<User(name='wendy', fullname='Wendy Williams', password='foobar')>
<User(name='mary', fullname='Mary Contrary', password='xxg527')>
<User(name='fred', fullname='Fred Flinstone', password='blah')>
```

基本的`Query`操作一般包括`LIMIT`和`OFFSET`，可以很方便的使用Python索引、切片操作符来实现。

```pyhton
>>> for u in session.query(User).order_by(User.id)[1:3]
...     print(u)
<User(name='wendy', fullname='Wendy Williams', password='foobar')>
<User(name='mary', fullname='Mary Contrary', password='xxg527')>
```

过滤集也可以使用`filter_by()`方法，它使用关键字参数来完成查询。

```python
>>> for name in session.query(User.name).\
...             filter_by(fullname='Ed Jones'):
...     print(name)
ed
```

或者使用`filter()`，它使用更加灵活的SQL语言构造器。它让你可以使用常规的Python操作符写成一个表达式，操作类属性，它的内部会将之转换为SQL语言。

```python
>>> for name in session.query(User.name).\
...             filter(User.name == 'ed').\
...             filter(User.fullname == 'Ed Jones'):
...     print(user)
<User(name='ed', fullname='Ed Jones', password='f8s7ccs')>
```

### 常用Filter操作符

下面是在`filter()`中常用的操作符总结。

* equals:

        query.filter(User.name == 'ed')

* not equals:

        query.filter(User.name != 'ed')

* LIKE:

        query.filter(User.name.like('%ed%'))

    注意`like()`是对大小写敏感的，如果想要忽略大小写敏感，可以使用`ilike()`方法。

* ILIKE:

        query.filter(User.name.ilike('%ed%'))

* IN:

    ```python
    query.filter(User.name.in_(['ed', 'wendy', 'jack']))

    # 可以传入子查询
    query.filter(User.name.in_(
        session.query(User.name).filter(User.name.like('%ed%'))
    ))
    ```

* **NOT IN**:

        query.filter(~User.name.in_(['ed', 'wendy', 'jack']))

    这里的NOT使用`~`来表达。

* IS NULL:

    ```python
    query.filter(User.name == None)

    # 替代方法，如果考虑pep8的话使用下面语法
    query.filter(User.name.is_(None))
    ```

    这里的`is_()`是应为防治命名冲突，`is`是Python的操作符。

* IS NOT NULL:

    ```python
    query.filter(User.name != None)

    # 替代方法，如果考虑pep8的话使用下面语法
    query.filter(User.name.isnot(None))
    ```

* AND:

    ```python
    # 使用and_()
    from sqlalchemy import and_
    query.filter(and_(User.name == 'ed', User.fullname == 'Ed Jones'))

    # 或者为filter()传入多个表达式
    query.filter(User.name == 'ed', User.fullname == 'Ed Jones')

    # 或者可以链式调用filter()和filter_by()
    query.filter(User.name == 'ed').filter(User.fullname == 'Ed Jones')
    ```

    主要这里的`and_()`是SQLAlchemy的函数，而不是Python`and`操作符。

* OR：

    ```python
    from sqlalchemy import or_
    query.filter(or_(User.name == 'ed', User.name == 'wendy'))
    ```

* MATCH

        query.filter(User.name.match('wendy'))

    `match()`方法使用特定数据库的`MATCH`和`CONTAINS`函数，它的作用和行为可能是不同的。

### 返回列表(list)和标量(scalars)

`Query`对象有若干方法用来立即发出SQL并返回一个包含数据库结果集的值。

* `all()`返回一个列表：

    ```python
    >>> query = session.query(User).filter(User.name.like('%ed').order_by(User.id))
    >>> query.all()
    [<User(name='ed', fullname='Ed Jones', password='f8s7ccs')>,
        <User(name='fred', fullname='Fred Flinstone', password='blah')>]
    ```

* `first()`用来限制一个返回值，并返回结果的第一个值作为标量:

    ```python
    >>> query.first()
    <User(name='ed', fullname='Ed Jones', password='f8s7ccs')>
    ```

* `one()`取回结果集的所有值，但是如果结果不足一个或多于一个都会抛出一个错误。

    ```python
    >>> user = query.one()
    Traceback (most recent call last):
    ...
    MultipleResultsFound: Multiple rows were found for one()
    ```

    如果结果少于一行，即没有匹配的结果。

    ```pyhton
    >>> user = query.filter(User.id == 99).one()
    Traceback (most recent call last):
    ...
    NoResultFound: No row was found for one()
    ```

    `one()`方法类似于Django的`get_object_or_404()`，在某些情况下很实用。

* `one_or_none()`很像`one()`，除了如果没有发现结果，它不会抛出错误，而是返回None。但是如果返回多个结果，它仍然会抛出错误。

* `scalar()`调用`one()`方法，如果成功返回该行第一列。

    ```python
    >>> query = session.query(User.id).filter(User.name == 'ed').order_by(User.id)
    >>> query.scalar()
    1
    ```

### 使用文本SQL

`Query`中可以使用弹性的字符串，使用`text()`构造器，它可以用语大多数方法，如`filter()`和`filter_by()`。

```python
>>> from sqlalchmey import text
>>> for user in session.query(User).\
...             filter(text("id<224")).\
...             order_by(text("id")).all()
...     print(user.name)
ed
wendy
mary
fred
```

绑定参数可以用传统的字符串SQL，使用冒号占位符。传入参数，需要使用`params()`方法：

```python
>>> session.query(User).filter(text('id<:value and name=:name')).\
...     params(value=224, name='fred').order_by(User.id).one()
<User(name='fred', fullname='Fred Flinstone', password='blah')>
```

想要使用原生SQL语言，需要在`Query`对象的`from_statement()`方法中传入`text()`构造器。

```python
>>> session.query(User).from_statement(
...                     text("SELECT * FROM users WHERE name=:name")).\
...                     params(name='ed').all()
[<User(name='ed', fullname='Ed Jones', password='f8s7ccs')>]
```

```python
>>> stmt = text("SELECT name, id, fullname, password "
                "FROM users WHERE name=:name")
# 注意下面columns()的用法
>>> stmt = stmt.columns(User.name, User.id, User.fullname, User.password)
>>> session.query(User).from_statement(stmt).params(name='ed').all()
[<User(name='ed', fullname='Ed Jones', password='f8s7ccs')>]
```

```
>>> stmt = text("SELECT name, id FROM users where name=:name")
>>> stmt = stmt.columns(User.name, User.id)
SQL>>> session.query(User.id, User.name).\
...          from_statement(stmt).params(name='ed').all()
[(1, u'ed')]
```

### 计数

`Query`提供了一个方便的用来计数的方法，叫做`count()`。

```python
>>> session.query(User).filter(User.name.like('%ed')).count()
2
```

`count()`确定返回值中有多少行数据。

想使用SQL中的count函数，需要在表达式中使用`func.count()`。

```python
>>> from sqlalchemy import func
>>> session.query(func.count(User.name), User.name).group_by(User.name).all()
[(1, u'ed'), (1, u'fred'), (1, u'mary'), (1, u'wendy')]
```

想要写类似SQL-`SELECT COUNT(*) FROM table;`，只要这样：

```python
>>> session.query(func.count("*")).select_from(User).scalar()
4
```

如果我们单纯想计数User的主键，可以去掉`select_from()`方法。

```python
>>> session.query(func.count(User.id)).scalar()
4
```

## 建立一个关系

现在考虑创建第二个表，让它关联User，可以映射和查询。Users在我们系统中可以存储任意数量的email地址，和她们的username相关联，即一对多关系。这个新表称为addresses，使用声明式语法，定义这个表的映射类叫做`Address`。

```python
>>> from sqlalchemy import ForeignKey
>>> from sqlalchemy.orm import relationship

class Address(Base):
...     __tablename__ = 'addresses'
...     id = Column(Integer, primary_key=True)
...     email_address = Column(String, nullable=False)
...     user_id = Column(Integer, ForeignKey('users.id'))
...
...     user = relationship("User", backref="addresses")
...
...     def __repr__(self):
...         return "<Address(email_address='{}')>".format(self.email_address)

>>> User.addresses = relationship('Address', order_by=Address.id, back_populates='users')
```

上面例子应用了ForeignKey结构，它直接作用于Column中，指出这一列应该收到外键约束。这是关系型数据库的核心特性之一，ForeignKey中的参数是指`Address.user_id`被`users.id`键作外键约束。

## 使用关联对象

现在我们创建一个`User`，它将拥有一个空白的`Address`集合，这个集合可以是各式数据类型，默认情况下是一个列表(list)。

```python
>>> jack = User(name='jack', fullname='Jack Bean', password='giffdd')
>>> jack.addresses
[]
```
我们可以自由地为User加入Address，在这里例子中我们可以直接赋值整个列表给这个属性。

```python
>>> jack.addresses = [
...                 Address(email_address='jack@google.com'),
...                 Address(email_address='j25@yahoo.com')]
```

当我们使用双边关系，一端增加的数据会自动出现在另一端。这个行为通过Python的属性修改时事件特性实现，不需要使用SQL。

```python
>>> jack.addresses[1]
<Address(email_address='j25@yahoo.com')>

>>> jack.addresses[1].user
<User(name='jack', fullname='Jack Bean', password='gjffdd')>
```

让我们把`Jack Bean`通过commit加入到数据库，和他关联的两个Address对象也会自动插入数据库，这个过程被称为级联操作(cascading)。

```python
>>> session.add(jack)
>>> session.commit()
```

对Jack的查询，只会返回Jack而不会发出对它addresses属性的SQL。

```python
>>> jack = session.query(User).\
...             filter_by(name='jack').one()
>>> jack
<User(name='jack', fullname='Jack Bean', password='gjffdd')>
```

让我们看看`addresses`集合，sqlalchemy这是会发出SQL语句。

```python
>>> jack.addresses
[<Address(email_address='jack@google.com')>, <Address(email_address='j25@yahoo.com')>]
```

当我们访问`addresses`集合时，SQL将会立即发出。这是一个惰性加载关系的实例。现在`addresses`集合已经载入，它的行为和普通列表一样。

## 使用join查询

现在我们有两张表了，我们可以展示`Query`的更多特性，特别是如何创建一个查询同时处理两张表。[Wiki:SQL-JOIN](http://en.wikipedia.org/wiki/Join_%28SQL%29)WIKI的这个页面很好的介绍了join技术。

想要在User和Address构建一个简单的隐式join，我们只需要使用`Query.filter()`把它们两个相对应的列做个相等表达式。

```python
>>> for u, a in session.query(User, Address).\
...                 filter(User.id == Address.user_id).\
...                 filter(Address.email_address == 'jack@google.com').\
...                 all():
...     print(u)
...     print(a)
<User(name='jack', fullname='Jack Bean', password='gjffdd')>
<Address(email_address='jack@google.com')>
```

真正的join语法，也是更加简便的语法，是使用`Query.join()`方法。

```python
>>> session.query(User).join(Address).\
...             filter(Address.email_address == 'jack@google.com').\
...             all()
[<User(name='jack', fullname='Jack Bean', password='gjffdd')>]
```

`Query.join()`知道怎么对User和Address完成join，因为它们之间只有一个外键。如果没有外键或多个外键，`Query.join()`最好用下面的用法。

```python
query.join(Address, User.id == Address.user_id)     # 显示表明条件
query.join(User.addresses)                          # 表明关系是从左到右的
query.join(Address, User.addresses)                 # 相同，有明确目标
query.join('addresses')                             # 使用字符串形式
```

如果你想使用外join的话，可以使用`outerjoin()`方法。

```python
query.outerjoin(User.addresses)     # 左外join
```

想要控制join左边的值，需要使用`select_from()`来指定。

```python
query = session.query(User, Address).select_from(Address).join(User)
```

### 使用Alias

当使用多表查询时，如果同一张表被引用多于一次，SQL的用法通常是需要把表明赋值一个Alias。`Query`支持使用`aliased`构造器显式地声明。

```pyhton
>>> from sqlalchemy.orm import aliased
>>> adalias1 = aliased(Address)
>>> adalias2 = aliased(Address)
>>> for username, email1, email2 in \
...     session.query(User.name, adalias1.email_address, adalias2.email_address).\
...     join(adalias1, User.addresses).\
...     join(adalias2, User.addresses).\
...     filter(adalias1, email_address == 'jack@goole.com').\
...     filter(adalias2, email_address == 'j25@yahoo.com'):
...     print(username, email1, email2)
jack jack@google.com j25@yahoo.com
```

### 使用Subquery

`Query`对象适用于用来生成子查询。假设我们想要统计每个user有多少关联的address，最好的方法是生成一个SQL -- 先求出根据user_id分组的addresses计数，然后JOIN回parent。

```sql
SELECT users.* adr_count.address_count FROM users LEFT JOIN
    (SELECT user_id, count(*) AS address_count
        FROM addresses GROUP BY user_id) AS adr_count
    ON users.id == adr_count.user.id
```

下面是SQLAlchemy的写法：

```pyhton
>>> from sqlalchemy.sql import func
>>> stmt = session.query(Address.user_id, func.count(*).label('address_count')).\
...             groupy_by(Address.user.id).subquery()
```

```python
>>> for u, count in session.query(User, stmt.c.address_count).\
...         outerjoin(stmt, User.id == stmt.c.user_id).order_by(User.id):
...     print(u, count)
<User(name='ed', fullname='Ed Jones', password='f8s7ccs')> None
<User(name='wendy', fullname='Wendy Williams', password='foobar')> None
<User(name='mary', fullname='Mary Contrary', password='xxg527')> None
<User(name='fred', fullname='Fred Flinstone', password='blah')> None
<User(name='jack', fullname='Jack Bean', password='gjffdd')> 2
```

### 从子查询中查询实体

我们想要子查询映射一个实体应该怎么办？我们使用`aliased()`来关联一个映射类的alias和一个子查询：

```python
>>> stmt = session.query(Address).\
...                 filter(Address.email_address == 'j25@yahoo.com').\
...                 subquery()
>>> adalias = aliased(Address, stmt)
>>> for user, address in session.query(User, adalias).\
...                         join(adalias, User.addresses):
...     print(user)
...     print(address)
<User(name='jack', fullname='Jack Bean', password='gjffdd')>
<Address(email_address='jack@google.com')>
```

### 使用EXISTS

SQL中的EXISTS是一个操作符，如果给定的表达式包含结果则返回True。

sqlalchemy有一个显式的`EXISTS`构造器。

```pyhton
>>> from sqlalchemy.sql import exists
>>> stmt = exists().where(Address.user_id == User.id)
>>> for name in session.query(User.name).filter(stmt):
...     print(name)
jack
```

`Query`有如果操作符来自动使用EXISTS，比如上面的例子，可以对`User.addresses`使用`any()`来替代。

```python
>>> for name in session.query(User.name).\
...             filter(User.addresses.any())
...     print(name)
jack
```

`any()`也接受标准，限制匹配的行数。

```python
>>> from name in session.query(User.name).\
...         filter(User.addresses.any(Address.email_address.like('%google%'))):
...     print(name)
jack
```

`has()`和`any()`操作符类似，但应用于多对一关系(注意下面例子中的`~`，它代表None)。

```python
>>> session.query(Address).\
...     filter(~Address.user.has(User.name == 'jack')).all()
[]
```

### 常用的关系操作符

* `__eq__()`(多对一“相等”比较)

        query.filter(Address.user == someuser)

* `__ne__()`(多对一“不想等”比较)

        query.filter(Address.user != someuser)

* `IS NULL`(多对一比较，同样是用`__eq__()`)

        query.filter(Address.user == None)

* `contains()`(作用于一对多集合)

        query.filter(User.addresses.contains(someaddresses))

* `any()`(用于集合)

    ```python
    query.filter(User.addresses.any(Address.email_address == 'bar'))

    # 可以接受关键字参数
    query.filter(User.addresses.any(email_addresses='bar'))
    ```

* `has()`(用于标量引用)

        query.filter(Address.user.has(name='ed'))

* `Query.with_parent()`(用于任何关系)

        session.query(Address).with_parent(someuser, 'addresses')

## 贪婪加载

前面我们说到了惰性加载操作，当我们访问`User.addresses`时会发出一个SQL命令。如果你想减少查询的数量，我们可以在查询操作时采用贪婪加载(eager load)。SQLAlchemy提供了三种方式来提供贪婪加载，其中两种是自动化的，第三种是自定义标准。都是通过`Query.options()`方法来进行。

### Subquery Load

如果我们想贪婪加载`User.addresses`。一个好选择是使用`orm.subqueryload()`，它会发出第二个SELECT。

```python
>>> from sqlalchemy.orm import subqueryload
>>> jack = session.query(User).\
...                 options(subqueryload(User.addresses)).\
..                  filter_by(name='jack').one()
>>> jack
<User(name='jack', fullname='Jack Bean', password='gjffdd')>

>>> jack.addresses
[<Address(email_address='jack@google.com')>, <Address(email_address='j25@yahoo.com')>]
```

> 注意
>> 在组合`subqueryload()`和限制方法如`Queue.first()`、`Queue.limit()`和`Queue.offset()`的时候，需要包含`Queue.order_by()`方法来确保返回的数据是正确的。

### Joined Load

另一个自动化的贪婪加载函数是`orm.joinedload()`。这个载入的风格是发出JOIN命令，默认情况下是**left outer join**。

```python
>>> from sqlalchemy.orm import joinedload

>>> jack = session.query(User).\
...                 options(joinedload(User.addresses)).\
...                 filter_by(name='jack').one()
>>> jack
<User(name='jack', fullname='Jack Bean', password='gjffdd')>

>>> jack.addresses
[<Address(email_address='jack@google.com')>, <Address(email_address='j25@yahoo.com')>]
```

### 显示join + Eagerload

第三种风格的贪婪加载是我们根据主键显示构建一个JOIN
。这个特性使用`orm.contains_eager()`来实现。

```python
>>> from sqlalchemy.orm import contains_eager
>>> jacks_addresses = session.query(Address).\
...                     join(Addresses.user).\
...                     filter(User.name == 'jack').
...                     options(contains_eager(Address.user)).\
...                     all()
>>> jacks_addresses
[<Address(email_address='jack@google.com')>, <Address(email_address='j25@yahoo.com')>]

>>> jack_addresses[0].user
<User(name='jack', fullname='Jack Bean', password='gjffdd')>
```

更多关于贪婪加载，请看章节[关系加载技术](http://docs.sqlalchemy.org/en/rel_1_1/orm/loading_relationships.html)

## 删除

让我们试试删除`jack`然后看看会发生什么。

```python
>>> session.delete(jack)
>>> session.query(User).filter_by(name='jack').count()
0
```

那么Address对象现在状态如何呢？

```python
>>> session.query(Address).filter(
...     Address.email_address.in_(['jack@google.com', 'j25@yahoo.com']))
...     ).count()
2
```

发现它们还存在在那里，可以发现这些对象的`user_id`列的值为NULL，但是行记录没有被删除。SQLAlchemy并不会假定级联删除。

### 设置级联删除

我们可以在`User.addresses`设置一个`cascade`选项来设置级联删除行为。

首先让关闭回话。

```python
>>> session.close()
ROLLBACK
```

然后使用一个新的`declarative_base()`。

```python
>>> Base = declarative_base()
```

然后我们声明一个User类，为它增加addresses关系并设置级联配置。

```python
>>> class User(Base):
...     __tablename__ = 'users'
...
...     id = Column(Integer, primary_key=True)
...     name = Column(String)
...     fullname = Column(String)
...     password = Column(String)
...
...     addresses = relationship("Address", backref='user',
...                             cascade='all, delete, delete-orphan')
...
...     def __repr__(self):
...         return "<User(name='{}', fullname='{}', password='{}'".\
...             format(self.name, self.fullname, self.password)
```

然后创建Address类。

```python
>>> class Address(Base):
...     __tablename__ = 'addresses'
...     id = Column(Integer, primary_key=True)
...     email_address = Column(String, nullable=False)
...     user_id = Column(Integer, ForeignKey('users.id'))
...     user = relationship("User", back_populates="addresses")
...
...     def __repr__(self):
...         return "<Address(email_address='%s')>" % self.email_address
```

现在我们再删除一个User对象后，与它关联的Address对象都会被删除。

```python
# 使用主键载入jack
>>> jack = session.query(User).get(5)

# 删除一个address
>>> del jack.addresses[1]

# 只剩下一个address
>>> session.query(Address).filter(
...             Address.email_address.in_(['jack@google.com', 'j25@yahoo.com'])
...             ).count()
1
```

删除Jack后，另一个Address也会被删除。

```python
>>> session.delete(jack)

>>> session.query(User).filter_by(name='jack').count()
0

>>> session.query(Address).filter(
...             Address.email_address.in_(['jack@google.com', 'j25@yahoo.com'])
...             ).count()
0
```

## 使用多对多关系

让我们展示一下多对多关系。假定我们创造一个博客程序，当用户写了一个BlogPost，它会有一个关联的Keyword。

为解释多对多关系，我们需要创建一个未映射的Table结构，让它作为关联表。

```python
>>> from sqlalchemy import Table, Text
>>> # 关联表
>>> post_keywords = Table('post_keywords', Base.metadata,
...         Column('post_id', ForeignKey('posts.id'), primary_key=True),
...         Column('keyword_id', ForeignKey('keywords.id'), primary_key=True)
... )
```

上面我们可以看到使用`Table`的声明和映射类稍微不一样。`Table`是一个构造器函数，所以每个Column都是用逗号分割的(即参数)。Column中显式给定了名称，而不是赋值给一个属性名。

然后我们定义`BlogPost`和`KeyWord`，使用辅助型的`relationship()`，都要引用`post_keywords`作为关联表。

```python
>>> class BlogPost(Base):
...     __tablename__ = 'posts'
...     id = Column(Integer, primary_key=True)
...     user_id = Column(Integer, ForeignKey('users.id'))
...     headline = Column(String(255), nullable=False)
...     body = Column(Text)
...
...     # 多对多 Blogpost <-> Keyword
...     keywords = relationship('Keyword',
...                             secondary=post_keywords,
...                             backref='posts')
...
...     def __init__(self, headline, body, author):
...         self.author = author
...         self.headline = headline
...         self.body = body
...
...     def __repr__(self):
...         return 'BlogPost({}, {}, {})'.formart(self.headline, self.body, self.author)

>>> class Keyword(Base):
...     __tablename__ = 'keywords'
...
...     id = Column(Integer, primary_key=True)
...     keyword = Column(String(50), nullable=False, unique=True)
...     posts = relationship('BlogPost',
...                         secondary=post_keywords,
...                         backref='keywords')
...
...     def __init__(self, keyword):
...         self.keyword = keyword
```

定义多对多关系是通过在`relationship()`中传入一个关键字参数完成，这个参数叫做`secondary`，传入的值应该是一个`Table`对象，这张表应该只包含多对多关系两张表的外键。

另外我们想为`BlogPost`加入一个`author`字段，我们加入另一个双边关系。但是当我们访问`User.posts`时不希望读取整个post集合。想要设置这种行为，我们需要对`relationship()`传入参数`lazy='dynamic'`，它对属性设置了个交替的读取策略。

```python
>>> BlogPost.author = relationship(User, back_populates='posts')
>>> Users.posts = relationship(BlogPost, back_populates='author', lazy='dynamic')
```

创建新表：

```python
>>> Base.metadata.create_all(engine)
```

让我们为Wendy发一些文章。

```python
>>> wendy = session.query(User).\
...                 fitler_by(name='wendy').\
...                 one()
>>> post = BlogPost("Wendy's Blog Post", "This is a test", wendy)
>>> session.add(post)
```

另外要创建keyword。

```python
>>> post.keywords.append(Keyword('wendy'))
>>> post.keywords.append(Keyword('firstpost'))
```

现在我们可以用firstpost查询博客文章了。我们对post使用`any`操作符，看它是不是拥有关键字"firstpost"：

```python
>>> session.query(BlogPost).\
...         filter(BlogPost.keywords.any(keyword='firstpost')).\
...         all()
[BlogPost("Wendy's Blog Post", 'This is a test', <User(name='wendy', fullname='Wendy Williams', password='foobar')>)]
```

我们也可以基于wendy对象来做博客查询。

```python
>>> session.query(BlogPost).\
...             filter(BlogPost.author == wendy)
...             filter(BlogPost.keywords.any(keyword='firstpost')).\
...             all()
[BlogPost("Wendy's Blog Post", 'This is a test', <User(name='wendy', fullname='Wendy Williams', password='foobar')>)]
```

抑或，我们可以直接使用wendy的`posts`关系，这是一个动态关系，使用的语法是这样：

```python
>>> wendy.posts.\
...         filter(BlogPost.keywords.any(keywords='firstpost')).\
...         all()
[BlogPost("Wendy's Blog Post", 'This is a test', <User(name='wendy', fullname='Wendy Williams', password='foobar')>)]
```

## 更多参考

* [Mapper配置](http://docs.sqlalchemy.org/en/rel_1_1/orm/mapper_config.html)
* [关系配置](http://docs.sqlalchemy.org/en/rel_1_1/orm/relationships.html)
* [使用Session](http://docs.sqlalchemy.org/en/rel_1_1/orm/session.html)








