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

我们当然也可以使用correlated subquery.correlated subquery可移植性更好，但是在SQL层面的效率相比稍差。我们可以使用这个技术来计算所有账号的余额:

```python
from sqlalchemy import Column, Integer, ForeignKey, Numeric, String
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybird import hybird_property
from sqlalchemy import select, func

Base = declarative_base()


class SavingsAccount(Base):
    __tablename__ = 'account'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    balance = Column(Numeric(15, 5))


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)

    accounts = relationship('SavingsAccount', backref='owner')

    @hybird_property
    def balance(self):
        return sum(acc.balance for acc in self.accounts)

    @balance.expression
    def balance(cls):
        return select([func.sum(SavingsAccount.balance)]).\
                where(SavingsAccount.user_id == cls.id).\
                label('total_balance')
```

上面的例子将会让balance生成这样一个SQL:

```python
>>> print s.query(User).filter(User.balance > 400)
SELECT "user".id AS user_id, "user".name AS user_name
FROM "user"
WHERE (SELECT sum(account.balance) AS sum_1
FROM account
WHERE account.user_id = "user".id) > :param_1
```

### Building Custom Comparators

hybird属性包含一个helper，可以用于创建自定义比较符：

`hybird_property.comparator()`装饰器和`hybird_property.expression`不能一起使用。

下面例子允许属性不区分大小写地比较:

```python
from sqlalchemy.ext.hybird import Comparator, hybird_property
from sqlalchemy import func, Column, Integer, String
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class CaseInsensitiveComparator(Compartor):
    def __eq__(self, other):
        return func.lower(self.__clause_element__()) == func.lower(other)


class SearchWord(Base):
    __tablename__ = 'searchword'
    id = Column(Integer, primary_key=True)
    word = Column(String(255), nullable=False)

    @hybird_property
    def word_insensitive(self):
        return self.word.lower()

    @word_insensitive.compartor
    def word_insensitive(cls):
        return CaseInsensitiveComparator(cls.word)
```

上面例子中，`word_insensitive`的SQL形态将会对它使用`LOWER()`这个SQL函数:

```python
>>> print(Session().query(SearchWord).filter_by(word_insensitive='Trucks'))
SELECT searchword.id AS searchword_id, searchword.word AS searchword_word
FROM searchword
WHERE lower(searchword.word) = lower(:lower_1)
```

`CaseInsensitiveComparator`实现了`ColumnOperators`的部分接口。可以在`Comparator.operate`方法中，将任意的比较操作使用"类型转换"操作:

```python
class CaseInsensitiveCompartor(Comparator):
    def operate(self, op, other):
        return op(func.lower(self.__cluase_element__()), func.lower(other))
```

### Reusing Hybird Properties across Subclasses

hybird可以继承自父类，可以在子类中重写`hybird_property.getter()`, `hybird_property.setter()`.这和Python中的`@property`类似:

```python
class FirstNameOnly(Base):
    # ...
    first_name = Column(String)

    @hybird_property
    def name(self):
        return self.first_name

    @name.setter
    def name(self, value):
        self.first_name = value


class FirstNameLastName(FirstNameOnly):
    # ...
    last_name = Column(String)

    @FirstNameOnly.name.getter
    def name(self):
        return self.first_name + ' ' + self.last_name

    @name.setter
    def name(self, value):
        self.firstname, self.lastname = value.split(' ', 1)
```

上面例子中，`FirstNameLastName`引用了`FirstNameOnly`中的hybird，将它作为自己的getter和setter.

在覆盖`hybird_property.expression()`和`hybird_property.comparator()`时，需要使用`hybird_property.overrides`，否则会发生冲突的问题：

```python
class FirstNameLastName(FirstNameOnly):
    # ...

    last_name = Column(String)

    @FirstNameOnly.overrides.expression
    def name(cls):
        return func.concat(cls.first_name, ' ', last_name)
```

### Hybird Value Objects

注意在我们上一个例子中，如果我们将`SearchWord`实例的`.word_insensitive`属性和普通的Python字符串比较时，字符串并不会自动的变为小写。`@word_insensitive.compartor`只作用于SQL端。

自定义比较符的一个稍复杂形态叫做`Hybird Value Object`.这个技术可以同样应用到实例端和SQL表达式一端。让我们讲之前例子中的`CaseInsensitiveComparator`类换成`CaseInsensitiveWord`:

```python
class CaseInsensitiveWord(Comparator):
    """Hybird value object representign a lower case representation of a word."""

    def __init__(self, word):
        if isinstance(word, basestring):
            self.word = word.lower()
        elif isinstance(word, CaseInsensitiveWord):
            self.word = word.word
        else:
            self.word = func.lower(word)

    def operator(self, op, other):
        if not isinstance(other, CaseInsensitiveWord):
            other = CaseInsensitiveWord(other)
        return op(self.word, other.word)

    def __clause_element__(self):
        return self.word

    def __str__(self):
        return self.word

    key = 'word'
    # 'Label to apply to Query tuple results'(query结果的label)
```

