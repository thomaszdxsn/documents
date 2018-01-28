## Indexable

通过`Indexable`类型为映射表的列加上索引。

"index"属性关联了一个`Indexable`列元素，它有着预先定义的索引。`Indexable`类型包含的类型包括`ARRAY`, `JSON`, `HSTORE`.

`indexalbe`扩展为元素加入了类似`Column`的接口。可以将它当做一个列－映射属性来看待.

### Synopsis

给定一个`Person`model，它具有一个主键和JSON字段。这个(JSON)字段中可能有很多编码的元素，我们可能想独立访问其中的`name`:

```python
from sqlalchemy import Column, JSON, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.indexable import index_property

Base = declarative_base()


class Person(Base):
    __tablename__ = 'person'

    id = Column(Integer, primary_key=True)
    data = Column(JSON)

    name = index_property('data', 'name')
```

上面例子中，`name`属性可以当做一个列来访问。我们可以创建一个Person实例然后设置`name`的值:

```python
>>> person = Person(name='Alchemist')
```

这个值现在可以被访问：

```python
>>> person.name
'Alchemist'
```

在幕后，JSON字段也会更新:

```python
>>> person.data
{'name': 'Alchemist'}
```

这个字段是可以修改的:

```python
>>> person.name = 'Renamed'
>>> person.name
'Renamed'
>>> person.data
{'name': 'Renamed'}
```

当使用`index_property`之后，我们对这个属性的修改同样会追踪它的来源处；我们不再需要使用`MutableDict`来追踪这个修改。

删除操作也可以：

```python
>>> del person.name
>>> person.data
{}
```

上面代码，删除的只是字典`person.data`中的键，而不是字典本身。

如果键不存在，则会抛出`AttributeError`, **注意这里不是返回None, 否则语义不正确**:

```python
>>> person = Person()
>>> person.name
...
AttributeError: 'name'
```

除非你设置了默认值:

```python
>>> class Person(Base):
>>>     __tablename__ = 'person'
>>>     id = Column(Integer, primary_key=True)
>>>     data = Column(JSON)
>>>     name = index_property('data', 'name', default=None)

>>> person = Person()
>>> person.name
None
```

这个属性同样可以当做类属性来访问，可以生成SQL表达式:

```python
>>> from sqlalchemy.orm import Session
>>> session = Session()
>>> query = session.query(Person).filter(Person.name == 'Alchemist')
```

上面的查询等同于：

```python
>>> query = session.query(Person).filter(Person.data['name'] == 'Alchemist')
```

可变的`index_property`可以链接来生成多级indexing:

```python
from sqlalchemy import Column, JSON, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.indexable import index_property

Base = declarative_base()


class Person(Base):
    __tablename__ = 'person'

    id = COlumn(Integer, primary_key=True)
    data = Column(JSON)

    birthday = indexable('data', 'birthday')
    year = indexable('birthday', 'year')
    month = indexable('birthday', 'month')
    day = indexable('birthday', 'day')
```

使用上面例子的查询如下:

```python
q = session.query(Person).filter(Person.year == '1980')
```

在一个PostgreSQL后端中，上面查询将会渲染成如下SQL:

```python
SELECT person.id, person.data
FROM person
WHERE person.data -> %(data_1)s -> %(param_1)s = %(param_2)s
```

### Default Values

`index_property`在碰到indexed数据结构不存在时会发生特殊的行为，将会进行如下操作:

- 对于一个给定整数index值的`index_property`，默认的数据结构将会为``None`值的列表，长度为index值.即如果你index设为0，那么列表就是`[None]`, 如果index是5，那么列表就是`[None, None, None, None, None]`

- 对于其它任何类型索引值(通常是string)的`index_property`，将会使用Python字典作为默认的数据结构
- 默认的数据结构是可以自定义的，将可调用对象传入到`index_property.datatype`即可

### Subclassing

`index_property`可以被继承，通常用于将一个SQL表达式做类型转换。下面是一个PostgreSQL JSON类型的例子，我们想自动为它使用`astext()`:

```python
class pg_class_property(index_property):
    def __init__(self, attr_name, index, cast_type):
        super(pg_json_property, self).__init__(attr_name, index, cast_type)
        self.cast_type = cast_type

    def expr(self, model):
        expre = super(pg_class_property, self).expr(model)
        return expr.astext.cast(self.cast_type)
```

上面的`index_property`子类可以用于PostgreSQL版本的JSON字段：

```python
from sqlalchemy import Column, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import JSON

Base = declarative_base()


class Person(Base):
    __tablename__ = 'person'

    id = Column(Integer, primary_key=True)
    data = Column(JSON)

    age = pg_class_property('data', 'age', Integer)
```

这个`age`的实例属性和之前一样；不过在渲染SQL时，将会使用PostgreSQL操作符`->>`来进行索引访问，而不是使用之前的`->`:

```python
>>> query = session.query(Person).filter(Person.age < 20)
```

这个查询将会渲染为：

```python
SELECT person.id, person.data
FROM person
WHERE CAST(person.data ->> %(data_1)s AS INTEGER) < %(param_1)%
```

### API

- class`sqlalchemy.ext.indexable.index_property(attr_name, index, default=<object object>, datatype=None, mutable=True, onebased=True)`

    Bases: `sqlalchemy.ext.hybird.hybird_property`

    一个property生成器。生成一个符合`Indexable`列的对象属性.

    - `__init__(attr_name, index, default=<object object>, datatype=None, mutable=True, onebased=True)`

        创建一个新的`index_property`.

        参数:

        - `attr_name`: 一个`Indexable`类型列的属性名，或者一个其它属性但是最终返回indexable结构。

        - `index`: 这个index用来获取和设置这个值

        - `default`: 如果没有默认值，在碰到索引不存在时会抛出`AttributeError`

        - `datatype`: 在字段为空时使用的默认datatype.默认情况下，这个类型应该来源自使用索引的类型。对于列表使用整数索引，对于字典使用hashable索引.
        - `mutable`: 如果设为False，就不可以更改或删除这个属性。
        - `onebased`: 如果设置True，第一个索引是1而不是0。