# tqdm

`tqdm`是阿拉伯语"进度"(tqdadum)的意思，是西班牙短语"I love you so much"的意思。

想要让你的循环显示一个进度条 -- 只需将可迭代对象使用`tqdm(iterable)`封装就好了:

```python
from tqdm import tqdm

for i in tqdm(range(10000)):
    ...
```

`76%|████████████████████████████         | 7568/10000 [00:33<00:10, 229.00it/s]`

`trange(N)`是`tqdm(xrange(N))`的一个快捷方式。

另外可以将它当作一个单独的模块，通过管道符来使用它：

```shell
$ seq 9999999 | tqdm --unit_scale | wc -l
10.0Mit [00:02, 3.58Mit/s]
9999999
$ 7z a -bd -r backup.7z docs/ | grep Compressing | \
    tqdm --total $(find docs/ -type f | wc -l) --unit files >> backup.log
100%|███████████████████████████████▉| 8014/8014 [01:37<00:00, 82.29files/s]
```

它的开销是很低的，每次迭代大概只需消耗60ns。

除了低开销，`tqdm`使用了一种聪明的算法可以预测剩余时间，跳过不必要的迭代显示，
有时候甚至无需开销。

## Installation

`pip install tqdm`

## Changelog

[link](https://github.com/tqdm/tqdm/releases)

## Usage

`tqdm`用途非常广泛。它的主要三个使用场景如下：

### Iterable-based

使用`tqdm()`封装任意可迭代对象:

```python
text = ""
for char in tqdm(['a', 'b', 'c', 'd']):
    text += char
```

`trange(i)`是`tqdm(range(i))`的快捷方式:

```python
for i in trange(100):
    pass
```

也可以在循环外面实例化:

```python
pbar = tqdm(['a', 'b', 'c', 'd'])
for char in pbar:
    pbar.set_description("Processing %s" % char)
```

### Manual

可以通过`with`语句来手动控制`tqdm()`的更新:

```python
with tqdm(total=100) as pbar:
    for i in range(10):
        pbar.update(10)
```

如果提供了可选参数`total`，将会显示预测数值。

`with`也是可选的：

```python
pbar = tqdm(total=100)
for i in range(10):
    pbar.update(10)
pbar.close()
```

### Module

可能tqdm最有用的地方就是可以在脚本或者命令行中。只要将`tqdm`插入管道符号之前
就好了。

```shell
$ time find . -name '*.py' --exec cat \{} \; | wc -l
857365

real    0m3.458s
user    0m0.274s
sys     0m3.325s

$ time find . -name '*.py' -exec cat \{} \; | tqdm | wc -l
857366it [00:03, 246471.31it/s]
857365

real    0m3.585s
user    0m0.862s
sys     0m3.358s
```

注意，在命令行中也可以为`tqdm`指定参数:

```shell
$ find . -name '*.py' --exec cat \{} \; |
    tqdm --unit loc --unit_scale --total 857366 >> /dev/null
100%|███████████████████████████████████| 857K/857K [00:04<00:00, 246Kloc/s]
```

## FAQ and Known Issues

用户最长碰到的问题是关于进度条多行显示的问题。

- 控制台必须支持回车(`CR`, `\r`)
- 嵌套型进度条
    - 控制台必须支持光标移动到之前的行。一些IDE缺乏这些支持。
- 封装枚举型可迭代对象：请使用`enumerate(tqdm(...))`而不是`tqdm(enumerate(...))`.
- 封装zip型可迭代对象：请使用`zip(tqdm(a), b)`而不是`tqdm(zip(a, b))`.

## Document

```python
class tqdm(object):
    """
    装饰一个可迭代对象，返回一个迭代器，其实还是最初的可迭代对象，但是会打印一
    个动态更新的进度条。
    """
    
    def __init__(self, iterable=None, desc=None, total=None, leave=None,
                 file=None, ncols=None, mininterval=0.1,
                 maxinterval=10.0, miniters=None, ascii=None, disable=False,
                 unit='it', unit_scale=False, dynamic_ncols=False,
                 smooothing=0.3, bar_foramt=None, initial=0, position=None,
                 postfix=None):
```

参数:

- iterable: iterable, 可选

    为这个iterable装饰一个进度条。如果留空，需要手动进行更新。

- desc: str, 可选

    进度条的前缀。

- total: int, 可选

    期望迭代的次数。如果为默认值None，那么就使用`len(iterable)`作为值。

- leave: bool, 可选

    如果为默认值True，保持追踪终端的所有进度条.

- file: `io.TextIOWrapper`或者`io.StringIO`, 可选

    指定进度消息输出到哪里(默认:`sys.stderr`).

- ncols: int, 可选

    整个输出消息的宽度。

- minimalinterval: float, 可选

    进度显示更新的最小间隔，相对于时间单位seconds。

- maxinterval: float, 可选

    进度更新的最大间隔，相对于时间单位seconds.

- miniters: int, 可选

    进度更新的最小间隔，相对于迭代。

- ascii: bool, 可选

    如果未指定，或者为False。使用unicode来填充meter。

- disable: bool, 可选

    是否禁用整个进度条。

- unit: str, 可选

    一个字符串，用来定义每次迭代的单位。

- unit_scale: book | int | float，可选

    ...

- dynamic_ncols: bool, 可选

    如果设置，将会根据环境来修改`ncols`.

- smoothing: float, 可选

    速度预测的指标。

- bar_format: str, 可选

    指定一个自定义的bar字符串格式。可能会影响性能。

- initial: int, 可选

    初始的计数值。可以用来重启一个进度条。

- position: int, 可选

    指定这个bar打印时的行offset。
   
- unit_divisor: float, 可选

    默认为1000.

额外的命令行选项:

- delim: chr, 可选

    分隔字符，默认为`n`。

- buf_size: int, 可选

    在指定`delim`时字符串的缓冲bytes。

- bytes: bool, 可选

    如果为true，将会计数bytes，忽略`delim`.

## Examples

[examples](https://github.com/tqdm/tqdm/tree/master/examples) 
