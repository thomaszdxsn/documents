# Quickstart tutorial

## Prerequisites

首先需要了解Python。

其次要安装numpy。

## The Basics

NumPy的最要对象是一个同质多维度数组。

它是一个元素(通常是数字)表，元素都是同一个类型，由一个正整数元祖作为索引。

NumPy的唯独叫做`axes`，axes的数量叫做`rank`.

NumPy的array类叫做`ndarray`。它通常也叫做`array`。请注意，它和Python标准库的
`array.array`不一样。

一个`ndarray`最重要的属性如下：

- `ndarray.ndim`

    这个array的axes数量(也就是rank，维度的数量)。

- `ndarray.shape`

    array的维度。这是一个整数元祖，代表数组的每一个维度。比如一个矩阵拥有`n` rows，
    m `columns`，那么它的`shape`就是`(n, m)`。因此，shape元祖的长度就是rank。

- `ndarray.dtype`

    一个对象，描述array中元素的类型。可以指定为标准的Python类型，或者使用NumPy
    提供的类型，`numpy.int32`， `numpy.int16`, `numpy.float64`...

- `ndarray.size`

    数组中的元素总数。

- `ndarray.itemsize`

    数组中每个元素的大小(以bytes计)。

    例如，一个数组的元素类型为`float64`，拥有`itemsize8(=64/8)`；类型`complex32`
    的`itemsize4(=32/8)`.

- `ndarray.data`

    包含array元素的缓冲区。通常我们不需要直接使用这个元素，因为我们一般通过索引
    来访问。

### An example

...

### Array Creation

有多种方式可以创建一个数组.

例如你可以通过`array`函数接受一个常规的Python list或者tuple来构建一个array。

array的type取决于序列对象元素的type。

嵌套的序列可以转换为多维数组.

NumPy还提供了一个函数叫做`arange`，它模范自内置函数`range`，但是会返回一个array.

如果arange是有浮点数作为step参数，它可能造成不可预见的切分，这是因为浮点数精度
的问题。处于这个原因，我们可以使用`linspace`函数，它可以让我们指定想要的元素数量，
而不是根据step来切分:

```python
>>> from numpy import pi
>>> np.linspace(0, 2, 9)
array([ 0.  ,  0.25,  0.5 ,  0.75,  1.  ,  1.25,  1.5 ,  1.75,  2.  ])
>>> x = np.linspace(0, 2*pi, 100)
>>> f = np.sin(x)
```

### Printing Arrays

想你想要打印一个数组的时候，NumPy会把它们以嵌套list的形式来打印，但是有下面的布局:

- 最后的一个axis会从左到右打印
- 第二个到最后一个将会从上之下打印
- 剩下的同样会从上倒下打印，通过空白来分割.

### Basic Operations

除了支持常规的操作符以外，还支持很多unary操作:

```python
>>> a = np.random.random((2, 3))
>>> a 
array([[ 0.18626021,  0.34556073,  0.39676747],
       [ 0.53881673,  0.41919451,  0.6852195 ]])
>>> a.sum()
2.5718191614547998
>>> a.min()
0.1862602113776709
>>> a.max()
0.6852195003967595
```

默认情况，这些操作会应用到整个array。你可以通过`axis`参数指定你要应用维度:

```python
>>> b = np.arange(12).reshape(3, 4)
>>> b
array([[ 0,  1,  2,  3],
       [ 4,  5,  6,  7],
       [ 8,  9, 10, 11]])
>>> b.sum(axis=0)   # 计算每一列的sum
array([12, 15, 18, 21])
>>> b.min(axis=1)
array([0, 4, 8])
>>> b.cumsum(axis=1)
array([[ 0,  1,  3,  6],
       [ 4,  9, 15, 22],
       [ 8, 17, 27, 38]])
```

### Universal Functions

NumPy提供了一些熟悉的数学函数如sin, cos, exp...

在NumPy中，它们都叫做"universal functions"(ufunc).

在NumPy中，这些函数将会操作到数组的元素，生产另一个数组作为输出:

```python
>>> B = np.arange(3)
>>> B
array([0, 1, 2])
>>> np.exp(B)
array([ 1.        ,  2.71828183,  7.3890561 ])
>>> np.sqrt(B)
array([ 0.        ,  1.        ,  1.41421356])
>>> C = np.array([2., -1., 4.])
>>> np.add(B, C)
array([ 2.,  0.,  6.])
```

