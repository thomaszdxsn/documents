## Horizontal Sharding

支持水平分片.

定义一个基础的"horizontal sharding"系统，允许session跨数据库执行查询和持久化操作。

### API

- class`sqlalchemy.ext.horizontal_shard.ShardedSession(shard_chooser, id_chooser, query_chooser, shard=None, query_cls=<class 'sqlalchemy.ext.horizontal_shard.ShardedQuery'>, **kwargs)`

    基类: `sqlalchemy.orm.session.Session`

    - `__init__(shard_chooser, id_chooser, shards=None, query_cls=<class 'sqlalchemy.ext.horizontal_shard.ShardedQuery'>, **kwargs)`

        构建一个Sharded Session.

        参数:

        - `shard_chooser`: 一个可调用对象，接受一个Mapper, 一个mapper实例，或者一个SQL字句，返回Shard ID.
        - `id_chooser`: 一个可调用对象，传入一个查询或者标识值，它应该返回一个shard列表。对数据库的查询安装这个列表的顺序进行.
        - `query_chooser`: 通过一个给定的查询，返回这个查询提到的shard ID.
        - `shards`: 一个字典，包含shard engine对象的字符串名称。


- class`sqlalchemy.ext.horizontal_shard.ShardedQuery(*args, **kwargs)`

    Base: `sqlalchemy.orm.query.Query`

    - `set_shard(shard_id)`

        限制单个shard ID， 返回一个新的查询。

        所有接下来的操作都会基于这单个shard。

    