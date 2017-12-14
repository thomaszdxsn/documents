# Automap

定义了`sqlalchemy.ext.declarative_base`系统的扩展，可以根据数据库模式自动生成映射类和关系。

## 基本用法

下面是把存在的数据库反射为model的最简单的一个方式。我们使用`automap_base()`创建一个`AutomapBase`类，类似于我们创建一个`declarative_base`类.当我们调用`AutomapBase.prepare()`之后，将会查询数据库模式并生成映射类：

```python
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine

Base = automap_base()

# engine, 假定这个数据库含有两个表: "user"和 "address"
engine = create_engine("sqlite:////mydatabase.db")

# 反射表
Base.prepare(engine, reflect=True)

# 映射类现在通过匹配的表名来创建
User = Base.classes.user
Address = Base.classes.address

session = Session(engine)

# 基本的关系也可以创建
session.add(Address(email_address='foo@bar.com', user=User(name='foo')))
session.commit()

# 集合关系默认命名为"<classname>_collection"
print(u1.address_collection)
```

在上面例子中，在调用`AutomapBase.prepare()`并传入参数`AutomapBase.prepare.reflect`后，意味着将会对declarative_base类的`MetaData`集合调用`Metadata.reflect()`方法；然后，MetaData中每个可用的的`Table`都会获取自动生成一个新的映射类。如果不同的表之间具有`ForeignKeyConstraint`联系，将会根据这个建立起`relationship()`.

## 从存在的MetaData生成映射

我们可以讲一个预先声明的`MetaData`对象传入到`automap_base()`中。这个对象可以在任何地方创建，包括编程，一个序列化文件...下面例子我们将`Automap`反射和显示的base声明组合使用：

```python
from sqlalchemy import create_engine, MetaData, Table, Column, ForeignKey
from sqlalchemy.ext.automap import automap_base


# 生成我们自己的MetaData对象
metadata = MetaData()

# 我们可以直接使用metadata来反射，使用选项参数如”only“来限制反射的表
metadata.reflect(engine, only=['user', 'address'])

# ..或者可以直接使用它来定义我们自己的Table(不需要再去create)
Table('user_order', metadata,
        Column('id', Integer, primary_key=True),
        Column('user_id', ForeignKey('user.id')))

# 我们可以从这个MetaData生成一组映射
Base = automap_base(metadata=metadata)

# 调用prepare()以后就会建立映射类和关系
User, Address, Order = Base.classes.user, Base.classes.address, \
                        Base.classes.user_order
```

## 显式的设定类

`sqlalchemy.ext.automap`扩展允许类可以显式定义，就像使用`DeferredReflection`类一样。继承自`AutomapBase`就像常规的declarative_base一样，但是再它们构建完成后并不会直接映射，只有在调用`AutomapBase.prepare()`以后才会被映射，注意只有表名一样的表／类才会映射：

```python
from sqlalchemy.ext.automap import automap_base
from sqlalchemy import create_engine


# automap base
Base = automap_base()

# 对user表的预声明User类
class User(Base):
    __tablename__ = 'user'

    # 覆盖scheme的元素，比如Column
    user_name = Column('name', String)

    # 如果可能，也应该覆盖relationship
    # 我们必须和数据库中表名使用同样的名称
    address_collection = relationship("address", collection_class=set)


# 反射
engine = create_engine("sqlite:///mydatabase.db")
Base.prepare(engine, reflect=True)

# 我们同样可以访问反射自address表的Address
Address = Base.classes.address

u1 = session.query(User).first()
print(u1.address_collection)

# backref仍然存在
a1 = session.query(Address).first()
print(a1.user)
```

上面例子中，`relationship`的第一个参数使用表名"address".


## 覆盖命名模式(naming schemes)

`sqlalchemy.ext.automap`用于通过scheme来生成映射类和关系名，意味着要根据这些一些外键的名称才能决定。三个函数对应三个决定的方式，分别可以传入到`Automap.prepare()`方法中，分别是`classname_for_table()`, `name_for_scalar_relationship()`, `name_for_collection_relationship()`.下面例子中的`inflect`包来设置"复数“命名法，代表集合名称，驼峰命名法代表类名：

