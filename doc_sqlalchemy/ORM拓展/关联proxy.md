[TOC]

# Association Proxy

`association proxy`用于创建一个对于关系中的目标属性的*读/写*视图。它本质上是隐藏了两个端点中的中间属性，可以用来从一个相关对象的集合中择优挑选字段，或者用来减少使用关联对象模式的繁杂。通过有想法的应用，accociation proxy可以用来构建复杂的集合以及虚拟集合的视图(dictionary views of virtually any geometry)，使用标准的方式持久化到数据库，透明的配置关系模式。

## 简化标量集合

考虑两个类(`User`和`Keyword`)之间的一个多对多映射.每个`User`可以包含任意数量的`Keyword`对象，反之亦然:

```python
from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(64))
    kw = relationship('Keyword', secondary=lambda: userkeywords_table)

    def __init__(self, name):
        self.name = name


class Keyword(Base):
    __tablename__ = 'keyword'
    id = Column(Integer, primary_key=True)
    keyword = Column("keyword", String(64))

    def __init__(self, keyword):
        self.keyword = keyword


userkeywords_table = Table("userkeywords", Base.metadata,
        Column("user_id", Integer, ForeignKey("user.id")),
        Column("keyword_id", Integer, ForeignKey("keyword.id"),
                primary_key=True)
        )
```

想要读取和操作和`User`关联的"keyword"字符串集合，需要遍历集合中的每个元素的`.keyword`属性，这种操作看起来很笨拙:

```python
>>> user = User('jek')
>>> user.kw.append(Keyword('cheese inspector'))
>>> print(user.kw)
[<__main__.Keyword object at 0x12bf830>]
>>> print(user.kw[0].keyword)
cheese insepector
>>> print([keyword.keyword for keyword in user.kw])
['cheese inspector']
```

使用`association_proxy`可以对`kw`关系生成一个“视图”，只暴露每个`Keyword`对象的`.keyword`字符串值：

```python
from sqlalchemy.ext.associationproxy import association_proxy


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(64))
    kw = relationship("Keyword", secondary=lambda: userkeywords_table)

    def __init__(self, name):
        self.name = name

    # 代理"kw"关系中的"keyword"属性
    keywords = association_proxy("kw", "keyword")
```

我们现在可以看到`.keyword`是一个字符串列表，包含了可读性和可写性。写入时只需要追加字符串，新的`Keyword`对象会自动帮我们创建：

```python
>>> user = User('jek')
>>> user.keywords.append('cheese inspector')
>>> user.keywords
['cheese inspector']
>>> user.keywords.append("snack ninja")
>>> user.kw
[<__main__.Keyword object at 0x12cdd30>, <__main__.Keyword object at 0x12cde30>]
```

`association_proxy`函数生成的`AssociationProxy`对象是一个Python描述符实例。它应该总是定义在用户定义的映射类或者mapper中。

proxy函数通过操作底层的属性或者集合来响应操作，对proxy的修改将会立即显示到映射的属性中，反之亦然。底层属性仍然保持可访问。

当首次访问后，`association proxy`会对目标集合执行一次*内省(introspection)*操作，用以保证它的行为正确。内省的细节包括检查本地代理的属性是一个集合或标量属性，以及集合是一个set，list还是dict都要纳入考量，然后proxy才能正常工作。

## 新值的创建


