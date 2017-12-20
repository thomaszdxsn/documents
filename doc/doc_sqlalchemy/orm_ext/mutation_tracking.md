[TOC]

## Mutation Tracking

支持追踪标量值的就地(in-place)修改，它会传播到所属父对象的ORM修改事件中。

### Establishing Mutability on Scalar Column Values

"mutable"的一个典型例子就是Python字典.下面的例子中，我们使用自定义的类型，在持久化前让一个Python字典转换为JSON字符串：

```python
from sqlalchemy.types import TypeDecorator, VARCHAR
import json


class JSONEncodedDict(TypeDecorator):
    """代表一个不可变的JSON编码字符串"""
    
    impl = VARCHAR

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)
        return value
    
    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value
```

上面例子中的对象不可变。`sqlalchemy.ext.mutable`扩展可以用于Python中所有可变类型对象，包括`PickleType`, `postgresql.ARRAY`,等等。。。

当使用`sqlalchemy.ext.mutabla`的时候，这个值本身会追踪所有引用它的父对象。下面例子中，我们介绍一种简单版本的`MutableDict`字典对象，它继承了`Mutable`这个mixin和`dict`类型.

```python
from sqlalchemy.ext.mutable import Mutable


class MutableDict(Mutable, dict):
    
    @classmethod
    def coerce(cls, key, value):
        """讲普通的字典转换为MutableDict"""
        
        if not isinstance(value, MutableDict):
            if isinstance(value, dict):
                return MutableDict(value)
            return Mutable.coerce(key, value)
        else:
            return value

    def __setitem__(self, key, value):
        """检查字典的set事件，并发出改动事件"""

        dict.__setitem__(self, key, value)
        self.changed()

    def __delitem__(self, key, value):
        """检查字典的delete事件，并发出改动事件"""

        dict.__setitem__(self, key, value)
        self.changed()
```

上面的字典例子接受了Python内置`dict`的所有方法，并且通过`__setitem__`监听了所有改动的事件。有些这种方法的变体，比如`UserDict.UserDict`或者`collections.MutableMapping`;这个例子最重要的部分就是在数据接口无论何时发送更改时都调用了`Mutable.changed()`方法。

我们定义的`MutableDict`提供了一个类方法`as_mutable()`，它可以用于列定义时作为类型使用。这个方法收集给定的对象或者类，并将它关联到一个监听器，将会持续追踪这个对象的改动:

```python
from sqlalchemy import Table, Column, Integer

my_data = Table("my_data", metadata, 
    Column('id', Integer, primary_key=True),
    Column(MutableDict.as_mutable(JSONEncodedDict)) 
)
```

上面例子中，`as_mutable`返回一个`JSONEncodedDict`实例(如果这个类型对象还不是实例)，它会拦截针对这个类型的属性映射。下面我们对`my_table`建立一个简单的映射:

```python
from sqlalchemy import mapper


class MyDataClass(object):
    pass


# 关联mutation listeners 和　MyDataClass.data
mapper(MyDataClass, my_data)
```

现在`MyDataClass.data`在发生改动时会接受到通知。

使用declarative时，用法也不变:

```python
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class MyDataClass(Base):
    __tablename__ = 'my_data'
    id = Column(Integer, primary_key=True)
    data = Column(MutableDict.as_mutable(JSONEncodedDict))
```

任何对`MyDataClass.data`的修改都会让父对象的属性标记为"*dirty*".

```python
>>> from sqlalchemy.orm import Session

>>> session = Session()
>>> m1 = MyDataClass(data={"value1": "foo"})
>>> session.add(m1)
>>> session.commit()

>>> m1.data['value1'] = 'bar'
>>> assert m1 in session.dirty:
True
```

通过使用`associate_with()`方法，`MutableDict`可以一次性关联所有的`JSONEncodedDict`实例。这方法和`as_mutable()`类似，除了它不用单独的声明而是拦截所有JSONEncodedDict的实例改动。

```python
MutableDict.associate_with(JSONEncodedDict)


class MyDataClass(Base):
    __tablename__ = 'my_data'
    id = Column(Integer, primary_key=True)
    data = Column(JSONEncodeedDict)
```

#### Supporting Picking

pass