```python
import re
import inflect


def camelize_classname(base, tablename, table):
    """生成一个驼峰式'类名', 
    比如: 'words_and_underscores' -> 'WordsAndUnderscores'
    """

    # re.sub()可以传入callable参数，这是一个小技巧
    return str(tablename[0].upper() + \
            re.sub(r'_([a-z])', lambda m: m.group(1).upper(), tablename[1:]))


_pluralizer = inflect.engine()
def pluralize_collection(base, local_cls,  referred_cls, constraint):
    """生成一个'非驼峰式' '复数式'的类名
    比如: 'SomeTerm' -> 'some_terms'
    """
    referred_name = referred_cls.__name__
    uncamelized = re.sub(r"[A-Z]",
                        lambda m: "_%s" %m.group(0).lower(),
                        referred_name[1:])
    pluralized = _pluralizer.plural(uncamelized)
    return pluralized


from sqlalchemy.ext.automap import automap_base

Base = automap_base()

engine = create_engine("sqlite:///mydatabase.db")

Base.prepare(engine, reflect=True,
            classname_for_table=camelize_classname,
            name_for_collection_relationship=pluralize_collection)
```

在上面的例子中，我们现在具有两个类，名称分别是`User`和`Address`，`User`中的关系集合叫做:`User.addresses`:

```python
User, Address = Base.classes.User, Base.classes.Address

u1 = User.(addresses=[Address(email='foo@bar.com')])
```

## 关系的探测(detection)

`Automap`完成的最大一部分工作就是根据外键生成了`relationship()`结构。下面的步骤是automap在处理**多对一**或者**一对多**关系时的机制：

1. 给定一个`Table`，将会将它映射到一个特定的类，然后检查是否有`ForeignKeyConstraint`对象.
2. 对于每个`ForeignKeyConstraint`, remote的`Table`如果存在，则对应它要映射的类。否则就跳过.
3. 如果从一个即时映射的类中发现有`ForeignKeyConstraint`相符的引用，将会在具有外键约束的类和引用的类中建立起一个**多对一**关系.反过来，也会在引用到的类和具有外键约束的类之间建立起**一对多**关系.
4. 如果属于`ForeignKeyConstraint`的列具有`nullable=False`,将会在关系中传入级联参数`cascade='all,delete-orphan'`.如果这个`ForeignKeyConstraint`对象报告`ForeignKeyConstraint.ondelete`设置了`CASCADE`不为空，或者为`SET NULL`, 将会为关系配置可选参数`passive_deletes=True`，注意`ON DELETE`没有backref的设置.
5. 关系的名称讲取决于`AutomapBase.prepare.name_for_scalar_relationship`和`AutomapBase.prepare.name_for_collection_relationship`可调用函数。值得注意的是，默认的关系命名取决于**真实的类名**.
6. 类可以在`Base.classes`的属性中找到。如果关系中的一方检测到，另一方没有检测到，`AutomapBase`将会试图在缺失的一侧创建一个关系，然后使用`relationship.back_populates`参数。
7. 在通常处理一侧没有关系存在时，`AutomapBase.prepare()`在**多对一**一侧创建关系，再通过参数`backref`来匹配另一侧.
8. `relationship()`和`backref()`的生成取决于`AutomapBase.prepare.generate_relationship()`函数。

### 自定义关系参数

`AutomapBase.prepare.generate_relationship`钩子可以用来为关系添加参数。在多数情况下，我们可以使用已经存在的`automap.generate_relationship()`(注意这是一个库函数，而不是钩子)函数来返回对象，并且在这个函数的参数字典中传入我们自己的参数:

```python
from sqlalchemy.ext.automap import generate_relationship, interfaces


def _gen_relationship(base, direction, return_fn,
                        attrname, local_cls, referred_cls, **kw):
    if direction is interfaces.ONETOMANY:
        kw['cascade'] = 'all, delete-orphan'
        kw['passive_deletes'] = True
    # 利用内置函数，返回合格的结果
    return generate_relationship(base, direction, return_fn,
                                    attrname, local_cls, referred_cls, **kw)


from sqlalchemy.ext.automap import automap_base
from sqlalchemy import create_engine

Base = automap_base()
engine = create_engine("sqlite:///mydatabase.db")

Base.prepare(engine, reflect=True,
            generate_relationship=_gen_relationship)
```

### 多对多关系

`sqlalchemy.ext.automap`可以生成多对多关系，也就是说可以包含`secondary`参数。下面是执行的步骤:

1. 检查一个给定`Table`的`ForeignKeyConstraint`对象。
2. 如果这个对象正好包含两个`ForeignKeyConstraint`对象，这个表中所有Column就是这两个`ForeignKeyConstraint`，这个表会被假定为`secondary`，不会被直接映射.
3. 两(在自引用时，一个)个外部表匹配了这个外键约束
4. 如果两个映射类都被定位，那么就直接生成`relationship()`和`backref()`
5. 想要覆盖上面的这个默认关系生成行为，需要覆盖参数`generate_relationship()`

### 关系和继承

`sqlalchemy.ext.automap`在继承关系中不会生成任何关系：

