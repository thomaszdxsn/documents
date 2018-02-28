# User's Guide

## Creation

可以简单的创建当前时间的对象：

```python
>>> arrow.utcnow()
<Arrow [2013-05-07T04:20:39.369271+00:00]>

>>> arrow.now()
<Arrow [2013-05-06T21:20:40.841085-07:00]>

>>> arrorw.now('US/Pacific')
<Arrow [2013-05-06T21:20:44.761511-07:00]>
```

也可以通过时间戳来创建：

```python
>>> arrow.get(1367900664)
<Arrow [2013-05-07T04:24:24+00:00]>

>>> arrow.get('1367900664')
<Arrow [2013-05-07T04:24:24+00:00]>

>>> arrow.get(1367900664.152325)
<Arrow [2013-05-07T04:24:24.152325+00:00]>

>>> arrow.get('1367900664.152325')
<Arrow [2013-05-07T04:24:24.152325+00:00]>
```

可以接受`datetime`对象作为参数:

```python
>>> arrow.get(datetime.utcnow())
<Arrow [2013-05-07T04:24:24.152325+00:00]>

>>> arrow.get(datetime(2013, 5, 5), 'US/Pacific')
<Arrow [2013-05-05T00:00:00-07:00]>

>>> from dateutil import tz
>>> arrow.get(datetime(2013, 5, 5), tz.gettz('US/Pacific'))
<Arrow [2013-05-05T00:00:00-07:00]>

>>> arrow.get(datetime.now(tz.gettz('US/Pacific')))
<Arrow [2013-05-06T21:24:49.552236-07:00]>
```

可以从字符串解析：

```python
>>> arrow.get('2013-05-05 12:30:45', 'YYYY-MM-DD HH:mm:ss')
<Arrow [2013-05-05T12:30:45+00:00]>
```

从字符串中搜索date：

```python
>>> arrow.get('June was born in May 1980', 'MMMM YYYY')
<Arrow [1980-05-01T00:00:00+00:00]>
```

支持解析部分的ISO-8601格式:

```python
>>> arrow.get('2013-09-30T15:34:00.000-07:00')
<Arrow [2013-09-30T15:34:00-07:00]>
```

`Arrow`对象可以直接实例化，接受和`datetime`一样的参数：

```python
>>> arrow.get(2013, 5, 5)
<Arrow [2013-05-05T00:00:00+00:00]>

>>> arrow.Arrow(2013, 5, 5)
<Arrow [2013-05-05T00:00:00+00:00]>
```

## Properties

可以转换成datetime或者timestamp形式：

```python
>>> a = arrow.utcnow()
>>> a.datetime
datetime.datetime(2013, 5, 7, 4, 38, 15, 447644, tzinfo=tzutc())

>>> a.timestamp
1367901495
```

获取一个原生的datetime以及tzinfo:

```python
>>> a.naive
datetime.datetime(2013, 5, 7, 4, 38, 15, 447644)

>>> a.tzinfo
tzutc()
```

获取任何datetime的属性值：

```python
>>> a.year
2013
```

可以调用datetime的方法:

```python
>>> a.date()
datetime.date(2013, 5, 7)

>>> a.time()
datetime.time(4, 38, 15, 447644)
```

## Replace & shift

可以修改一些数据，然后返回给你一个新的Arrow对象：

```python
>>> arw = arrow.utcnow()
>>> arw
<Arrow [2013-05-12T03:29:35.334214+00:00]>

>>> arw.replace(hour=4, minute=40)
<Arrow [2013-05-12T04:40:35.334214+00:00]>
```

获取获取向前/向后的一个时间：

```python
>>> arw.shift(weeks=+3)
<Arrow [2013-06-02T03:29:35.334214+00:00]>
```

可以直接替换时区：

```python
>>> arw.replace(tzinfo='US/Pacific')
<Arrow [2013-05-12T03:29:35.334214-07:00]>
```

## Format

```python
>>> arrow.utcnow().format('YYYY-MM-DD HH:mm:ss ZZ')
'2013-05-07 05:23:16 -00:00'
```

## Convert

可以通过时区名称来转换：