### Indexing, Slicing and Interating

**一维**数组可以被索引，切片以及迭代:

```python
>>> a = np.arange(10) ** 3
>>> a
array([  0,   1,   8,  27,  64, 125, 216, 343, 512, 729])
>>> a[2]
8
>>> a[2:5]
array([ 8, 27, 64])
>>> a[:6:2] = -1000    # equivalent to a[0:6:2] = -1000; from start to position 6, exclusive, set every 2nd element to -1000
>>> a
array([-1000,     1, -1000,    27, -1000,   125,   216,   343,   512,   729])
>>> a[ : :-1]                                 # reversed a
array([  729,   512,   343,   216,   125, -1000,    27, -1000,     1, -1000])
>>> for i in a:
...     print(i**(1/3.))
...
nan
1.0
nan
3.0
nan
5.0
6.0
7.0
8.0
9.0
```

**多维**数组的每个axis都有索引。所以索引以元祖形式传入:

```python
>>> def f(x, y):
...     return 10 * x + y
...
>>> b = np.fromfunction(f, (5, 4), dtype=int)
>>> b
array([[ 0,  1,  2,  3],
       [10, 11, 12, 13],
       [20, 21, 22, 23],
       [30, 31, 32, 33],
       [40, 41, 42, 43]])
>>> b[2,3]
23
>>> b[0:5, 1]                       # each row in the second column of b
array([ 1, 11, 21, 31, 41])
>>> b[ : ,1]                        # equivalent to the previous example
array([ 1, 11, 21, 31, 41])
>>> b[1:3, : ]                      # each column in the second and third row of b
array([[10, 11, 12, 13],
       [20, 21, 22, 23]])
```

`narray.flat`属性可以将数组压缩成为一个list，所以你可以迭代它了。

### Shape Manipulation

#### Changing the shape of an array

```python
>>> a = np.floor(10*np.random.random((3,4)))
>>> a
array([[ 2.,  8.,  0.,  6.],
       [ 4.,  5.,  1.,  1.],
       [ 8.,  9.,  3.,  6.]])
>>> a.shape
(3, 4)

# .ravel() # 返回flatten的(一维)数组
>>> a.ravel()
array([ 2.,  8.,  0.,  6.,  4.,  5.,  1.,  1.,  8.,  9.,  3.,  6.])

# .reshape() 可以修改数组的shape
>>> a.rshape(6, 2)
array([[ 2.,  8.],
       [ 0.,  6.],
       [ 4.,  5.],
       [ 1.,  1.],
       [ 8.,  9.],
       [ 3.,  6.]])
# .T 返回transposed，逆转的数组
>>> a.T
array([[ 2.,  4.,  8.],
       [ 8.,  5.,  9.],
       [ 0.,  1.,  3.],
       [ 6.,  1.,  6.]])
>>> a.T.shape
(4, 3)
>>> a.shape
(3, 4)
```

#### Stacking together different arrays

几个arrays可以使用不同的axies组合在一起:

```python
>>> a = np.floor(10*np.random.random((2, 2)))
>>> a
array([[ 8.,  8.],
       [ 0.,  0.]])
>>> b = np.floor(10*np.random.random((2, 2)))
>>> b
array([[ 1.,  8.],
       [ 0.,  4.]])
>>> np.vstack((a, b))   # 0 axies
array([[ 8.,  8.],
       [ 0.,  0.],
       [ 1.,  8.],
       [ 0.,  4.]])
>>> np.hstack((a, b))   # 1 axies
array([[ 8.,  8.,  1.,  8.],
       [ 0.,  0.,  0.,  4.]])
```

### Copies and Views

在操作数组的时候，它们的数据有时候会被拷贝到一个新的数组中，有时候却不会，
新手很容易在这个时候搞混。

下面是三种情况.

#### No Copy at All

简单的复制不会造成数据拷贝.

对函数传入的参数也不会拷贝.

#### View or Shallow Copy

不同的array对象可以分享同样的数据。

`view`方法可以创建一个array的拷贝.

对一个array切片也会返回它的view.

#### Deep Copy

`copy`方法会完整地拷贝一个array的数据.

