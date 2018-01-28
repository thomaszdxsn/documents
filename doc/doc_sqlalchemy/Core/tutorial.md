# SQL Expression Language Tutorial

## Version Check

```python
>>> import sqllachemy
>>> sqlalchemy.__version__
1.2.0
```

## Connecting

我们使用`create_engine()`来与数据库连接：

```python
>>> from sqlalchemy import create_engine
>>> engine = create_engine('sqlite://:memory:', echo=True)
```

`create_engine()`返回的值是一个`Engine`实例，它代表数据库的核心接口，并使用一种Python DBAPI来处理一些方言的细节。

首次调用方法`Engine.execute()`或者`Engine.connect()`之后，`Engine`将会建立起一个真正的DBAPI连接，使用它来发出SQL。

## Define and Create Tables

我们将所有的表都定义在一个`Metadata`中，下面是一个创建表的例子:

```python
>>> from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey
>>> metadata = MetaData()
>>> users = Table('users', metadata,
...     Column('id', Integer, primary_key=True),
...     Column('name', String),
...     Column('fullname', String))

>>> addresses = Table('addresses', metadata,
...     Column('id', Integer, primary_key=True),
...     Column('user_id', None, ForeignKey('users.id')),
...     Column('email_address', String, nullable=False))
```

然后，我们使用`.create_all()`方法来创建所有的表。这个方法首先会检查每个表是否存在，所以可以放心的多次调用它：

```python
>>> metadata.create_all(engine)
SE...
```

## Insert Expressions

我们构造的首个SQL表达式是使用`Insert`构造器，它代表`INSERT`语句。它使用目标表来相关的创建SQL语句：

```python
>>> ins = users.insert()
```

想要看看这个构造器创建的SQL，请使用`str()`函数:

```python
'INSERT INTO users (id, name, fullname) VALUES (:id, :name, :fullname)'
```

注意上面的语句中每个列名都存在。可以使用`.values()`来指定`INSERT`中的`VALUES`:

```python
>>> ins = users.inserts().values(name='jack', fullname='Jack Jones')
>>> str(ins)
'INSERT INTO users (name, fullname) VALUES (:name, :fullname)'
```

上面例子中，`.values()`方法限制了`VALUES`字句中的列名。至于实际的值需要使用这种方式来获取:

```python
>>> ins.compile().params
{'fullname': 'Jack Jones', 'name': 'jack'}
```

## Executing

在这片教程中，我们聚焦于执行一个SQL构造最显式的一种方法，之后我们使用一些快捷方式来做这些。我们创建的`engine`对象是一个数据库连接的仓库，可以用之连接数据库。想要获取一条连接，我们可以使用`connect()`方法：

```python
>>> conn = engine.connect()
>>> conn
<sqlalchemy.engine.base.Connection object at 0x...>
```

`Connection`对象代表一个激活的DBAPI连接资源。让我们喂给它一个`Insert`对象看看会发生什么:

```python
>>> result = conn.execute(ins)
INSERT INTO users (name, fullname) VALUES (?, ?)
('jack', 'Jack Jones')
COMMIT
```


现在我们看到有参数值了，怎么做到的呢？因为在执行后，`Connection`用SQLite方言来生成这条语句。我们也可以手动看到这条语句:

```python
>>> ins.bind = engine
>>> str(ins)
'INSERT INTO users (name, fullname) VALUES (?, ?)'
```

至于生成的主键，我们可以这样获取:

```python
>>> result.inserted_primary_key
[1]
```

## Executing Multiple Statements

下面是另一种执行SQL的方式：

```python
>>> ins = users.insert()
>>> conn.execute(ins, id=2, name='wendy', fullname='Wendy Williams')
INSERT INTO users (id, name, fullname) VALUES (?, ?, ?)
(2, 'wendy', 'Wendy Williams')
COMMIT
<sqlalchemy.engine.result.ResultProxy object at 0x...>
```

想要执行DBAPI的`executemany()`方法，我们可以插入一个包含多个字典的列表：

