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

#### 2.3.3.5.Reference fields

将另一个Document作为参数传入即可：

```python
class User(Document):
    name = StringField()


class Page(Document):
    content = StringField()
    author = ReferenceField(User)


john = User(name='John Smish')
john.save()

post = Page(content='Test Page')
post.author = john
post.save()
```

`User`对象会在幕后自动转换为引用id，在取回`Page`时会自动转换为对象。

如果想要**自引用**，传入`'self'`即可.想要引用一个尚未定义的Document，传入这个Document的字符串名称即可:

```python
class Employee(Document):
    name = StringField()
    boss = ReferenceField('self')
    profile_page = ReferenceField('ProfilePage')


class PorfilePage(Document):
    content = StringField()
```

##### 2.3.3.5.1.One to Many with ListFields

如果你通过一个reference list实现了一对多，那么你需要这样来查询:

```python
class User(Document):
    name = StringField()


class Page(Document):
    content = StringField()
    authors = ListField(ReferenceField(User))


bob = User(name='Bob Jones').save()
john = User(name='John Smish').save()


Page(content='Test Page', authors=[bob, john]).save()
Page(content='Another Page', authors=[john]).save()


# 找到Bob的所有Page
Page.objects(authors__in=[bob])

# 找到Bob,John联名的Page
Page.objects(authors__all=[bob, john])

# 将Bob从一篇Page移除
Page.objects(id='...').update_one(pull__authors=bob)

# 将John加入一篇Page
Page.objects(id='...').update_one(push__authors=john)
```

##### 2.3.3.5.2 Dealing with deletion of referred documents

默认情况下，MongoDB不会检查你的数据完整性。Mongoengine的`ReferenceField`加入了一下功能，可以确保某些数据库完整性问题。比如"级联删除"可以在`ReferenceField`中传入`reverse_delete_rule`参数:

```python
class ProfilePage(Document):
    ...
    employee = ReferenceField('Employee', reverse_delete_rule=mogoengine.CASCADE)
```

这个例子的意思是，如果一个Employee对象被移除，那么所有引用它的ProfilePage对象都会被移除。

这个参数可接受的值包括:

- `mongoengine.DO_NOTHING`

    这是默认值，代表什么都不做。

- `mongoengine.DENY`

    如果有对对象引用的其它对象存在，删除请求会被拒绝。

- `mongoengine.NULLIFY`

    任何引用这个对象的字段都会被清空(使用mongo的`unset`操作)

- `mongoengine.CASCADE`

    任何引用这个对象的对象也会被删除。

- `mongoengine.PULL`

    从`ListField`对象中移除这个引用(使用mongo的`pull`操作)

> 警告
>
>> 由于这种级联关系定义在app级别，所以需要确保让MongoEngine知道这些关系的存在。
>>
>> 比如，在Django中，确认它们所存在的app都列在了`INSTALLED_APPS`上面.

##### 2.3.3.5.3.Generic reference fields

第二种引用字段是`GenericReferenceField`，它可以让你引用任何类型的Document，所以不需要接受一个Document类作为参数:

```python
class Link(Document):
    url = StringField()


class Post(Document):
    title = StringField()


class Bookmark(Document):
    bookmark_object = GenericReferenceField()


link = Link(url='http://hmarr.com/mongoengine/')
link.save()

post = Post(title='Using MongoEngine')
post.save()

Bookmark(bookmark_object=link).save()
Bookmark(bookmark_object=post).save()
```

#### 2.3.3.6.Uniqueness constraints

MongoEngine允许你对`Field`传入`unique`参数来限制字段在集合中唯一。如果插入重复的值，将会抛出`NotUniqueError`。如果你想要多个字段唯一，可以使用`unique_with`:

```python
class User(Document):
    username = StringField(unique=True)
    first_name = StringField()
    last_name = StringField(unique_with='first_name')
```

#### 2.3.3.7.Skipping Document validation on save

你可以在调用`save()`的时候传入`validate=False`，效果是这次操作不会在进行任何验证操作：

```python
class Recipient(Document):
    name = StringField()
    email = EmailField()


recipient = Recipient(name='admin', email='root@localhost')
recipient.save()                # 会抛出 ValidationError
recipient.save(validate=False)  # 不会抛出错误
```

### 2.3.4.Document collections

Document类都在数据库中拥有它们的集合(collection)。collection的名称默认使用类的名称(转换为小写).如果你想要指定collection的名称，可以通过`meta`来指定：

