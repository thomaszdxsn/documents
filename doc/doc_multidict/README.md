# multidict

Multidict是一个类字典集合，是可以包含(key, value)对的集合，key可能在集合中
出现多次。

## Introduction

HTTP头部和URL query string要求一个特殊的数据结构：`multidict`. 这个数据结构和
dict很类似，但是它可以为同一个key指定多个值，并且保持插入时的顺序。

key是`str`(或者在大小写不敏感的字典中使用`istr`).

`multidict`拥有四个multidict类：`MultiDict`, `MultiDictProxy`, 
`CIMultiDict`以及`CIMultiDictProxy`.

不可变类型的proxies(`MultiDictProxy`和`CIMultiDictProxy`)提供了代理multidict的动态
view，这个view反射了底层集合的变化。它们实现了`collections.abc.Mapping`的接口。

常规的可变类型(`MultiDict`和`CIMultiDict`)类提供了`collection.abc.MutableMapping`)
的接口实现，允许修改它们的内容。

大小型不敏感的类型(`CIMultiDict`和`CIMultiDictProxy`)假设它们的值是大小写不敏感的:

```
>>> dct = CIMultiDict(key='val')
>>> 'Key' in dct
True
>>> dct['Key']
'val'
```

Keys应该是`str`或者`istr`实例。

这个库出于速度的原因，提供了Cpython的优化.



