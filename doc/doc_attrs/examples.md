# attrs by Example

## Basics

最简单的用法

```python
>>> import attr
>>> @attr.s
... class Empty(object):
...     pass
>>> Empty()
Empty()
>>> Empty() == Empty()
True
>>> Empty() is Empty()
False
```

换取话说，即使没有属性，`attrs`也是有用的。

但是你通常需要在类中加入一些数据:

```python
>>> @attr.s
... class Coordinates(object):
...     x = attr.ib()
...     y = attr.ib()
```

默认情况下，会为你加入所有的特性，所以你可以立即地创建一个完整功能的数据类，
并且具有良好的`repr`string和比较方法：

```python
>>> c1 = Coordinates(1, 2)
>>> c1
Coordinates(x=1, y=2)
>>> c2 = Coordinates(x=2, y=1)
>>> c2
Coordinates(x=2, y=1)
>>> c1 == c2
False
```

就像我们展示地一样，生成的`__init__`方法可以允许位置参数和关键字参数。

如果玩笑式的命名让你不爽，`attrs`也有严肃版的API命名:

```python
>>> from attr import attrs, attrib
>>> @attrs
... class SeriousCoordinates(object):
...     x = attrlib()
...     y = attrlib()
>>> SeriousCoordinates(1, 2)
SeriousCoordinates(x=1, y=2)
>>> attr.fields(Coordinates) == attr.fields(SeriousCoordinates)
True
```

对于隐私属性，`attrs`将会在关键字参数中为你去掉开头的下划线:

```python
>>> @attr.s
... class C(object):
...     _x = attr.ib()
... C(x=1)
C(_x=1)
```

如果你想要自己来初始化隐私属性:

```python
>>> @attr.s
>>> class C(object):
...     _x = attr.lib(init=False, default=42)
>>> C()
C(_x=42)
>>> C(23)
Traceback (most recent call last):
   ...
TypeError: __init__() takes exactly 1 argument (2 given)
```

另外还有一些方式可以用来定义属性。

```python
>>> class SomethingFromSomeoneElse(object):
...     def __init__(self, x):
...         self.x = x
>>> SomethingFromSomeoneElse = attr.s(
...     these={
...         'x': attr.ib()
...     }, init=False)(SomethingFromSomeoneElse)
>>> SomethingFromSomeoneElse(x=1)
)
```

继承不太好，但是`attrs`也可以处理:

```python
>>> @attr.s
... class A(object):
...     a = attr.ib()
...     def get_a(self):
...         return self.a
>>> @attr.s
... class B(object):
...     b = attr.ib()
>>> @attr.s
... class C(A, B):
...     c = attr.ib()
>>> i = C(1, 2, 3)
>>> i
C(a=1, b=2, c=3)
>>> i == C(1, 2, 3)
True
>>> i.get_a()
1
```

属性的顺序有`MRO`(method resolve order)来决定.

在Python3，在其它类中的类会被探测，并且在`__repr__`中映射出来。在Python2中不可以。

因此`@attr.s`有一个`repr_ns`选项，可以手动设置:

```
>>> @attr.s
... class C(object):
...     @attr.s(repr_ns='C')
...     class D(object):
...         pass
>>> C.D()
C.D()
```

## Converting to Collections Types

在你拥有一个具有数据的类的时候，你通常希望把它转换为dict。

```python
>>> attr.asdict(Coordinates(x=1, y=2))
{'x': 1, 'y': 2}
```

有些字段不能被转换。因此，`attr.asdict()`提供给你一个callback，让你来决定那些
属性应该包含在内:

```python
>>> @attr.s
... class UserList(object):
...     user = attr.ib()
>>> @attr.s
... class User(object):
...     email = attr.ib()
...     password = attr.ib()
>>> attr.asdict(UserList([User('jane@doe.invalid', 's33kred'),
...                       User('joe@doe.invalid', 'p4ssw0rd')]),
...             filter=lambda attr, value: attr.name != 'password')
{'users': [{'email': 'jane@doe.invalid'}, {'email': 'joe@doe.invalid'}]}
```

