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

pass