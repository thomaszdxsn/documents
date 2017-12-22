## Periodict Tasks

### Introduce

**celery beat**是一个规划器；它使用一个有规律的间隔来触发任务，然后被cluster中的空闲worker执行。

默认的entries从`beat_schedule`设置提取出来，但是也可以使用自定义的存储方式，就像在一个数据库存储entries一样。

你必须确保只有一次只运行一个规划器(scheduler)来规划任务，否则会导致重复的任务。使用一个中心化的方法意味着规划必须要再担心同步问题，也就是不需要为它的操作加上锁。

### Time Zones

周期任务默认使用UTC时区，但是你可以使用`timezone`setting来更改时区。

下面是一个例子:

```python
timezone = 'Europe/London'
```

这个setting必须加入到你的app中，要么直接加入如`app.conf.timezone = 'Europe/London'`，或者在你设定了配置模块时加入到文件中。

默认的规划器(将schedule存储在`celerybeat-schedule`文件)将会自动察觉时区变化，然后会修改本身的schedule，但是其它的scheduler未必有这么聪明了，这种情况你就需要手动解决。

> Django用户须知:
>
>> 在修改时区设置后必须手动通知scheduler:
>>
>> ```python
>> $ python manage.py shell
>> >>> from dcelery.models import PeriodicTask
>> >>> PeriodicTask.objects.update(last_run_at=None)
>> ```

### Entries

想要周期性的调用一个任务，你必须将它加入到beat schedule list.

```python
from celery import Celery
from celery.shedules import crontab

app = Celery()

@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # 每10秒调用一次 test('hello')
    sender.add_periodic_task(10.0, test.s('hello'), name='add every 10')
    
    # 每30秒调用一次 test('world')
    sender.add_periodic_task(30.0, test.s('world'), expires=10)

    # 每周一早上7:30执行
    sender.add_periodic_task(
        crontab(hour=7, minute=30, day_of_week=1),
        test.s('Happy Mondays!')
    )


@app.task
def test(arg):
    print(arg)
```

设置`on_after_configure`这个handler意味着在使用`test.s()`的时候不会在这个模块级别evaluate app。

`add_periodic_task()`函数将会在幕后把entry加入到`beat_schedule`设置，同样的设置可以手动在每个周期任务上面设定。

例子：每30秒运行一次`task.add`任务:

```python
app.conf.beat_schedule = {
    'add-every-30-seconds`: {
        "task": "tasks.add",
        "schedule": 30.0,
        "args": (16, 16)
    },
}

app.conf.timezone = 'UTC'
```

就像`cron`一样，如果在碰到下一个任务的时候第一个任务还没有执行完毕，这个任务将会被覆盖。如果你担心这个事情，可以使用locking策略来确保一次只运行一个实例。

#### Available Fields

- `task`

    想要执行的任务名称。

- `schedule`

    任务执行的频率。

    这个参数可以指定为一个整数值，`timedelta`对象，或者一个`crontab`对象。另外可以通过schedule的接口定义你自己的时间类型。

- `args`

    位置参数(`list`或者`tuple`)

- `kwargs`

    关键字参数(`dict`)

- `options`

    执行选项(`dict`)

    可以传入任何`apply_asnyc()`支持的参数

- `relative`

    如果`relative=True`，`timedelta`规划将会“by the clock"来规划。

    默认为False，频率会相对于`celery beat`启动的时间。


### Crontab schedules

如果你想要更加精度的控制一个任务的执行，例如，一个特定日期或者礼拜的时间，你可以使用`crontab`schedule类型.

```python
from celery.schedules import crontab