```python
>>> conn.execute(addresses.insert(), [
...    {'user_id': 1, 'email_address' : 'jack@yahoo.com'},
...    {'user_id': 1, 'email_address' : 'jack@msn.com'},
...    {'user_id': 2, 'email_address' : 'www@www.org'},
...    {'user_id': 2, 'email_address' : 'wendy@aol.com'},
... ])
INSERT INTO addresses (user_id, email_address) VALUES (?, ?)
((1, 'jack@yahoo.com'), (1, 'jack@msn.com'), (2, 'www@www.org'), (2, 'wendy@aol.com'))
COMMIT
<sqlalchemy.engine.result.ResultProxy object at 0x...>
```

当执行多组参数时，每个字典**必须**拥有相同的键；

"executemany"同样可以使用在`insert()`，`update()`，`delete()`构造。

## Selecting

我们可以使用`select()`函数来构建基本的SELECT语句:

```python
>>> from sqlalchemy.sql import select
>>> s = select([users])
>>> result = conn.execute(s)
SELECT users.id, users.name, users.fullname
FROM users
()
```

返回的结果是一个`ResultProxy`对象，它很像DBAPI的cursor，同样包含方法`fetchone()`和`fetchmany()`。可以直接迭代获取这些数据rows：

```python
>>> for row in result:
...     print(row)
(1, u'jack', u'Jack Jones')
(2, u'wendy', u'Wendy Williams')
```

在上面的输出中，我们看到每个row以类元组的形式表现。我们有很多方式访问这个类元组对象。比如可以使用字典键的形式访问:

```python
>>> result = conn.execute(s)
>>> row = result.fetchone()
>>> print("name: ", row['name'], "; fullname: ", row['fullname'])
name: jack; fullname: Jack Jones
```

也可以使用整数索引(元组索引):

```python
>>> row = result.fetchone()
>>> print("name: ", row[1], "; fullname: ", row[2])
name: wendy; fullname: Wendy Williams
```

另一种方式是，直接使用表中的Column对象作为键：

```python
>>> for row in conn.execute(s):
...     print("name: ", row[users.c.name], "; fullname: ", row[user.c.fullname])
name: jack; fullname: Jack Jones
name: wendy; fullname: Wendy Williams
```

`ResultProxy`对象在垃圾回收的时候会自动返回给连接池，当然也可以手动关闭这个连接：

```python
>>> result.close()
```

如果你想要在query中控制查询的COLUMNS对象，可以通过`Table`对象的`c`属性来访问它们：

```python
>>> s = select([users.c.name, users.c.fullname])
>>> result = conn.execute(s)
>>> for row in result:
...     print(row)
(u"jack", u"Jack Jones"),
(u"wendy", u"Wendy Williams")
```

让我们观察FROM字句中的一些有趣的事情。让我们把两个Table放入到`select()`语句中：

```python
>>> for row in conn.execute(select([users, addresses])):
...     print(row)
(1, u'jack', u'Jack Jones', 1, 1, u'jack@yahoo.com')
(1, u'jack', u'Jack Jones', 2, 1, u'jack@msn.com')
(1, u'jack', u'Jack Jones', 3, 2, u'www@www.org')
(1, u'jack', u'Jack Jones', 4, 2, u'wendy@aol.com')
(2, u'wendy', u'Wendy Williams', 1, 1, u'jack@yahoo.com')
(2, u'wendy', u'Wendy Williams', 2, 1, u'jack@msn.com')
(2, u'wendy', u'Wendy Williams', 3, 2, u'www@www.org')
(2, u'wendy', u'Wendy Williams', 4, 2, u'wendy@aol.com')
```

熟悉SQL的人都知道这是卡迪尔积；我们需要使用WHERE字句，请使用`Select.where()`:

```python
>>> s = select([users, addresses]).where(users.c.id == addresses.c.user_id)
>>> for row in conn.execute(s):
...     print(row)
(1, u'jack', u'Jack Jones', 1, 1, u'jack@yahoo.com')
(1, u'jack', u'Jack Jones', 2, 1, u'jack@msn.com')
(2, u'wendy', u'Wendy Williams', 3, 2, u'www@www.org')
(2, u'wendy', u'Wendy Williams', 4, 2, u'wendy@aol.com')
```

