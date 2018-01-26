# sqlalchemy的一些坑

## mysql连接数过高

有时会发现mysql数据库无法返回结果，然后检查数据库，输入`show processlist`命令会发现连接数过高(超过设置的max值),
出现这种情况有以下原因:

- 使用`Session`没有显式使用`Session.close()`关闭
- 因为Web框架的debug模式原因，导致一些Session没有成功关闭<sup>\[1\]</sup>.

## MySQL server has gone away

可能服务器运行一段时间以后会出现这个问题.发生的原因可能是想要使用的一条MySQL链接已经不在了，可能出现的原因：

- 如果使用的是`scoped_session`, 那么可能没有显式的调用`Session.remove()`让sqlalchemy回收session
- sqlalchemy的`create_engine()`有一个参数叫做`pool_recycle`，指定一个时间(秒)，在超时后自动回收sleep
的链接．注意MySQL数据库同样有变量用来回收连接:`interactive_timeout`和`wait_timeout`．sqlalchemy的
回收时间应该低于后两个值<sup>\[2\]</sup>.另外在Tornado中使用`pool_recycle`好像没有作用．(乐观锁)
- 回收的悲观锁是每次连接时都预先ping一下，在sqlalchemy1.2为`create_engine`引入了一个
参数叫做`pool_pre_ping`<sup>\[3\]</sup>，在每次连接时都会对数据库发送一个低延时的`select 1`,如果发现
连接不可获取，则直接丢弃并重新获取一个连接.主要使用这个参数必须使用sqlalchemy1.2以上，目前该版本为beta状态，
想要安装需要使用命令`pip install sqlalchemy --pre`<sup>\[4\]</sup>.

### 使用apscheduler出现MySQL server has gone away

可能是因为使用`.add_jobstore()`方法时，传入的是第一个参数字符串，即apsheduler会根据uri(第一个位置参数)来生成
`engine`即数据库配置，这可能和你想要的东西相反(你可能设置了`pool_size`, `pool_recycle`，在这里都没有用了).

**解决方案**就是传入关键字参数`engine=`, 传入的值必须是一个`engine`对象，即`create_engine()`返回的值.


 
## 参考

-- | --
-- | -- 
\[1\] | [https://www.cnblogs.com/zzcflying/p/4285691.html](https://www.cnblogs.com/zzcflying/p/4285691.html)
\[2\] | [http://blog.csdn.net/bytxl/article/details/30460153](http://blog.csdn.net/bytxl/article/details/30460153)
 \[3\] | [http://docs.sqlalchemy.org/en/latest/core/pooling.html#pool-events](http://docs.sqlalchemy.org/en/latest/core/pooling.html#pool-events)
\[4\] | [https://stackoverflow.com/questions/6471549/avoiding-mysql-server-has-gone-away-on-infrequently-used-python-flask-server](https://stackoverflow.com/questions/6471549/avoiding-mysql-server-has-gone-away-on-infrequently-used-python-flask-server)
\[5\] | [SQLAlchemy数据库连接池排查记录](http://amitmatani.com/scoping-sqlalchemys-session-while-using-tornado-dot-gen)
\[6\] |  有一个博客作者提到自己通过monkey patch实现了tornado和sqlalchemy的集成,但是没有具体的实现代码[链接](http://amitmatani.com/scoping-sqlalchemys-session-while-using-tornado-dot-gen)
