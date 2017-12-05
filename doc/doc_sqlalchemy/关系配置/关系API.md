[TOC]

## relationships API

```python
sqlalchemy.orm.relationship(argument, secondary=None, primaryjoin=None, secondaryjoin=None,
foreign_keys=None, uselist=None, order_by=False, backref=None, back_populates=None, post_update=False,
cascade=False, extension=None, viewonly=False, lazy='select', collection_class=None, passive_deletes=False,
passive_updates=True, remote_side=None, enable_typechecks=True, join_depth=None, comparator_factory=None,
single_parent=False, innerjoin=False, distinct_target_key=None, doc=None, active_hisory=False,
cascade_backrefs=True, load_on_pending=False, back_quires=True, _local_remote_pairs=None,
query_class=None, info=None)
```

为两个映射类提供一个关系．

符合父－子关联性表关系．这个构造类是一个`RelationshipProperty`的实例．

在经典映射中`relationship()`的一般用法：

```python
mapper(Parent, properties={
    "children": relationship(Child)
})
```

`relationship()`接受的一些参数可以选择传入可调用对象，这个传入的参数可以被调用来生成最终值．调用时间在`Mapper`的"映射初始化"时间，只有当映射首次使用时发生，并且假定所有映射构建完成．这可以用来解决声明顺序和其它依赖性问题，比如下面的例子：

```python
mapper(Parent, properties={{
    "children": relationship(lambda: Child,
                            order_by=lambda: Child.id)
})
```

当使用声明扩展时，声明初始器允许在`relationship()`中传入字符串参数．这些字符串参数可以转换为可调用对象，使用生命类－注册器作为命名空间．可以通过字符串名称查询相关的类，但是需要在模块中引入这些类：

```python
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Parent(Base):
    __tablename__ = 'parent'
    id = Column(Integer, primary_key=True)
    chidlren = relationship("Child", order_by='Child.id'
```

参数：

- `argument`

    一个映射类，或者Mapper实，表单想要建立关系的目标．

    `argument`可以传入可调用对象，在映射初始化的时候将会把它调用，也可以传入字符串名称，declartive内部代码会把它当作eval字符串．

- `secondary`

    对于多对多关系，指定一个中间表，一般是一个Table实例．在一些很少见的情况下，这个参数可以指定一个`Alias`对象，甚至一个`Join`对象．

    `secondary`也可以传入一个可调用对象，在映射初始化时间将它调用．当使用Declarative时，也可以传入一个字符串参数，这个字符串提到`Table`传先在`Metadata`集合中的名称．

    `secondary`关键字参数一般应用场景在中间表`Table`不是其它类映射的情况．如果"secondary"表显式映射其它东西，考虑使用`viewonly`参数，所以这个`relationship()`不可以进行持久化操作否则会和其它的关联对象模式相冲突．

- `active_history=False`

    当设置为`True`时，指明在多对一引用的替换中，将会读取之前的值(如果没有读取).通常来说，简单多对一history追踪的逻辑只需要在新值刷新时注意一下．

    这个值设置为True后，属性之前的值可以通过`attributes.get_history()`来获得．

- `bakcref`

    指明在关系另一侧中访问关系的属性名．在映射配置好后，其它的属性应当自动创建．也可以传入一个`backref()`对象，来更加细粒度的控制关系的另一端．

- `back_populates`

    接受一个字符串名称，用途和`backref`类似，除了另一侧的关系属性不会自动创建，在另一个映射中必须显式配置，必须同样使用`back_populates`来确保功能正常．

- `bake_queries=True`

    使用`BakeQuery`来缓存惰性加载的SQL。默认为True，如果join条件有一些不常见的特性，不需要缓存的功能，那么可以设置为False。

- `cascade`

    一个逗号分割的字符串，包含一些级联规则，它们让Session决定使用哪种级联策略。默认为False，以为着使用默认的级联规则 - `save-updates, merge`.

    可用的级联规则包括`save-update`, `merge`, `expunge`, `delete`, `delete-orphan`以及`refresh-expire`.还有一个额外的选项，`all`代表`save-update, merge, refresh-expire, expunge, delete`的一个快捷方式，并且有种习惯的用法，使用`all, delete-orphan`来指示关联对象应该完全依靠父对象，并且在解除关联时被删除。

- `cascade_backrefs=True`

    一个布尔值，指明如果有级联`save-update`，应该在反式引用的操作中包含一个赋值拦截事件。

- `collection_class`

    一个类，或者一个可调用对象。它返回一个新的容器对象，用来存储关系集合数据。

- `comparator_factory`

    一个继承自`RelationshipProperty.Comparator`的类，它提供生成自定义操作符比较的SQL子句。

- `distinct_target_key=None`

    指明如果一个“子查询”的贪婪加载，应该对最里面的SELECT使用DISTINCT关键字。当设置为None时(默认值)，在目标列不是目标表的完整主键(即联合主键也不作数)时使用DISTINCT关键字。当设置为True时，DISTINCT关键字无条件应用于最里层的SELECT。

- `doc`

    文档字符串，应用于结果描述符。

- `extension`

    一个`AttributeExtension`实例，或者一组extension列表，它们会添加到属性监听器列表的前面。

