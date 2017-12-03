[TOC]

## Session API

### Session和sessionmaker()

- `sqlalchemy.orm.session.sessionmaker(bind=None, class_=<class 'sqlalchemy.orm.session.Session'>, autoflush=True, autocommit=False, expire_on_commit=True, info=None, **kw)`

    基类： `sqlalchemy.orm.session._SessionClassMethods`

    一个可配置的`Session`工厂。

    这个`sessionmaker`会在被调用后返回新的`Session`对象，使用建立时给定的参数来配置。

    例如：

    ```python
    # 全局域
    Session = sessionmaker(autoflush=False)

    # 然后，在一个局部域中，使用它来创建一个局部session
    session = Session()
    ```

    传入这个构造器的关键字参数将会覆盖“configured”关键字：

    ```python
    Session = sessionmaker()

    # 绑定一个单独的session到一个连接
    session = Session(bind=connection)
    ```

    这个类同样包含一个方法`configure()`，它可以为工厂指定额外的关键字参数，它会影响之后生成的Session对象。一般用于关联多个engine对象：

    ```python
    # 应用启动
    Session = sessionmaker()
    
    # ...之后的某个时候
    engine = create_engine('sqlite:///foo.db')
    Session.configure(bind=engine)

    session = Session()
    ```

    方法：

    - `__call__(**local_kw)`

        使用sessionmaker的配置参数生成一个新的`Session`对象。

        在Python中，`__call__`这个魔术方法可以通过函数调用的方式调用一个对象。

        ```python
        Session = sessionmaker()
        session = Session()     # 调用了sessionmaker.__call__()
        ```

    - `__init__(bind=None, class_=<class 'sqlalchemy.orm.session.Session'>, autoflush=True, autocommit=False, expire_on_commit=True, info=None, **kw)`

        构建一个新的`sessionmaker`.

        除了`class_`以外的所有参数都会直接传入Session。可以查看`Session.__init__()`的docstring获得更多细节。

        参数：

        - `bind`: 一个`Engine`或者`Connectable`对象，它将会关联新创建的Session对象。
        - `class_`: 用于创建新的Session对象的类。默认为`Session`.
        - `autoflush`: 新创建的Session对象的autoflush配置。
        - `autocommit`: 新创建的Session对象的autocommit配置。
        - `expire_on_commit=True`: 新创建的Session对象的expire_on_commit配置。
        - `info`: 可选的信息参数(字典), 可以通过`Session.info`来获取。注意对一个Session的info参数操作时，字典会被更新而不是替换。
        - `**kw`: 所有其它传入Session对象的关键字参数。

    - `close_all()`

        继承自`_SessionClassMethods.close_all()`方法.

        关闭内存中的所有session。

    - `configure(**new_kw)`

        重新设置这个sessionmaker的参数。

        例如:

        ```python
        Session = sessionmaker()
        Session.configure(bind=create_engine("sqlite://"))
        ```

    - `identity_key(*args, **kwargs)`

        继承自`_SessionClassMethods.identity_key()`方法.

        返回一个标识键。

        这个方法是`util.identity_key()`的别称。

    - `object_session(instance)`

        继承自`_SessionClassMethods.object_session()`方法.

        返回一个对象属于的Session。

        这个方法是`object_session()`的别称。