```python
class Page(Document):
    title = StringField(max_length=200, required=True)
    meta = {
        "collection": "cmsPage"
    }
```

#### 2.3.4.1.Capped collections

*cappee collection: 定长集合，适合用于存储限定长度的数据，比如日志*

`Document`可以使用`Capped Collection`，通过指定meta数据`max_documents`和`max_size`。`max_size`最好设定为256的倍数。如果指定`max_documents`而没有指定`max_size`,`max_size`的默认值为`10485760(10MB)`。

下面的例子,`Log` document限定为1000个document数量和2MB的硬盘容量:

```python
class Log(Ducoment):
    ip_address = StringField()
    meta = {
        "max_documents": 1000,
        "max_size": 2000000
    }
```

### 2.3.5.Indexes

你可以设置index，让查询更加快速。

`+`, `-`代表排序方向，`$`代表是Text index, `#`代表是Hashed index:

```python
class Page(Document):
    category = IntField()
    title = StringField()
    rating = StringField()
    created = DateTimeFIeld()
    
    meta = {
        'indexes': [
            'title',
            '$title',
            '#title',
            ('title', '-rating'),
            ('category', '_cls'),
            {
                "fields": ['created'],
                'expireAfterSeconds': 3600
            }
        ]
    }
```

如果传入字典，可以使用下面的选项:

- `fields`(默认: `None`)

    想要索引的字段。

- `cls`(默认: `True`)

    如果你使用了多态model，打开了`allow_inheritance`，你可以考虑是否为index加入`_cls`作为前缀。

- `sparse`(默认:`False`)

    索引是否应该sparse.

- `unique`(默认:`False`)

    索引是否应该unique.

- `expireAfterSeconds`(可选)

    允许自动让集合中的数据过期。(单位:秒)

#### 2.3.5.1.Global index default options

下面是一些index全局默认值选项：

```python
class Page(Document):
    title = StringField()
    rating = StringField()
    meta = {
        "index_options": {},
        "index_background": True,
        "index_drop_dups": True,
        "index_cls": False
    }
```

- `index_options` (Optional)

    设置默认的index options

- `index_background` (Optional)

    如果index在后台被indexed，设置一个默认值

- `index_cls` (Optional)

    设置index是否加入`_cls`前缀

- `index_drop_dups` (Optional)

    设置一个默认选项，在index重复时是否drop它。

#### 2.3.5.2.Compound Indexes and Indexing sub documents

混合索引(compound)可以通过embedded field实现。

#### 2.3.5.3.Geospatial indexes

pass...

#### 2.3.5.4.Time To Live indexes

有一种特殊的索引类型，允许你在一个给定的周期内自动的将集合中的数据过期：

```python
class Session(Document):
    created = DateTimeField(default=datetime.now)
    meta = {
        'indexes': [
            {'fields': ['created'], 'expireAfterSeconds': 3600}
        ]
    }
```

#### 2.3.5.5.Comparing Indexes

使用`mongoengine.Document.compare_indexes()`可以比较数据库中的真实索引和Document定义的索引。

### 2.3.6.Ordering

默认的排序也可以在meta中指定(`ordering`)，在`QuerySet`构成后将会变为默认的排序，但是之后可以使用`order_by()`来覆盖：

```python
from datetime import datetime


class BlogPost(Document):
    title = StringField()
    published_date = DateTimeField()
    
    meta = {
        "ordering": ['-published_date']
    }


blog_post_1 = BlogPost(title="Blog Post #1")
blog_post_1.published_date = datetime(2010, 1, 5, 0, 0 ,0)

blog_post_2 = BlogPost(title="Blog Post #2")
blog_post_2.published_date = datetime(2010, 1, 6, 0, 0 ,0)

blog_post_3 = BlogPost(title="Blog Post #3")
blog_post_3.published_date = datetime(2010, 1, 7, 0, 0 ,0)

blog_post_1.save()
blog_post_2.save()
blog_post_3.save()

# 使用默认排序，获取"first"BlogPost
latest_post = BlogPost.objects.first()
assert latest_post.title == "Blog Post #3"

# 覆盖默认的排序
first_post = BlogPost.objects.order_by('+published_date').first()
assert first_post.title == "Blog Post #1"
```

### 2.3.7.Shard keys

如果你的集合已经sharded了，你需要将shard key以元组形式传入：