有时你想要使用include，有时你想要使用exclude:

```python
>>> @attr.s
... class User(object):
...     login = attr.ib()
...     password = attr.ib()
...     id = attr.ib()
>>> attr.asdict(
...     User('jane', 's33kred', 42),
...     filter=attr.filters.exclude(attr.fields(User).password, int))
{'login': 'jane'}
>>> @attr.s
... class C(object):
...     x = attr.ib()
...     y = attr.ib()
...     z = attr.ib()
>>> attr.asdict(C("foo", "2", 3),
...             filter=attr.filters.include(int, attr.fields(C).x))
{'x': 'foo', 'z': 3}
```

有时，你想要元祖，`attrs`不会让你失望的:

```python
>>> import sqlite3
>>> import attr
>>> @attr.s
... class Foo:
...    a = attr.ib()
...    b = attr.ib()
>>> foo = Foo(2, 3)
>>> with sqlite3.connect(":memory:") as conn:
...    c = conn.cursor()
...    c.execute("CREATE TABLE foo (x INTEGER PRIMARY KEY ASC, y)") 
...    c.execute("INSERT INTO foo VALUES (?, ?)", attr.astuple(foo)) 
...    foo2 = Foo(*c.execute("SELECT x, y FROM foo").fetchone())
<sqlite3.Cursor object at ...>
<sqlite3.Cursor object at ...>
>>> foo == foo2
True
```

## Defaults

有时你想要为你的初始化器加入一些默认值。

有时你想使用可变对象作为默认值。

```python
>>> import collections
>>> @attr.s
... class Connection(object):
...     socket = attr.ib()
...     @classmethod
...     def connect(cls, db_string):
...         # ...
...         return cls(socket=42)
>>> @attr.s
... class ConnectionPool(object):
...     db_string = attr.ib()
...     pool = attr.ib(default=attr.Factory(collections.deque))
...     debug = attr.ib(default=False)
...     def get_connection(self):
...         try:
...             return self.pool.pop()
...         except IndexError:
...             if self.debug:
...                 print("New connection!")
...             return Connection.connect(self.db_string)
...     def free_connection(self, conn):
...         if self.debug:
...             print("Connection returned!")
...         self.pool.appendleft(conn)
...
>>> cp = ConnectionPool("postgres://localhost")
>>> cp
ConnectionPool(db_string='postgres://localhost', pool=deque([]), debug=False)
>>> conn = cp.get_connection()
>>> conn
Connection(socket=42)
>>> cp.free_connection(conn)
>>> cp
ConnectionPool(db_string='postgres://localhost', pool=deque([Connection(socket=42)]), debug=False)
```

default的factory还可以使用装饰器的方式来声明.

```python
>>> @attr.s
... class C(object):
...     x = attr.ib(default=1)
...     y = attr.ib()
...     @y.default
...     def name_does_not_matter(self):
...         return self.x + 1
>>> C()
C(x=1, y=2)
```

## Validators

虽然你的初始化器应该尽可能做少量的事情(理性情况下，应该只根据给定的参数来为你
初始化实例)，还可以选择用它来进行参数的验证。

`attrs`有两种方式可以定义validatos.

### Decorator

这是定义属性`validator`最直接的方式。这个方法接受三个参数:

1. 实例本身
2. 要验证的属性
3. 传入的值

```python
>>> @attr.s
... class C(object):
...     x = attr.ib()
...     @x.validator
...     def check(self.attribute, value):
...         if value > 42:
...             raise ValueError('x must be smaller or equal to 42')
>>> C(42)
C(x=42)
>>> C(43)
Traceback (most recent call last):
   ...
ValueError: x must be smaller or equal to 42
```

### Callable

如果你想要重用你的validatos，你可以对`attr.ib()`传入`validator`参数.

这个参数接受单个callble，或者callble lists。

因为validators会在实例化以后被运行，你可以在这个时候引用其它属性.

