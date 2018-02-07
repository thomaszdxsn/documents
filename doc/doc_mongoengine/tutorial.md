# 1.Tutorial

这篇教程教你创建一个**Tumblelog**应用，**Tumblelog**是一个blog，支持多媒体内容，包括文本、图片、链接、视频、音频等。

## 1.1.Getting started

首先安装`mongoengine`:

`pip install mongoengine`

然后我们需要连接`mongod`。可以使用`connect()`方法，如果是本地运行，我们只需要提供MongoDB的数据库名称即可:

```python
from mongoengine import *
connect('thumblelog')
```

## 1.2.Defining our documents

MongoDB是无schema的，意思就是不必对数据库指定schema。

我们的**Tumblelog**主要有若干不同的`user` collection，不同类型的`post` collection，以及和`post`关联的`tag`，`comment`.

### 1.2.1 Users

我们可以定义一个User可能包含的字段(这并不算真正的schema):

```python
class User(Document):
    email = StringField(required=True)
    first_name = StringField(max_length=50)
    last_name = StringField(max_length=50)
```

这个类schema的结构和MongoDB没有关系，它只是一个应用层的schema，可以方便之后的改动和管理。另外`User` docuement会存放在一个MongoDB Collection中，而不是存放在一个数据表。

### 1.2.2 Posts, Comments and Tags

为了存储我们需要的信息，如果我们使用的是关系型数据库，我们还需要定义一个`posts`表，一个`comments`，和一个`tags`表。我们需要在`comments`表中放入一个外键以和`posts`表相关联。我们还需要一个中间表，帮助建立`tags`和`posts`之间的多对多关系。

#### 1.2.2.1 Posts

很幸运Mongo不是关系型数据库，所以我们不必那么麻烦。为了支持不同类型的Post，我们可以利用OOP的继承。建立一个基类`Post`，然后继承它分别实现`TextPost`, `ImagePost`, `LinkPost`.想要在MongoEngine中这么做，你需要开启继承，即在`meta`中设置`allow_inheritance`为`True`:

```python
class Post(Document):
    title = StringField(max_length=120, required=True)
    author = ReferenceField(User)

    meta = {
        "allow_inheritance": True
    }


class TestPost(Post):
    content = StringField()


class ImagePost(Post):
    image_path = StringField()


class LinkPost(Post):
    link_url = StringField()
```

我们使用`ReferenceField`对象来存储post作者的引用。这很像传统ORM的外键。

#### 1.2.2.2 Tags

怎么让`tags`关联`posts`呢？MongoDB原生支持存储list数据结构：

```python
class Post(Document):
    title = StringField(max_length=120, required=True)
    author = ReferenceField(User)
    tags = ListField(StringField(max_length=30))
```

`ListField`接收的第一个参数即定义它的类型。

#### 1.2.2.3 Comments

`comments`通常关联一个`post`.使用MongoDB我们可以将`Comment`以`embedded documents`的形式直接存储在一个`post document`中。embedded document和一般的document没有什么不同，只不过它在数据库中没有属于自己的集合罢了:

```python
class Comment(EmbeddedDocument):
    content = StringField()
    name = StringField(max_length=120)
```

可以在我们的`Post Document`中存储`Comment Document`的list.

```python
class Post(Document):
    title = StringField(max_length=120, required=True)
    author = ReferenceField(User)
    tags = ListField(StringField(max_length=30))
    comments = ListField(EmbeddedDocumentField(Comment))
```

##### Handling deletions of references

`ReferenceField`对象接受关键字参数`reverse_delete_rule`用来处理集联删除.如果像下面这样设置，在删除user的时候会把它的所有posts都删除:

```python
class Post(Document):
    title = StringField(max_length=120, required=True)
    author = ReferenceField(User, reverse_delete_rule=CASCADE)
    tags = ListField(StringField(max_length=30))
    comments = ListField(EmbeddedDocumentField(Comment))
```

## 1.3 Adding data to our Tumblelog

让我们试着对数据库插入一些数据。首先，我们需要创建一个`User`对象:

```python
ross = User(
    email='ross@example.com',
    first_name='Ross',
    last_name='Lawley'
).save()
```

> 也可以使用属性赋值的方式定义User
>
>> ```python
>> ross = User(email='ross@example.com')
>> ross.first_name='Ross'
>> ross.last_name='Lawley'
>> ross.save()
>> ```


假定我们已经像上面一样定义了另一个用户`john`.

现在我们从数据库中获取了user信息，让我们加入一下posts:

```python
post1 = TextField(title='Fun with MongoEngine', author=john)
post1.content = 'Took a look at MongoEngine today. looks pretty cool.'
post1.tags = ['mongodb', 'mongoengine']
post1.save()

post2 = LinkPost(title='MongoEngine Documentation', author=ross)
post2.link_url = 'http://docs.mongoengine.com/'
post2.tags = ['mongoengine']
post2.save()
```

> 如果你修改一个已经创建的对象并再次调用`.save()`方法，会使用`update`对它更新.

## 1.4 Accessing our data

怎样访问数据库中posts呢？每个继承`Document`的类都有一个`objects`数据，可以使用它来访问数据库集合:

```python
for post in Post.objects:
    print(post.title)
```

### 1.4.1 Retrieving type-specific information

上面语句可以打印每条post的标题。那么如何访问特定类型的数据(比如link_url, content等等)？简单的办法就是直接访问子类的`objects`属性:

```python
for post in TextPost.objects:
    print(post.content)
```

但是还有更通用的办法，判断对象是哪个类的实例:

```python
for post in Post.objects:
    print(post.title)
    print('=' * len(post.title))

    if isinstance(post, TextPost):
        print(post.content)
    
    if isinstance(post, LinkPost):
        print("Link: {}".format(post.link_url))
```

### 1.4.2 Searching our posts by tag

`Document`的`objects`属性其实是一个`QuerySet`对象。这是一个惰性的查询对象，你可以对它进行进一步的筛选：

```python
for post in Post.objects(tags='mongodb'):
    print(post.title)
```

另外`QuerySet`还有若干结果方法，比如调用`first()`返回第一个结果。`QuerySet`对象使用聚集函数:

```python
num_posts = Post.objects(tags='mongodb').count()
print("Found {} posts with tag 'mongodb'".format(num_posts))
```

### 1.4.3 Learning more about MongoEngine