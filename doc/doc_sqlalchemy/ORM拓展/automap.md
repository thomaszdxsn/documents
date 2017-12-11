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

