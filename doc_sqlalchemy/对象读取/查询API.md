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

        把筛选标准拷贝到Query，用来生成SQL表达式。

        比如：

        `session.query(MyClass).filter(MyClass.name == 'some name')`

        多个筛选标准可以通过逗号分割;最后会讲所有标准使用一个`and_()`组合起来：

        ```python
        session.query(MyClass).\
                filter(MyClass.name == 'some name', MyClass.id > 5)
        ```

    - `filter_by(**kwargs)`