它实现的原理是重载了Column对象的操作符，让我们看看这种表达式的结果：

```python
>>>> users.c.id == address.c.user_id
<sqlalchemy.sql.elements.BinaryExpression object at 0x...>
```

很奇怪是吧？它没有返回True或者False。那么到底是什么呢？

```python
>>> str(users.c.id == addresses.c.user_id)
'users.id = addresses.user_id'
```

## Operators

我们已经知道两个column是如何进行相等比较的：

```python
>>> print(users.c.id == addresses.c.user_id)
users.id = addresses.user_id
```

如果我们使用一个字面量值，我们获取一个bind参数:

```python
>>> print(users.c.id == 7)
users.id = :id_1
```

字面量`7`嵌入到了`ColumnElement`的结果中；我们可以使用一种小技巧来获取它们：

```python
>>> (uesrs.c.id == 7).compile().params
{u"id_1": 7}
```

大多数Python运算符都进行了重载，比如相等，不等，...

```python
>>> print(users.c.id != 7)
users.id != :id_1

>>> # None 转变为 IS NULL
>>> print(users.c.name == None)
users.name IS NULL

>>> # 将两个操作对象反过来也一样
>>> print('fred' > users.c.name)
users.name < :name_1
```

如果我们相加两个INTEGER COLUMN，我们会获取一个相加的表达式：

```python
>>> print(users.c.id + addresses.c.id)
users.id + addresses.id
```

**Column的类型很重要！**，如果我们对STRING COLUMN使用`+`，将会生成不同的表达式:

```python
>>> print(users.c.name + users.c.fullname)
users.name || users.fullname
```

`||`是大多数数据库使用的字符串连接操作符。但也不是全部，比如MySQL:

```python
>>> print((users.c.name + users.c.fullname).complie(bind=create_engine('mysql://')))
concat(users.name, users.fullname)
```

MySQL中使用`concat()`函数来替代`||`.

如果某种操作符在Python里面没有参照物，你可以使用`Operators.op()`方法来生成任何操作符：

```python
>>> print(users.c.name.op('tiddlywinks')('foo'))
users.name tiddlywinks :name_1
```

可以使用这个函数来生成位操作符。例如:

```python
somecolumn.op('&')(0xff)
```

当使用`Operators.op()`的时候，返回表达式的类型是很重要的。如果不能确定，请使用`type_coerce()`:

```python
from sqlalchemy import type_coerce
expr = type_coerce(somecolumn.op('-%>')('foo'), MySpecialType())
stmt = select([expr])
```

对于布尔操作符，请使用`Operators.bool_op()`方法，它会确保返回的表达式被当作布尔值处理:

```python
somecolumn.bool_op('-->')('some value')
```

### Operator Customization

pass

## Conjunctions

我们展示了`select()`中可以使用的一些操作符，不过我们可以继续深入的讨论一下它们，让我们首先介绍一下拼接。拼接，比如AND、OR，NOT可以将一些字句组合在一起：

```python
>>> from sqlalchemy.sql import and_, or_, not_
>>> print(and_(
...         users.c.name.like('j%'),
...         users.c.id == addresses.c.user_id,
...         or_(
...             addresses.c.email_address == 'wendy@aol.com',
...             addresses.c.email_address == 'jack@yahoo.com',
...         ),
...         not_(users.c.id > 5)
...      )
... )
users.name LIKE :name_1 AND users.id = addresses.user_id AND
(addresses.email_address = :email_address_1
    OR addresses.email_address = :email_address_2)
AND users.id <= :id_1
```

另外你可以使用位操作符，但是需要在适当的地方加入括号以避免操作符优先级问题:

```python
>>> print(users.c.name.like('j%') & (users.c.id == addresses.c.user_id) &
...         (
...             (addresses.c.email_address == 'wendy@aol.com') | \
...             (addresses.c.email_address == 'jack@yahoo.com')
...         ) \
...         & ~ (users.c.id > 5)
... )
users.name LIKE :name_1 AND users.id = addresses.user_id AND
(addresses.email_address = :email_address_1
    OR addresses.email_address = :email_address_2)
AND users.id <= :id_1
```