```python
>>> utc = arrow.utcnow()
>>> utc
<Arrow [2013-05-07T05:24:11.823627+00:00]>

>>> utc.to('US/Pacific')
<Arrow [2013-05-06T22:24:11.823627-07:00]>

>>> utc.to(tz.gettz('US/Pacific'))
<Arrow [2013-05-06T22:24:11.823627-07:00]>
```

或者使用简写形式：

```python
>>> utc.to('local')
<Arrow [2013-05-06T22:24:11.823627-07:00]>

>>> utc.to('local').to('utc')
<Arrow [2013-05-07T05:24:11.823627+00:00]>
```

## Humanize

相对于当前时间的humanize：

```python
>>> past = arrow.utcnow().shift(hours=-1)
>>> past.humanize()
'an hour ago'
```

或者相对于另一个Arrow或datetime对象：

```python
>>> present = arrow.utcnow()
>>> feature = present.shift(hours=2)
>>> feature.humanize(present)
'in 2 hours'
```

支持local化:

```python
>>> future = arrow.utcnow().shift(hours=1)
>>> future.humanize(a, locale='ru')
'через 2 час(а,ов)'
```

## Range & spans

获取任何单位内的时间跨度：

```python
>>> arrow.utcnow().span('hour')
(<Arrow [2013-05-07T05:00:00+00:00]>, <Arrow [2013-05-07T05:59:59.999999+00:00]>)
```

后者直接获取它的floor或者ceiling：

```python
>>> arrow.utcnow().floor('hour')
<Arrow [2013-05-07T05:00:00+00:00]>

>>> arrow.utcnow().ceil('hour')
<Arrow [2013-05-07T05:59:59.999999+00:00]>
```

也可以获取一个范围内的所有时间跨度：

```python
>>> start = datetime(2013, 5, 5, 12, 30)
>>> end = datetime(2013, 5, 5, 17, 15)
>>> for r in arrow.Arrow.span_range('hour', start, end):
...     print(r)
...
(<Arrow [2013-05-05T12:00:00+00:00]>, <Arrow [2013-05-05T12:59:59.999999+00:00]>)
(<Arrow [2013-05-05T13:00:00+00:00]>, <Arrow [2013-05-05T13:59:59.999999+00:00]>)
(<Arrow [2013-05-05T14:00:00+00:00]>, <Arrow [2013-05-05T14:59:59.999999+00:00]>)
(<Arrow [2013-05-05T15:00:00+00:00]>, <Arrow [2013-05-05T15:59:59.999999+00:00]>)
(<Arrow [2013-05-05T16:00:00+00:00]>, <Arrow [2013-05-05T16:59:59.999999+00:00]>)
```

或者直接迭代一个时间范围:

```python
>>> start = datetime(2013, 5, 5, 12, 30)
>>> end = datetime(2013, 5, 5, 17, 15)
>>> for r in arrow.Arrow.range('hour', start, end):
...     print repr(r)
...
<Arrow [2013-05-05T12:30:00+00:00]>
<Arrow [2013-05-05T13:30:00+00:00]>
<Arrow [2013-05-05T14:30:00+00:00]>
<Arrow [2013-05-05T15:30:00+00:00]>
<Arrow [2013-05-05T16:30:00+00:00]>
```

## Factories

可以自定义Arrow类型：

```python
>>> class CustomArror(arrow.Arrow):
...     
...     def days_till_xmas(self):
...         xmas = arrow.Arrow(self.year, 12, 25)
...         if self > xmas:
...             xmas = xmas.shift(years=1)
...         return (xmas - self).days
```

然后可以将它作为一个工厂函数使用：

```python
>>> factory = arrow.ArrowFactory(CustomArrow)
>>> custom = factory.utcnow()
>>> custom
>>> <CustomArrow [2013-05-27T23:35:35.533160+00:00]>

>>> custom.days_till_xmas()
>>> 211
```

## Tokens