```python
class LogEntry(Document):
    machine = StringField()
    app = StringField()
    timestamp = DateTimeField()
    data = StringField()
    
    meta = {
        "shard_key": ("machine", "timestamp", )
    }
```

### 2.3.8.Document inheritance

```python
# Stored in a collection named 'page'
class Page(Document):
    title = StringField(max_length=200, required=True)

    meta = {'allow_inheritance': True}

# Also stored in the collection named 'page'
class DatedPage(Page):
    date = DateTimeField()
```

#### 2.3.8.1.Working with existing data

只需定义和现存的collection相符的schema并加入meta属性`collection`即可:

```python
class Page(Document):
    title = StringField(max_length=200, required=True)
    meta = {
        "collection": "cmsPage"
    }
```

### 2.3.9.Abstract classes

如果你想为一组Document类加入一些功能，但是并不想基类被定义为集合，可以设置meta数据`abstract`:

```python
class BaseDocument(Document):
    meta = {
        'abstact': True,
    }

    def check_permissions(self):
        # ...


class User(BaseDocument):
    # ...
```

## 2.4.Documents Instances

可以通过构造器创建一个Document实例:

```python
>>> page = Page(title='Test Page')
>>> page.title
'Test Page'
```

然后可以对实例属性重新赋值：

```python
>>> page.title = "Example Page"
>>> page.title
'Example Page'
```

### 2.4.1.Saving and deleting documents

MongoEngine追踪document的改动。想要把数据保存到数据库，可以使用`save()`方法。如果数据库中没有，则会新建。如果已经存在，则会自动更新修改的部分。例如:

```python
>>> page = Page(title="Test Page")
>>> page.save()  # Performs an insert
>>> page.title = "My Page"
>>> page.save()  # Performs an atomic set on the title field.
```

#### 2.4.1.1.Pre save data validation and cleaning

MongoEngine允许你创建自定义的清理规则(`clean()`方法)，在调用`save()`后调用这些规则。

```python
class Essay(Document):
    status = StringField(choices='Published', 'Draft'), required=True)
    pub_date = DateTimeField()

    def clean(self):
        if self.status == 'Draft' and self.pub_date is not None:
            msg = 'Draft entries should not have a publication date.'
            raise ValidationError(msg)
        if self.status == 'Published' and self.pub_date is None:
            self.pub_date = datetime.now()
```

#### 2.4.1.2.Cascading Saves

如果你的Document包含`GenericReferenceField`或`ReferenceField`，可以在`save()`时候传入`cascade=True`，让它们一起保存，而不是单独对每个对象都save()一下。

#### 2.4.1.3.Deleting documents

想要删除一个document，调用`.delete()`即可。但是要确保它已经存在于数据库并且有一个合法的`id`.

### 2.4.2.Document IDs

数据库中的每个document都有一个唯一的ID：

```python
>>> page = Page(title="Test Page")
>>> page.id
>>> page.save()
>>> page.id
ObjectId('123456789abcdef000000000')
```

另外，你可以自行定义主键。MongoDB会把这个字段作为id：

```python
>>> class User(Document):
...     email = StringField(primary_key=True)
...     name = StringField()
...
>>> bob = User(email='bob@example.com', name='Bob')
>>> bob.save()
>>> bob.id == bob.email == 'bob@example.com'
True
```

`.pk`属性是`.id`的一个别称:

```python
>>> page = Page(title="Another Test Page")
>>> page.save()
>>> page.id == page.pk
True
```

## 2.5.Querying the database

`Document`有一个`objects`属性，它是一个`QuerySetManager`对象，可以创建并返回一个新的`QuerySet`对象以供访问。`QuerySet`是可迭代对象:

```python
# 打印数据库中所有用户的名称
for user in User.objects:
    print(user.name)
```

> 注意
>
>> MongoEngine0.8以后默认会利用本地缓存，迭代QuerySet多次也只消耗了一个QuerySet，如果想不用缓存，可以调用`no_cache`.

### 2.5.1.Filtering queries

调用`QuerySet`对象可以进一步筛选要查询的结果:

```python
# 下面这条语句会返回一个新的QuerySet，它会筛选出`country`字段是`uk`的document
uk_users = User.objects(country='uk')
```

embedded document也可以查询，可以使用一种特殊的lookup语法，用两个下划线来代替属性访问的点(dot):

```python
# 这条筛选会过滤出作者的国家为'uk'的page
uk_pages = Page.objects(author__country='uk')
```