```python
>>> def x_smaller_than_y(instance, attribute, value):
...     if value >= instance.y:
...         raise ValueError("'x' has to be smaller than 'y'!")
>>> @attr.s
... class C(object):
...     x = attr.ib(validator=[attr.validators.instance_of(int),
...                            x_smaller_than_y])
...     y = attr.ib()
>>> C(x=3, y=4)
C(x=3, y=4)
>>> C(x=4, y=3)
Traceback (most recent call last):
   ...
ValueError: 'x' has to be smaller than 'y'!
```

这个例子其实是`attr.validators.and_()`的语法糖：你传入一个list，所有的validators
都必须通过。

`attrs`不会监听你对属性地改动，但是你可以调用`attr.validate()`来进行手动验证:

```python
>>> i = C(4, 5)
>>> i.x = 5
>>> attr.validate(i)
Traceback (most recent call last):
   ...
ValueError: 'x' has to be smaller than 'y'!
```

`attrs`内置了一堆validators:

```python
>>> @attr.s
... class C(object):
...     x = attr.ib(validator=attr.validators.instance_of(int))
... C(42)
C(x=42)
>>> C('42')
Traceback (most recent call last):
   ...
TypeError: ("'x' must be <type 'int'> (got '42' that is a <type 'str'>).", Attribute(name='x', default=NOTHING, factory=NOTHING, validator=<instance_of validator for type <type 'int'>>, type=None), <type 'int'>, '42')
```

当然，你可以混合使用，怎么方便就那样:

```python
>>> @attr.s
... class C(object):
...     x = attr.ib(validator=attr.validators.instance_of(int))
...     @x.validator
...     def fits_byte(self, attribute, value):
...         if not 0 < value < 256:
...             raise ValueError("value out of bounds")
>>> C(128)
C(x=128)
>>> C('128')
Traceback (most recent call last):
   ...
TypeError: ("'x' must be <class 'int'> (got '128' that is a <class 'str'>).", Attribute(name='x', default=NOTHING, validator=[<instance_of validator for type <class 'int'>>, <function fits_byte at 0x10fd7a0d0>], repr=True, cmp=True, hash=True, init=True, metadata=mappingproxy({}), type=None, converter=one), <class 'int'>, '128')
>>> C(256)
Traceback (most recent call last):
   ...
ValueError: value out of bounds
```

最后，你可以全局禁用validators.

```python
>>> attr.set_run_validators(False)
>>> C("128")
C(x='128')
>>> attr.set_run_validators(True)
>>> C("128")
Traceback (most recent call last):
   ...
TypeError: ("'x' must be <class 'int'> (got '128' that is a <class 'str'>).", Attribute(name='x', default=NOTHING, validator=[<instance_of validator for type <class 'int'>>, <function fits_byte at 0x10fd7a0d0>], repr=True, cmp=True, hash=True, init=True, metadata=mappingproxy({}), type=None, converter=None), <class 'int'>, '128')
```

## Conversion

属性可以指定`converter`函数。

```python
>>> @attr.s
... class C(object):
...     x = attr.ib(converter=int)
>>> o = C('1')
>>> o.x
1
```

Converter会在validator之前运行，所以你可以validators来检查最终的值:

```python
>>> def validate_x(instance, attribute, value):
...     if value < 0:
...         raise ValueError('x must be be at least 0.')
>>> @attr.s
... class C(object):
...     x = attr.ib(converter=int, validator=validate_x)
>>> o = C('0')
>>> o.x
0
>>> C('-1')
Traceback (most recent call last):
    ...
ValueError: x must be be at least 0.
```

## Metadata

所有的`attrs`属性都可以包含任意数量的metadata，它们都存储在一个只读字典内:

```python
>>> @attr.s
... class C(object):
...     x = attr.ib(metadata={"my_metadata": 1})
>>> attr.fields(C).x.metadata
mappingproxy({"my_metadata": 1})
>>> attr.fields(C).x.metadata['my_metadata']
1
```

## Types

`attrs`允许你将属性关联一个类型，可以使用PEP526的类型注解：

