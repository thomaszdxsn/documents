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

当一个`list.append()`事件(或者`set.add()`, `dict.__setitem__()`，抑或标量赋值事件)被association proxy拦截后，将会使用“中间“对象的构造器来实例化一个新的实例，将会把给定的值作为单个参数传入到构造器中。

在我们上面的例子中，一个类似于下面的操作：

`user.keywords.append('cheese inspector')`

将会在association proxy的操作中被转译为：

`user.kw.append(Keyword('cheese inspector'))`

这个例子可以成功是因为我们设计了`Keyword`的构造器只接受一个位置参数:`keyword`.在一些情况下不能使用单参数的构造器，association proxy可以使用`creator`参数来自定义对象创建行为，这个参数接收一个可调用对象(比如：Python函数),然后返回生成的对象：

```python
class User(Base):
    # ...

    # 对append()事件使用Keyword(keyword=kw)
    keywords = association_proxy('kw', 'keyword',
                        creator=lambda kw: Keyword(keyword=kw))
```

`creator`函数在list或set的情况接收单个参数.在dict的情况它接收两个参数: `key`和`value`.

### 简化关联对象

“association object“模式是多对多关系的一个扩展，具体信息请看[文档#Association Object](http://docs.sqlalchemy.org/en/latest/orm/basic_relationships.html#association-pattern)."Association proxies是一个对于“association object”常规用法更加方便的使用技巧。

假设上面的`userkeywords`表具有一些额外的列，我们需要显示映射它们，但是大多数时候我们并不需要直接访问它们。在下面的例子中，我们通过一个引入`UserKeyword`类的新映射来阐释，它其实是上面的`userkeywords`的映射类形式。这个类增加了一个额外的列`special_key`，包含一个我们偶尔会用到的值。我们在User类使用"association proxy"，绑定了`keywords`属性,这个属性桥接了`User.keywords`和每个`UserKeyword.keyword`:

```python
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, backref

from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


Class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(64))

    # "user_keywords"集合to“keyword"属性的一个association_proxy
    keywords = association_proxy("user_keywords", "keyword")
    
    def __init__(self, name):
        self.name = name


class UserKeyword(Base):
    __tablename__ = 'user_keyword'
    user_id = Column(Integer, ForeignKey("user.id"), primary_key=True)
    keyword_id = Column(Integer, ForeignKey("keyword.id"), priamry_key=True)
    sepecial_key = Column(String(50))

    # "user"/"user_keywords"的双向属性/关系
    user = relationship(User, 
                        backref=backref("user_keywords", 
                                        cascade="all, delete-orphan",
                                        ))

    # 引用"Keyword"对象
    keyword = relationship("Keyword")

    def __init__(self, keyword=None, user=None, special_key=None):
        self.user = user
        self.keyword = keyword
        self.special_key = special_key


class Keyword(Base):
    __tablename__ = 'keyword'
    id = Column(Integer, primary_key=True)
    keyword = Column('keyword', String(64))

    def __init__(self, keyword):
        self.keyword = keyword

    def __repr__(self):
        return 'Keyword(%s)' %repr(self.keyword)
```

在上面的配置中，我们可以直接针对每个`User`对象的`.keywords`集合进行操作，`UserKeyword`的使用被隐藏了：

```
>>> user = User('log')
>>> for kw in (Keyword('new_from_blammo'), Keyword('its_big')):
...     user.keywords.append(kw)
...
>>> print(user.keywords)
[Keyword('new_from_blammo'), Keyword('its_big')]
```

在上面例子中，每个`.keywords.append()`操作等同于：

```python
>>> user.user_keywords.append(UserKeyword(Keyword('its_heavy')))
```

这个`UserKeyword`关联对象(association object)在这里构成了两个属性；`.keyword`参数直接构成，并且会传入到`Keyword`对象的构造器作为首个参数。`.user`参数将会作为传入`UserKeyword`对象并追加到`User.user_keywords`集合中，当`User.user_keywords`和`UserKeyword`的双向关系建立后，造成的结果就是会自动构成`UserKeyword.user`属性。上面的`special_key`属性会让它保留为默认值`None`。

有些时候我们需要`special_key`有一个值，我们需要显式创建`UserKeyword`.下面例子我们赋予了所有三个参数,在赋值`.user`时将会造成`UserKeyword`追加到`User.user_keywords`集合中：

```pyhton
>>> UserKeyword(Keyword('its_woord'), user, special_key='my special key')
```

最后再次调用`association proxy`, 将会返回代表之前所有操作的`Keyword`对象集合:

```python
>>> user.keywords
[Keyword('new_from_blammo'), Keyword('its_big'), Keyword('its_heavy'), Keyword('its_wood')]
```

### 代理一个基于字典的集合

association proxy也可以代理一个基于字典的集合。SQLAlchemy的映射通常通常使用`attribute_mapped_collection()`集合类型来创建字典集合，其实还可以使用一种扩展技术:[自定义基于字典的集合](http://docs.sqlalchemy.org/en/latest/orm/collections.html#id1)

association prxoy在发现集合是一个字典时会改变行为。当一个新的值加入到字典后，association proxy实例化过程会传入两个参数到创建函数而不是一个，即key和value.这个创建函数当然就是中间类的构造器，也可以通过这个参数`creator`来自定义。

下面例子中，我们修改了例子中的`UserKeyword`，现在`User.user_keywords`将会使用将会映射为一个字典，`UserKeyword.special_key`将会作为字典的键。我们在`User.keywords`代理中使用了`creator`参数，所以在新元素加入到字典后，这些值可以被正确赋值：

```python
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.collections import attribute_mapped_collection

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(64))

    # 代理到"user_keywords", 实例化UserKeyword使用"special_key"作为键
    # 使用"keyword"作为值
    keywords = association_proxy("user_keywords", "keyword",
                            creator=lambda k, v:
                                    UserKeyword(special_key=k, keyword=v))
    
    def __init__(self, name):
        self.name


class UserKeyword(Base):
    __tablename__ = 'user_keyword'
    user_id = Column(Integer, ForeignKey('user.id'), primary_key=True)
    keyword_id = Column(Integer, ForeignKey('keyword.id', primary_key=True))
    special_key = Column(String)

    # 双向user/user_keywords关系
    # 映射user_keywords为一个字典，用special_key作为它的键

    user = relationship(User, backref=backref(
        "user_keywords",
        collection_class=attribute_mapped_collection("special_key"),
        cascade='all, delete-orphan'
    ))
    keyword = relationship("Keyword")


class Keyword(Base):
    __tablename__ = 'keyword'
    id = Column(Integer, primary_key=True)
    keyword = Column('keyword', String(64))

    def __init__(self, keyword):
        self.keyword = keyword

    def __repr__(self):
        return "Keyword(%s)" % repr(self.keyword)
```

使用下图可以阐释如何把`.keywords`集合当字典使用，使用`UserKeyword.special_key`作为键，使用`Keyword`对象作为值：

```python
>>> user = User('log')

>>> user.keywords['sk1'] = Keyword('kw1')
>>> user.keywords['sk2'] = Keyword['kw2']

>>> print(user.keywords)
{'sk1': Keyword('kw1'), 'sk2': Keyword('kw2')}
```

### 混合association proxies

将上面例子中的代理关系变为代理标量属性，代理一个关联对象，代理一个字典，我们可以讲这三种技术组合在一起使用。这时`UserKeyword`和`Keyword`都将隐藏起来：

```python
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalcehmy.ext.declarative import declarative_base
from sqlalchemy.orm.collections import attribute_mapped_collection

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(64))

    # 和字典例子中一样的"user_keywords" -> "keyword"代理
    keywords = association_proxy(
        "user_keywords",
        "keywords",
        creator=lambda k, v: UserKeyword(special_key=k, keyword=yv)
    )

    def __init__(self, name):
        self.name = name


class UserKeyword(Base):
    __tablename__ = 'user_keyword'
    user_id = Column(Integer, ForeignKey('user.id'), primary_key=True)
    keyword_id = Column(Integer, ForeignKey('keyword.id', primary_key=True))

    special_key = Column(String)
    user = relationship(User, backref=(
        "user_keywords",
        collection_class=attribute_mapped_collection("special_key"),
        cascade="all,delete-orphan"
    ))
    # 现在和Keyword之间的关系名改为“kw"
    kw = relationship("Keyword")
    # "keyword"改为指向"Keyword.keyword"的一个代理
    keyword = association_proxy("kw", "keyword")


class Keywrod(Base):
    __tablename__ = 'keyword'
    id = Column(Integer, primary_key=True)
    keyword = Column('keyword', String(64))

    def __init__(self, keyword):
        self.keyword = keyword
```

现在`User.keywords`是一个字符串对字符串的字典了，`UserKeyword`和`Keyword`对象的创建/移除过程对我们来说都是不可见的了。下面的例子我们通过赋值操作符来解释：

```python
>>> user = User("log")
>>> user.keywords = {
...     "sk1": "kw1",
...     "sk2": "kw2”    
... }
>>> print(user.keywords)
{"sk1": "kw1", "sk2": "kw2"}

>>> user.keywords["sk3"] = "kw3"
>>> del user.keywords['sk2']
>>> print(user.keywords)
{'sk1': 'kw1', 'sk3': 'kw3'}

>>> #　下面解释如何查看(代理的)底层对象
>>> print(user.user_keywords['sk3'].kw)
<__main__.Keyword object at 0x12ceb90>
```

在我们例子中一个值得注意的地方就是，因为`Keyword`在每个字典操作中都会单独创建，所以这个例子中的使用方式不能去检查"Keyword"的唯一性。在需要检查唯一性的使用场景下，推荐使用[UniqueObject](https://bitbucket.org/zzzeek/sqlalchemy/wiki/UsageRecipes/UniqueObject)，或者一个可比较的创建策略，它们都采用“首先查询，然后创建”的策略来构建`Keyword`类，所以如果一个给定的名称已经存在，就会返回这个已经存在的`Keyword`对象.


### 查询Association proxies

pass