> 如果字段和mongodb的操作符名称有冲突，比如`type, lte...`，在查询的时候加入两个下划线后缀即可。

### 2.5.2.Query operators

操作符可以以后缀的形式(两个下划线，然后是操作符名称)出现在lookup语法中:

```python
# 查找年龄少于等于18的user
young_users = User.objects(age__lte=18)
```

可用的操作符包括：

- `ne` - 不等
- `lt` - 小于
- `lte` - 小于等于
- `gt` - 大于
- `gte` - 大于等于
- `not` - 否定操作符，可以用在另一个操作符之前，比如`Q(age__not__mod=5)`
- `in` - list包含该值(s)
- `nin` - list不包含该值(s)
- `mod` - mod操作符
- `all` - list的值和给定的参数完全相等
- `size` - 数组的大小
- `exists` - 这个字段是否有值存在

#### 2.5.2.1 String queries

下面的操作符是各种正则表达式的快捷方式(并不是真实的mongodb操作符)：

- `exact` - 字符串字段完全一致
- `iexact` - 字符串字段完全一致(不区分大小写)
- `contains` - 字符串字段包含该值
- `icontains` - 字符串字段包含该值(不区分大小写)
- `startswith` - 字符串字段开始的值
- `istartswith` - 字符串字段开始的值(不区分大小写)
- `endswith` - 字符串字段结尾的值
- `idenswith` - 字符串字段结尾的值(不区分大小写)
- `match` - 使用`$elemMatch`,你可以匹配一个数组中的所有元素

#### 2.5.2.2 Geo queries

pass

#### 2.5.2.3 Querying lists

对于`ListField`，如果提供单个值，会判断是否list中包含这个item：

```python
class Page(Document):
    tags = ListField(StringField())


# 这条语句会查询所有在tags list中包含'coding'的page
Page.objects(tags='coding')
```

也可以按list中的索引位置来查询。比如，你想要查询tags list第一个位置为db的pages:

```python
Page.objects(tags__0='db')
```

如果你只是想要list中的一部分。比如：你想要让一个list分页，那么需要使用`slice`操作符:

```python
# comments -- skip 5, limit 10
Page.objects.fields(slice__comments=[5, 10])
```

想要更新这个的document，如果你知道它在list中的位置，可以用`$`操作符:

```python
Post.objects(comment_by='joe').update(
    **{'inc__comments_$_votes': 1}
)
```

也可以使用大写`S`:

```python
Post.objects(comment_by='joe').update(inc__comments__S__votes=1)
```

#### 2.5.2.4.Raw queries

如果想要使用原生的MongoDB查询语句，可以传入`__raw__`关键字参数:

```python
Page.objects(__raw__={"tags": "coding"})
```

### 2.5.3.Limiting and skipping results

可以对`QuerySet()`对象使用`limit()`和`skip()`方法，不过更推荐直接使用列表切片语法：

```python
# 前5个people
users = User.objects[:5]

# 前5个之后的所有people
users = User.objects[5:]

# 从第11个开始，找5个people
users = User.objects[10:15]
```

如果没有数据存在，将会抛出`IndexError`:

```python
>>> # Make sure there are no users
>>> User.drop_collection()
>>> User.objects[0]
IndexError: list index out of range
>>> User.objects.first() == None
True
>>> User(name='Test User').save()
>>> User.objects[0] == User.objects.first()
True
```

#### 2.5.3.1.Retrieving unique results

如果一个数据在collection中是唯一的，可以使用`.get()`来获取它。如果没有相匹配的document，会抛出`DoesNotExist`错误。如果有多个值匹配，将会抛出`MultipleObjectsReturned`.这些异常已经定义在Document中了，比如`MyDoc.DoesNotExist`.

### 2.5.4.Default Document queries

默认的`objects`属性会返回一个不经过任何筛选的`QuerySet`，但是你可以通过`queryset_manager()`**装饰器**来定义新的`QuerySetManager`:

```python
class BlogPost(Document):
    title = StringField()
    date = DateTimeField()

    @queryset_manager
    def objects(doc_cls, queryset):
        return queryset.order_by('-date')
```

```python
class BlogPost(Document):
    title = StringField()
    published = BooleanField()

    @queryset_manager
    def live_posts(doc_cls, queryset):
        return queryset.filter(published=True)


BlogPost(title='test1', published=False).save()
BlogPost(title='test2', published=True).save()
assert len(BlogPost.objects) == 2
assert len(BlogPost.live_posts) == 1
```

