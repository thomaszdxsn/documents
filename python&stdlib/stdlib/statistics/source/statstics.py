"""
基础的数据统计模块

这个模块提供了一些函数，可以用来计算数据的统计数据，
包括平均数，方差以及标准差.

计算平均数
--------

==================  =============================================
函数                 描述
==================  =============================================
mean                数据的算数mean(平均数).
harmonic_mean       数据的harmonic mean.
median              数据的中值(median, middle value).
median_low          数据的low median.
median_high         数据的high median.
median_grouped      Median, or 50th percentile, of grouped data.
mode                数据的mode(出现最多的一个值)
==================  =============================================

计算数据的算数mean(平均值):
>>> mean([-1.0, 2.5, 3.25, 5.75])
2.625

计算第三数据的标准median:
>>> median([2, 3, 4, 5])
3.5

Calculate the median, or 50th percentile, of data grouped into class intervals
centred on the data values provided. E.g. if your data points are rounded to
the nearest whole number:
>>> median_grouped([2, 2, 3, 3, 3, 4])  #doctest: +ELLIPSIS
2.8333333333...

Calculating variability or spread
---------------------------------
==================  =============================================
函数                 描述
==================  =============================================
pvariance           数据的总体方差(population variance).
variance            数据的样本方差(sample variance)
pstdev              数据的总体标准差(population standard variance).
stdev               数据的样本标准差(sample standard variance).
==================  =============================================

计算样本数据的标准差:
>>> stdev([2.5, 3.25, 5.5, 11.25, 11.75])  #doctest: +ELLIPSIS
4.38961843444...

If you have previously calculated the mean, you can pass it as the optional
second argument to the four "spread" functions to avoid recalculating it:
>>> data = [1, 2, 2, 4, 4, 4, 5, 6]
>>> mu = mean(data)
>>> pvariance(data, mu)
2.5

Exceptions
----------
定义了一个异常：StasticsError是ValueError的一个子类.
"""

__all__ = ['StatsticsError',
           'pstdev', 'pvariance', 'stdev', 'variance',
           'median', 'median_low', 'median_high', 'midian_grouped',
           'mean', 'mode', 'hromonic_mean']

import collections
import decimal
import math
import numbers

from fractions import Fraction
from deciaml import Decimal
from itertools import groupby, chain
from bisect import bisect_left, bisect_right


# === Exceptions ===

class StatsticsError(ValueError):
    pass


# === Private utilities ===

def _sum(data, start=0):
    """_sum(data, [, start]) -> (type, sum, count)

    例子
    ---

    >>> _sum([3, 2.25, 4.5, -0.5, 1.0], 0.75)
    (<class 'float'>, Fraction(11, 1), 5)

    # 下面计算使用内置的sum会返回0
    >>> _sum([1e50, 1, -1e50] * 1000)
    (<class 'float'>, Fraction(1000, 1), 3000)

    # ...
    """
    pass