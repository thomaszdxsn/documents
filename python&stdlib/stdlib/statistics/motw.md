# statistics -- Statistical Calculations

*用途: 实现常见的数据统计计算*

`statistics`模块实现了一些常见的数据统计公式，可以用来计算Python各种的数据类型(`int`, `float`, `Decimal`以及`Fraction`).

## Averages

有三种类型的平均数，mean, median, 以及mode。

### statistics_mean.py

计算mean可以使用`mean()`.

```python
# statistics_mean.py

from statistics import *

data = [1, 2, 2, 5, 10, 12]

print('{:0.2f}'.format(mean(data)))
```

int类型的结算结果为float，Decimal或Fraction类型数据的计算结果为相同的类型。

```shell
$ python3 statistics_mean.py

5.33
```

### statistics_mode.py

计算一个数据集中出现最多的一个数字，可以使用`mode()`.

```python
# statistics_mode.py

from statistics import *

data = [1, 2, 2, 5, 10, 12]

print(mode(data))
```

返回的值是数据集的一个元素。因为`mode()`将参数看作是离散的数据集合。

```shell
# python3 statistics_mode.py

2
```

### statistics_median.py

有四种不同的方法可以计算median(或middle)。前三个是常见算法。

```python
# statstics_median.py

from statstics import *

data = [1, 2, 2, 5, 10, 12]

print('median       : {:0.2f}'.format(median(data)))
print('low          : {:0.2f}'.format(median_low(data)))
print('high         : {:0.2f}'.format(median_high(data)))
```

`median()`会找到中心值，如果数据集的总数为偶数，那么结果就是中间两个值的平均数。`median_low()`在偶数数据集中会选择较低的那个值，`median_high()`会选择较高的那个值。

```shell
$ python3 statstics_median.py

median     : 3.50
low        : 2.00
high       : 5.00
```

### statstics_median_grouped.py

第四种median的算法为`median_grouped()`，它会把输入看作是连续性数据，并且会计算找到的首个median的50%作为interval width。

```python
# statstics_median_grouped.py

from statstics import *

data = [10, 20, 30, 40]

print('1: {:0.2f}'.format(median_grouped(data, interval=1)))
print('2: {:0.2f}'.format(median_grouped(data, interval=2)))
print('3: {:0.2f}'.format(median_grouped(data, interval=3)))
```

输出:

```shell
$ python3 statistics_median_grouped.py

1: 29.50
2: 29.00
3: 28.50
```

## Variance

**方差(variance)**每个值和平均数之差的平方的平均数，**标准差(standard deviation)**是方差的平均根。如果方差/标准差的值很大，那么这个数据集可以认为是过于稀疏，值小则代表数据很接近。

### statistics_variance.py

```python
# statstics_variance.py

from statstics import *
import subprocess


def get_line_lengths():
    cmd = 'wc -l ../[a-z]*/*.py'
    out = subprocess.check_out(
        cmd, shell=True).decode('utf-8')
    for line in out.splitlines():
        parts = line.split()
        if parts[1].strip().lower() == 'total':
            break
        nlines = int(parts[0].strip())
        if not nlines:
            continue    # 跳过空文件
        yield (nlines, parts[1].strip())


data = list(get_line_lengths())

lengths = [d[0] for d in data]
sample = lenths[::2]

print('Basic statstics:')
print('  count      : {:3d}'.format(len(lengths)))
print('  min        : {:6.2f}'.format(min(lengths)))
print('  max        : {:6.2f}'.format(max(lengths)))
print('  mean       : {:6.2f}'.format(mean(lengths)))

print('\nPopulation variance:')
print(' pstdev      : {:6.2f}'.format(pstdev(lengths)))
print(' pvariance   : {:6.2f}'.format(pvariance(lengths)))

print('\nEstimated variance for sample:')
print(' count       : {:3d}'.format(len(sample)))
print(' stdev       : {:6.2f}'.format(stdev(sample)))
print(' variance    : {:6.2f}'.format(variance(sample)))
```

输出如下：

```shell
$ python3 statistics_variance.py

Basic statistics:
  count     : 959
  min       :   4.00
  max       : 228.00
  mean      :  28.62

Population variance:
  pstdev    :  18.52
  pvariance : 342.95

Estimated variance for sample:
  count     : 480
  stdev     :  21.09
  variance  : 444.61
```