- `sqlalchemy.orm.session.Session(bind=None, autoflush=True, expire_on_commit=True, _enable_transaction_accounting=True, autocommit=False, twophase=False, weak_identity_map=True, binds=None, extension=None, enable_baked_queries=True, info=None, query_cls=<class 'sqlalchemy.orm.query.Query'>)`

    基类: `sqlalchemy.orm.session._SessionClassMethods`

    管理ORM映射对象的持久化操作。

    方法：

    - `__init__(bind=None, autoflush=True, expire_on_commit=True, _enable_transaction_accounting=True, autocommit=False, twophase=False, weak_identity_map=True, binds=None, extension=None, enable_baked_queries=True, info=None, query_cls=<class 'sqlalchemy.orm.query.Query'>)`

        构建一个新的Session。

        参数：

        - `autocommit`

            > 警告
            >
            >> `autocommit`**并不是用于一般用途**，查询应该在`Session.begin()`/`Session.commit()`之间调用。在事务界限之外调用查询是一个旧的用法，在一些情况可以导致并发连接checkouts。
            
            默认为False.当设置为True时，Session不会保持持久化事务。当使用这个模式时，需要显示调用`Session.begin()`。

        - `autoflush`

            当设置为True时，所有的query操作都会在处理前对Session调用一次`flush()`.这是一个惯例特性，所以`flush()`不需要反复调用。一般情况下`autoflush`需要组合`autocommit=False`使用。在这个场景下，不需要显式调用`flush()`，一般只需要在结束时调用一次`commit()`即可。

        - `bind`

            可选Session应该绑定的一个Engine或者Connection。当指定这个参数时，所有对这个session执行的SQL操作都会在这个可连接对象上面执行。

        - `binds`

            一个可选的字典参数，它可以包含相比`bind`参数更加细粒度的“bind”信息。这个字典可以用来单独映射`Table`实例以及`Mapper`实例关联一个单独的`Engine`或者`Connection`对象。用法类似于：

            ```python
            Session = sessionmaker(binds={
                SomeMappedClass: create_engine("postgresql://engine1"),
                somemapper: create_engine("postgresql://engine2"),
                some_table: create_engine("postgresql://engine3")
            })
            ```
        
        - `class_`

            指定一个代替`sqlalchemy.orm.session.Session`的类，用来作为返回的结果。这个参数位于`sessionmaker`函数，直接传入Session构造器并没有意义。

        - `enable_baked_queries`

            默认为True。这个参数被`sqlalchemy.ext.baked`扩展消耗。当设置为False时，所有的缓存都会被禁用，将这个参数设置为False能大幅度减少内存的使用率。

        - `_enable_baked_queries`

            默认为True。

        - `expire_on_commit`

            默认为True。当这个参数为True时，在每次`commit()`以后，所有的对象都会过期，所以这时所有的属性/对象都会使用最近的数据库状态。

        - `extension`

            一个可选的`SessionExtension`实例，或者一个扩展实例的列表，它会接收commit/flush前后的事件，以及rollback以后的事件。已经废弃，请看`SessionEvents`。

        - `info`

            可选的一个字典参数，存储和Session关联的任意数据。可以通过`Session.info`属性来访问。注意这个字典在构建时被拷贝。所以在每个Session中对info的改动都是局部的。

        - `query_cls`

            用于创建新Query对象的类，也是`query()`对象返回的对象。默认为Query。

        - `twophase`

            当设置为True时，所有的事务都将以“two phase"事务形式开启。

        - `weak_identity_map`

            默认为True。当设置为False时，放置在Session中的对象将会是强引用，除非显式移除或者Session关闭。已经**废弃**

    - `add(instance, _warn=True)`

        将一个对象放置入`Session`中。

        在下次flush操作时，它的状态将会被持久化至数据库。

        重复的调用`add()`将会被忽略。和`add()`相对立的方法是`expunge()`。

    - `add_all(instances)`

        将给定的实例集合加入到`Session`中。

    - `begin(subtransactions=False, nested=False)`

        在这个Session中开启一个事务。

        如果Session已经在一个事务中，这个方法将会抛出一个错误，除非指定`subtransactions`或者`nested`被指定。

        参数：

        - `subtransactions`: 如果为True，指明`begin()`可以创建一个“子事务”
        - `nested`: 如果为True，开启一个SAVEPOINT事务，它等同于调用`begin_nested()`.

        返回：

        返回`SessionTransaction`对象。注意`SessionTransaction`实现了Python的上下文管理器语法。

    - `begin_nested()`

        在Session中开启一个“nested(嵌套)"事务。也就是SAVEPOINT。

        目标数据库和相关Python驱动必须支持SQL SAVEPOINT。

        返回：

        返回`SessionTransaction`。

    - `bind_mapper(mapper, bind)`

        将一个`Mapper`和一个`bind`相关联， `bind`即一个`Engine`或者`Connection`。

        给定的mapper将会加入到字典中，使用`Session.get_bind()`方法可以查询到它。

    - `bind_table(table, bind)`

        将一个`Table`和一个`bind`相关联， `bind`即一个`Engine`或者`Connection`。

        给定的Table将会加入到字典中，使用`Session.get_bind()`方法可以查询到它。

    - `bulk_insert_mappings(mapper, mappings, return_defaults=False, render_nulls=False)`

        将给定的映射列表执行一次批量插入。

        批量插入特性允许普通的Python字典简单INSERT操作的资源，可以更简单的分组执行高性能的"executemany"操作。使用字典，就无法使用状态管理特性，如果是一些简单的row，数量也相当大的话，可以使用这个方法来减少延迟。

        字典的值将会无修改的传入Core的`Insert()`构造。

        参数：

        - `mapper`: 一个映射类，或者一个真正的`Mapper`对象，代表映射列表的一种对象。

        - `mappings`: 一个字典列表，每个字典都会包含插入映射行的状态。

        - `return_defaults`: 当设置为True时，row中缺失的值都会以default值来替代。

        - `render_nulls`: 当设置为Ture时，一个值为None的值将会以NULL形式插入数据库。

    - `bulk_save_objects(objects, return_defaults=False, update_changed_only=True)`

        将一个对象列表执行批量保存。

        批量保存特性允许映射对象集合作为INSERT和UPDATE操作的资源，可以使用更高性能的“executemany“操作。

        对象不会被加入到Session中，也不会对它们建立额外的状态，除非设置了`return_default`参数为True，这个情况下主键和default值都会自动构成。

        参数：

        - `objects`

            一个映射对象实例的列表。映射对象将会被持久化，但是**不会**关联Session。

            对于每个对象，它是否发送INSERT或者UPDATE和Session传统操作的原理一样；如果对象的`InstanceState.key`属性已经设置，就会假定这个对象为detached状态，并发送一个UPDATE语句。否则就发送INSERT。

        - `return_defaults`

            当设置为True时，row中缺失的值可以使用默认值，主键值也可以生成。

        - `update_changed_only`

            当设置为True时，UPDATE语句将会根据属性的状态和变动而生成。如果设置为False，除了主键所有的属性都会生成在SET子句中。

    - `bulk_update_mappings(mapper, mappings)`

        对一个给定的字典列表执行一个批量更新操作。

        参数：

        - `mapper`: 一个映射类，或者一个Mapper对象。

        - `mappings`: 一个字典列表。

    - `close()`

        关闭这个Session。

        在处理时会清除所有的items，结束所有的事务。

        如果这个session通过`autocommit=False`创建，一个新的事务将会立即开启。注意这个新的事务不会使用任何连接资源，直到首次访问(懒加载).

    - `close_all()`

        关闭内存中的所有session.

    - `commit()`

        刷新待定的修改，然后提交当前事务。

        如果没有开启一个事务，将会抛出一个`InvalidRequestError`错误。

        默认情况下，在事务提交后`Session`将会把所有载入的状态过期。这个行为可以通过`expire_on_commit=False`来取消。

    - `connection(mapper=None, clause=None, bind=None, close_with_result=False, execution_options=None, **kw)`

        返回一个符合当前事务状态的Connection。

    - `delete(instance)`

        将一个实例标记为删除。

        数据库删除操作将会在flush()之后执行。

    - `deleted`

        Session中所有标记为删除状态的实例集合。

    - `dirty`

        所有被考虑为dirty的持久化实例集合。

        例如：

        ```python
        some_mapped_object in session.dirty
        ```

        实例被修改但不被标记为删除，即认为它是dirty。但是dirty的计算是“乐观的”，很多属性或集合的修改都会被标记为dirty，但是如果没有net修改，就不会发出SQL。

        想要检查属性是否真实修改，请使用`Session.is_modified()`方法。

    - `enable_relationship_loading(obj)`

        一个对象的关联对象读取后与Session的关联。

        > 警告
        >
        >> `enable_relationship_loading()`是为了几个特殊使用场景而存在的，不推荐一般用途来使用它。

    - `execute(clause, params=None, mapper=None, bind=None, **kw)`

        在当前事务中执行一个SQL构造体，或者执行一个SQL字符串。

        返回一个代表SQL语句执行结果的`ResultProxy`对象，和Engine以及Connection的效果一样。

        例如：

        ```python
        result = session.execute(
            user_table.select().where(user_table.c.id == 5)
        )
        ```

        `execute()`接收任何可执行语句构造，比如`select()`, `insert()`, `update()`, `delete()`, 和`text()`。SQL字符串也可以传入，这个字符串会用`text()`来包裹。

        例如下面这个例子：

        ```python
        result = session.execute(
            "SELECT * FROM user WHERE id=:param",
            {"param": 5}
        )
        ```

        等同于：

        ```python
        from sqlalchemy import text

        result = session.execute(
            text("SELECT * FROM user WHERE id=:param"),
            {"param": 5}
        )
        ```

        传入`session.execute()`的第二个位置参数是可选的参数集(SQL参数).等同于`Connection.execute()`的行为，是否传入一个字典或者一个字典列表，取决于DBAPI使用`execute()`还是`executemany()`.一个INSERT构造可以被单个row来调用：

        ```python
        result = session.execute(
            users.insert(), {"id": 7, "name": "somename"}
        )
        ```

        或者也可以插入多条row：

        ```python
        result = session.execute(users.insert(), [
            {"id": 7, "name": "somename7"},
            {"id": 8, "name": "somename8"},
            {"id": 9, "name": "somename9"}
        ])
        ```

        参数：

        - `clause`: 一个可执行的语句构造，或者一个可以执行的字符串SQL语句。

        - `params`: 可选的字典，或者字典列表，包含绑定的参数值。

        - `mapper`: 可选的`mapper()`或者映射类，用来标示合适的bind。

        - `bind`: 可选的可以用来bind的`Engine`.

        - `**kw`: 可选的关键字参数，将会传入到`Session.get_bind()`


    - `expire(instance, attribute_names=None)`

        过期一个实例的属性。

        标记一个实例的属性已经过期。

        参数：

        - `instance`: 想要过期的实例。

        - `attribute_names`: 可选的属性名称(字符串)列表，指定想要过期的实例属性子集。

    - `expire_all()`

        将这个Session中的所有持久化实例过期。

    - `expunge(instance)`

        将一个实例从Session中移除。

        这个操作将会释放实例的内部引用。将会根据expunge级联规则来应用级联。

    - `expunge_all()`

        将Session中的所有实例移除。

    - `flush(objects=None)`

        将所有对象的变化刷新到数据库。

        参数：

        - `objects`: 可选。限制刷新操作的集合。

    - `get_bind(mapper=None, clause=None)`

        返回这个Session绑定的"bind".

        "bind"通常是一个`Engine`实例，有时也可以是一个`Connection`.

        ...

    - `identity_key(*args, **kwargs)`

        返回一个indentity key。

        这个方法是`util.identity_key()`的别称。

    - `identity_map=None`

        一个对象识别的映射。

        通过迭代`Session.identity_map.values()`，可以访问一个Session中的所有持久化对象。

    - `info`

        一个可以让用户修改的字典。

    - `invalidate()`

        使用连接无效(invalidate)来关闭这个Session。

        这是`Session.close()`的一个变种，但是附增了对所有Connection对象调用`Connection.invalidate()`.

        例如:

        ```python
        try:
            session = Session()
            session.add(User())
            session.commit()
        except gevent.Timeout:
            session.invalidate()
            raise
        except:
            session.rollback()
            raise
        ```

    - `is_active`

        如果Session在事务模型中并且不在部分回滚状态，返回True。

        ...

    - `is_modified(instance, include_collections=True, passive=True)`

        如果给定的实例还有局部修改的属性，返回True。

        ...

    - `merge(instance, load=True)`

        拷贝一个给定实例的状态到这个Session中的一个相符实例中。

        `Session.merge()`检查资源实例的主键属性，并且试图将它和Session中相符的实例相协调。如果在当前Session中没有找到，它将会试图通过主键去数据库查找。

        参数：

        - `instance`: 想要合并的实例.

        - `load`:

            布尔值。当设置为False时，`merge()`将会调整为“高性能模式”

    - `new`

        返回所有标记为“new”的实例集合。

    - `no_autoflush`

        返回一个禁用自动刷新的**上下文管理器**：

        ```python
        with session.no_autoflush:
            some_object = SomeClass()
            session.add(some_object)
            # 不会自动刷新
            some_object.related_thing = session.query(SomeRelated).first()
        ```

    - `object_session(instance)`

        返回对象所属的Session。

        这个方法是`object_session()`函数的别称。

    - `prepare()`

        将当前的事务准备进入"two phase"提交

    - `prune()`

        移除identity map中的未引用实例缓存。

        > 已经废弃使用

    - `query(*entities, **kwargs)`

        返回符合这个Session的一个新的`Query`对象。

    - `refresh(instance, attribute_names=None, with_for_update=None, lockmode=None)`

        将一个给定的实例过期并刷新。

        将会对数据库发出一个新的查询，这个实例的所有属性都将会符合当前数据库中的值。

        懒加载关系属性将会保持在懒加载。

        参数：

        - `attribute_names`: 可选。一个想要刷新的属性子集。
        - `with_for_update`: 可选的布尔参数。指明是否应该使用FOR UPDATE。
        - `lockmode`: 传入Query后加上`with_lockmode()`。

    - `rollback()`

        回滚当前事务。

    - `scalar(clause, params=None, mapper=None, bind=None, **kw)`

        就像`execute()`一样，但是返回标量结果。

    - `transaction=None`

        当前的激活或未激活`SessionTransaction`.


