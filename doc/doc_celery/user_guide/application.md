[TOC]

## Application

使用Celery库必须实例化一个Celery实例，这个实例一般叫做application(简称app).

application是线程安全的，所以可以在一个进程空间中共存多个不同配置，组件和任务的appliaction。

现在让我们创建一个application：

```python
>>> from celery improt Celery
>>> app = Celery()
>>> app
<Celery __main__:0x100469fd0>
```

最后一行展示了应用的文本形式：包含app的类名(Celery)，当前模块的名称(`__main__`)，以及对象的内存地址(0x100469fd0).

### Main Name

只有一个东西是重要的，即main模块的名称。让我们看一看为什么这样说。

当你在一个Celery中发送一个任务消息，这个消息并不会包含任何源代码，只会包含你要执行的任务名称。这个模式很像internet中hostname的模式：每个worker维持一份任务名称和真实函数的映射，通过任务resgiry来调用。

无论何时你定义一个任务，这个任务同样会加入到局部的registry：

```python
>>> @app.task
... def add(x, y):
...     return x + y

>>> add
<@task: __main__.add>

>>> add.name
__main__.add

>>> app.tasks['__main__.add']
<@task: __main__.add>
```

在这里你可以再次看到`__main__`；无论何时Celery不能够函数所属的模块，它会使用main模块名来生成任务名的初始部分。

在一些使用例子会被受限：

1. 如果模块的task在一个运行的程序中被定义
2. 如果这个应用创建于Python的shell中

任务模块同样用于启动一个worker，调用:`app.worker_main()`

```python
# tasks.py
from celery import Celery

app = Celery()

@app.task
def add(x, y):
    return x + y


if __name__ == '__main__':
    app.worker_main()
```

当这个模块被执行后，任务名称会以`__main__`来起始，但是当模块被其它进程import时，这些任务将会以`tasks`(真实的模块名称)作为名称的开始部分:

```python
>>> from tasks import add
>>> add.name
tasks.add
```

你可以在主模块中定义一个其它的名称：

```python
>>> app = Celery('tasks')
>>> app.main
'tasks'

>>> @app.task
... def add(x, y):
...     return x + y

>>> add.name
tasks.add
```

### 配置

可以通过一些选项来改动Celery的运行方式。这些选项可以直接在app的实例化时传入，或者使用一个专门的配置模块。

这些配置可以通过`app.conf`来获取：

```python
>>> app.conf.timezone
'Europe/London'
```

你也可以直接设置一个配置值：

`>>> app.conf.enable_utc = True`

或者使用`update`方法一次性更新多个键：

```python
>>> app.conf.update(
...     enable_utf=True,
...     timezone='Europe/London'    
)
```

这些配置对象构成了多个配置字典，最后会以如下顺序决定优先级：

1. 运行时的改动
2. 配置模块(如果存在)
3. 默认配置(`celery.app.defaults`)

你甚至可以通过`app.add_defaults()`方法增加新的默认值。

#### Configure_from_object

`app.config_from_object()`方法可以从一个配置(configuration)对象读取配置。

配置对象可以是一个配置模块，或者一个包含配置属性的任意对象。

注意在调用`config_from_object()`之前的配置都会被重置。

#### 例子1:使用一个模块的名称

`app.config_from_object()`方法可以使用一个Python模块的名称，或者可以是一个Python属性名称。例如：`celeryconfig`, `myproj.config.celery`或者`myproj.config:CeleryConfig`:

```python
from celery import Celery

app = Celery()
app.config_from_object('celeryconfig')
```

这个`celeryconfig`模块可能看起来像这样：

```python
# celeryconfig.py

enable_utc = True
timezone = 'Europe/London'
```

#### 例子2: 传入一个真正的模块对象

也可以传入一个引入(imported)的模块对象，但是并不推荐这样使用。

```python
import celeryconfig

from celery import Celery

app = Celery()
app.config_from_object(celeryconfig)
```

#### 例子3: 使用一个配置类/对象

```python
from celery import Celery

app = Celery()


class Config:
    enable_utc = True
    timezone = 'Europe/London'

app.config_from_object(Config)
```

#### config_from_envvar

`app.config_from_envvar()`可以从环境变量中拿到配置模块名称。

例如 -- 想要读取一个特定的环境变量`CELERY_CONFIG_MODULE`，使用它作为配置模块的名称：

```python
import os
from celery import Celery

# 设置默认的配置模块名称
os.environ.setdefault('CELERY_CONFIG_MODULE', 'celeryconfig')

app = Celery()
app.config_from_envvar('CELERY_CONFIG_MODULE')
```

`$ CELERY_CONFIG_MODULE='celeryconfig.prod' celery worker -l info`

#### Censored configuration

如果你想要打印配置，就像debugging信息一样显示，但是你也想要筛选掉敏感信息如密码和API key。

Celery提供了很多工具方法可以展示配置信息，其中的一个就是`humanize()`:

`>>> app.conf.humanize(with_defaults=False, ceonsord=True)`