另外可以利用`.label()`来创建AS字句:

```python
>>> s = select([(users.c.fullname + 
...               ", " + addresses.c.email_address).
...               label('title')]).\
...         where(
...             and_(
...                 users.c.id == addresses.c.user_id,
...                 users.c.name.between('m', 'z'),
...                 or_(
...                     addresses.c.email_address.like('%@aol.com'),
...                     addresses.c.email_address.like('%@msn.com')
...                 )
...             )
...         )
>>> conn.execute(s).fetchall()

SELECT users.fullname || ? || addresses.email_address AS title
FROM users, addresses
WHERE users.id = addresses.user_id AND users.name BETWEEN ? AND ? AND
(addresses.email_address LIKE ? OR addresses.email_address LIKE ?)
(', ', 'm', 'z', '%@aol.com', '%@msn.com')

[(u'Wendy Williams, wendy@aol.com',)]
```

`and_()`也可以多次调用`.where()`字句来替代，比如可以把上面的例子改写成这样:

```python
>>> s = select([(users.c.fullname + 
...                  ", "  + addresses.c.email_address).
...                  label('title')]).\
...         where(users.c.id == addresses.c.user_id).\
...         where(users.c.name.between('m', 'z')).\
...         where(
...             or_(
...                 addresses.c.email_address.like('%@aol.com'),
...                 addresses.c.email_address.like('%@msn.com')
...             )
...         )
>>> conn.execute(s).fetchall()

SELECT users.fullname || ? || addresses.email_address AS title
FROM users, addresses
WHERE users.id = addresses.user_id AND users.name BETWEEN ? AND ? AND
(addresses.email_address LIKE ? OR addresses.email_address LIKE ?)
(', ', 'm', 'z', '%@aol.com', '%@msn.com')

[(u'Wendy Williams, wendy@aol.com',)]
```


## Using Textual SQL

我们最后的例子有多个类型。我们可以使用原生的SQL文本：

```python
>>> from sqlalchemy.sql import text
>>> s = text(
...     "SELECT users.fullname || ', ' || addresses.email_address AS title "
...         "FROM users, addresses "
...         "WHERE users.id = addresses.user_id "
...         "AND users.name BETWEEN :x AND :y "
...         "AND (addresses.email_address LIKE :e1 "
...             "OR addresses.email_address LIKE :e2)")
SQL>>> conn.execute(s, x='m', y='z', e1='%@aol.com', e2='%@msn.com').fetchall()
[(u'Wendy Williams, wendy@aol.com',)]
```

请注意两行语句之间都有空格，否则不是合法的SQL。bind参数还是通过`.execute()`传入的。

### Specifying Bound Parameter Behaviors

`text()`可以通过使用`TextCluase.bindparams()`方法来预先绑定参数:

```python
stmt = text('SELECT * FROM users WHERE users.name BETWEEN :x AND :y')
stmt = stmt.bindparams(x='m', y='z')
```

这些参数也可以显式的类型声明:

```python
stmt = stmt.bindparams(bindparam("x", String), bindparam("y", String))
result = conn.execute(stmt, {"x": "m", "y": "z"})
```

### Specifying Result-Column Behaviors

我们可以使用`TextClause.columns()`来指定关于结果column的信息；这个方法可以用来指定返回的类型：

```python
stmt = stmt.columns(id=Integer, name=String)
```

或者可以以位置参数的形式传入:

```python
stmt = text('SELECT id, name FROM users')
stmt = stmt.columns(users.c.id, users.c.name)
```

当我们调用`TextClause.columns()`的时候，返回一个`TextAsFrom`对象，可以继续对它进行进一步的query:

```python
j = stmt.join(addresses, stmt.c.id == addresses.c.user_id)

new_stmt = select([stmt.c.id, addresses.c.id]).\
    select_from(j).where(stmt.c.name == 'x')
```

