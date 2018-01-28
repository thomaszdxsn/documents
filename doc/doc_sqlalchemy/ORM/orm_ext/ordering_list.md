## Ordering List

一个自定义列表，用于管理包含元素的索引/位置信息。

`orderinglist`是一个mutabled有序关系的助手扩展。它会拦截对一个`relationship()`的列表操作-管理这个集合以及自动同步一个目标标量属性的列表位置改动。

例子：一个`slide`表，每一行引用了一个或多个`bullet`表的内容。slide中的bullet是有序排列的，基于bullet表本身的`position`字段。一个bullet被重新排序后，`position`属性应该作出相应的反射：

```python
Base = declarative_base()


class Slide(Base):
    __tablename__ = 'slide'

    id = Column(Integer, primary_key=True)
    name = Column(String)

    bullets = relationship('Bullet', order_by='Bullet.position')


class Bullet(Base):
    __tablename__ = 'bullet'

    id = Column(Integer, priamry_key=True)
    slide_id = Column(Integer, ForeignKey('slide.id'))
    position = Column(Integer)
    text = Column(String)
```

标准的关系将会在每个`Slide`对象中生成一个类似列表的属性，这个列表中包含和它关联的`Bullet`对象，但是对这个列表的再次排序并不会影响到数据库。当将一个`Bullet`追加到`Slide.bullets`后，`Bullet.position`属性会保持未设置，直到手动对它赋值。当一个`Bullet`插入到列表的中间，其它的`Bullet`对象的position也应该作出相应的变动。

`OrderingList`对象自动完成了这个任务，它会管理集合中所有`Bullet`对象的`position`属性。使用`ordering_list()`这个工厂来构建它(`OrderingList`):

```python
from sqlalcehmy.ext.orderinglist import ordering_list

Base = declarative_base()


class Slide(Base):
    __tablename__ = 'slide'

    id = Column(Integer, primary_key=True)
    name = Column(String)

    bullets = relationship('Bullet', order_by='Bullet.position',
                        collection_class=ordering_list('position'))


class Bullet(Base):
    __tablename__ = 'bullet'

    id = Column(Integer, primary_key=True)
    slide_id = Column(Integer, ForeignKey('slide.id'))
    position = Column(Integer)
    text = Column(String)
```

使用上面的映射，`Bullet.position`可以被自动管理了：

```pythons
>>> s = Slide()
>>> s.bullets.append(Bullet())
>>> s.bullets.append(Bullet())
>>> s.bullets[1].position
1
>>> s.bullets.insert(1, Bullet())
>>> s.bullets[2].position
2
```

`OrderingList`对象只有在一个集合变动时才会有用，并且不需要从数据库初始化相关数据，但是要求列表在被读取时就已经排好序了。所以，**请确保对`relationship()`设定了`order_by`**.

>　警告
>
>> `OrderingList`不能作用于带主键，unique约束的列

`ordering_list`关联对象排序属性的名称作为参数。默认情况下，将会使用以０开始的索引和排序属性保持同步：索引 0对应position 0...如果想要以０获取其它整数开始，请传入参数`count_from`，比如`ordering_list('order_attr', count_from=1)`.

### API Reference

- `sqlalchemy.ext.orderinglist.ordering_list(attr, count_from=None, **kw)`

    `OrderingList`的工厂。

    返回一个对象，可以适用于`Mapper`关系的`collection_class`选项:

    ```python
    from sqlalchemy.ext.orderinglist import ordering_list


    class Slide(Base):
        __tablename__ = 'slide'

        id = Column(Integer, primary_key=True)
        name = Column(String)

        bullets = relationship('Bullet', order_by='Bullet.position',
                            collection_class=ordering_list('position'))
    ```

    参数：

    - `attr`: 一个映射属性的名称，用来存储和取回排序信息.
    - `count_from`: 设置一个整数排序，从`count_from`开始。

    额外的关键字参数都会传入到`OrderingList`构造器中.

- `sqlalchemy.ext.orderinglist.count_from_0(index, collection)`

    一个Numbering函数：从０开始的连续整数

- `sqlalchemy.ext.orderinglist.count_from_1(index, collection)`

    一个Numbering函数：从１开始的连续整数

- `sqlalchemy.ext.orderinglist.count_from_n_factory(start)`

    Numbering函数：从任意数字开始的连续整数

- class`sqlalchemy.ext.orderinglist.OrderingList(ordering_attr=None, ordering_func=None, reorder_on_append=False)`

    基类: `__bultin__.list`

    一个自定义的list,可以管理其中成员的位置信息.

    `OrderingList`对象通常通过`ordering_list()`函数来生成，和`relationship()`函数组合使用.

    - `__init__(ordering_attr=None, ordering_func=None, reorder_on_append=False)`

        `OrderingList`是`collection_class`的一个列表实现，可以在一个Python列表和映射对象之间进行位置信息映射同步.
        
        实现需要依赖于列表在载入后就保持排序状态，所以需要**确保**在关系中加入`order_by`参数.

        参数：

        - `ordering_attr`: 对象存储排序信息的属性.
        - `ordering_func`

            可选。一个映射Python列表和ordering_attr属性的函数。通常应该返回一个整数值。

            `ordering_func`在被调用时传入两个位置参数：元素在列表中索引和列表本身。

        - `reorder_on_append`

            默认为False.当对一个存在的排序列表追加对象的时候，如果这个参数设为True，那么会重新排序。

            推荐讲这个值设为False.如果你对一个已经排序的实例进行`append()`操作，或者做了一些手动的ＳＱＬ插入后，才应该手动调用`reorder()`

    - `append(entity)`

        讲一个对象追加到尾部.

    - `insert(index, entity)`

        讲一个对象插入到index之前.

    - `pop([index])`

        移除一个索引(默认为最后一个)的元素，并将它返回。

        如果列表为空，将会抛出`IndexError`错误.

    - `remove(entity)`

        移除第一个发现的元素。如果没有发现该元素，抛出`ValueError`错误.

    - `reorder()`

        讲整个集合重新排序。

        