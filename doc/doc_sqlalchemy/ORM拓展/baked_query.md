# Baked Queries

`baked`为`Query`对象提供了一套可供替代的创建模式，可以缓存对象的创建和字符串编译的步骤。这意味着，对于一个特定的要使用多次的`Query`创建场景，所有Python函数调用这个查询会发出SQL时只会进行一次初始化过程。

这个系统能够大幅度减少**SQL发出前**Python解释器的开销。"baked"系统的缓存并**没有**减少SQL调用的次数，**也没有缓存返回结果**.想要缓存结果需要使用`Dogpile Caching`技术.


> 注意
>> `sqlalchemy.ext.baked`扩展并不是为新手准备的。想要正确的使用它需要对SQLAlchemy有深入的理解。这个扩展在一般情况下面也用不上。另外再次强调：**它不是用来缓存查询的**(只是用来缓存SQL字符串的构造过程).

## 概要

baked系统的用法需要从所谓的`bakery`开始，它代表一个特定的查询对象序列的存储体：

```python
from sqlalchemy.ext improt baked

bakery = baked.bakery()
```

上面的**bakery**将会使用LRU算法存储默认200个元素，注意在查询时一个ORM查询通常包含一个entry，以及每个entry对应一个数据库dialect的SQL字符串。

bakery允许我们通过一系列的Python可调用对象来创建一个Query对象，通常是使用`lambda`匿名函数：

```python
from sqlalchemy import bindparam


def search_for_user(session, username, email=None):
    
    baked_query = bakery(lambda session:session.query(User))
    baked_query += lambda q: q.filter(User.name == bindparam('username'))
    
    baked_query += lambda q: q.order_by(User.id)

    if email:
        baked_query += lambda q: q.filter(User.email == bindparam('email'))

    result = baked_query(session).params(username, email=email).all()
```

上面代码有以下值得注意的点：

1. `baked_query`对象是一个`BakedQuery`实例。这个对象本质上是`Query`对象的一个"建造者(builder)"，但它也不是一个真正的`Query`对象.
2. 一开始真正的`Query`对象还没有被创建，直到函数末尾调用`Result.all()`.
3. 上面步骤中自追加的`baked_query`对象都是以Python函数形式存在，一般是lambda.第一个lambda接收了一个`Session`作为它的参数。接下来的lambda都接受一个`Query`作为它的参数。
4. 在上面的代码中，即使我们的应用调用了多次`search_for_user()`，所有的lambda都只会被调用一次。只要查询已经缓存在bakery中，所有的**lambda**都不会被调用多次.
5. 缓存的实现通过引用**lambda对象**作为缓存键；也就是说会根据传入参数不同来缓存多个对象，比如上面例子中，`search_for_user()`指定了参数`email`,将会把lambda`lambda q: q.filter(User.email == bindparam('email'))`作为缓存键的一部分存储。当没有指定参数`email`时，就不会加入这部分lambda作为缓存键.
6. 因为lambda只会被调用一次,本质上lambda中的变量部分不能发生改变。而是把SQL字符串中的绑定值作改变，我们使用`bindparam()`来构建命名参数，然后在晚些时候通过`Result.params()`来传入参数。


## 性能

baked查询可能看起来有些古怪&笨拙&啰嗦。然而，它可以大幅降低Python编译SQL字符串时的性能压力。下面的例子可以比较用了baked和没用之间的性能差异。

这是没有使用baked的查询：

```python
session = Session(bind=engine)
for id_ in ramdom.sample(ids, n):
    session.query(Customer).filter(Customerid == id_).one()
```

下面是使用了baked的查询：

```python
bakery = baked.bakery()
s = Session(bind=engine)
for id_ in random.sample(ids, n):
    q = bakery(lambda s: s.query(Customer))
    q += lambda q: q.filter(Cusomter.id == bindparam('id'))
    q(s).params(id=id_).one()
```

下面是各调用一万次时的函数调用次数比较：

```python
test_baked_query:   test a baked query of the full entity.
                    (10000 iterations); total fn calls 1951294.
                    
test_orm_query: test a straight ORM query of the full entity.
                (10000 iterations); total fn calls 7900535.
```

下面是用时的比较：

```python
test_baked_query:   test a baked query of the full entity.
                    (10000 iterations); total time 2.174126 sec

test_orm_query:     test a straight ORM query of the full entity.
                    (10000 iterations); total time 7.958516 sec
```