```python
class Empolyee(Base):
    __tablename__ = 'employee'
    id = Column(Integer, primary_key=True)
    type = Column(String(50))
    __mapper_args__ = {
        "polymorphic_identity": "employee", "polymorphic_on": type
    }


class Enginner(Employee):
    __tablename__ = 'engineer'
    id = Column(Integer, ForeignKey('employee.id'), primary_key=True)
    __mapper_args__ = {
        "polymorhpic_identity": "engineer"
    }
```

在`Engineer`和`Employee`之间的关系并没有使用外键，而是通过两表之间的继承建立起了关联.

但是`automap`不会在继承关系中生成一个`relationship()`.下面例子中，我们显示指定了外键，并且在`inherit_condition`时候设定了我们想要的关系：

```python
class Employee(Base):
    __tablename__ = 'employee'
    id = Column(Integer, primary_key=True)
    type = Column(String(50))
    
    __mapper_args__ = {
        'polymorphic_identity': 'employee', "polymorphic_on': type
    }


class Engineer(Employee):
    __tablename__ = 'engineer'
    id = Column(Integer, ForeignKey('employee.id'), primary_key=True)
    favorite_employee_id = Column(Integer, ForeignKey('employee.id'))

    favorite_employee = relationship(Employee,
                                    foreign_keys=favorite_employee_id)

    __mapper_args__ = {
        "polymorphic_identity": "engineer"
        "inherit_condition"：　id == Employee.id
    }
```

### 处理简单的命名冲突

如果在映射时发生了命名冲突，可以按需覆盖`classname_for_table()`, `name_for_scalar_relationship()`以及`name_for_collection_relationship()`。例如，如果automap试图讲一个多对一关系取得名称和一个存在的列名冲突：

```sql
CREATE TABLE table_a (
    id INTEGER PRIMARY KEY
);

CREATE TABLE table_b (
    id INTEGER PRIMARY KEY,
    table_a INTEGER,
    FOREIGN KEY(table_a) REFERENCE table_a(id)
);
```

上面的数据库scheme将会首先映射`table_a`表为一个类，名称也是`table_a`;但是在映射`table_b.table_a`的时候发生了命名冲突，所以会抛出一个错误.

我们可以使用一个下划线来解决冲突:


```python
def name_for_scalar_relationship(base, local_cls, referred_cls, constraint):
    name = referred_cls.__name__.lower()
    local_table = local_cls.__table__
    # 如果name存在于表的列名中
    if name in local_table.columns:
        newname = name + "_"
        warning.warn(
            "Already detected name %s present. using %s" %
            (name, newname)
        )
        return newname
    return name


Base.prepare(engine, reflect=True,
    name_for_scalar_relationship=name_for_scalar_relationship)
```

另外，我们也可以修改列名。列的映射可以直接在映射类中赋值即可:

```python
Base = automap_base()


class TableB(Base):
    __tablename__ = 'table_b'
    _table_a = Column('table_a', ForeignKey('table_a.id'))

Base.prepare(engine, reflect=True)
```

## 使用显式声明的Automap

之前提到过，automap并不依赖于`reflect`:

```python
from sqlalchemy.ext.automap import automap_base
from sqlalchemy import Column, Integer, String, ForeignKey

Base = automap_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String)


class Address(Base):
    __tablename__ = 'address'
    id = Column(Integer, primary_key=True)
    email = Column(String)
    user_id = Column(ForeignKey('user.id'))
    

# 生成关系
Base.prepare()

# 映射完成后，在user中有一个"address_collection"关系
a1 = Address(email='u1')
a2 = Address(email='u2')
u1 = User(address_collection=[a1, a2])
assert a1.user is u1
```

注意在继承`AutomapBase`以后，必须也调用`AutomapBase.prepare()`.

## API

- `sqlalchemy.ext.automap.automap_base(declarative_base=None, **kw)`

    生成一个声明式的automap base.

    这个函数生成一个新的base类，它是一个携带`declarative.declarative_base()`参数的`automap_base`类.

    除了`declarative_base`以外的所有关键字参数都将会传入到`declarative_declarative_base()`函数中。

    参数:

    - `declarative_base`: 一个已经存在的，通过`declarative_base()`生成的类。当这个参数传入后，这个函数就不会再去调用`declarative_base()`，其它的关键字参数也会被忽略.
    - `**kw`: 最终将会被传入到`declarative_base()`之中的关键字参数.