上面例子中，`CaseInsensitiveWord`对象的`self.word`，可能是一个SQL函数，或者原生Python对象.通过覆盖`operate()`和`__cluase_elment__()`都是为了`self.word`，让所有比较操作都针对了转换后的`self.word`:

```python
class SearchWord(Base):
    __tablename__ = 'searchword'
    id = Column(Integer, primary_key=True)
    word = Column(String(255), nullable=False)
    
    @hybird_property
    def word_insensitive(self):
        return CaseInsensitiveWord(self.word)
```

现在`.word_insensitive`属性可以通用级别忽略大小写，包含SQL表达式和Python表达式:

```python
>>> print(Session().query(SearchWord).filter_by(word_insensitive='Trucks'))
SELECT searchword.id AS searchword_id, searchword.word AS searchword_word
FROM searchword
WHERE lower(searchword.word) = :lower_1
```
SQL表达式　比较　SQL表达式：

```python
>>> sw1 = aliased(SearchWord)
>>> sw2 = aliased(SearchWord)
>>> printSession().query(
...     sw1.word_insensitive,
...     sw2.word_insensitive).\
...         filter(
...             sw1.word_insensitive > sw2.word_insensitive    
...         )    
SELECT lower(searchword_1.word) AS lower_1,
lower(searchword_2.word) AS lower_2
FROM searchword AS searchword_1, searchword AS searchword_2
WHERE lower(searchword_1.word) > lower(searchword_2.word)
```

Python表达式:

```python
>>> ws1 = SearchWord(word='SomeWord')
>>> ws1.word_insensitive == 's0mEw0rD'
True
>>> ws1.word.insensitive == 'X0mEw0rX'
False
>>> print(ws1.word_insensitive)
someword
```

**Hybird Value**模式在面对**值具有多种表现形式**的场景时非常有用，比如时间戳，时间delta，度量单位，货币以及加密密码.

### Building Transformers

*transformer*是一个对象，它可以接受一个Query对象并返回一个新的Query对象。这个`Query`对象包含一个方法`with_transformation()`，它返回通过函数变形后新的一个`QUery`.

我们可以将它和`Compartor`组合起来。

考虑一个映射类`Node`,它使用adjacency模式组装成一个树结构:

```python
from sqlalchemy import Column, Integer, Foreignkey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Node(Base):
    __tablename__ = 'node'
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('node.id'))
    parent = relationship("Node", remote_side=id)
```

假设我们想要增加一个访问器`grandparent`.它将会返回`parent`的`Node.parent`.当我们有一个`Node`实例时，这很简单：

```python
from sqlalchemy.ext.hybird import hybird_property


class Node(Base):
    # ...

    @hybird_property
    def grandparent(self):
        return self.parent.parent
```

对于表达式来说，事情就没那么简单了。我们需要构建一个`Query`，需要join两次`Node.parent`来获取grandparent.但是我们可以组合使用`Comparator`和`transfomer`：

```python
from sqlalchemy.ext.hybird import Comparator


class GrandparentTransformer(Comparator):
    def operate(self, op, other):
        def transform(q):
            cls = self.__clause_element__()
            parent_alised = aliased(cls)
            return q.join(parent_alias, cls.parent).\
                        filter(op(parent_alias.parent, other))
        return transform


Base = declarative_base()


classs Node(Base):
    __tablename__ = 'node'
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('node.id'))
    parent = relationship("Node", remote_side=id)

    @hybird_property
    def grandparent(self):
        return self.parent.parent

    @hybird.comparator
    def grandparent(cls):
        return GrandparentTransformer(cls)
```

`GrandparentTransformer`覆盖了核心`Operators.operate()`方法，返回一个query-transform的可调用对象，它在一个特殊上下文里面使用运行给定的比较操作。比如，在上面例子中，`operate()`方法被调用,在`Operators.eq`(相等比较)的右侧是`Node(id=5)`.调用`transform`函数后，将会把Query和`Node.parent`　join起来，然后比较`parent_alias`，将它传入到`Query.filter()`中:

```python
>>> from sqlalchemy.orm import Session
>>> session = Session()
>>> session.query(Node).\
...     with_transformation(Node.grandparent == Node(id=5)).\
...     all()
```

我们可以修改这个模式让它更加啰嗦，但是更具弹性，可以在"fiter"步骤中分离出"join"步骤:

```python
class Node(Base):
    # ...

    @grandparent.comparator
    def grandparent(cls):
        # 为每个类缓存一个GrandparentFormer
        if "_gp" not in cls.__dict__:
            cls._gp = GrandparentTransformer(cls)
        return cls._gp


class GrandparentTransformer(Comparator):

    def __init__(self, cls):
        self.parent_cls = aliased(cls)

    @property
    def join(self):
        def go(q):
            return q.join(self.parent_alias, Node.parent)
        return go

    def operate(self, op, other):
        return op(self.parent_alias.parent, other)
```