注意只测试了针对一行结果的情况。如果查询返回多行，baked查询的性能优势将会少的多。再次强调**baked查询只是用来创建查询本身，不是用来取回结果**.使用baked特性并不能保证应用能够更快；只有在确定应用具有众多SQL编译开销时才有用。


## 基本原理

上面例子中的lambda方法只是baked查询传统"参数化"使用方法的一个超集.假设我们想创建一个简单的系统，我们想要只创建一个`Query`，然后把存入字典以备之后使用。只需要把查询创建完毕，再移除`Session`即可。通过`my_cache_query = query.with_session(None)`来实现:

```python
my_simple_cache = {}


def lookup(session, id_argument):
    if "my_key" not in my_simple_cache:
        query = session.query(Model).filter(Model.id == bindparam('id'))
        my_simple_cache['my_key'] = query.with_session(None)
    else:
        query = my_simple_cache['my_key'].with_session(session)
    return query.params(id=id_argument).all()
```

上面的方法可以让我们获得很小的性能优势。为了重用`Query`，我们通过`session.query(Model).filter(Model.id == bindparam('id'))`来构建查询，这会在`Query.filter()`时跳过Core表达式的构建.但是在每次调用`Query.all()`的时候还是会重新生成整个`Select`对象.

想要减少额外的开销，我们需要一些额外的逻辑,需要缓存select对象的构建.让我们假定我们实现了一个`bake`方法，可以对Query预先编译SQL:

```python
my_simple_cache = {}


def lookup(session, id_argument):
    if "my_key" not in my_simple_cache:
        query = session.query(Model).filter(Model.id == bindparam('id'))
        my_simple_cache['my_key'] = query.with_session(None).bake()
    else:
        query = my_simple_cache['my_key'].with_session(session)
    return query.params(id=id_argument).all()
```

上面的代码解决了性能瓶颈，但是还有个字符串缓存键需要处理.

我们可以使用“bakery"方法来重构:

```python
bakery = baked.bakery()


def lookup(session, id_argument):
    def create_model_query(session):
        return session.query(Model).filter(Model.id == bindparam('id'))
        
    parameterized_query = bakery.query(create_model_query)
    return parameterized_query(session).params(id=id_argument).all()
```

上面例子中，我们使用"baked"系统来简化"缓存一个query"的系统。然而，它使用的代码要少上两行,不需要一个硬编码"my_key".

同样对于上面例子来说，如果我们问自己"要如何通过条件来选择查询?",应该怎么解决呢:

```python
my_simple_cache = {}


def lookup(session, id_argument, include_frobnizzle=False):
    if include_frobnizzle:
        cache_key = "my_key_with_frobnizzle"
    else:
        cache_key = "my_key_without_frobnizzle"

    if cache_key not in my_simple_cache:
        query = (session.query(Molde)
                        .filter(Molde.id == bindparam('id')))
        if include_frobnizzile:
            query = query.filter(Model.frobnizzle == True)
        my_simple_cache[cache_key] = query.with_session(None).bake()
    else:
        query = my_simple_cahce[cache_key].with_session(session)

    return query.params(id=id_argument).all()
```

我们可以把上面的例子通过bakery来简化：

```python
bakery = baked.bakery()


def lookup(session, id_argument, iclude_frobnizzle=False):
    def create_model_query(session):
        return session.query(Model).filter(Model.id == bindparam('id'))

    parameterized_query = bakery.query(create_mode_query)

    if include_frobnizzle:
        def include_frobnizzle_in_query(query):
            return query.filter(Model.frobnizzle == True)
        
        parameterized_query = parameterized_query.with_criteria(
            include_frobnizzle_in_query
        )
    
    return paramterized_query(session).params(id=id_argument).all()
```

这些代码仍然很啰嗦。我们可以考虑将方法`BakedQuery.add_criteria()`和`BakedQuery.with_criteria()`简化为操作符,并且推荐使用简单的lambda:

```python
bakery = baked.bakery()


def lookup(session, id_argument, include_frobnizzle=False):
    parameterized_query = bakery.bake(
        lambda s: s.query(Model).filter(Model.id == bindparam('id'))
    )
    
    if include_frobnizzle:
        parameterized_query += lambda q: q.filter(Model.frobnizzle == True)

    return paramterized_query(session).params(id=id_argument).all()
```