`TextClause.columns()`使用位置参数是特别有用的，因为可以利用它来不在担心SQL text中的列名在关键字参数中存在的冲突:

```python
>>> stmt = text(
...     "SELECT users.id, addresses.id users.id, "
...         "users.name, addresses.email_address AS email "
...     "FROM users JOIN addresses ON users.id=addresses.user_id "
...     "WHERE users.id = 1").columns(
...         users.c.id,
...         addresses.c.id,
...         addresses.c.user_id,
...         users.c.name,
...         addresses.c.email_address)
>>> result = conn.execute(stmt)
```

上面的例子中，有三个column叫做id，但是因为我们以位置参数的形式传入所以不会发生冲突。获取`email_address`列可以这样作：

```python
>>> row = result.fetchone()
>>> row[addresses.c.email_address]
'jack@yahoo.com'
```

也可以使用字符串形式的列名作为键，但是如果存在多个同名列，那么就会发生错误:

```python
>>> row["id"]
Traceback (most recent call last):
...
InvalidRequestError: Ambiguous column name 'id' in result set column descriptions
```

### Using text() fragments inside bigger statement

`text()`可以生成SQL片段，可以将它直接用于`select()`对象。下面例子中，我们组合`text()`和`select()`使用。这样我们可以不许定义任何`Table`metadata即可以创建一个SQL语句：

```python
>>> s = select([
...   text(
...     "users.fullname || ', ' || addresses.email_address AS title"
...    )]).\
...     where(
...         and_(
...             text("users.id = addresses.user_id"),
...             text("users.name BETWEEN 'm' AND 'z'"),
...             text(
...                 "(addresses.email_address LIKE :x "
...                 "OR addresses.email_address LIKE :y)")
...         )
...     ).select_from(text('users, addresses'))
>>> conn.execute(s, x='%@aol.com', y='%@msn.com').fetchall()
[(u'Wendy Williams, wendy@aol.com',)]
```

### Using More Specific Text with `table()`, `literal_column()`, and `column()`

还可以灵活的使用`literal_column()`， `table()`

```python
>>> from sqlalchemy import select, and_, text, String
>>> from sqlalchemy.sql import table, literal_column
>>> s = select([
...     literal_column('users.fullname', String) + 
...     ', ' +
...     literal_column('addresses.email_address').label('title')
... ]).\
...     where(
...         and_(
...             literal_column('users.id') == literal_column('addresses.user_id'),
...             text("users.name BETWEEN 'm' AND 'z'"),
...             text(
...                 "(addresses.email_address LIKE :x OR "
...                 "addresses.email_address LIKE :y)")
...         )
...     ).select_from(table('users')).select_from(table('addresses'))

>>> conn.execute(s, x='%@aol.com', y='%@msn.com').fetchall()
[(u'Wendy Williams, wendy@aol.com',)]
```

### Ordering or Grouping by a Label

如果在`select()`构造中使用了label，我们可以将这个label直接在`group_by()`或者`order_by()`中使用：

```python
>>> from sqlalchemy import func
>>> stmt = select([
...     addresses.c.user_id,
...     func.count(addresses.c.id).label('num_addresses')]).\
...     order_by('num_addresses')

>>> conn.execute(stmt).fetchall()
[(2, 4)]
```

我们可以使用`asc()`或者`desc()`来定义排序方向：

```python
>>> from sqlalchemy import func, desc
>>> stmt = select([
...     addresses.c.user_id,
...     func.count(addresses.c.id).label('num_addresses')]).\
...     order_by(desc('num_addresses'))

>>> conn.execute(stmt).fetchall()
[(2, 4)]
```

如果要比较同一个表但是不想用text的方式:

```python
>>> u1a, u1b = users.alias(), users.alias()
>>> stmt = select([u1a, u1b]).\
...         where(u1a.c.name > u1b.c.name).\
...         order_by(u1a.c.name)   # 这里不能直接使用"name"

>>> conn.execute(stmt).fetchall()
[(2, u'wendy', u'Wendy Williams', 1, u'jack', u'Jack Jones')]
```

## Using Aliases