这个方法将会把配置以tabulated字符串形式返回。这个操作将只会包含修改的默认配置。

如果你更想将配置显示为字典形式，可以使用`table`方法：

`>>> app.conf.table(with_defaults=False, censored=True)`

请注意Celery不会移除所有的敏感信息，只会使用正则表达式来筛选掉常见的键名。

如果你的信息很敏感，考虑在键名中包含以下子串：

`API, TOKEN, KEY, SECRET, PASS, SIGNATURE, DATABASE`

### Laziness

applcation实例是懒加载的，意味着直到真正需要时它才会被加载。

创建一个`Celery`只会做以下的事情：


1. 创建一个逻辑时钟实例，用于事件。
2. 创建一个任务注册器。
3. 将它设置为当前app(但是如果禁用了`set_as_current`的参数就不会)。
4. 调用`app.on_init()`回调.

`app.task()`装饰器在任务定义时并不会创建任务，而是把任务的创建推迟到任务被使用时或者应用已经*finalized*再执行。

下面这个例子展示了直到你使用任务(或者访问它的属性)之前这个任务都不会被创建：

```python
>>> @app.task
>>> def add(x, y):
...     return x + y

>>> type(add)
<class 'celery.local.PromiseProxy'>

>>> add.__evaluated__()
False

>>> add     # 调用了对象的__repr__()方法
<@task: __main__.add>

>>> add.__evaluated__()
True
```

app的finalization可以通过显式调用`app.finalize()` - 抑或隐式访问`app.tasks`属性来实现。

finalizing对象将会：

1. 拷贝任务必须在apps之间分片(shared)

    任务默认是被分片的(shared)，然是如果任务装饰器中禁用了`shared`参数，那么这个任务将会绑定当前app，供它私有使用。

2. evaluate所有的pending任务装饰器。

3. 确保所有的任务都绑定到了当前的app。

    任务绑定到一个app，所以可以从配置中读取默认值。

> "default app"
>>
>> Celery并不是一开始就有application的，它主要用于当作模块级API，并且会在celery发布版本5.0之前保持API的向后兼容性。
>>
>> Celery总是会创建一个特殊的app -- `default app`，如果没有实例化自定义app这会使用这个默认app。
>>
>> `celery.task`模块适应了旧式API。你应该总是使用app实例的方法，而不是模块级别的API
>>
>> 例如，旧的`Task`基类有很多兼容性特性，但是很多新的特性并不兼容，比如任务方法：
>>
>> ```python
>> from celery.task import Task     # << 旧的Task基类
>>
>> from celery import Task          # << 新的Task基类
>> ```

### 打破枷锁(breaking the chain)

有时可能会很依赖当前设置的app，最佳实践是总是在任何需要的地方传入这个app实例。

这也叫做“app chain”， 它根据传入的app创建了一个实例的链条。

下面的例子可以任务是一个差的实践：

```python
from celery import current_app


class Scheduler(object):
    def run(self):
        app = current_app
```

它更应该接受一个`app`参数：

```python
class Scheduler(object):
    def run(self, app):
        self.app = app
```

Celery内部使用`celery.app.app_or_default()`函数：

```python
from celery.app import app_or_default

class Scheduler(object):
    def __init__(self, app=None):
        self.app = app_or_default(app)
```

在开发中，你可以设置`CELERY_TRACE_APP`环境变量，在碰到app chain破裂的时候可以抛出错误：

`$ CELERY_TRACE_APP=1 celery worker -l info`

## 抽象任务

所有通过`@task`装饰器创建的任务都是继承自应用的`Task`基类。

可以使用`base`参数来指定一个不同的base类：

```python
@app.task(base=OtherTask)
def add(x, y):
    return x + y
```

想要创建一个自定义Task基类，你需要继承中立(netural)基类`celery.Task`:

```python
from celery import Task

class DebugTask(Task):
    def __call__(self, *args, **kwargs):
        print('TASK STARING: {0.name}[{0.request.id}]'.format(self))
        return super(DebugTask, self).__call__(*args, **kwargs)
```

> tips
>>
>> 如果你覆盖了任务的`__call__`方法时，一个很重要的地方就是要调用super()方法让基类的`__call__()`将会进行的工作继续完成。

中立基类是特殊的，因为它没有绑定任何特定的app。一旦任务绑定一个app以后它就会从中读取配置读取配置作为默认值。

想要使用一个基类，你需要使用`app.task()`装饰器：

```python
@app.task(base=DebugTask)
def add(x, y):
    return x + y
```

甚至也可以更改`app.Task()`属性来更改一个application的基类：

```python
>>> from celery import Celery, Task

>>> app = Celery()

>>> class MyBaseTask(Task):
...     queue = 'hipri'

>>> app.Task = MyBaseTask
>>> app.Task
<unbound MyBaseTask>

>>> @app.task
... def add(x, y):
...     return x + y

>>> add
<@task: __main__.add>


>>> add.__class__.mro()
[<class add of <Celery __main__:0x1012b4410>>,
 <unbound MyBaseTask>,
 <unbound Task>,
 <type 'object'>]
```

