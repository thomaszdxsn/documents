[TOC]


## mapper()函数

```
sqlalchemy.orm.mapper(class_, local_table=None, properties=None, primary_key=None, non_primary=False, inherits=None,
inherit_condition=None, inherit_foreign_keys=None, extension=None, order_by=False, always_refresh=False, version_id_col=None, version_id_generator=None, polymorphic_on=None,
_polymorphic_map=None, polymorphic_identity=None, concrete=False, with_polymorphic=None, polymorphic_load=None, allow_partial_pks=True,
batch=True, column_prefix=None, include_properties=None, exclude_properties=None, passive_updates=True,
passive_deletes=False, confirm_deleted_rows=True, eager_defaults=False, legacy_is_orphan=False, _compiled_cache_size=100)
```

返回一个新的`Mapper`对象.

这个函数一般在声明拓展(Declarative extension)的幕后使用，当使用声明式映射，一般的`mapper()`参数会通过声明扩展自己处理生成，包括`class_`, `local_table`, `properties`和`inherits`.其它的一些选项会通过类属性`__mapper_args__`传递给`mapper()`:

```python
class MyClass(Base):
    __tablename__ = 'my_table'
    id = Column(Integer, primary_key=True)
    type = Column(String(50))
    alt = Column("some_alt", Integer)

    __mapper_args__ = {
        "plymorphic_on": type
    }
```

显示调用`mapper`一般用于经典映射．上面的声明例子等同于下面的经典形态：

```python
my_table = Table('my_table', metadata,
                Column('id', Interger, primary_key=True)
                Column('type', String(50)),
                Column('some_alt', Integer)
)


class MyClass(object):
    pass


mapper(MyClass, my_table,
     polymorphic_on=my_table.c.type,
     properties={
         "alt": my_table.c.some_alt
     })
```

### 参数

- `class_`

    并映射的这个类．当使用声明式映射，会自动将声明类传入到这个参数．
- `local_table`

    `Table`或其它可选择(selectable)对象．如果这个映射是通过单表继承的话这个值可能为None．当使用声明映射时，这个参数会自动传入，基于`__table__`参数的配置或通过列和`__tablename__`生成的表．

- `always_refresh`

    如果为True，所有对于这个映射类的查询操作都会session中一存在的对象实例数据．不推荐使用这个标识，作为替代解决方法，可以考虑`Query.populate_existing()`.

-  `always_partial_pks`

    默认为True.指明混合主键包含一些NULL值也可以考虑存在于数据库中．这将影响到是否一个映射将会把一个传入的列赋予一个已经存在的实体，以及如果`Session.merge()`将会检查数据库首个特定的主键．

-  `batch`

    默认为True，指明一些多个实体的操作可以批量操作，用来提高效率．设置为False，表示一个实例必须完全保存后才能保存下一个实例．后面一种情况用于极少的情景，如`MapperEvents`监听需要在每个单独行持久化操作之间调用．

- `column_prefix`

    一个字符串，可以作为列名的前缀．不影响显示制定的列属性．

- `concrete`

    如果为True，这个映射将会对它的父映射采取`concret表继承`

- `confirm_deleted_rows`

    默认为True；当一个DELETE语句出现在多行，将会出现一个警告．

- `eager_defaults`

    如果为True,ORM将会在`INSERT`或`UPDATE`后立即取回服务器端生成的默认值，而不是把它们当作过期值直到下次访问时才能获取．

- `exclude_properties`

    一个字符串列表或集合，包含映射时应该排除在外的列名．

- `extension`

    一个`MapperExtension`实例或一组`MapperExtension`实例列表，可以应用于这个映射的所有操作．（已经被弃用，请看`MapperEvents`）.

- `include_properties`

    一个需要映射的列名集合，列表．

- `inherits`

    一个映射类，即应该被继承的映射类．

- `inherit_condition`

    对于联接表继承，一个SQL表达式定义两表如何被join;默认为`natural join`.

- `inherit_foreign_keys`

    当使用`inherit_condition`并且列缺少一个外键设置，这个参数可以设置用来指明哪个列作为外键．大多数时候把这个参数保持为`None`就行了．

- `legacy_is_orphan`

    布尔值，默认为False.

- `non_primary`

    表明这个映射排除为主映射．就是不是用来持久化的映射．这个创建映射的方法表示这是一个专门映射，作为替代选择．

- `order_by`

    一个单独列或者一个列list，作为实体的默认排序．默认情况下没有预先定义的排序．

    > 弃用
    >> 这个参数已经被弃用，请通过`Query.order_by()`来决定如何对结果集排序．

- `passive_deletes`

    当一个链接表继承实体被删除时，将会对外键列作删除操作．对基础映射默认为False；对于继承映射，默认为False，除非在超类映射设置为True.

    当为True时，将定在超类表中设置了`ON DELETE CASCADE`，即当单元工作(unit of work)试图删除一个实体时会把外键同时删除．

- `passive updates`

    当一个链接表继承映射主键列改变时将会有`UPDATE`操作，默认为True.

- `polymorphic_load`

    制定＂多态载入＂的行为：

    －`inline`: 指出这个类应该是**with_polymorphic**映射的一部分．即它的列应该包含在基类的`SELECT`查询中．

    －`selectin`: 指出当这个类的实例被载入后，将会发出一个额外的`SELECT`来取回子类中指定的列，这个`SELECT`使用`IN`来一次性取回多个子类．