app.conf.beat_schedule = {
    "add-every-monday-morning": {
        'task': 'tasks.add',
        'schedule': crontab(hour=7, minute=30, day_of_week=1),
        'args': (16, 16)
    },
}
```

Crontab表达式的语法是非常弹性的。

一些例子:

例子 | 意义
-- | --
crontab() | 每分钟执行一次
crontab(minute=0, hour=0) | 每天午夜执行一次
crontab(minute=0, hour='*/3') | 每三个小时执行一次
crontab(minute=0, hour='0,3,6,9,12,15,18,21') | 每三小时执行一次
crontab(minute='%15') | 每15分钟执行一次
crontab(day_of_week='sunday') | 周日的每分钟执行一次
crontab(minute='*', hour='*', day_of_week='sun') | 周日的每分钟执行一次
crontab(minute='*/10', hour='3,17,22' day_of_week='thu,fri') | 在周4，周5的3点，17点，22点每十分钟执行一次
crontab(minute=0, hour='\*/2,\*/3') | 每个能被2,3整除的小时执行一次.
crontab(minute=0, hour='*/5') | 在每个能被5整除的小时执行一次
crontab(minute=0, hrou='*/3,8-17') | 在每天8-17时的每个能被3整除的小时执行一次
crontab(0, 0, day_of_month='1-7,15-21') | 在每个月的第一周和第三周执行一次
crontab(0, 0, day_of_month='11', month_of_year='5') | 在每年的5月11日执行一次
crontab(0, 0, month_of_year='*/3') | 在每个季度的第一个月执行一次

### Solar schedules

如果你有个任务需要在按照每天的日出，日落，黄昏来执行，你可以使用`solar`类型:

```python
from celery.schedules import solar

app.conf.beat_schedule = {
    # Executes at sunset in Melbourne
    'add-at-melbourne-sunset': {
        'task': 'tasks.add',
        'schedule': solar('sunset', -37.81753, 144.96715),
        'args': (16, 16)
    },
}
```

参数很简单：`solar(event, latitude, longitude)`

确保使用正确的经纬度符号:

符号 | 参数 | 意义
-- | -- | --
+ | latitude | north
- | latitude | south
+ | longitude | east
- | longitude | west

可能的事件类型为:

事件 | 意义
-- | --
dawn_astronomical | 在天不是完全暗的受执行。也就是在太阳低于地平线18度的时候。
dawn_nautical | 在天边有一点光的时候执行。也就是太阳低于地平线12度的时候。
dawn_civil | 在光亮足够，可以进行户外活动的时候执行。也就是太阳低于地平线6度的时候。
sunrise | 在太阳和东边地平线持平时执行。
solar_noon | 在太阳距地平线最高的时候执行（正午）。
sunset | 在晚上，太阳正在从地平线的西边消失时执行。
dusk_civil | 在晚上，太阳低于地平线6度的时候执行。
dusk_nautical | 在晚上，太阳低于地平线12度的时候执行.
dusk_astronomical | 在晚上，太阳低于地平线18度的时候执行.

所有的solar事件都是基于UTC计算而来，因此不受你的时区设置影响。


### Starting the Scheduler

想要启动`celery beat`服务:

`$ celery -A proj beat`

你可以通过`-B`选项将beat嵌入到worker，如果只运行了一个worker node，这个方法很方便，但是并不推荐在生产环境这么使用。

`$ celery -A proj worker -B`

Beat需要将任务运行的最后时间存储在一个本地的数据库文件中(默认叫做`celerybeat-schedule`)，所以需要当前目录的写入权限，或者你可以通过命令指定一个存放文件的位置:

`$ celery -A proj beat -s /home/celery/var/run/celerybeat-schedule`


#### Using custom scheduler classes

可以通过命令行指定自定义的schduler class(`--scheduler`).

默认的scheduler是`celery.beat.PersistentScheduler`,它只是简单的使用`shelve`数据库保持了对任务最后运行时间的追踪。

另外有一个`django-celery-beat`扩展，它将shedule存储在Django的数据库中，并且提供了一个方便的后台界面可以让你管理周期性任务.

如果你想要安装和使用这个扩展：

1. 使用`pip`安装这个包:

    `$ pip install django-celery-beat`

2. 将`django_celery_beat`模块添加到Django的配置`INSTALLED_APPS`中：

    ```python
    INSTALL_APPS = (
        ...,
        'django_celery_beat',
    )
    ```

    注意模块名会自动将`-`转换为下划线.

3. 使用Django数据库迁移，创建需要的表:

    `$ python manage.py migrate`

4. 使用`django_celery_beat.schedulers:DatabaseScheduler`来开启`beat`服务：

    `$ celery -A proj beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler`

5. 去Django-Admin界面设置一些周期性任务