使用下面的token来解析/格式化。注意这里的token和`strptime()`函数使用的不同：

 | | Token | Output
 -- | -- | --
 Year | YYYY | 2000, 2001, 2002...
 | | YY | 00, 01, 02...
 Month | MMMM | January, February, March...
 | | MMM | Jan, Feb, Mar
 | | MM | 01, 02, 03 ... 11, 12
 | | M | 1, 2, 3...
 Day of Year | DDDD | 001, 002...364, 365
 | | DDD | 1, 2, 3...
 Day of Month | DD | 01, 02,...30, 31
 | | D | 1, 2, 3..., 4, 5
 | | Do | 1st, 2nd...31st
 Day of Week | dddd | Monday...
 | | ddd | Mon ...
 | | dd | 1, 2 ...
 Hour | HH | 00, 01, ... 24
 | | H | 0, 1, 2...24
 | | hh | 01, 02, ... 12
 | | h | 1, 2, 3 ... 12
AM/PM | A | AM, PM, am, pm
| | a | am,pm
Minute | mm | 00, 01 .. 58, 59
| | m | 0, 1, 2, ... 58, 59
Second | ss | 00, 01 .. 58, 59
| | s | 0, 1, 2...58, 59
Sub-Second | S... | 0, 02, 003, ...
Timezone | ZZZ | Asia/Baku, Europe/Warsaw, GMT
| | ZZ | -07:00, -06:00 ... +06:00, +07:00
| | Z | -0700, -0600 ... +0600, +0700
Timestamp | X | 1381685817

## API Guide