- `polymophic_on`

    指定列，属性或者SQL表达式用来决定传入行的目标列：

    ```python
    class Employee(Base):
        __tablename__ = 'employee'

        id = Column(Integer, primary_key=True)
        discriminator = Column(String(50))

        __mapper_args = {
            "polymorphic_on": discriminator,
            "polymorphic_identity": "empolyee"
        }
    ```

    同样可以指定为一个SQL表达式，下面这个例子使用`case()`来构建一个条件判断的方式：

    ```python
    class Employee(Base):
        __tablename__ = 'employee'

        id = Column(Integer, primary_key=True)
        discriminator = Column(String(50))

        __mapper_args__ = {
            "polymorphic_on": case([
                (discriminator == 'EN', 'engineer'),
                (discriminator == "MA", "manager")
            ], else_="employee"),
            "polymorhpic_identity": "employee"
        }
    ```

    同样可以引用`column_property()`中的属性，或者它们之中一个的字符串名称：

    ```python
    class Employee(Base):
        __tablename__ = "employee"

        id  = Column(Integer, primary_key=True)
        discriminator = Column(String(50))
        employee_type = column_property(
         case([
                (discriminator == 'EN', 'engineer'),
                (discriminator == "MA", "manager")
            ], else_="employee"
        )

        __mapper_args__ = {
            "polymorphic_on": employee_type,
            "polymorphic_identity": "employee"
        }
    ```

- `polymorphic_identity`

- `properties`

- `primary_key`

- `version_id_col`

- `version_id_generator`

- `with_polymorphic`

## 其它函数

- `sqlalchemy.orm.object_mapper(instance)`

    给定一个对象，返回一个关联该对象的主映射．

    如果没有配置映射，将会抛出一个`sqlalchemy.orm.exc.UnmappedInstanceError`

    这个函数可以通过inspection系统来获取：

    `inspect(instance).mapper`

    使用inspection系统时，发现如果实例没有匹配的映射同样也会抛出一个`sqlalchemy.exc.NoInspectionAvailable`异常．

- `sqlalchemy.orm.class_mapper(class_, configure=True)`

    给定一个类，返回一个关联该类的主映射．

    如果给定的类没有配置相关映射，将会抛出一个`UnmappedClassError`

    相同的功能，可以通过`inspect()`函数来获得：

    `inspect(some_mapped_class)`

    如果没有类映射，将会抛出一个`sqlalchemy.exc.NoInspectionAvailable`

- `sqlalchemy.orm.configure_mappers()`

    初始化所有映射间的关系，因此可以构建所有的映射．

    这个函数可以被调用任意多次，但是大多数情况下它是被自动调用的，首次使用映射时．

    `confutre_mappers()`函数提供了如果事件钩子，包括：

    －`MapperEvents.before_configured()` - 在`configure_mappers()`做什么事情之前嗲用一次；这个钩子可以用来建立额外的选项，属性或操作程序之前的相关映射．

    －`MapperEvents.mapper_configured()` - 在处理中每个单独映射被调用后都会被调用一次；包含所有的映射状态，除了反向关系的映射．

    －`MapperEvents.after_configured()`－在`configure_mappers()`完成后调用一次；在这个阶段，所有的映射对象都已经配置完成．

- `sqlalchemy.orm.clear_mappers()`

    移除所有类的所有映射．

    这个函数移除类中所有的构造，并废弃所有与它们关联的映射．一旦被调用，这个类变成未映射状态并且可以在随后重新映射．

    `clear_mappers()`并不是用于平常用途．一般来说，映射是用户定义类的永久性结构组件，并且不会单独的被丢弃．如果一个映射类本身被垃圾回收，它的映射也同样会被废弃．因此，`clear_mappers()`仅仅用于测试单元，测试同一个类的不同映射，这个函数的使用场景极为罕见．

- `sqlalchemy.orm.util.identity_key(*args, **kwargs)`

    生成**identity key**元组，在字典`Session.identity_map`字典中当作键来使用．

    这个函数可以有若干种使用方法：

    - `identity_key(class, ident)`

        这个用法接受一个映射类，以及一个主键标量(或元组)当作参数：

        ```python
        >>> identity_key(MyClass, (1, 2))
        (<class "__main__.MyClass">, (1, 2))
        ```

        参数:

        - class: 映射类(必须为位置参数)
        - ident: 主键，可以是一个标量或者元组

    - `identity_key(instance=instance)`

        这个用法会根据传入的实例生成一个标识键．这个实例不需要持久化，只需要构成主键属性即可：

        ```python
        >>> instance = MyClass(1, 2)
        >>> identity_key(instance=instance)
        (<class "__main__.MyClass">, (1, 2))
        ```

        在这个用法里，给定的实例最后会传入`Mapper.identity_key_from_instance()`函数，如果相关行的对象已经过期则会执行一个数据库检查．

        参数：

        - instance: 对象实例(必须通过关键字参数传入)

    - identity_key(class, row=row)

        这个用法和地一个**类/元组**的用法类似，除了应该传入一个`RowProxy`对象:

        ```python
        >>> row = engine.execute("select * from table where a = 1 and b = 2").first()
        >>> identity_key(MyClass, row=row)
        (<class '__main__.MyClass', (1, 2))
        ```

        参数:

        - class: 映射类(必须是一个位置参数)
        - row: 一个通过`ResultProxy`返回的`RowProxy`对象(必须使用关键字参数传入)


- `sqlalchemy.orm.util.polymorphic_union(table_map, typecolname, aliasname='p_union', cast_nulls=True)`

    使用多态映射创建一个`UNION`语句．

    参数：

    －table_map: Table对象的多态标识映射．

    －typecolname: 一个"区分列"的字符串名称，它可以源自与查询，对每行生成一个多态标识符．如果为None，将不会生成多态区分符．

    －aliasname:通过`alias()`构造生成的变量名．

    －cast_nulls: 如果为True，不存在的列将会被标记为NULL，并传入CAST．