```python
>>> session.query(Node).\
...     with_tranformation(Node.grantdparent.join).\
...     filter(Node.grandparent==Node(id=5))
```

"transfomer"是一个高级特性，只推荐老手程序员使用。

### API

- class`sqlalchemy.ext.hybird.hybird_method(func, expr=None)`

    Base: `sqlalchemy.orm.base.InspectionAttrInfo`

    一个装饰器，可以装饰一个Python方法，让它的类级别使用和实例级别使用都具有各自的行为.

    - `__init__(func, expr=None)`

        创建一个`hybird_method`

        通常使用装饰器语法:

        ```python
        from sqlalchemy.ext.hybird import hybird_method


        class SomeClass(object):
            @hybird_method
            def value(self, x, y):
                return self._value + x + y

            @value.expression
            def value(self, x, y):
                return func.some_function(self._value, x, y)
        ```
    - `expression(expr)`

        提供一个修改装饰器，可以定义生成SQL表达式的方法.


- class`sqlalchemy.ext.hybird.hybird_property(fget, fset=None, fdel=None, expr=None, custom_comparator=None, update_expr=None)`

    Base: `sqlalchemy.orm.base.InsepectionAttrInfo`

    一个装饰器，允许为实例级别和类级别都定义各自行为的描述符。

    - `__init__(fget, fset=None, fdel=None, expre=None, custom_comparator=None, update_expr=None)`

        创建一个新的`hybird_property`

        通常使用装饰器语法:

        ```python
        from sqlalchemy.ext.hybird import hybird_property


        class SomeClass(Base):
            @hybird_property
            def value(self):
                return self._value

            @value.setter
            def value(self, value):
                self._value = value
        ```

    - `comparator(comparator)`

        提供一个修改方法，允许定义一个生成自定义比较符的方法.

        被装饰方法返回的值应该是一个`Comparator`实例。

        > 注意
        >
        > `hybird_property.comparator()`装饰器将会替换`hybird_property.expression()`。所以两者不能一起使用。

        当一个hybird在类级别被调用，给定的`Comparator`对象将会被封装到一个特殊的`QueryableAttribute`,它和ORM用来表示其它映射属性的类型相同。理由是其它类级的属性如`docstring`或者hybird的一个引用将会在维持在一个数据结构中并返回，并不会修改原始传入的比较符。

        > 如果想要在子类中覆盖这个装饰器，请使用`hybird_proeprty.overrides`

    - `deleter(fdel)`

        提供一个修改装饰器，可以用来定义一个删除方法。

    - `expression(expr)`

        提供一个修改装饰器，可以用来定义一个生成SQL表达式的方法.

    - `getter(fget)`

        提供一个修改装饰器，可以用来定义一个getter方法.

    - `overrides`

        装饰一个方法，将它定义为一个存在属性的覆盖方法。

        `hybird_property.overrides`访问器只会返回这个hybird对象。可以在它的基础上面继续使用`expression()`，`comparator()`.

        ```python
        class SuperClass(object):
            # ...
            
            @hybird_property
            def foobar(self):
                return self._foobar


        class SubClass(SuperClass):
            # ...

            @SuperClass.foobar.overrides.expression
            def foobar(self):
                return func.subfoobar(self._foobar)
        ```

    - `setter(fset)`

        提供一个修改装饰器，可以用来定义一个`setter`方法.

    - `update_expression(meth)`

        提供一个修改装饰器，可以定义一个生成UPDATE元祖的方法。

        这个方法接受单个值，这个值将会被用来生成UPDATE语句的SET字句。这个方法应该将这个值处理成独立的列表达式，让它和最终的SET子句相符，并返回一个2-元祖的序列。每个元祖包含一个列表达式作为键，想要生成的SET值作为值.

        比如：

        ```python
        class Person(Base):
            # ...

            first_name = Column(String)
            last_name = Column(String)

            @hybird_property
            def fullname(self):
                return self.first_name + " " + self.last_name

            @fullname.update_expression
            def fullname(cls, value):
                fname, lname = value.split(" ", 1)
                return [
                    (cls.first_name, fname),
                    (cls.last_name, lname)
                ]
        ```

- 类`sqlalchemy.ext.hybird.Comparator(expression)`

    Base: `sqlalchemy.orm.interfaces.PropComparator`

    一个helper类，可以帮助你们在使用hybirds时可以创建一个自定义的`PropComparator`

- `sqlalchemy.ext.hybird.HYBIRD_METHOD` = `symbol('HYBRID_METHOD')`
- `sqlalchemy.ext.hybird.HYBIRD_PROPERTY` = `symbol('HYBIRD_PROPERTY')`

    