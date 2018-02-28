# Arrow: better dates and times for Python

## What?

Arrow是一个Python库，可以提供比标准库datetime更好的时间对象处理功能。

## Why？

Python标准库的缺点是：

- 模块太多:datetime, time, calendar, dateutil, pytz等等
- 类型太多:date, time, datetime, tzinfo, timedelta, relativedelta
- 时区和时间戳的转换太啰嗦，也很不友好
- 原生支持的时区太少
- 缺少功能：ISO-8601解析，时间跨度，易阅读格式

## Feature

- 可以完全的代替datetime
- 支持Python 2.6, 2.7, 3.3, 3.4 3.5
- 时区敏感，默认支持UTC
- 对常见场景支持超简单的创建选项
- 更新，替换方法支持相对值，包括week
- 自动格式化和解析字符串
- 部分ISO-8601支持
- 时区转换
- 时间戳可以作为priperty获取(datetime是一个方法)
- 生成时间跨度，范围，下限和上下的单位从年到毫秒
- 可以自定义Arrow衍生类型
- 支持humanize

