# Working with Engines and Connections¶

## Basic Usage

`engine`可以直接向数据库发送SQL。一般情况都需要生成一个连接资源，可以通过`Engine.connect()`方法来获取:

```python
connection = engine.connect()
result = connection.execute("select username from users")
for row in result:
    print("username: ", row['username'])
connection.close()
```

connection是一个`Connection`实例，它是一个真实DBAPI连接的代理(proxy)对象。`Connection`对象创建时会从连接池取回一个DBAPI连接资源。

返回的result是一个`ResultProxy`实例，它实现了DBAPI的大部分接口。

当调用`.close()`方法之后，引用的DBAPI资源将会被释放回连接池。

上面的执行过程可以有一种更快捷的方式，即直接使用`Engine`本身的`.execute()`方法：

```python
result = engine.execute('SELECT username FROM users')
for row in result:
    print("username: ", row['username'])
```

在这个例子返回的`ResultProxy`，会包含一个flag：`close_with_result`，它代表当底层的DBAPI cursor被关闭(消耗完)后，`Connection`对象也会被关闭，然后DBAPI连接就会释放回连接池，释放连接资源。

`ResultProxy`可能仍然没有被消耗殆尽，可以显式地关闭它：

```python
result.close()
```

## Using Transaction

`Connection`对象提供了一个`begin()`方法，它返回一个`Transaction`对象。这个对象通常在try/except代码块中使用，可以正确的调用`Transaction.rollback()`，`Transaction.commit()`：

```python
connection = engine.connect()
trans = connection.begin()
try:
    r1 = connection.execute(table1.select())
    connection.execute(table1.insert(), col1=7, col2='this is some data')
    trans.commit()
except:
    trans.rollback()
    raise
```

上面的代码可以使用上下文管理器，让语法更加简洁。可以通过`Engine`开启事务：

```python
# 开启一个事务
with engine.begin() as connection:
    r1 = connection.execute(table1.select())
    connection.execute(table1.insert(), col1=7, col2='this is some data')
```

也可以通过`Connection`开启一个`Transaction`事务：

```python
with connection.begin() as trans:
    r1 = connection.execute(table1.select())
    connection.execute(table1.insert(), col1=7, col2='this is some data')
```

### Nesting of Transaction Blocks

`Transaction`对象可以用来创建嵌套的事务。在这个例子中，两个函数都基于Connection开启了一个事务，但是只有最外层的Transaction对象会在commit阶段生效:

```python
# methods_a开启一个事务然后调用method_b
def method_a(connection):
    trans = connection.begin()
    try:
        method_b(connection)
        trans.commit()
    except:
        trans.rollback()
        raise

# method_b开启一个事务
def method_b(connection):
    trans = connection.begin()
    try:
        connection.execute('insert into mytable values ("bat", "lala")')
        connection.execute(mytable.insert(), col1='bat', col2='lala')
        trans.commit()  # 事务还没有被提交
    except:
        trans.rollback()
        raise


# 开启一个连接，然后调用method_a
conn = engine.connect()
method_a(conn)
conn.close()
```

## Understanding Autocommit

pass

## Connectionless Execution, Implicit Execution

之前章节中提到，我们并不需要显式的使用`Connection`，这叫做"**Connectionless**":

```python
result = engine.execute('select username from users')
for row in result:
    print('username: ', row['username'])
```

也可以对任意的`Executable`构造使用`.execute()`方法。SQL表达式对象会引用`Engine`或者`Collection`为*bind*，使用它来提供所谓的"隐式(implicit)"执行服务。

假定有下面这一个表：

```python
from sqlalchemy import MetaData, Table, Column, Integer

metadata = MetaData()
users_table = Table('users', metadata,
                Column('id', Integer, primary_key=True),
                Column('name', String(50))
)
```

显式执行可以对`Connection.execute()`方法传入SQL文本或者SQL构造:

```python
engine = create_engine('sqlite:///file.db')
connection = engine.connect()
result = connection.execute(users_table.select())
for row in result:
    # ...
connection.close()
```

显式，也可以将SQL文本/对象交给`Engine.execute()`来执行：

```python
engine = create_engine('sqlite:///file.db')
result = engine.execute(users_table.select())
for row in result:
    # ...
result.close()
```

隐式(implicit)执行也可以是connectionless的，可以通过一个表达式本身的`.execute()`方法来使用。会自动采用MetaData.bind属性作为Engine资源：

```python
engine = create_engine('sqlite:///file.db')
meta.bind = engine
result = users_table.select().execute()
for row in result:
    # ...
result.close()
```

上面例子中，`Table`的`select()`会有一个`execute()`方法，它将会搜索关联这个`Table`的`Engine`.

"绑定metadata“拥有三个主要的效果:

- SQL表达式对象拥有一个`Executable.execute()`方法，它可以自动获取绑定的Engine。
- ORM`Session`对象支持使用"bound metadata"
- `Metadata.create_all()`, `Metadata.drop_all()`, `Table.create()`，`Table.drop()`，以及"autoload"特性都会自动使用绑定的这个`Engine`。

## Translation of Schema Names

pass

## Engine Disposal

pass

## Using the Threadlocal Execution Strategy

"threadlocal"engine策略是一个可选的特性，可以在使用非ORM的应用中关联当前线程和事务。

可以这样激活`threadlocal`:

```python
db = create_engine('mysql://localhost/test', strategy='threadlocal')
```

上面例子中的`Engine`实例可以使用thread-local的变量:

```python
def call_operation1():
    engine.execute('insert into users values(?, ?)', 1, "john")


def call_operation2():
    users.update(users.c.user_id == 5).execute(name='ed')

db.begin()
try:
    call_operation1()
    call_operation2()
    db.commit()
except:
    db.rollback()
```

另一个例子:

```python
db.begin()
conn = db.connect()
try:
    conn.execute(log_table.insert(), message="Operation started")
    call_operation1()
    call_operation2()
    db.commit()
    conn.execute(log_table.insert(), message="Operation succeeded")
except:
    db.rollback()
    conn.execute(log_table.insert(), message="Operation failed")
finally:
    db.close()
```

## Working with Raw DBAPI Connections

想要获取原生的DBAPI连接。可以通过`Connection.connection`来获取:

```python
connection = engine.connect()
dbapi_conn = connection.connection
```

也可以通过`Engine.raw_connection()`来获取:

```python
dbapi_conn = engine.raw_connection()
```

用完记得关闭:

```python
dbapi_conn.close()
```

### Calling Stored Procedures

pass

### Multiple Result Sets

可以通过DBAPI cursor的`.nextset()`方法获取多个结果集合:

```python
connection = engine.raw_connection()
try:
    cursor = connection.cursor()
    cursor.execute("select * from table1; select * from table2")
    results_one = cursor.fetchall()
    cursor.nextset()
    results_two = cursor.fetchall()
    cursor.close()
finally:
    connection.close()
```

## Registring New Dialects

pass

### Registering Dialects In-Process

pass

## API

pass
