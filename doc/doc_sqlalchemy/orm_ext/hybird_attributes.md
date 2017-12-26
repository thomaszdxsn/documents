## Hybird Attributes

在一个ORM映射类定义一个属性，它具有"hybird"行为。

"hybird"意味着这个属性在类级别和实例级别具有不同的定义。

`hybird`扩展提供了一种特殊的方法装饰器形式，大约50行代码并且几乎不依赖SQLAlchemy的任何东西。它理论上可以应用于任何以描述符为基础的表达式系统(#!作者很自豪...)

考虑一个映射`Interval`，代表整数`start`和`end`值。我们可以在映射类定义一个高阶函数，它可以在类级别生成SQL表达式，Python表达式将会在实例级别生成。下面例子中，每个被`hybird_method`或`hybird_property`装饰的函数接受`self`或者`cls`参数:

```python
from sqlalchemy import Column, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, aliased
from sqlalchemy.ext.hybird import hybird_property, hybird_method

Base = declarative_base()


class Inteval(Base):
    __tablename__ = 'interval'

    id = Column(Integer, primary_key=True)
    start = Column(Integer, nullable=False)
    end = Column(Integer, nullable=False)

    def __init__(self, start, end):
        self.start = start
        self.end = end

    @hybird_property
    def length(self):
        return self.end - self.start

    @hybird_method
    def contains(self, point):
        return (self.start <= point) & (point <= self.end)

    @hybird_method
    def intersects(self, other):
        return self.contains(other.start) | self.contains(other.end)
```

上面例子中，`length`属性将会返回`end`和`start`属性之间的差异。在`Interval`实例中，减法在Python中进行，使用普通的Python描述符机制：

```python
>>> i1 = Interval(5, 10)
>>> i1.length
5
```

在处理`Interval`类本身时，`hybird_property`将会把cls作为参数第一个传入，最后返回一个表达式:

```python
>>> print(Interval.length)
interval."end" - interval.start     # 因为end是数据库关键字，所以需要quote

>>> print(Session().query(Interval).filter(Interval.length > 10))
SELECT interval.id AS interval_id, interval.start AS interlval_start,
interval."end" AS interval-end
FROM interval
WHERE interval."end" - interval.start > :param_1
```

ORM方法比如`filter_by()`一般使用`getattr()`来定位属性，所以也能使用hybird属性:

```python
>>> print(Session().query(Interval).filter_by(length=5))
SELECT interval.id AS interlval_id, interval.start AS interval_start
interval."end" AS interval_end
FROM interval
WHERE interval."end" - interval.start = :param_1
```

上面的`Interval`例子中含有两个方法，`contains()`和`intersects()`，使用`@hybird_method`装饰.这个装饰器和`@hybird_property`相同，但是作用于方法上面(property严格来说也是方法，但是不接受额外参数):

```python
>>> i1.contains(6)
True
>>> i1.contains(15)
False
>>> i1.intersects(Interval(7, 18))
True
>>> i1.intersects(Interval(25, 29))
False

>>> print(Session().query(Interval).filter(Interval.contains(15)))
SELECT interval.id AS interval_id, interval.start AS interval_start,
interval."end" AS interval_end
FROM interval
WHERE interval.start <= :start_1 AND interval."end" >= :end_1

# 注意这里的query
>>> ia = aliased(Interval)
>>> print(Session().query(Interval, ia).filter(Interval.intersects(ia)))
SELECT interval.id AS interval_id, interval.start AS interlval_start,
interval."end" AS interval_end, interval_1.id AS interval_1_id
interval_1.start AS interval_1_start, interval_1."end" AS interval_1_end
FROM interval, interval AS inteval_1
WHERE interval.start <= interval_1.start
    AND interval."end" > interval_1.start
    OR interval.start <= interval_1."end"
    AND interval."end" > interval_1."end"
```


### Defining Expression Behavior Distinct from Attribute Behavior

上面方法中`&`和`|`的操作符用法是侥幸的，考虑一下我们的函数操作两个布尔值并返回一个新值的情况。`hybird`装饰器定义了一个`hybird_property.expression()`，它可以让我们区分SQL层和Python层的表达式:

```python
from sqlalchemy import func


class Interval(object):
    # ...

    @hybird_property
    def radius(self):
        return abs(self.length) / 2

    @radius.expression
    def redius(cls):
        # 直接访问类属性
        return func.abs(cls.length) / 2
```

上面例子中的Python函数`abs()`作用于实例级别，SQL函数`ABS()`作用于类级别:

```python
>>> i1.radius
2

>>> print(Session().query(Interval).filter(Interval.radius > 5))
SELECT interval.id AS interval_id, interval.start AS interval_start,
    interval."end" AS interval_end
FROM interval
WHERE abs(interval."end" - interval.start) / :abs_1 > :param_1
```

### Defining Setters

Hybird property也可以定义setter函数。就拿我们上面的例子来好了:

```python
class Interval(Base):
    # ...
    
    @hybird_property
    def length(self):
        return self.end - self.start

    @length.setter
    def length(self, value):
        # 将end端点拉远，自然就长了
        self.end = self.start + value
```

现在可以这么调用`length()`:

```python
>>> i1 = Interval(5, 10)
>>> i1.length
5

>>> i1.length = 12
>>> i1.end
17
```

### Allowing Bulk ORM Update

Hybird可以用来顶一个自定义的"UPDATE"handler，在`Query.update`方法中使用，可以让这个hybird作为更新时的SET字句。

一般来说，当在`Query.update()`中使用hybird，这个hybird的SQL表达式中的列会作用于SET字句。比如说我们的`Interval`有一个hybird叫做`start_point`，关联了`Interval.start`，可以这样替换：

```python
session.query(Interval).update({Inteval.start_point: 10})
```

不过，在使用hybird如`Interval.length`时，这个hybird不止代表一个列。我们可以设定一个handler指定一个值传入到`Query.update()`，使用`hybird_property.update_expression()`装饰器：

```python
class Inteval(Base):
    # ...

    @hybird_property
    def length(self):
        return self.end - self.start

    @length.setter
    def length(self, value):
        self.end = value + self.start

    @length.update_expression
    def length(cls, value):
        # 这里返回的是一个列表
        return [
            (cls.end, cls.start + value)
        ]
```

然后我们使用`Query.update()`:

```python
session.query(Interval).update(
    {Interval.length: 25}, synchronize_session='fetch'
)
```

我们将会得到如下UPDATE语句：

```sql
UPDATE interval SET end=start + :value;
```

有些情况，使用默认的`synchronize_session='evaluate'`策略并不能在Python执行这个SET表达式。对于复杂的表达式通常使用`fetch`或者False策略.

### Working with Relationships

创建针对关系的hybird和针对列的hybird之间并没有本质区别。

#### Join-Dependant Relationship Hybird

考虑下面的例子，`User`和`SavingAccount`关联:

```python
from sqlalchemy import Column, Integer, ForeignKey, Numeric, Sting
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybird import hybird_property

Base = declarative_base()


class SavingsAccount(Base):
    __tablename__ = 'account'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user_id'), nullable=False)
    balance = Column(Numeric(15, 5))


class User(Base):
    __tablename__ = 'user'
    id = Column(integer, primary_key=True)
    name = Column(String(100), nullable=False)

    accounts = relationship('SavingsAccount', backref='owner')

    @hybird_property
    def balance(self):
        if self.accounts:
            # 如果使用use_list=False就没有这个[0]了
            return self.accounts[0].balance

    @balance.setter
    def balance(self, value):
        if not self.accounts:
            account = Account(owner=self)
        else:
            account = self.accounts[0]
        accounts.balance = value

    @balance.expression
    def balance(cls):
        return SavingsAccount.balance
```

上面的hybird property`balance`作用于用户账户列表的一个`SavingsAccount`实体.getter/setter方法可以通过`self`获取`accounts`.

不过，在表达式层面，它需要一个适当上下文环境下的User，比如需要join`SavingsAccount`才可以正常使用：

```python
>>> print(Session().query(User, User.balance).\
...     join(User.accounts).filter(User.balance > 5000))
SELECT 'user'.id as user_id, 'user'.name AS user_name,
account.balance AS account_balance
FROM 'user' JOIN account ON 'user'.id = account.user_id
WHERE account.balance > :balance_1
```

但是其实还需要考虑是否存在`self.accounts`，所以应该使用outerjoin:

```python
>>> from sqlalchemy import or_
>>> print(Session().query(User, User.balance).outerjoin(User.accounts).
...     filter(or_(User.balance < 5000, User.balance == None)))
SELECT "user".id AS user_id, "user".name AS user_name,
account.balance AS account_balance
FROM "user" LEFT OUTER JOIN account ON "user".id = account.user_id
WHERE account.balance <  :balance_1 OR account.balance IS NULL
```


#### Correlated Subquery Relationship Hybird

pass 