### 2.5.5.Custom QuerySets

可以自定义`QuerySet`，然后通过自定meta属性`queryset_class`的方式指定给Document:

```python
class AwesomeQuerySet(QuerySet):
    
    def get_awesome(self):
        return self.filter(awesome=True)


class Page(Document):
    meta = {
        "queryset_class": AwesomeQuerySet
    }


Page.objects.get_awesome()
```

### 2.5.6.Aggregation

#### 2.5.6.1.Counting results

使用`.count()`:

```python
num_users = User.objects.count()
```

`len()`会取回所有的数据，而`.count()`利用了MongoDB的聚集函数，所以后者速度快的多。

#### 2.5.6.2.Further aggregation

你可能想计算某个字段的总和:

```python
yearly_expense = Employee.objects.sum('salary')
```

计算平均值:

```python
mean_age = User.objects.average('age')
```

MongoEngine提供了一个helper方法，可以获取list中的item在整个集合中出现的频率 -- 这个方法即`item_frequencies()`。比如可以用它来生成标签云:

```python
class Article(Document):
    tag = ListField(StringField())


# 假设已经生成了若干有tag的article
tag_freqs = Article.objects.item_frequencies('tag', normalize=True)

from operator import itemgetter
top_tags = sorted(tag_freqs.items(), key=itemgetter(1), reverse=True)[:10]
```

### 2.5.7.Query efficiency and performance

#### 2.5.7.1.Retrieving a subset of fields

```python
>>> class Film(Document):
...     title = StringField()
...     year = IntField()
...     rating = IntField(default=3)
...
>>> Film(title='The Shawshank Redemption', year=1994, rating=5).save()
>>> f = Film.objects.only('title').first()
>>> f.title
'The Shawshank Redemption'
>>> f.year      # 没有值
>>> f.rating    # 因为没有请求rating,使用默认值
3
```

如果你之后需要另外的字段，只需要对这个对象调用`.reload()`即可.

#### 2.5.7.2.Getting related data

pass

#### 2.5.7.3.Turning off dereferencing

pass

### 2.5.8.Advanced queries

`Q`代表query的一部分，想要构建一个负载的query，你可以使用`&`(and)或者`|`(or)来组合`Q`对象：

```python
from mongoengine.queryset.visitor import Q

# Get published posts
Post.objects(Q(published=True) | Q(publishe_date__lte=datetime.now()))

# Get top posts
Post.objects(Q(featured=True) & Q(hits__gte=1000) | Q (hits__gte=5000))
```

### 2.5.9.Atomic updates

Documentk可以通过方法: `update_one()`, `update()`, `modify()`来原子更新.下面是更新可用的修饰符:

- `set` - 设置一个特定值
- `unset` - 删除一个特定值
- `inc` - 通过给定的amount增量这个值
- `dec` - 通过给定的amount减量这个值
- `push` - 将一个值推送到list中
- `push_all` - 将多个值推送到list中
- `pop` - 移除list首/尾的第一个值
- `pull` - 从list中移除一个值
- `pull_all` - 从list中移除多个值
- `add_to_set` - 如果list中没有该值，将它加入

原子更新的语法很像查询语法，不过修饰符放在了前面:

```python
>>> post = BlogPost(title='Test', page_views=0, tags=['database'])
>>> post.save()
>>> BlogPost.objects(id=post.id).update_one(inc__page_views=1)
>>> post.reload()   # 这个doc修改了，需要重新读区
>>> post.page_views
1
>>> BlogPost.objects(id=post.id).update_one(set_title='Example Post')
>>> post.reload()
>>> post.title
'Example Post'
>>> BlogPost.objects(id=post.id).update_one(push__tags='nosql')
>>> post.reload()
>>> post.tags
['database', 'nosql']
```

如果没有指定修饰符，会默认使用`$set`，所以以下语句是一样的:

```python
>>> BlogPost.objects(id=post.id).update(title='Example Post')
>>> BlogPost.objects(id=post.id).update(set__title='Example Post')
```

另外可以加入索引，以后缀的形式。如`push__tags__0`...

### 2.5.10.Server-side javascript execution

服务器端的JS函数可以通过`.exec_js()`来执行。

## 2.6.GridFS

pass

## 2.7.Signals

pass

## 2.8.Text Search

`.search_text()`方法...

pass

## 2.9.Use mongomock for testing

https://github.com/vmalloc/mongomock/