- `sqlalchemy.orm.session.SessionTransactio(session, parent=None, nested=False)`

    一个Session级别的事务。

    `SessionTransaction`一般情况下不会出现在应用代码中，因为它是一个“**幕后工作者**”。

    - `nested=False`

        指明这个事务是否是嵌套或者SAVEPOINT事务。

    - `parent`

        这个事务的父事务.


### Session实用工具

- `sqlalchemy.orm.session.make_transient(instance)`

    修改给定实例的状态，让它变为`transient`.

    给定的实例状态假定为`persistent`或者`detached`状态。

- `sqlalchemy.orm.session.make_transient_to_detached(instance)`

    将给定的transient实例变为detached。

- `sqlalchemy.orm.session.object_session(instance)`

    返回实例所属的Session。

- `sqlalchemy.orm.util.was_deleted(object)`

    如果给定的实例在一次刷新操作后被删除，返回True。


### 属性和状态管理工具

- `sqlalchemy.orm.util.object_state(instance)`

    给定一个对象，返回关联这个对象的`InstanceState`.

    如果没有配置映射，将会抛出一个`sqlalchemy.orm.exc.UnmappedInstanceError`.

    相同的功能：比如`inspect()`函数.

    ```python
    inspect(instance)
    ```

- `sqlalchemy.orm.attirbutes.del_attribute(instance, key)`

    删除一个属性值，触发历史事件。