```python
>>> @attr.s
... class C:
...     x = attr.ib(type=int)
...     y: int = attr.ib()
>>> attr.fields(C).x.type
<class 'int'>
>>> attr.fields(C).y.type
<class 'int'>
```

## Slots

默认情况下，类的实例都有一个字典来作为属性的存储体。如果数据量很少的话，这会
浪费内存。如果创建过多实例的话，内存的浪费是很惊人的。

Python类可以通过定义`__slots__`来避免使用一个单独的字典。对于`attrs`类，需要
设置`slots=True`:

```python
>>> @attr.s(slots=True)
... class Coordinates(object):
...     x = attr.ib()
...     y = attr.ib()
```

slot类和普通类有些区别。

- 如果对实例一个不存在的属性赋值，将会抛出`AttributeError`.

- 非slot类在创建以后不能转换为slot类。

- 对slot类使用`pickle`要求Pickle 2以上的协议。

- 对于slot类，如果你想要使用weak-reference，你必须实现`__weakref__` slot.

## Immutablity

有时你想要让实例是实例化以后不要修改。

不可变性在函数式编程中很常见，它也确实是一个好东西。

```python
>>> @attr.s(frozen=True)
... class C(object):
...     x = attr.ib()
>>> i = C(1)
>>> i.x = 2
Traceback (most recent call last):
   ...
attr.exceptions.FrozenInstanceError: can't set attribute
>>> i.x
1
```

你需要明白在Python中实现我完全的不可变是不可能的，但是你也能达到99%的不可变性。

不可变类应该用于长时间存活的对象，它们永远不应该修改；就像配置一样。

为了使用常规的程序流，你需要一种方式来通过修改的属性创建新的实例。在Clojure中这
种函数叫做`assoc`，`attrs`无耻地模仿了它`attr.evolve()`:

```python
>>> @attr.s(frozen=True)
... class C(object):
...     x = attr.ib()
...     y = attr.ib()
>>> i1 = C(1, 2)
>>> i1
C(x=1, y=2)
>>> i2 = attr.evolve(i1, y=3)
>>> i2
C(x=1, y=3)
>>> i1 == i2
False
```

## Other Goodies

有时你想要通过程序式的方式来创建类。`attrs`通过`attr.make_class()`帮助你实现：

```python
>>> @attr.s
... class C1(object):
...     x = attr.ib()
...     y = attr.ib()
>>> C2 = attr.make_class('C2', ['x', 'y'])
>>> attr.fields(C1) == attr.fields(C2)
True
```

如果你通过字典传入属性，可以更加细粒度地控制属性.

```python
>>> C = attr.make_class('C', {'x': attr.ib(default=42), 
...                           'y': attr.ib(default=attr.Factory(list)},
...                     repr=False)
>>> i = C()
>>> i
<__main__.C object at ...>
>>> i.x
42
>>> i.y
[]
```

如果你需要通过`attr.make_class()`动态的创建类，那么你需要继承一些除了`object`以外的
东西，然后传入`base`参数.

```python
>>> class D(object):
...     def __eq__(self, other):
...         return True
>>> C = attr.make_class('C', {}, bases=(D,), cmp=False)
>>> isinstance(C(), D)
```

有时，你想要让你的类的`__init__`方法除了初始化以外另外做一些事情。你可以在你的
类中定义`__attrs_post_init__`方法。它会在`__init__`方法的结尾被调用(钩子).

```python
>>> @attr.s
... class C(object):
...     x = attr.ib()
...     y = attr.ib()
...     z = attr.ib(init=False)
...
...     def __attrs_post_init__(self):
...         self.z = self.x + self.y
>>> obj = C(x=1, y=2)
>>> obj
C(x=1, y=2, z=3)
```

最后，你可以为每个特定的方法排除某个属性:

```python
>>> @attr.s
... class C(object):
...     user = attr.ib()
...     password = attrib(repr=False)
>>> C('me', 's3kr3t')
C(user='me')
```
