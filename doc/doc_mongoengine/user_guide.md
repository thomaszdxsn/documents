# 2.User Guide

## 2.1.Installing MongoEngine

## 2.2 Connecting to MongoDB

想要连接`mongod`实例，使用`connect()`函数:

```python
from mongoengine import connect
connect('project1')
```

默认情况下，MongoDB假定`mongod`实例运行在`localhost:27017`.你可以通过`host`和`port`另行制定：

```python
connect('project1', host='192.168.1.35', port=12345)
```

身份验证:

```python
connect('project1', username='webapp', password='pwd123')
```

也支持URI风格的参数:

```python
connect('project1', host='mongodb://localhost/database_name')
```

### 2.2.1.Replica Sets

MongoEngine支持连接replica sets:

```python
from mongoengine import connect

# 常规连接方式
connect('dbname', replcaset='rs-name')

# URI风格连接方式
connect(host='mongodb://localhost/dbname?replicaSet=rs-name')
```

可以针对单个Query设置读取优先:

```python
Bar.objects().read_preference(ReadPreference.PRIMARY)
Bar.objects(read_preference=ReadPreference.PRIMARY)
```

### 2.2.2.Multiple Databases

想要使用多个数据库，你可以在使用`connect()`的时候为连接提供一个`alias`名称，如果没有提供`alias`则使用`default`.

在后端你可以使用`register_connection()`来存储数据。

每个单独的documents都支持存入不同的数据库，需要你在它的元数据中提供`db_alias`:

```python
class User(Document):
    name = StringField()
    
    meta = {
        "db_alias": "user-db"
    }


class Book(Document):
    name = StringField()

    meta = {
        "db_alias": "book-db"
    }


class AuthorBooks(Document):
    author = ReferenceField(User)
    book = ReferenceField(Book)

    meta = {
        "db_alias": "users-books-db"
    }
```

### 2.2.3.Context Managers

有时你可能想针对一个查询切换数据库或集合。例如，需要获取从一个单独的数据库获取旧的数据，或者为了性能原因让写入函数自动选择一个collection写入.

#### 2.2.3.1.Switch Database

`swich_db`上下文管理器允许把一个给定的Document类切换数据库:

```python
from mongoengine.context_managers import switch_db


class User(Document):
    name = StringField()

    meta = {
        "db_alias": "user-db"
    }


with swich_db(User, "archive-user-db") as User:
    User(name='Ross').save()
```

#### 2.2.3.2.Swich Collection

`swich_collection`上下文管理区允许你修改一个给定类使用的集合:

```python
from mongoengine.context_managers import switch_collection


class Group(Document):
    name = StringField()


Group(name='test').save()


with switch_collection(Group, "group2000") as Group:
    Group(name='hello Group 2000 collection').save()
```

> 注意
>
> 请确保在使用上下文管理器之前以及通过`register_connection()`或`connect()`把Document类和alias关联。

## 2.3. Defining documents

在MongoDB中，一个`document`大概等于RDMS中的一条`row`.在RDMS中，row要放在`table`中，MongoDB吧`document`放在`collection` -- 最主要的差异是collection不需要预先定义schema。

### 2.3.1.Defining a document's schema

MongoEngine允许你为Document定义schema，这可以帮助你减少编码上的错误，可以在这上面定义一些辅助函数帮助你分离数据和逻辑。

```python
from mongoengine import *
import datetime


class Page(Document):
    title = StringField(max_length=200, required=True)
    date_modified = DateTimeField(default=datetime.datetime.now)
```

BSON是会保持顺序的，`Document`使用OrderDict，根据属性定义的顺序来确定顺序。

### 2.3.2.Dynamic document schemes

MongoDB的优势之一就是collection允许动态schema。

`DynamicDocument`对象和`Document`一样，不过任何赋予的数据/属性都会被保存:

```python
from mongoengine import *


class Page(DynamicDocument):
    title = StringField(max_length=200, required=True)


# Create a new page and add tags
>>> page = Page(title='Using MongoEngine')
>>> page.tags = ['mongodb', 'mongoengine']
>>> page.save()

>>> Page.objects(tags='mongoengine').count()
>>> 1
```

> DynamicDocument的警告
>>
>> 字段名不能以`_`开头。

### 2.3.3.Fields

