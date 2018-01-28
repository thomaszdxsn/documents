# Connection Pooling¶

## Connection Pool Configuration

最常用的`QueuePool`配置都通过在`create_engine()`传入关键字参数来设定：`pool_size`, `max_overflow`, `pool_recycle`和`pool_timeout`。例如:

```python
engine = create_engine('postgresql://me@localhost/mydb',
                       pool_size=20, max_overflow=0)
```

## Switching Pool Implementations

想要使用另一种连接池，可以通过`create_engine`的关键字参数`poolclass`来指定：

```python
from sqlalchemy.pool import QueuePool
engine = create_engine('sqlite:///file.db', poolclass=QueuePool)
```

使用`NullPool`可以禁用连接池：

```python
from sqlalchemy.pool import NullPool
engine = create_engine(
          'postgresql+psycopg2://scott:tiger@localhost/test',
          poolclass=NullPool)
```

## Using a Custom Connection Function

所有的`Pool`类都接受一个`creator`可调用对象，可以用它来创建一个新的连接。`create_engine`同样接受这个参数，然后传给Pool：

```python
import sqlalchemy.pool as pool
import psycopg2


def getconn():
    c = psycopg2.connect(username='ed', host='127.0.0.1', dbname='test')
    # 可以在这里对c做一些事情
    return c

engine = create_engine('postgresql+psycopg2://', creator=getconn)
```

## Constructing a Pool

pass

## Pool Events

pass

## Dealing with Disconnects¶

pass

### Disconnect Handling - Pessimistic(连接失去的处理 - 悲观)

