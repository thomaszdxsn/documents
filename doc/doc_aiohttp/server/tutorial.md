# Server Tutorial

你是否想要学习`aiohttp`但是不知道从何开始？我们为你准备了一个示例，这个投票app
是学习aiohttp的绝佳之处。

如果你想要这个应用的完整源码，请[点击](https://github.com/aio-libs/aiohttp/tree/master/demos/polls/)

## Setup your environment

首先要检查你的Python版本：

```python
$ python -V
Python 3.5.0
```

这篇教程需要Python3.5或以上的版本.

我们假设你已经安装了`aiohtto`库。你可以检查安装的aiohttp是哪个版本:

```python
$ python3 -c 'import aiohttp; print(aiohttp.__version__)'
2.0.5
```

我们的项目结构看起来会像下面这样:

```txt
.
├── README.rst
└── polls
    ├── Makefile
    ├── README.rst
    ├── aiohttpdemo_polls
    │   ├── __init__.py
    │   ├── __main__.py
    │   ├── db.py
    │   ├── main.py
    │   ├── routes.py
    │   ├── templates
    │   ├── utils.py
    │   └── views.py
    ├── config
    │   └── polls.yaml
    ├── images
    │   └── example.png
    ├── setup.py
    ├── sql
    │   ├── create_tables.sql
    │   ├── install.sh
    │   └── sample_data.sql
    └── static
        └── style.css
```

## Getting started with aiohttp first app

这篇教程是基于Django的poll教程的。

## Application 

所有的aiohttp服务器都是基于`aiohttp.web.Application`实例。它使用startup/cleanup信号
来进行注册，连接路由等等。

下面的代码可以创建一个application：

```python
from aiohttp import web

app = web.Application()
web.run_app(app, host='127.0.0.1', port=8080)
```

将它保存在`aiohttpdemo/polls/main.py`文件，然后启动服务器：

`$ python3 main.py`

你可以在命令行中看到如下输出:

```python
======== Running on http://127.0.0.1:8080 ========
(Press CTRL+C to quit)
```

在你的浏览器打开`http://127.0.0.1:8000`，或者输入下面的命令:

`$ curl -X GET localhost:8080`

你应该看到服务器返回了`404: Not Found.`这意味着我们需要创建route和view。

## Views

让我们来开始写第一个views。创建文件`aiohttpdemo_polls/views.py`:

```python
from aiohttp import web

async def index(request):
    return web.Response(text='Hello Aiohttp!')
```

这可能是Aiohttp最简单的view了。现在我们需要为这个`index`view创建一个route。让我
们将route代码放入`aiohttpdemo_pool/routes.py`:

```python
from views import index


def setup_routes(app):
    app.router.add_get('/', index)
```

我们需要在某个地方调用`setup_routes`函数，最佳的地方是放在`main.py`里面:

```python
from aiohttp import web
from routes import setup_routes

app = web.Application()
web.run_app(app, host='127.0.0.1', prot=8000) 
```

重启服务器。然后再次打开浏览器，我们会看到:

```python
$ curl -X GET localhost:8000
Hello Aiohttp!
```

成功了！现在我们的项目目录应该是下面这个样子:

```txt
.
├── ..
└── polls
    ├── aiohttpdemo_polls
    │   ├── main.py
    │   ├── routes.py
    │   └── views.py
```

## Configuration files

aiohttp对于配置持不可知论。意味着这个库并不强制要求任何配置方法，也没有基于
任何的配置模式。

但是请考虑下面这些方面的因素：

1. 99%的服务器都有配置文件
2. 每个项目(除了Django，Flask这种有Python解决方式的)，都不会把配置文件和源代码
存放在一起。
    
    比如，Nginx的配置文件默认存放在`/etc/nginx`文件夹。

    Mongo的配置放在`/etc/mongod.conf`.

3. 配置文件验证是一个好主意，强验证可以预防产品开发时出现的愚蠢错误。

因此，我们**建议**使用下面的方法：

1. 使用`yaml`格式作为配置文件
2. 从一个预先定义的位置读取`yaml`配置
3. 可以通过命令行覆盖配置文件位置,或特定的一些配置
4. 对载入的字典执行严格的验证.

下面是读取配置文件并推送到app的代码:

```python
# 从当前目录的yaml文件读取配置
conf = load_config(str(pathlib.Path('.') / 'config' / 'pools.yaml'))
app['config'] = conf
```

## Database

### Setup

这篇教程我们会使用最新的PostgreSQL数据库。你可以通过下面的教程来安装PostgreSQL:

http://www.postgresql.org/download/

### Database schema

我们使用SQLAlchemt来描述数据库模式。在这篇教程中，我们创建两个简单的model，
`question`和`choice`:

```python
import sqlalchemy as sa

meta = sa.metaData()

question = sa.Table(
    'question', meta,
    sa.Column('id', Integer, nullable=False),
    sa.Column('question_text', sa.String(200), nullable=False),
    sa.Column('pub_date', sa.Date, nullable=False),

    sa.PrimaryKeyConstraint('id', name='question_id_pkey'))
)


choice = sa.Table(
    'choice', meta,
    sa.Column('id', sa.Integer, nullalbe=False),
    sa.Column('question_id', sa.Integer, nullable=False),
    sa.Column('choice_text', sa.String(200), nullable=False),
    sa.Column('votes', sa.Integer, server_default='0', nullable=False),

    sa.PrimaryKeyConstraint('id', name='choice_id_pkey'),
    sa.ForeignKeyConstraint(['question_id'], [question.c.id],
                            name='choice_question_id_fkey',
                            ondelete='CASCADE'),
)
```

你可以在数据库中找到下列的表描述。

第一个数据表是question:

question |
-- |
id | 
question_text |
pub_date |

第二个数据表是choice:

choice | 
-- |
id |
choice_text |
votes |
question_id |

### Creating connection engine

想要执行DB查询，我们需要一个engine实例。假设`conf`是一个字典，包含Postgresql
的连接配置信息：

```python
async def init_pg(app):
    conf = app['config']['postgres']
    engine = await aiopg.sa.create_engine(
        database=conf['database'],
        user=conf['user'],
        password=conf['password'],
        host=conf['host'],
        port=conf['port'],
        minsize=conf['minsize'],
        maxsize=conf['maxsize'],
        loop=app.loop
    )
    app['db'] = engine
```

连接DB的最佳地方是放在`on_startup`信号中：

```python
app.on_startup.append(init_pg)
```

### Graceful shutdown

在程序退出的时候断开所有的资源是一个好习惯。

让我们使用`on_cleanup`信号类切断DB连接:

```python
app.on_cleanup.append(close_pg)
async def close_pg(app):
    app['db'].close()
    await app['db'].wait_closed()
```

## Templates

让我们加入一些更有用的vies:

```python
@aiohttp_jinja2.template('detail1.html')
async def poll(request):
    async with request.app['db'].acquire() as conn:
        request_id = request.match_info['question_id']
        try:
            question, choices = await db.get_quest(conn, question_id)
        except db.RecordNotFound as e:
            raise web.HTTPNotFound(text=str(e))
        return {
            'question': question,
            'choices': choices
        }            
```

模版使用来快速编写网页的。我们返回一个dict，`aiohttp_jinja2.template`装饰器
将会把这个dict传入我们要渲染的字典中。

想要建立一个模版引擎，我们首先要安装`aiohttp_jinja2`:

`$ pip install aiohttp_jinja2`

安装以后，我们需要setup这个库：

```python
import aiohttp_jinja2
import jinja2


aiohttp_jinja2.setup(
    app, loader=jinja2.PackageLoader('aiohttpdemo_polls', 'templates')
)
```

## Static files

任何网站都有静态文件，图片，JS文件，CSS文件等等。

处理静态文件的最好方式是使用NGINX这种反向代理，或者使用CDN服务。

但是开发环境也要使用静态文件，aiohttp可以处理这种情况。

```python
def setup_static_routes(app):
    app.router.add_static('/static/',
                          path=PROJECT_ROOT / 'static',
                          name='static')
```

## Middlewares

中间件会在每个web-handler中堆栈。它们会在handler处理request之前被调用，
会在处理给定的response之后再次被调用。

下面我们加入了一个简单的中间件，可以显示一些好看的404/500页面。

中间件可以通过app注册，通过把中间件加入到`app.middlewares`这个list中:

```python
def setup_middlewares(app):
    error_middleware = error_pages({404: handle_404,
                                    500: handle_500})
    app.middlewares.append(error_middleware)
```

中间件本身是一个工厂，可以接受application和next handler。

这个工厂会返回一个中间件handler，它的参数签名和普通的web handler意义 - 
接受request，返回response。

下面是`error_pages`中间件：

```python
def error_pages(overrides):
    async def middleware(app, handler):
        async def middleware_handler(request):
            try:
                response = awiat handler(request)
                override = overrides.get(response.status)
                if override is None:
                    return False
                else:
                    return await override(request, response)
            except web.HTTPException as ex:
                override = overrides.get(ex.status)
                if override is None:
                    raise
                else:
                    return await override(request, ex)
            return middleware_handler
    return middleware
```

注册的overrides是一些简单的Jinja2模版renderer:

```python
async def handle_404(request, response):
    response = aiohttp_jinja2.render_template('404.html',
                                              request',
                                              {})
    return response
```

```python
async def handle_500(request, response):
    response = aiohttp_jinja2.render_template('500.html',
                                              request',
                                              {})
    return response
```