- `sqlalchemy.ext.automap.AutomapBase`

    "automap"模式的基类。

    `AutomapBase`一般用来和`declarative_base()`生成的类Base相比较。在实践中，`AutomapBase`一直用于在使用`declarative_base()`之中以mixin的形式存在.

    一个可继承的`AutomapBase`，一般使用`automap_base()`函数生成.

    - `classes = None`

        一个`util.Properties`实例，它可以包含类.

        这个对象的行为很像表中的`.c`集合。类将会出现在`classes`的命名属性后，例如：

        ```python
        Base = automap_base()
        Base.prepare(engine=some_engine reflect=None)

        User, Address = Base.classes.User, Base.classes.Address
        ```

    - 类方法`prepare(engine=None, reflect=False, schema=None, classname_for_table=<function classname_for_table>, collection_class=<type 'list'>, name_for_scalar_relationship=<function name_for_scalar_relationship>, name_for_collection_relationship=<function name_for_collection_relationship>, generate_relationship=<function generate_relationship>)`

        从`MetaData`中提取出映射类和关系并执行映射.

        参数：

        - `engine`: 一个用于执行模式反射的`Engine`或者`Connection`。如果`AutomapBase.prepare.reflect`设定为False，这个对象将会被忽略。
        - `reflect`: 如果为True,将会调用关联的`MetaData`的`Metadata.reflect()`方法.
        - `classname_for_table`: 一个可调用的函数，用于通过给定一个表名，生成新的类名。默认使用本模块的`classname_for_table()`函数.
        - `name_for_scalar_relationship`: 一个可调用的函数，用于为一个标量关系生成关系名称。默认使用本模块的`name_for_scalar_relationship()`.
        - `name_for_collection_relationship`: 一个可调用的函数，用于为一个集合关系生成关系名称。默认使用本模块的`name_for_collection_relationship()`.
        - `generate_relationship`: 一个可调用的函数，用于生成`relationship()`和`backref()`构造。默认使用`generate_relationship()`
        - `collection_class`: 一个Python的集合类，用于生成集合的类型，默认为`list`.
        - `schema`

- `sqlalchemy.ext.automap.classname_for_table(base, tablename, table)`

    给定一个表名，返回一个要使用的类名。

    默认实现为：

    `return str(tablename)`

    另外的实现可以通过最终传入`AutomapBase.prepare.classname_for_table`参数来完成。

    参数:

    - `base`: 进行准备的这个`AutomapBase`
    - `tablename`: `Table`的字符串名称
    - `table`: `Table`对象本身

    返回:

    一个字符串名称。

- `sqlalchemy.ext.automap.name_for_scalar_relationship(base, local_cls, referred_cls, constraint)`

    返回一个标量关系的属性名称.

    默认的实现为：

    `return referred_cls.__name__.lower()`

    另外的实现可以通过最终传入`AutomapBase.prepare.name_for_scalar_relationship`参数来完成.

    参数:

    - `base`: 进行准备的这个`AutomapBase` 
    - `local_cls`: 局部端映射的类.
    - `referred_cls`: 引用端映射的类
    - `constraint`: 一个`ForeignKeyConstaint`，用于探测并生成这个关系.

- `sqlalchemy.ext.automap.name_for_collection_relationship(base, local_cls, referred_cls, constraint)`

    返回一个集合关系的属性名称.

    默认的实现为：

    `return referred_cls.__name__.lower() + "_collection`

    另外的实现可以通过最终传入`AutomapBase.prepare.name_for_collection_relationship`参数来完成.

    参数:

    - `base`: 进行准备的这个`AutomapBase` 
    - `local_cls`: 局部端映射的类.
    - `referred_cls`: 引用端映射的类
    - `constraint`: 一个`ForeignKeyConstaint`，用于探测并生成这个关系.

- `sqlalchemy.ext.automap.generate_relationship(base, direction, return_fn, local_cls, referred_cls, **kw)`

    在两个映射类生成一个`relationship()`或者`backref()`.

    如果自定了这个函数可以通过指定`AutomapBase.prepare.generate_relationship`参数来完成。

    默认实现的函数如下：

    ```python
    if return_fn is backref:
        return return_fn(attrname, **kw)
    elif return_fn is relationship:
        return return_fn(referred_cls, **kw)
    else:
        raise TypeError("Unknown relationship function: %s" % return_fn)
    ```

    参数：

    - `base`: 做准备的`AutomapBase`类。
    - `direction`: 指代关系的“方向”；可以是`ONETOMANY`, `MANYTOONE`, `MANYTOMANY`中的一个.
    - `return_fn`: 默认用于生成关系的函数。可以是`relationship()`或者`backref()`中的一个。
    - `attrname`: 关系赋值的属性名。
    - `local_cls`: 关系中"local"端的类
    - `referred_cls`: 关系中"引用"端的类
    - `**kw`: 传入到函数中的额外关键字参数

    返回：

    通过`generate_relationship.return_fn`参数,返回一个`relationship()`或者`backref()`构造。