- `foreign_keys`

    一个Column实例的列表，它们用来当作外键，或者一个列引用了remote列的值，应用于这个`relationship()`的`primaryjoin`条件。也就是说，如果这个`relationship()`的`primaryjoin`条件是`a.id == b.a_id`，并且`b.a_id`的值要求出现在`a.id`，那么`relationship()`中的`foreign_keys`应该设置为`b.a_id`.

    在平常的情况下，这个`foreign_key`参数不是必须的。`relationship()`在考虑`primaryjoin`条件时会根据标明为`ForeignKey`的`Column`自动决定哪个列为外键，或者根据结构`ForeignKeyConstraint`来决定。这个参数只在如下情况下被需要：

    1. 有多于一种方法来join当前表和远方表，以及提供了多个外键引用。设置`foreign_keys`将会限制`relationship()`考虑使用制定的列作为外键。

        > 多外键的join含糊问题可以通过使用`foreign_keys`参数独立解决，无需显式设置`primaryjoin`了。

    2. `Table`映射可能没有`ForeignKey`或者`ForeignKeyConstraint`结构，因为从一个数据库反式映射的Table可能并不支持外键反射。

    3. `primaryjoin`参数用来构建一个非标准的join条件，它的表达式中没有像一般情况那样引用它的父列，比如使用SQL函数作复杂比较的一个join条件表达式。

    当出现条件模糊的情况时，`relationship()`将会抛出错误信息，并且建议使用`foreign_keys`参数。在多数情况下，如果`relationship()`并不抛出任何异常，`foreign_keys`参数通常也不需要。

    `foreign_keys`参数可以传入一个可调用对象或者Python的`eval`字符串，只要最终返回的值是所期待的类型就行。

    > `foreign()` - 允许使用`exec`字符串的形式直接在`primaryjoin`条件汇总注解外键列。

- `info`

    可选的数据字典，最后会构成`MapperProperty.info`属性。

- `innerjoin=False`

    当设置为`True`时，贪婪加载的join将会选择使用inner join而不是outer join。这个选项的作用通常是因为性能，因为inner join的性能通常优于outer join。

    当一个多对一关系中使用的外键`nullable=False`时，可以把这个flag设置为True，或者一个一对一关系的引用中，保证至少有一个关联对象的时候也可以设置。

    这个选项支持类似`joinedload.innerjoin`的"nested"和"unnested"选项。

- `join_depth`

    当值不为None时，传入一个整数值来指明**对于一个自引用或循环关系**中最深等级的join。

- `lazy='select'`

    指定相关联对象应该如何被读取。默认值为`select`，可选的值为：

    - `select` - 关联对象应该在属性首次被访问时惰性加载，使用一个独立的SELECT语句，或者使用标识图来直接获取简单的多对一引用。
    - `immediate` - 关联对象在父对象读取时一并读取，使用一个独立的SELECT语句，或者使用标识图来直接获取简单的多对一引用。
    - `joined` - 关联对象在读取父对象时使用“贪婪”读取在一个query里面读取，使用`JOIN`(`LEFT OUT JOIN`).关于join的类型取决于`innerjoin`参数。
    - `subquery` - 关联对象在读取父对象时“贪婪”读取，使用一个额外的SQL语句，对于每个集合请求，对子查询和原始声明之间加一个JOIN。
    - `selectin` - 关联对象在读取父对象时“贪婪”读取，使用一个或多个额外的SQL语句，对父对象使用一个JOIN，并且通过IN子句来指定主键标识。
    - `noload` - 在任何时候都不读取。这个参数值支持“只写”属性，或者一些具有独特风格的属性值。
    - `raise` - 禁用惰性读取；如果值没有经过贪婪读取，访问这个属性时，将会抛出一个`InvalidRequestError`。
    - `raise_on_sql` - “惰性加载发出SQL”被禁用；如果值没有经过贪婪读取，访问这个属性时，将会抛出一个`InvalidRequestError`。
    - `dynamic` - 这个属性将会返回一个预先设置的`Query`对象，并支持所有读取操作；用来作更进一步的筛选。
    - `True` - 和`select`同义
    - `False` - 和`joined`同义
    - `None` - 和`noload`同义

- `load_on_pendging=False`

    指明短暂或待定父对象的读取行为。

    当设置为True时，引起“惰性读取器”将会对父对象发出一个查询，确定它没有被持久化，意味着它不会被刷新。这将禁用待定对象的自动刷新，或者不存在于待定集合中待时在`Session`中处于“attached”状态的短暂对象。

    `load_on_pending`标识在ORM的正常使用情况下没什么用。对象引用应该在对象层面构造，而不是外键层面，所以在刷新前它不应该出现。这个标识并不是用于一般用途。

- `order_by`

    指出读取的关联对象应该使用的排序。`order_by`应该是关联目标映射中的一个Column对象。

    `order_by`也可以传入一个可调用对象，或者Python的eval字符串。

- `passive_deletes=False`

    指明在delete操作时的读取行为。

    设置为True时，指明在对父对象进行删除操作时不读取子对象。一半来说，当一个父对象被删除后，引用它的所有子对象都应该被删除，或者把外键引用设置为NULL。设置这个值为True，一般也暗含使用了`ON DELETE <CASCADE|SET NULL>`规则，可以在数据库端设置级联删除／更新。

    另外，设置这个参数为字符串值`all`，当父对象没有设置delete或delete-orphan级联规则时，也会禁用对子对象外键的"nulling out"操作。

- `passive_updates=True`

    指明