- `sqlalchemy.orm.attirbutes.get_attribute(instance, key)`

    获取属性的值。

- `sqlalchemy.orm.attributes.get_histroy(obj, key, passive=symbol('PASSIVE_OFF'))`

    返回给定对象和属性键的一条`History`纪录。

    参数：

    - `obj`: 一个对象
    - `key`: 字符串属性名称
    - `passive`: 指明属性的读取方式。

- `sqlalchemy.orm.attributes.init_collection(obj, key)`

    初始化一个集合属性，然后返回集合的适配器。

    这个函数用来对之前一个未访问属性提供一个内部集合的直接访问功能：

    ```python
    collection_adapter = init_collection(someobject, "elements")
    for elem in values:
        collection_adapter.append_without_event(elem)
    ```

- `sqlalchemy.orm.attributes.flag_modified(instance, key)`

    标记一个实例的属性，让它变为“modified”。


- `sqlalchemy.orm.attributes.flag_dirty(instance)`

    将一个实例标记为"dirty"。

- `sqlalchemy.orm.attributes.instance_state()`

    返回一个给定映射对象的`InstanceState`.

- `sqlalchemy.orm.instrumentation.is_instrunmented(instance, key)`

    如果给定实例的给定属性是通过属性package来instrumented过的，返回True。

- `sqlalchemy.orm.attributes.set_attribute(instance, key, value)`

    设置一个实例的属性，触发历史事件。

- `sqlalchemy.orm.attributes.set_committed_value(instance, key, value)`

    设置一个实例的属性，不触发历史事件。

- `sqlalchemy.orm.attributes.History`

    加入一个3位元组。

    可以通过`inspect()`函数来查看：

    ```python
    from sqlalchemy import inspect

    hist = inspect(myobject).attrs.myattributes.history
    ```

    每个元组元素都是一个可迭代序列：

    - `added`: 增加到属性的item集合(首个元组元素)
    - `unchanged`: 没有修改的属性集合(第二个元组元素)
    - `deleted`: 属性中删除的集合(第三个元素)

    - `empty()`

        如果`Histroy`保持为修改状态。返回True。

    - `has_changes()`

        如果`History`发生变动，返回True。

    - `non_added()`

        返回未修改+已删除集合。

    - `non_deleted()`

        返回已增加+未改动集合。

    - `sum()`

        返回已增加+未改动+已删除的集合。

        





        
            

            

            

            

            