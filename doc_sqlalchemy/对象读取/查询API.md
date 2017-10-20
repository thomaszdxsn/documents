[TOC]

## Query对象

`Query`按照给定的Session生成，使用`query()`方法：

`q = session.query(SomeMappedClass)`

下面都是Query对象的接口：

- class`sqlalchemy.orm.query.Query(entities, session=None)`

    ORM级别的SQL构建对象。

    `Query`是通过ORM生成的SELECT语句源头，所有Query对象都是通过用户查询操作以及高等级
    内部操作（如关联对象读取）生成的。它提供了一个生成式接口特性，因此接连的调用都会返回一个
    新的Query对象，之前对象的额外标准与option都会保留下来，即实现了链式操作。

    `Query`对象通常在`Session.query()`中初始生成，很少见的情况是通过直接实例化一个
    `Query`然后通过`Query.with_session()`把它关联到一个Session。

    - `__init__(entities, session=None)`

        直接构造`Query`。

        比如：

        `q = Query([User, Address], session=some_session)`

        上面代码等同于：

        `q = some_session.query(User, Address)`

        参数：

        - `entities`: 一个实体/SQL表达式序列

        - `session`: 这个Query将要关联的Session。另外，Query也可以通过它的方法
                `Query.with_session()`来关联一个Session。

    - `add_column(column)`

        增加一个列(column)表达式到列表中，最后返回时也会包含这个列。

        **将要配废弃：`add_column()`将要被`add_columns()`取代。**

    - `add_columns(*column)`

        增加一个或多个列(column)表达式到列表中，最后返回时也会包含这个列。

    - `add_entity(entity, alias=None)`

        增加一个映射实体到列表中，最后返回时将会包含它的所有列。

    - `all()`

        把这个Query的结果以列表形式返回。

        这个结果是最后查询的执行结果。

    - `as_scalar()`

        返回这个Query代表的完整的SELECT语句，转换成一个scalar子查询。

        类似的还有`sqlalchemy.sql.expression.SelectBase.as_scalar()`

    - `autoflush(setting)`

        返回一个指定"autoflush"设置的`Query`。

        注意一个Session如果设置了AutoFlush=False，那么就不会自动刷新，即使在Query
        级别上设置了这个flag。因此这个flag通常是用来**禁用**一个特定Query的自动刷新。

    - `column_descriptions`

        在这个Query返回时，包含这些列的元数据。

        格式是一个列表，包含了若干字典：

        ```python
        user_alias = aliased(User, name='user2')
        q = session.query(User, User.id, user_alias)

        # 使用这个表达式：
        q.column_descriptions

        # 将会返回：
        [
            {
                'name':'User',
                'type':User,
                'aliased':False,
                'expr':User,
                'entity': User
            },
            {
                'name':'id',
                'type':Integer(),
                'aliased':False,
                'expr':User.id,
                'entity': User
            },
            {
                'name':'user2',
                'type':User,
                'aliased':True,
                'expr':user_alias,
                'entity': user_alias
            }
        ]
        ```

    - `correlate(*args)`

        返回一个`Query`对象，它可以用来给一个`Query`或者`select()`做FROM子句。

        这个方法接受映射类，`aliased()`对象，以及`mapper()`对象作为参数，最后会被解析
        为表达式构造。

        这个相关参数在完成表达式构造后,最终会传入`Select.correlate()`。

        这个相关参数在诸如使用`Query.from_self()`时会起作用，或者在把一个由
        `Query.subquery()`返回的子查询嵌入到另一个`select()`对象后起作用。

    - `count()`

        返回这个查询中行(row)的计数。

        这个查询生成的SQL类似以下：

        ```python
        SELECT count(1) AS count_1
        FROM (SELECT <rest of query follows...>) AS anon_1
        ```

        为了更加细粒度地控制指定列的计数，跳过FROM子句中的子查询，或者使用一些聚集函数，
        可以在`query()`中使用`func`表达式：

        ```python
        from sqlalchemy import func

        # 计数User数量，并且不使用子查询
        session.query(func.count(User.id))

        # 返回通过"name"分组的"user.id"计数
        session.query(func.count(User.id)).\
                    group_by(User.name)

        from sqlalchemy import distinct

        # 计数带distinct的"name"值
        session.query(func.count(distinct(User.name)))
        ```

    - `cte(name=None, recursive=False)`

        返回这个Query代表的完整SELECT语句，表现为一个公共表表达式(common table expression, CTE).

        参数和用法和`SelectBase.cte()`方法相同；

        下面是一个**PostgreSQL WITH RECURSIVE**例子。注意，在这个例子中，这个`include_parts`cte
        和它的`incl_alias`都是Core的可选择对象(selectables)，意味着列是通过`.c.`来访问的。
        `parts_alias`对象是`Part`实体的一个`orm.aliased()`实例，所以列映射属性可以直接获取：

        ```python
        from sqlalchemy.orm import aliased

        class Part(Base):
            __tablename__ = 'part'
            part = Column(String, primary_key=True)
            sub_part = Column(String, primary_key=True)
            quantity = Column(Integer)

        included_parts = session.query(
                                Part.sub_part,
                                Part.part,
                                Part.quantity).\
                                    filter(Part.part == 'our part').\
                                    cte(name="includeed_parts", recursive=True)

        incl_alias = aliased(included_parts, name='pr')
        parts_alias = aliased(Part, name='p')
        included_parts = included_parts.union_all(
            session.query(
                parts_alias.sub_part,
                parts_alias.part,
                parts_alias.quantity).\
                     filter(parts.part == incl_alias.c.sub_part)
        )

        q = session.query(
                included_parts.c.sub_part,
                func.sum(included_parts.c.quantity).
                    label("total_quantity")
        ).\
        group_by(included_parts.c.sub_part)
        ```

    - `delete(synchronize_session='evaluate')`

        执行一个批量删除查询。

        从数据库中删除符合这个查询的行（row）。

        比如：

        ```python
        session.query(User).filter(User.age == 25).\
                delete(sychronize_session=False)

        session.query(User).filter(User.age == 25).\
                delete(sychronize_session='evaluate')
        ```

        > 警告
        >> `Query.delete()`方法是一个"批量"操作，为了更高的性能，
        它自动绕过了ORM的unit-of-work，请阅读以下的所有警告。

        参数：

        - `synchronize_session`

            选择匹配对象从session中移除的策略。合法的值为：

            - `False`: 不要同步到session中。这个选择是最高效，如果session过期这也是
                最值得信赖的，session过期一般出现在`commit()`或者显式使用`expire_all()`
                之后。在过期之前，这个对象事实上删除了但是仍然会保留在session在，如果在
                通过`get()`访问结果时很容易让人混淆。

            - `'fetch'`: 在删除找到的对象之前执行一个select查询来取得这个对象。匹配的对象
                将会在session中被移除。

            - `evaluate`: 如果评估标注没有实现，将会抛出一个异常。

            这个表达式估算器(evaluator)目前并不会考虑数据库和Python之间不同字符串编码的区别。

        返回：

        通过数据库的"行计数"特性来返回匹配的行计数。

        > 警告
        >
        > 批量查询删除的额外警告
        >
        >> - 由于SQL不支持多表删除的缘故，以及一个继承映射器的join条件不会自动渲染，
            这个方法在joined继承映射中不会生效。必须注意在任何多表删除的时候，首先需要
            采用其它关联表删除的方法，以及需要显式在这些表中指定join条件，虽然在映射中
            一般这些都是自动化完成的。举例来说，如果一个类`Engineer`，以及子类`Employee`，
            对`Employee`表实现DELETE一般像这样：
        >>   ```python
        >>   session.query(Engineer).\
        >>          filter(Engineer.id == Employee.id).\
        >>          filter(Employee.name == 'dilbert').\
        >>          delete()
        >>   ```
        >>   然而，上面的SQL并不会对Engineer做删除，除非在数据库建立了`ON DELETE CASCADE`。
        >>
        >>   简单来说，**不要对joined继承映射使用这个方法，除非你采取了其它方法让这个行为可行**
        >> - 多态identity的WHERE标准并**不**包含single和joined表更新 - 对于单表继承必须手动添加。
        >> - 这个方法并**不**提供Python中的关系级联 - 它假定**ON DELETE CASECADE/SET NULL/等等**
             已经设置好了，否则数据库可能会发出违反完整性约束的错误。
        >>
        >>   在一个DELETE之后，根据对象是否存在与session，可能因为没有包含当前状态，
             在ON DELETE时冲突。至于过期对象的访问，将首先发出一个SELECT来查询，如果
             查询的结果为空，那么会抛出一个`ObjectDeleteError`。
        >> - ``fetch`策略会发出一个额外的SELECT语句，这将会极大的降低性能。
        >> - `'evaluate'`策略会在session中对所有匹配对象做一次扫描；如果session中的内容过期，
             比如在调用`session.commit()`之后，这个配置将会对每个匹配的对象发出一个SELECT来重新获取。
        >> - `MapperEvents.before_delete()`和`MapperEvents.after_delete()`事件**并不会**
             在这个方法中被调用。作为替代，`SessionEvents.after_bulk_delete()`方法将作为这个事件的钩子。

    - `distinct(*expr)`

        对查询使用`DISTINCT`，并且返回新的`Query`。

        > 注意
        >> `distinct()`包含的逻辑会把ORDER BY子句中的列自动加入到SELECT中，用以满足
            SQL规范。但是这个加入的列并不会加入到query()，也就是不会影响结果。这个列可以
            通过使用`Query.statement`访问器看到。

        参数

        - `*expr` - 可选列表达式。当使用这个参数时，PostgreSQL方言会渲染一个语句：
                    `DISTINCT ON (<expression>)`

    - `enable_assertions(value)`

        控制是否生成断言。

        当设置为False时，Query的返回在操作之前不会断言它本身的状态，包括在filter()调用后
        不会应用LIMIT／OFFSET，在get()调用后没有标准存在，在filter()/order_by()/group_by()
        的时候不会存在"from_statemen()"等等。更加宽松的行为需要通过继承Query来实现。

        必须谨慎确保使用方式是可行的。比如，对一个Query应用from_statement()将会覆盖
        其它的通过filter()或者order_by()返回的标准集合。

    - `enable_eagerloads(value)`

        控制是否渲染贪婪joined和子查询。

        当设置为False时，返回的Query不会渲染贪婪JOIN。无论是否设置`joinedload()`,
        `subqueryload`, `lazy='joined'`, `lazy='subquery'`。

        这个方法主要用于Query嵌套到一个子查询或者其它可查询对象时，或当使用`Query.yield_per()`。

    - `except_(*q)`

        让其它查询对这个Query生成一个EXCEPT.

        作用方式和`union()`同理。

    - `except_all(*q)`

        让其它查询对这个Query生成一个EXCEPT ALL.

        作用方式和`union()`同理。


    - `execution_options(**kwargs)`

        设置非SQL选项在执行时是否生效。

        这个方法和Core中的`Connection.execution_options()`一样。

        注意在使用`yield_per()`方法时，`stream_results`会自动生效。

    - `exists()`

        一个方便的方法，它把一个查询转换为EXISTS的子查询，如EXISTS（SELECT 1 FROM ... WHERE ...)

        比如:

        ```pyhton
        q = session.query(User).filter(User.name == 'fred')
        session.query(q.exists())
        ```

        生成的SQL类似下面：

        ```python
        SELECT EXISTS (
            SELECT 1 FROM users WHERE users.name = :name_1
        ) AS anon_1
        ```

        EXISTS构造通常用在WHERE子句中：

        ```python
        session.query(User.id).filter(q.exists()).scalar()
        ```

        注意一些数据库如SQL Server不允许EXISTS表达式出现在SELECT子句中。想要根据EXISTS
        的结果获得一个简单的布尔值，可以使用`literal()`:

        ```python
        from sqlalchemy import literal

        session.query(literal(True)).filter(q.exists()).scalar()
        ```

    - `filter(*)`

        把筛选标准拷贝到Query，使用(类似)SQL表达式的方式。

        比如：

        `session.query(MyClass).filter(MyClass.name == 'some name')`

        多个筛选标准可以通过逗号分割;最后会讲所有标准使用一个`and_()`组合起来：

        ```python
        session.query(MyClass).\
                filter(MyClass.name == 'some name', MyClass.id > 5)
        ```

    - `filter_by(**kwargs)`

        把筛选标准拷贝到Query，使用关键字参数的方式。

        比如：

        `session.query(MyClass).filter_by(name="some name")`

        多个标准也可以用逗号隔开；然后内部会自动使用`and_()`函数将它们组合起来：

        ```python
        session.query(MyClass).\
                filter_by(name='some name', id=5)
        ```

        关键字参数提取查询中主实体的列来使用，之后的实体列需要使用`Query.join()`显式声明。

    - `first()`

        返回这个Query结果的首个行（row），或者在结果中不包含任何row时返回None。

        first()在生成的SQL中使用了LIMIT 1，所以在服务端也只会生成一行数据。

    - `from_self(*entities)`

        返回一个Query，这个对象将会将SELECT的结果作为子查询。

        本质上`Query.from_self()`将一个SELECT语句转向它本身。给定一个查询如：

        `q = session.query(User).filter(User.name.like('e%'))`

        给定`Query.from_self()`版本：

        `q = session.query(User).filter(User.name.like('e%')).from_self()`

        这个查询将会渲染：

        ```python
        SELECT anon_1.user_id AS anon_1_user_id,
            anon_1.user_name AS anon_1_user_name
        FROM (SELECT "user".id AS user_id, "user".name AS user_name
        FROM "user"
        WHERE "user".name LIKE :name_1) AS anon_1
        ```

        有很多情况使用`Query.from_self()`都很有用。一个简单的例子是，当你想要对我们查询的
        结果做一个LIMIT行限制，然后对这个行限制后的结果使用join：

        ```python
        q = session.query(User).filter(User.name.like('e%')).\
                limit(5).from_self().\
                join(User.addresses).filter(Address.email.like('q%'))
        ````

        上面的查询会使用JOIN，但是只会针对User的前五行：

        ```python
        SELECT anon_1.user_id AS anon_1_user_id,
               anon_1.user_name AS anon_1_user_name
        FROM (SELECT "user".id AS user_id, "user".name AS user_name
        FROM "user"
        WHERE "user".name LIKE :name_1
            LIMIT :param_1) as anon_1
        JOIN address ON anon_1.user_id = address.user_id
        WHERE address.email LIKE :email_1
        ```

        **自动aliasing**

        `Query.from_self()`的另一个关键之处在于它对子查询内部的实体实现了*自动aliasing*，
        可以继续在外层引用。上面例子中，如果我们想要继续引用User实体，这些引用将会按照子查询中
        的实体引用：

        ```python
        q = session.query(User).filter(User.name.like('e%')).\
                limit(5).from_self().\
                join(User.addresses).filter(Address.email.like('q%')).\
                order_by(User.name)
        ```

        ORDER BY子句使用的User.name是子查询内部实体的列：

        ```python
        SELECT anon_1.user_id AS anon_1_user_id,
            anon_1.user_name AS anon_1_user_name
        FROM (SELECT "user".id AS user_id, "user".name AS user_name
        FROM "user"
        WHERE "user".name LIKE :name_1
         LIMIT :param_1) AS anon_1
        JOIN address ON anon_1.user_id = address.user_id
        WHERE address.email LIKE :email_1 ORDER BY anon_1.user_name
        ```

        自动aliasing的特性只有在受限的几种方式有效，比如简单的筛选和排序。更复杂的构造如
        引用实体来JOIN需要使用显示的子查询对象，一般通过`Query.subquery()`生成的对象。
        测试查询结构时必须看看生成的SQL来确保不会出乎意料的结果。

        **改变实体**

        `Query.from_self()`包含能够修改哪些列要被查询的特性。在之前的例子中，我们想要
        在内部查询中子查询中查询`User.id`，所以我们可以在外部JOIN`Address`实体，
        但是我们只想要外部查询返回`Address.email`列：

        ```python
        q = session.query(User).filter(User.name.like('e%')).\
            limit(5).from_self(Address.email).\
            join(User.addresses).filter(Address.email.like('q%'))
        ```

        生成的SQL：

        ```python
        SELECT address.email AS address_email
        FROM (SELECT "user".id AS user_id, "user".name AS user_name
        FROM "user"
        WHERE "user".name LIKE :name_1
            LIMIT :param_1) AS anon_1
        JOIN address ON anon_1.user_id = address.user_id
        WHERE address.email LIKE :email_1
        ```

        **查看内部／外部的列**

        记住在引用一个列时这个列来自于子查询时，我们需要这个列出现在子查询的SELECT子句中；
        这是SQL中最普通的部分。例如，如果我们想要使用`contains_eager()`来贪婪读取子查询，
        我们需要加入这些列。下面使用User和Address来阐释:

        ```python
        q = session.query(Address).join(Address.user).\
                filter(User.name.like('e%'))

        q = q.add_entity(User).from_self().\
                options(contains_eager(Address.user))
        ```

        我们在使用`Query.from_self()`之前使用了`Query.add_entity()`，所以在子查询中
        出现了User的列。所以我们能够使用`contains_eager()`：

        ```python
        SELECT anon_1.address_id AS anon_1_address_id,
           anon_1.address_email AS anon_1_address_email,
           anon_1.address_user_id AS anon_1_address_user_id,
           anon_1.user_id AS anon_1_user_id,
           anon_1.user_name AS anon_1_user_name
        FROM (
            SELECT address.id AS address_id,
                address.email AS address_email,
                address.user_id AS address_user_id,
                "user".id AS user_id,
                "user".name AS user_name
            FROM address JOIN 'user' ON 'user'.id = address.user_id
            WHERE 'user'.name LIKE :name_1)
            AS anon_1
        ```

        如果我们没有调用`add_entity(User)`, 而是直接使用`contains_eager()`来读取
        User实体，会强制把这个表增加到外面而不会正确的join - 注意下面的`anon1, "user"`:

        ```python
        # 不正确的查询
        SELECT anon_1.address_id AS anon_1_address_id,
           anon_1.address_email AS anon_1_address_email,
           anon_1.address_user_id AS anon_1_address_user_id,
           "user".id AS user_id,
           "user".name AS user_name
        FROM (
            SELECT address.id AS address_id,
            address.email AS address_email,
            address.user_id AS address_user_id
        FROM address JOIN "user" ON "user".id = address.user_id
        WHERE "user".name LIKE :name_1) AS anon_1, "user"
        ```

        参数：

        - `*entities`: 可选参数，传入的实体会代替最终SELECT的列。

    - `from_statement(statement)`

        执行给定的SELECT语句并返回结果。

        这个方法绕过所有内部语句编译，传入的语句可以无需修改地执行。

        传入的参数应该是一个`text()`或者`select()`构造器生成的对象，返回的列集合应该
        符合Query中实体类的列集合。

    - `get(ident)`

        根据给定的主键标识符返回实例，如果没有找到则返回None。

        比如：

        ```python
        my_user = session.query(User).get(5)

        some_object = session.query(VersionedFoo).get((5, 10))
        ```

        `get()`是特殊的，它可以直接访问Session的标识图。如果给定的主键标识符出现在本地的
        (Session)标识图中，对象会直接返回而不用发出SQL，但是在对象标记为过期后就无效了。
        如果主键标识没有出现在标识图中，将会发出一个SQL来取得对象。

        `get()`在对象出现在标识图并且标记为过期时会执行一个检查 - 会发出一个SQL来刷新对象
        以及确认这行(row)仍旧存在。如果没有，将会抛出一个`ObjectDeleteError`异常。

        `get()`只能用来返回单个映射实例，不能返回多个实例或者单独的列对象，并且限制使用
        单个主键值。原始的query()函数也必须这样构造，也就是必须传入单个实体并且没有额外的
        筛选标准。通过`options()`读取选项可能会生效。

        通过`relationship()`配置的惰性加载，多对一属性，使用简单的外键-主键标准，对它的
        访问也会首先访问标识图而不是查询数据库。

        参数：

        - `ident`: 一个代表主键的标量或元组。对于混合主键，主键值的顺序应该和Table主键一样。

        返回：

        一个对象实例，或者`None`。

    - `group_by(*criterion)`

        对查询应用一个或多个GROUP BY标准，并且返回新的Query。

        所有存在的GROUP BY设置都能够通过在使用这个方法并传入`None`来取消 - 这个取消
        方式也能应用于ORDER BY。

    - `having(criterion)`

        对查询应用HAVING标准，并返回新的Query。

        `having()`需要组合`group_by()`使用。

        HAVING标准可以在分组的基础上使用过滤／聚集函数：

        ```python
        q = session.query(User.id).\
                join(User.addresses).\
                group_by(User.id).\
                having(func.count(Address.id) > 2)
        ```

    - `instances(cursor, _Query__context=None)`

        给定一个由`connection.execution()`返回的`ResultProxy`，返回一个ORM迭代
        器版本的结果。

        比如：

        ```python
        result = engine.execute("select * from users")
        for u in session.query(User).instances(result):
            print(u)
        ```

    - `intersect(*q)`

        让一或多个查询针对这个Query生成一个INTERSECT。

        运行原理和`union()`一样.

    - `join(*props, **kwargs)`

        对这个Query的对象使用一个JOIN SQL，返回一个新的Query。

        **简单关系JOIN**

        考虑两个映射`User`和`Address`，`User.addresses`代表和每个User关联的Address
        对象。`join()`最常用于在这个关系中创建一个JOIN，使用`User.addresses`作为指示器
        来说明两个表中哪个值相等：

        `q = session.query(User).join(User.addresses)`

        上面例子对`User.addresses`调用了`Query.join()`，将会发出以下SQL：

        ```python
        SELECT
            user.*
        FROM user JOIN address
            ON user.id = address.user_id
        ```

        上面例子我们在`join()`引用的`User.addresses`出现在JOIN子句中，也就是会自动指定
        ON的条件。对于以上案例的单实体查询(我们最开始只查询了User，没有其他实体)，关系同样可以
        通过一个字符串名称来指定：

        `q = session.query(User).join("addresses")`

        `join()`同样支持多个"on子句"参数来组成JOIN链，比如下面我们JOIN了4个相关联的实体：

        `q = session.query(User).join('orders', 'items', 'keywords')`

        上面例子是3个独立`join()`的快捷方式，每次都用一个显式的属性字符串名称来指代真实实体：

        ```python
        q = session.query(User).
                    join(User.orders).\
                    join(User.items).\
                    join(Item.keywords)
        ```

        **对目标实体或可选择对象(selectable)JOIN**

        第二种使用`join()`的方法允许任意的映射实体和Core中的可选择对象作为目标传入。在
        这种用法中，`join()`会试图通过在两个实体的自然外键关系中创建一个JOIN：

        `q = session.query(User).join(Address)`

        如果上面的两个实体之间没有外键约束或者多个外键约束时，就会抛出一个错误。在上面的调用
        形式中，`join()`调用后自动为我们创建了一个"ON子句"。传入的参数可以是任何可选择对象，
        如`Table`:

        `q = session.query(User).join(addresses_table)`

        **对目标JOIN以及ON子句**

        第三种形式的调用可以允许目标实体和ON子句显式传入。假设我们想要JOIN`Address`两次，
        在第二次的时候使用alias。我们可以使用`aliased()`来区分Address不同的alias，
        传参中使用`target, onclause`形式来JOIN它们，所以alias可以设定显式地设置ON子句
        如何生成：

        ```python
        a_alias = aliased(Address)

        q = session.query(User).\
                join(User.addresses).\
                join(a_alias, User.addresses).\
                filter(Address.email_address == 'ed%foo.com').\
                filter(Address.email_address == 'ed%bar.com')
        ```

        在上面例子中，生成的SQL类似于：

        ```python
        SELECT user.* FROM user
            JOIN address ON user.id = address.user_id
            JOIN address AS address_1 ON user.id=address_1.user_id
            WHERE address.email_address =: email_address_1
            AND address_1.email_address =: email_address_2
        ```

        对`join()`使用两个参数，可以让我们构建任意形式的SQL"ON"子句，不必依赖设置的关系：

        ```python
        q = session.query(User).join(Address, User.id == Address.user_id)
        ```

        **高级JOIN目标和适配(adaption)**

        当使用`join()`选择"目标"时是有弹性空间的。就像之前提到的那样，它可以接受`Table`对象
        和其它的可选择对象如`alias()`和`select()`，无论是使用一参数或两个参数形式：

        ```python
        addresses_q = select([Address.user_id]).\
                    where(Address.email_address.endswith("%bar.com")).\
                    alias()

        q = session.query(User).\
                join(addresses_q, addresses_q.user_id == User.id)
        ```

        `join()`同样具有适配`relationship()`的特性 - 自动根据可选择对象来决定ON子句。
        下面例子中，我们构建了一个User对Address子查询的JOIN，在第二个参数传入relationship：
        `User.addresses`来适配目标：

        ```python
        address_subq = session.query(Address).\
                            filter(Address.email_address == 'ed@foo.com').\
                            subquery()

        q = session.query(User).join(address_subq, User.addresses)
        ```

        生成的SQL类似于：

        ```python
        SELECT user.* FROM user
            JOIN (
                SELECT address.id AS id,
                    address.user_id AS user_id,
                    address.email_address AS email_address
                FROM address
                WHERE address.email_address =: email_address_1
            ) AS anon_1 ON user.id = anon_1.user.id
        ```

        上面的用法也可以使用显式ON子句方式来写：

        ```python
        q = session.query(User).\
                joni(address_subq, User.id = address_subq.c.user_id)
        ```

        **控制JOIN对应的FROM**

        `join()`可以控制JOIN的右侧，但是有时也需要可以控制左侧，碰到这种情况是，我们需要
        使用`select_from()`。下面我们通过实体Address来构建一个查询，但是也可以通过设置
        Query首先查询`User`来时这个查询可以使用`User.addresses`作为"on"子句:

        ```python
        q = session.query(Address).select_from(User).\
                        join(User.addresses).\
                        filter(User.name == 'ed')
        ```

        生成的SQL类似如下：

        ```python
        SELECT address.* FROM user
            JOIN address ON user.id = address.user_id
            WHERE user.name = :name_1
        ```

        **构建匿名的alias**

        `join()`可以使用flag参数`aliased=True`来构建匿名aliases。这个特性在查询通过
        算法joined的时候特别有用，比如一个任意深度的子引用查询。

        ```python
        q = session.query(Node).\
                join("children", "children", aliased=True)
        ```

        当使用`aliased=True`时，真正的"alias"对象并不能显式的获取。类似`Query.filter()`
        的方法使用刚收到的实体作为最后JOIN的点：

        ```python
        q = session.query(Node).\
                join("children", "children", aliased=True).\
                filter(Node.name == 'grandchild 1')
        ```

        当使用自动aliasing时，`from_joinpoint=True`可以在join()调用之间插入，允许
        使用多节点join，所以每个path(节点)上面你都可以进一步筛选：

        ```python
        q = session.query(Node).\
                join("children", aliased=True).\
                filter(Node.name == 'child 1').\
                join("children", aliased=True, from_joinpoint=True).\
                filter(Node.name == 'grandchild 1')
        ```

        筛选节点可以通过`reset_joinpoint()`来重设为最开始的`Node`实体：

        ```python
        q = session.query(Node).\
                join("children", "children", aliased=True).\
                filter(Node.name == 'grandchild 1').\
                reset_joinpoint().\
                filter(Node.name == 'parent 1')
        ```

        对于`aliased=True`的例子，可以看看发布包的**XML持久化**，它解释了一个类Xpath
        的查询系统是怎么使用算法join的。

        参数：

        - `*props`: 一个或多个JOIN条件的集合，用一个绑定关系的属性或者一个表示关系名称
        的字符串用来代表"ON"子句，或者使用一个单独的目标实体，或者一个元组的参数形式
        `(target, onclause)`，也可以传入两个参数形式的`target, onclause`。

        - `aliased=False`: 如果为True，指明这个JOIN的目标应该使用匿名aliasing。随后的
        比如`filter()`类似的标准方法将会以这个alias作为目标，直到调用`reset_joinpoint()`
        ，目标将会重新改为query()中的主对象。

        - `isouter=False`: 如果为True，JOIN将使用`LEFT OUTER JOIN`，就像使用
        `Query.outerjoin()`方法一样。在Core中的`FromClause.join()`中同样有一个一样的
        flag参数。

        - `full=False`

            使用`FULL OUTER JOIN`；隐式地一并使用了`isouter`。

        - `from_joinpoint=False`

            当使用`aliased=True`时，这个setting也设置为True可以让随后的filter()
            使用最近的join目标为目标，而不是使用查询的原始FROM目标。

    - `label(name)`

        返回这个Query的一个完整表现形式，使用给定的name转换成一个带label的标量子查询。

        类似的还有`sqlalchemy.sql.expression.SelectBase.label()`

    - `limit(limit)`

        对查询使用一个`LIMIT`，返回一个新的`Query`对象。

    - `merge_result(iterator, load=True)`

        合并一个结果(result)到这个`Query`对象的session。

        给定的参数是一个结果和本查询一样的另一个Query返回的结果(result)，返回一个相同的
        结果迭代器，所有的映射实例都将使用`Session.merge()`合并到session中。这是一个优化
        的方法，用来合并所有的映射实例，相比对每个值显式调用`Session.merge()`，可以减少
        (多次)方法调用的开销。

        这个结果的结构取决于这个`Query`的Column列表 - 如果它们的结果不相符，将会抛出错误。

        `load`参数和`Session.merge()`中的参数作用一样。

        对于何时使用`merge_result()`，可以查看开发包的`Dogpile Caching`这个例子，
        `merge_result()`在这里用来把一个缓存的状态高效的恢复到目标Session中。

    - `offset(offset)`

        对查询使用一个`OFFSET`，返回一个新的`Query`对象。

    - `one()`

        要么返回一个结果，要么抛出一个异常。

        如果查询没有结果将抛出`sqlalchemy.orm.exc.NoResultFound`。

        如果查询发现多个结果，将抛出`sqlalchemy.orm.exc.MultipleResultsFound`。

        `one()`在最后一个Query使用。

    - `one_or_none()`

        返回一个结果，或返回`None`，或者抛出一个异常。

        如果查询没有结果，返回`None`。如果查询找到多个结果，将会抛出一个
        `sqlalchemy.orm.exc.MultipleResultsFound`。

    - `options(*criterion)`

        应用给定的映射器(mapper)选项(options)列表到查询中，返回一个新的Query。

        大多数有关的选项(options)都是和关于如何改变column，关系映射属性如何读取。

    - `order_by(*criterion)`

        对查询应用一个或多个ORDER BY标准，返回一个新的Query。

        所有的ORDER BY设置都可以通过传入一个`None`来阻止 - 在映射器中设置的ORDER BY
        同样也可以阻止。

        另外，传入`False`可以重置所有的ORDER BY，让默认的`mapper.order_by`重新生效。
        但是`mapper.order_by`已经被废弃了。

    - `outerjoin(*props, **kwargs)`

        对Query对象创建一个LEFT OUTER JOIN，返回一个新的Query。

        使用方法和`join()`相同。

    - `params(*args, **kwargs)`

        为`filter()`指定的参数绑定值。

        参数可以使用关键字参数传入，或者可以直接传入一个字典作为首个位置参数。原因是虽然
        `**kwargs`很方便，然而一些属性字典包含unicode键，这将导致`**kwargs`不能用。

    - `populate_existing()`

        返回一个Query，将会过期和刷新所有实例，像它们被读取过一样，或者重用当前Session
        中的实例。

        ORM正常使用时并不推荐使用`populate_existing()` - Session对象能够自动管理
        实例的状态。这个方法不适用于一般的情况。

    - `prefix_with(*prefixes)`

        对查询应用前缀，并返回一个新的Query。

        参数：

        - `*prefixes`: 可选的前缀，一般是字符串，不能使用逗号。在针对MySQl关键字时很有用。

        比如：

        ```python
        query = session.query(User.name).\
            prefix_with('HIGN_PRIORITY).\
            prefix_with("SQL_SMALL_RESULT", "ALL")
        ```

        将会生成如下SQL：

        ```python
        SELECT HIGH_PRIORITY SQL_SMALL_RESULT ALL user.name AS users_name
        FROM users
        ```

    - `reset_joinpoint()`

        "JOIN点(point)"重设为原始FROM中的实体，返回一个新的Query。

        这个方法通常在`join(aliased=True)`时使用。这个方法会把"JOIN点"设置为最近的
        一个JOIN目标。`reset_joinpoint()`就是用来重设"JOIN点"的。

    - `scalar()`

        返回第一个结果的第一个元素。如果查询发现多个行，将会抛出一个`MultipleResultsFound`。

        ```python
        >>> session.query(Item).scalar()
        <Item>
        >>> session.query(Item.id).scalar()
        1
        >>> session.query(Item.id).filter(Item.id < 0).scalar()
        None
        >>> session.query(Item.id, Item.name).scalar()
        1
        >>> session.query(func.count(Parent.id)).scalar()
        20
        ```

        这个方法应用于最后一个Query。

    - `select_entity_from(from_obj)`

        设置这个查询的FROM为一个Core可选择对象。

        `Query.select_entity_from()`提供了使用`aliased()`的一个替代方式。相比于
        显式的引用`aliased()`对象，`Query.select_entity_from()`自动采用所有出现的
        实体作为选择对象。

        先看一个`aliased()`的例子：

        ```python
        select_stmt = select([User]).where(User.id == 7)
        user_alias = aliased(User, select_stmt)

        q = session.query(user_alias).\
                filter(user_alias.name == 'ed')
        ```

        上面例子，我们显式传入`user_alias`对象到查询中。但是很多地方并不能显式引用`user_alias`,
        `Query.select_entity_from()`可以用在查询的开始，将现存的User实体用作alias：

        ```python
        q = session.query(User).\
                select_entity_from(select_stmt).\
                filter(User.name == 'ed')
        ```

        上面例子中，生成的SQL将会显式User实体适配到我们的语句中，即使是用在FROM子句：

        ```python
        SELECT anon_1.id AS anon_1_id, anon_1.name AS anon_1_name
        FROM (SELECT "user".id AS id, "user".name AS name
              FROM "user"
              WHERE "user".id = :id_1) AS anon_1
        WHERE anon_1.name = :name_1
        ```

        `Query.select_entity_from()`方法类似于`Query.select_from()`方法，都是
        设置查询中的FROM子句。不同之处在于它会自动采用主实体作为传入alias的引用对象。如果
        上面例子中换成了`Query.select_from()`，那么生成的SQL会变成这样：

        ```python
        # 使用select_from()，而不是select_entity_from()
        # 加入的实体/aliased将会作为JOIN子查询对象
        SELECT "user".id AS user_id, "user".name AS user_name
        FROM "user", (SELECT "user".id AS id, "user".name AS name
                    FROM "user"
                    WHERE "user".id = :id_1) AS anon_1
        WHERE "user".name = :name_1
        ```

        想用在`Query.select_entity_from()`使用文本型SQL，我们可以使用`text()`构造器。
        但是，`text()`需要符合我们实体中的列，可以使用`TextClause.columns()`方法来辅助实现：

        ```python
        text_stmt = text("select id, name from user").columns(
            User.id, User.name
        )

        q = session.query(User).select_entity_from(text_stmt)
        ```

        `Query.select_entity_from()`本身接受一个`aliased()`对象，所以`aliased()`
        的特殊选项比如`aliased.adapt_on_names`可以用在前者方法的改编版本。

        假设一个视图`user_view`同样返回`user`中的行,如果我们反射这个视图到一个`Table`中，
        这个视图没有我们映射的Table的关系，但是我们可以使用名称匹配的方式来查询：

        ```python
        user_view = Table("user_view", metadata,
                        autoload_with=engine)

        user_view_alias = aliased(
            User, user_view, adapt_on_names=True)
        q = session.query(User).\
                select_entity_from(user_view_alias).\
                order_by(User.name)
        )
        ```

        参数：

        - `from_obj`: 一个`FromClause`对象，它将会替换这个查询的FROM子句。同样可以
        传入一个`aliased()`对象。

    - `select_from(*from_obj)`

        显式设置Query的FROM子句。

        `Query.select_from()`通常结合`Query.join()`使用，用来控制使用哪个实体作为
        JOIN的左侧实体。

        多数时候调用`join()`左侧的实体对象能够决定一个查询的查询效率，如果没有设置join点，
        通常默认的join点是Query对象被选择的实体列表的最左边的一个实体。

        一个典型的例子是：

        ```python
        q = session.query(Address).select_from(User).\
                join(User.addresses).\
                filter(User.name == 'ed')
        ```

        生成的SQL如下：

        ```python
        SELECT address.* FROM user
        JOIN address ON user.id == address.user_id
        WHERE user.name = :name_1
        ```

        参数：

        - `*from_obj`: 子查询应用的一个或多个实体集合。实体可以是映射类，`AliasedClass`
        对象，`Mapper`对象以及使用Core中的`FromClause`用作子查询。

        > 注意
        >> v0.9以后：这个方法不再可以通过传入匹配实体的可选择对象当作FROM子句；可以选择使用
        `select_entity_from()`这个方法来替代。

    - `selectable`

        通过这个Query发出的查询返回一个`Select`对象。

        兼容使用`inspect()`，等同于：

        `query.enable_eagerloads(False).with_labels().statement`

    - `slice(start, stop)`

        通过给定的索引计算Query的切片，并返回一个新的Query。

        start和stop索引类似于Python内置的函数`range()`，这个方法集合了LIMIT和OFFSET
        的使用。

        举例来说：

        `session.query(User).order_by(User.id).slice(1, 3)`

        生成的SQL：

        ```python
        SELECT users.id AS users_id,
               users.name AS users_name
        FROM users ORDER BY users.id
        LIMIT ? OFFSET ?
        (2, 1)
        ```

    - `statement`

        这个Query代表的完整的SQL语句。

        这个语句默认并没有消除歧义的标签(label)，除非之前调用了`with_labels(True)`。

    - `subquery(name=None, with_labels=False, reduce_columns=False)`

        返回代表这个查询的完整SQL语句，嵌入到一个SQL中。

        对这个查询不能生成贪婪JOIN。

        参数：

        - `name`: 赋给alias的字符串名称；将会传入到`FromClause.alias()`中。如果值
        为None，将会根据编译时间生成一个名称。

        - `with_labels`： 如果为True，将会首先为查询调用`with_labels()`，对所以列
        生成表级别的标签。

        - `reduce_columns`: 如果为True，`Select.reduce_columns()`将会对返回的
        `select()`结果调用，移除一些同样名称的列。

    - `suffix_with(*suffixes)`

        对查询加入后缀并返回新的Query。

        参数：

        - `*suffixes`: 可选的后缀，一般为字符串，不能有任何逗号。

    - `union(*q)`

        对这个查询以及其它的一个或多个查询应用UNION。

        比如：

        ```python
        q1 = session.query(SomeClass).filter(SomeClass.foo == 'bar')
        q2 = session.query(SomeClass).filter(SomeClass.bar == 'foo')

        q3 = q1.union(q2)
        ```

        这个方法可以接受多个Query对象，所以能够控制嵌套的深度。连续的`union()`调用如：

        `x.union(y).union(z).all()`

        生成的SQL为：

        ```python
        SELECT * FROM (SELECT * FROM (SELECT * FROM X UNION
                SELECT * FROM y) UNION SELECT * FROM Z)
        ```

        另外：

        `x.union(y, z).all()`

        生成的SQL：

        ```python
        SELECT * FROM (SELECT * FROM X UNION SELECT * FROM y UNION
                SELECT * FROM Z)
        ```

        注意很多数据库不允许对UNION，EXCEPT等等使用ORDER BY。想要取消所有在映射器中设置
        的ORDER BY子句，可以使用`order_by(None)` - 返回的Query结果不会在有ORDER BY
        子句。

    - `union_all(*q)`

        对这个查询以及其它的一个或多个查询应用UNION ALL。

        原理和用法与`union()`一样。

    - `update(values, synchronize_session='evaluate', update_args=None)`:

        执行一个批量更新操作。

        更新数据库中匹配这个查询的所有行。

        比如：

        ```python
        session.query(User).filter(User.age == 25).\
            update({User.age: User.age - 10}, synchronize_session=False)

        session.query(User).filter(User.age == 25).\
            update({"age": User.age - 10}, synchronize_session='evaluate')
        ```

        参数：

        - `values`

            一个字典，以属性名称，或者映射属性，或者SQL表达式作为键名，以字面量值或者SQL
            表达式作为值。如果需要`parameter-ordered model`，这个值可以传入二维元组
            的列表；这需要在参数`Query.update.update_args`传入
            `preserve_parameter_order`。

        - `synchronize_session`

            选择session中对象属性更新的策略。合理的值为：

            - `False`: 并不同步到session中。这个选项在session马上要过期(使用
            `commit()`或`expire_all()`之后)的时候使用会获得高性能而没有副作用。
            在session过期之前，session中的值保持不变，小心处理，不然会导致一些混淆型的后果。

            - `fetch`: 在更新执行执行一个select找到匹配的对象。这个更新的属性将会替代
            匹配的对象。

            - `evaluate`: 对session的对象使用Python的方式估算Query标准。

            目前，表达式估算器并不会根据数据库而改变字符串比对(collation)方法。

        - `update_args`

            可选的字典，如果传入这个参数，将会在底层传入`update()`构造器的`**kw`参数。
            可能用来传入方言特性参数如`mysql-limit`，以及其它的特殊参数如
            `preserve_parameter_order`。

        返回：

        根据数据库的"行计数(row count)"特性返回匹配的行计数值。

        > 警告
        >> - 这个方法并不支持Python中的关系级联 - 它假定所有的外键引用都设置了**ON UPDATE CASCADE**，
        否则可能会抛出一个完整性约束错误。在UPDATE之后，根据Session中的对象是否实现ON UPDATE CASCADE，
        可能并不会包含当前的状态。
        >> - `fetch`策略将会发出额外的SELECT语句，这可能会严重影响性能。
        >> - `evaluate`策略会对Session中的匹配对象执行一次扫描；如果Session中的内容
        过期了，比如调用了`session.commit()`之后，**会对每个匹配对象执行一个SELECT查询**。
        >> - 这个方法支持多表更新，这个行为并不会支持joined继承或者其它多表映射。例子：
        >>     ```python
        >>      session.query(Enginner).\
        >>          filter(Enginner.id == Employee.id).\
        >>          filter(Employee.name == 'dilbert').\
        >>          update({"engineer_type": "programmer"})
        >>     ```
        >> - 多态实体WHERE标准并不会包含single或者joined更新 - 必须手动添加，即使
            在单表继承中
        >> - `MapperEvents.before_update()`和`MapperEvents.after_update()`事件
        并不会在这个方法中被调用。对于这个方法提供了一个`SessionEvents.after_bulk_update()`方法。

    - `value`

        返回一个符合给定列表达式的结果标量。

    - `values`

        返回一个符合给定列表达式的结果迭代器。

    - `whereclause`

        一个只读的属性，它返回当前查询的WHERE子句。

        返回的结果是一个SQL表达式构造，如果没有查询标准则返回None。

    - `with_entities(*entities)`

        通过给定的实体替换原来的SELECT列表，并且返回新的Query。

        例子：

        ```python
        # Users，通过一些任意的标准来筛选然后通过相关的邮件地址来排序
        q = (session.query(User)
                    .join(User.address)
                    .filter(User.name.like('%ed%'))
                    .order_by(Addreess.email))

        # 限制User.id == 5, Address.email以及'q'，接下来会返回什么？
        subq = (q.with_entities(Address.email)
                 .order_by(None)
                 .filter(User.id == 5)
                 .subquery())
        q = q.join((subq, subq.c.email < Address.email)).limit(1)
        ```

    - `with_for_update(read=False, nowait=False, of=None, skip_locaked=False, key_share=False)`

        对`FOR UPDATE`子句设定选项并返回一个新的Query。

        这个方法的行为等同于`SelectBase.with_for_update()`。如果不适用参数调用，结果中
        的`SELECT`语句将追加一个`FOR UPDATE`子句。当有参数传入时，数据库端特定选项如
        `FOR UPDATE NOWAIT`或者`LOCK IN SHARE MODE`将会生效.

        例如：

        `q = session.query(User).with_for_update(nowait=True, of=User)`

        上面的查询在PostgreSQL将会生成如下的SQL：

        ```python
        SELECT users.id AS users_id
        FROM users
            FOR UPDATE OF users NOWAIT
        ```

    - `with_hint(selectable, text, dialect_name=""`

        对查询中指定的实体或可选择对象加入一个索引或其他执行上下文提示(executional context hint)

        `selectable`可以是一个`Table`，`Alias`或者ORM实体／映射类。

    - `with_labels()`

        对`Query.statement`返回的值应用列标签。

        指明Query语句访问器对所有列添加`<tablename>_<columnname>`形式的列标签；一般用于
        多表具有同名列时消除歧义列。

        当查询发出SQL取回数据行时，总是使用列标签。

        > 注意
        >> `Query.with_labels()`方法只应用于`Query.statement`的输出，并不会应用
        Query的其它行结果调用系统，比如`Query.first()`，`Query.all()`等等。想要使用
        `Query.with_labels()`来执行一个查询，使用`Session.execute()`来执行
        `Query.statement`：
        >>
        >> `result = session.execute(query.with_lables().statement)`

    > `with_lockmode(mode)`

        返回一个特定"锁模型"的新查询，本质上引用了`FOR UPDATE`子句。

        > v0.9: 被`Query.with_for_update()`取代。

        参数：

        - `mode`: 一个代表合法锁模式的字符串：

            - `Node`: 转译为无锁模式
            - `update`: 转译为`FOR UPDATE`(标准SQL，被大多数方言支持）
            - `update_nowait`: 转译为`FOR UPDATE NOWAIT`(Oracle，PostgreSQL8.1以上支持)
            - `read`: 转译为`LOCK IN SHARE MODE`(MySQL), 以及`FOR SHARE`(PostgreSQL)

    - `with_parent(instance, property=None, from_entity=None)`

        增加筛选标准，并关联给定的实例为一个子对象或者集合，使用它的属性状态以及一个建立好
        的`relationship()`配置。

        这个方法使用`with_parent()`函数来生成子句，结果将会传入`Query.filter()`。

        接受的参数和`with_parent()`函数一样，有种例外情况可以让property为None，这种
        情况查询将会对Query的目标映射器执行搜索。

        参数：

        - `instance`: 一个配置`relationship()`的实例。
        - `property`: 字符串property名称，或者类绑定属性，它指定实例中的哪个关系用来
            构建父／子关系。
        - `from_entity`: 考虑设置为左侧的实体。默认的Query本身为"零"实体。

    - `with_polymorphic(cls_or_mappers, selectable=None, polymorphic_on=None)`

        读取继承类的列。

        ...

    - `with_session(session)`

        使用给定的Session来返回一个Query。

        虽然`Query`通常使用`Session.query()`来实例化，但是不使用Session转而直接构建
        `Query`也是可行的。比如一个`Query`对象，或者已经关联其他`Session`的`Query`,
        可以使用这个方法关联目标session并生成一个新的Query对象：

        ```python
        from sqlalchemy.orm import Query

        query = Query([MyClass]).filter(MyClass.id == 5)

        result = query.with_session(my_session).one()
        ```

    - `with_statement_hint(text, dialect_name='*')`

        对这个`Select`增加一个语句提示。

        这个方法类似于`Select.with_hint()`除了它并不需要一个单独的表，而是把整个语句
        当成一个表。

    - `with_transformation(fn)`

        通过给定的函数变形并返回一个新的Query。

        例如：

        ```python
        def filter_something(criterion):
            def transform(q):
                return q.filter(criterion)
            return transform

        q = q.with_transformation(filter_something(x==5))
        ```

        这个方法可以用来一些专门的Query对象的创建方式。

    - `yield_per(count)`

        一次只返回`count`行(迭代器)。

        这个方法用于大数据集(大于1万行)，这个方法将结果分批装入子集合并一次性生成它的这
        部分子集合，所以Python解释器不需要一次性一次性声明非常大的内存空间，可以在相同的
        时间消耗下减少内存的使用。在读取成百上千行时性能的提升更加显著。

        `Query.yield_per()`方法**在使用集合时不兼容subquery贪婪读取或者joinedload
        贪婪读取**。它可能兼容**select in**贪婪读取，取决于数据库驱动。

        因此在一些例子中，禁用贪婪读取会很有用，而不是无条件的使用`Query.enable_eagerloads()`:

        `q = session.query(Object).yield_per(100).enable_eagerloads(False)`

        或者可以使用`lazyload()`；比如使用星号来重置为默认读取器模式：

        ```python
        q = session.query(Object).yield_per(100).\
                options(lazyload('*'), joinedload(Object.some_related))
        ```

        > 警告
        >> 使用这个方法需要小心；如果一个实例出现在多于一个的"行批"中，客户端对属性的修改
            将会被覆盖。
        >>
        >> 因为集合在随后的结果批读取时会被清除，通常不可能使用这个配置组合贪婪读取的集合。
        >>
        >> 同样要注意`yield_per()`也会设置`stream_results=True`，但是目前来说只有
        `psycopg2`, `mysqldb`, `pymysql`方言可以理解并可以使用服务端游标代替预先缓冲
        来生成流式结果。其它的DBAPI都会预先缓冲所有的行。这个用法的内存消耗远小于ORM映射对象。


## ORM特定的Query构造

- `sqlalchemy.orm.aliased(element, alias=None, name=None, flat=False, adapt_on_names=False)`

    对给定的elemetn生成一个alias，通常是一个`AliasedClass`实例。

    例如：

    ```python
    my_alias = aliased(MyClass)

    session.query(MyClass, my_alias).filter(MyClass.id > my_alias.id)
    ```

    pass