默认情况下，字段都不是必填的。想要让这个字段必填，需要设置关键字参数`required`.字段还有一些其它的限制手段(如长度`max_length`).字段可以使用默认值，默认值可以是可调用对象，字段类型包括:

- BinaryField
- BooleanField
- ComplexDateTimeField
- DateTimeField
- DecimalField
- DictField
- EmailField
- EmbeddedDocumentField
- EmbeddedDocumentListField
- FileField
- FloatField
- GenericEmbeddedDocumentField
- GenericReferenceField
- GeoPointField
- ImageField
- ListField
- MapField
- ObjectIdField
- ReferenceField
- SequenceField
- SortedListField
- StringField
- URLField
- UUIDField
- PointField
- LineStringField
- PolygonField
- MultiPointField
- MultiLineStringField
- MultiPolygonField

#### 2.3.3.1.Field arguments

每个字段类型都可以定义若干关键字参数，下面的关键字参数可以设定给所有的字段:

- `db_field`(默认:`None`)

    MongoDB字段名称。

- `required`(默认:`False`)

    如果设置为True，插入时缺少这个字段会抛出`InvalidationError`.

- `default`(默认:`None`)

    字段的默认值.

    在定义可变类型时需要小心:

    ```python
    class ExampleFirst(Document):
        # 默认为空list
        value = ListField(IntField(), default=list)


    class ExampleSecond(Document):
        # 默认的list有一组值
        value = ListField(IntField(), default=lambda: [1, 2, 3])

    
    class ExampleDangerous(Document):
        # 如果射者了这样的默认值，会很危险
        value = ListField(IntField(), default=[1, 2, 3])
    ```

    - `unique`(默认:`False`)

        如果设置为True,同个集合内不允许存在重复的值。

    - `unique_with`(默认:`None`)

        可以接受一个字段的名称，这样在一个集合中不会允许同时两个字段都已经存在的情况。

    - `primary_key`(默认:`False`)

        如果设置为True，这个字段会作为集合的主键。`DictField`和`EmbededDocuments`都可以当作集合的主键。

    - `choices`(默认：`None`)

        一个可迭代对象，限定了字段可以使用的值。

        可以是一个嵌套的元组，第一个值作为存入Mongo的数据，第二个值作为供人阅读的值。

        ```python
        SIZE = (
            ('S', 'Small'),
            ('M', 'Medium'),
            ('L', 'Large'),
            ('XL', 'Extra Large'),
            ('XXL', 'Extra Extra Large')
        )


        class Shirt(Document):
            size = StringField(max_length=3, choices=SIZE)
        ```

        或者可以是一个flat的可迭代对象(只包含值):

        ```python
        SIZE = ('S', 'M', 'L', 'XL', 'XXL')


        class Shirt(Document):
            size = StringField(max_length=3, choices=SIZE)
        ```

    - `**kwargs`(可选)

        你可以指定任意其它的关键字参数作为额外的元数据。一般可用`help_text`和`verbose_name`.

#### 2.3.3.2.List fields

MongoDB支持存储list类型的字段。请使用`ListField`，它接受另一个Field对象作为它的第一个参数，这个Field可以指定list中元素的类型：

```python
class Page(Document):
    tags = ListField(StringField(max_length=50))
```

#### 2.3.3.3.Embedded documents

MongoDB支持嵌套的Document。想要使用mongoengine创建一个嵌套的document，请继承`EmbededDocument`:

```python
class Comment(EmbeddedDocument):
    content = StringField()
```

想要把这个嵌套Document放在另一个Document中，使用`EmbededDocumentField`即可：

```python
class Post(Document):
    comments = ListField(EmbededDocumentField(Comment))

comment1 = Comment(content='Good work!')
comment2 = Comment(content='Nice article!')
page = Page(comments=[comment1, comment2])
```

#### 2.3.3.4.Dictionary Fields

一般来说，推荐使用`EmbededDocumentField`代替`DictField`.后者并不支持字段验证等。但是有时你知道自己需求是什么，那么也可以使用`DictField`:

```python
class SurveyResponse(Document):
    date = DateTimeField()
    user = ReferenceField(User)
    answers = DictField()


survey_response = SurveyResponse(date=datetime.now(), user=request.user)
resposne_form = ResponseForm(request.POST)
survey_response.answers = response_form.clean_data()
survey_response.save()
```

字典可以存储复杂的数据，比如嵌套字典，列表，其它对象的引用...

#### 2.3.3.5.Refeence fields