- class`arrow.Arrow(year, month, day, hour=0, minute=0, second=0, microsecond=0, tzinfo=None)`

    参数:

    - year
    - month
    - day
    - hour
    - minute
    - second
    - microsecond
    - tzinfo
    
    方法：

    - classmethod`now(tzinfo=None)`

        构建一个新的Arrow对象，代表给定时区的当前时间(now)

    - classmethod`utcnow()`

        构件一个新的Arrow对象，代表UTC的当前时间

    - classmethod`fromtimestamp(timestamp, tzinfo=None)`

        用一个给定的timestamp来构件一个新的Arrow对象，将它转换为给定的时区。

    - classmethod`utcfromtimestamp(timestamp)`

        用一个给定的timestamp来构建一个新的Arrow对象，属于UTC时间

    - classmethod`fromdatetime(dt, tzinfo=None)`

        通过一个给定的`datetime`对象来构件一个新的`Arrow`对象，可以选择替换它的时区。

    - classmethod`fromdate(date, tzinfo=None)`

        通过一个给定的`date`对象来构件一个新的`Arrow`对象，可以选择替换它的时区。

    - classmethod`strptime(date_str, fmt, tzinfo=None)`

        使用`datetime.strptime`的格式化语法来构建一个`Arrow`对象。

    - classmethod`range(frame, start, end=None, tz=None, limit=None)`

        返回一个`Arror`对象的list，代表一个区间内的时间对象(按frame间隔)。

        参数:

        - `frame`：可以是任何`datetime`属性(year, month...字符串形式)
        - `start`
        - `end`
        - `tz`
        - `limit`

    - classmethod`span_range(frame, start, end, tz=None, limit=None)`

        返回一个tuple list，每个tuple代表一个时间跨度(xx:00 - xx:59)

    - classmethod`interval(frame, start, end, interval=1, tz=None)`

        返回一个tuple list，代表时间范围内的时间间隔.

        重点是interval参数，如果传入frame='hour', interval=2, 那么就代表间隔为2hour.

        用法：

        ```python
        >>> start = datetime(2013, 5, 5, 12, 30)
        >>> end = datetime(2013, 5, 5, 17, 15)
        >>> for r in arrow.Arrow.interval('hour', start, end, 2):
        ...     print(r)
        (<Arrow [2013-05-05T12:00:00+00:00]>, <Arrow [2013-05-05T13:59:59.999999+00:00]>)
        (<Arrow [2013-05-05T14:00:00+00:00]>, <Arrow [2013-05-05T15:59:59.999999+00:00]>)
        (<Arrow [2013-05-05T16:00:00+00:00]>, <Arrow [2013-05-05T17:59:59.999999+00:0]>)
        ```
    
    - `tzinfo`

    - `datetime`

    - `naive`

        返回naive datetime.

    - `timestamp`

        返回Arrow对象的UTC时间戳

    - `float_timestamp`

        返回Arrow对象的浮点数精度时间戳

    - `clone()`

        clone一个当前对象。

    - `replace(**kwargs)`

        修改一些属性，然后返回一个新的`Arrow`对象.对标`datetime.replace()`方法。

    - `shift(**kwargs)`

        使用复数的参数名来**相对性**地修改当前的值：

        ```python
        >>> import arrow
        >>> arw = arrow.utcnow()
        >>> arw
        <Arrow [2013-05-11T22:27:34.787885+00:00]>
        >>> arw.shift(years=1, months=-1)
        <Arrow [2014-04-11T22:27:34.787885+00:00]>
        ```

        甚至可以这样，直接把日期更改到本周周五：

        ```python
        >>> arw.shift(weekday=5)
        <Arrow [2013-05-11T22:27:34.787885+00:00]>
        ```
    
    - `to(tz)`

        根据给定的时区转换并返回一个新的Arrow对象。

    - `span(frame, count=1)`

        返回两个新的`Arrow`对象，代表Arrow对象给定timefram的时间跨度。

        用法：

        ```python
        >>> arrow.utcnow()
        <Arrow [2013-05-09T03:32:36.186203+00:00]>

        >>> arrow.utcnow().span('hour')
        (<Arrow [2013-05-09T03:00:00+00:00]>, <Arrow [2013-05-09T03:59:59.999999+00:00]>)

        >>> arrow.utcnow().span('day')
        (<Arrow [2013-05-09T00:00:00+00:00]>, <Arrow [2013-05-09T23:59:59.999999+00:00]>)

        >>> arrow.utcnow().span('day', count=2)
        (<Arrow [2013-05-09T00:00:00+00:00]>, <Arrow [2013-05-10T23:59:59.999999+00:00]>)
        ```
    
    - `floor(frame)`

        返回一个新的Arrow对象，代表这个对象在timeframe下的下标值。

    - `ceil(frame)`

        返回一个新的Arrow对象，代表这个对象在timeframe下的上标值。

    - `format(fmt='YYYY-MM-DD HH:mm:ssZZ', locale='en_us')`

        根据格式化字符串来将一个Arrow对象格式化输出。

    - `humanize(other=None, locale='en_us', only_distance=False, granularity='auto')`

        返回一个相对的，localized的，humanized的表达形式。

    - `date()`

    - `time()`

    - `timetz()`

    - `astimezone()`

    - `utcoffset()`

        返回一个`timedelta`对象，代表和UTC时间的差值。

    - `dst()`

        返回一个daylight savings time adjustment.

    - `timetuple()`

        返回当前时间的`time.struct_time`，当前时区

    - `utctimetuple()`

        返回当前时间的`time.struct_time`，UTC时间.

    - `toordinal()`

        Returns the proleptic Gregorian ordinal of the date.

    - `weekday()`

        返回weekday，0-6

    - `isoweekday()`

        返回ISO weekday，1-7

    - `isocalendar()`

        返回一个3-tuple (ISO year, ISO week number, ISO weekday)

    - `isoformat()`

        返回ISO8601格式的字符串。

    - `ctime()`

    - `stftime(format)`

        按照`datetime.strptime`的语法来格式化。

    - `for_json()`

        序列化simplejson的`for_json`协议


### arrow.factory

- class`arrow.factory.ArrowFactory(type=<class 'arrow.arrow.Arrow')`

    一个用于生成Arrow对象的factory。

    - `get(*args, **kwargs)`

        根据输入对象来决定怎么创建Arrow。

    - `utcnow()`

    - `now(tz=None)`

### arrow.api

将`ArrowFactory`的方法作为模块API呈现.

- `arrow.api.get(*args, **kwargs)`

- `arrow.api.utcnow()`

- `arrow.api.now(tz=None)`

- `arrow.api.factory(type)`

### arrow.locale

- class`arrow.locales.get_locale(name)`

- class`arrow.locales.Locale`

    ...
