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

