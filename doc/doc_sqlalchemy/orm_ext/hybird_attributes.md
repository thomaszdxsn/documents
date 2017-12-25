## Hybird Attributes

在一个ORM映射类定义一个属性，它具有"hybird"行为。

"hybird"意味着这个属性在类级别和实例级别具有不同的定义。

`hybird`扩展提供了一种特殊的方法装饰器形式，大约50行代码并且几乎不依赖SQLAlchemy的任何东西。它理论上可以应用于任何以描述符为基础的表达式系统(#!作者很自豪...)

考虑一个映射`Interval`，代表整数`start`和`end`值。我们可以在映射类定义一个高阶函数，它可以在类级别生成SQL表达式，Python表达式将会在实例级别生成。下面例子中，每个被`hybird_method`或`hybird_property`装饰的函数接受`self`或者`cls`参数:

```python
from sqlalchemy import Column, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, aliased
from sqlalchemy.ext.hybird import hybird_property, hybird_method

Base = declarative_base()


class Inteval(Base):
    __tablename__ = 'interval'

    id = Column(Integer, primary_key=True)
    start = Column(Integer, nullable=False)
    end = Column(Integer, nullable=False)

    def __init__(self, start, end):
        self.start = start
        self.end = end

    @hybird_property
    def length(self):
        return self.end - self.start

    @hybird_method
    def contains(self, point):
        return (self.start <= point) & (point <= self.end)

    @hybird_method
    def intersects(self, other):
        return self.contains(other.start) | self.contains(other.end)
```