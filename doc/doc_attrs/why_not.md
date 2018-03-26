# Why not...

## tuples?

### Readablity

下面两者在调试的时候哪种看起来更显而易见

`Point(x=1, y=2)`

或者

`(1, 2)`

?

让我们加入更多歧义:

`Customer(id=42, reseller=23, first_name="Jane", last_name="John")`

或者

`(42, 24, "Jane", "John")`

?

你不会喜欢`customer[2]`胜于`customer.first_name`把?

更别说加入嵌套的情况呢。如果你重来没有编写过复杂的元祖，你就不会知道
它有多可怕，在调试的时候更加是。

使用合适的类以及名称和类型，可以让程序代码更具可读性，更容易让人理解。

### Extendability

假设你有一个函数，接受或者返回一个tuple。特别是如果你使用tuple unpacking(比如:`x, y = get_point()`).
如果tuple增加了新的元素呢？你是不是要把程序中所有涉及的代码都改一遍。

使用为类加入属性名的方式，你只需要在访问的时候操心属性名称即可。

## namedtuples?

`collections.namedtuple()`是一个可以带名称的元祖，而不是class。

由于在Python中编写类很麻烦，这个数据结构某些时候更加方便。

但是这个方便是有代价的。

`namedtuple`和`attr`的最大区别就在于，后者是可以指定类型的:

```python
>>> import attr
>>> C1 = attr.make_class("C1", ['a'])
>>> C2 = attr.make_class("C2", ['a'])
>>> i1 = C1(1)
>>> i2 = C2(1)
>>> i1.a == i2.a
True
>>> i1 == i2
False
```

`nametuple`内部行为类似tuple，所以可以和tuple直接比较:

```
>>> from collections import namedtuple
>>> NT1 = namedtuple('NT1', 'a')
>>> NT2 = namedtuple('NT2', 'b')
>>> t1 = NT1(1)
>>> t2 = NT2(1)
>>> t1 == t2 == (1,)
True
```

还有其它一些副作用：

- 因为它继承自`tuple`，所以`nametuple`有length，并可以被迭代和索引访问。

- 可迭代性可能让你意外地将`namedtuple`给unpack.

- `nametuple`有它的示例上面有自己的方法，不管你需不需要.

- `namedtuple`总是不可变的.不由你决定.

- 想要为`nametuple`增加方法，只能继承它。

    但是你如果跟着标准库文档推荐的做法:

    ```
    class Point(namedtuple('Point', ['x', 'y'])):
        # ...
    ```

    你会发现在它的`__mro__`中有两个`Point`: `[<class 'point.Point'>, <class 'point.Point'>, <type 'tuple'>, <type 'object'>]`


## dicts

字典不支持固定的字段.

如果你有一个字典，它将一些东西映射到另一些东西上面。你应该可以增加和移除这些值。

`attrs`允许你实现；而字典不行。

换句话说：如果你的字典拥有固定对象，那么它就是一个对象，而不是hash。

## hand-written classes?

我们可以对比一下手写类并且实现9种方和`attrs`的不同.

`attrs`的方式:

```
>>> @attr.s
... class SmartClass(object):
...    a = attr.ib()
...    b = attr.ib()
>>> SmartClass(1, 2)
SmartClass(a=1, b=2)
```

手写类的方式:

```
>>> class ArtisanalClass(object):
...     def __init__(self, a, b):
...         self.a = a
...         self.b = b
...
...     def __repr__(self):
...         return "ArtisanalClass(a={}, b={})".format(self.a, self.b)
...
...     def __eq__(self, other):
...         if other.__class__ is self.__class__:
...             return (self.a, self.b) == (other.a, other.b)
...         else:
...             return NotImplemented
...
...     def __ne__(self, other):
...         result = self.__eq__(other)
...         if result is NotImplemented:
...             return NotImplemented
...         else:
...             return not result
...
...     def __lt__(self, other):
...         if other.__class__ is self.__class__:
...             return (self.a, self.b) < (other.a, other.b)
...         else:
...             return NotImplemented
...
...     def __le__(self, other):
...         if other.__class__ is self.__class__:
...             return (self.a, self.b) <= (other.a, other.b)
...         else:
...             return NotImplemented
...
...     def __gt__(self, other):
...         if other.__class__ is self.__class__:
...             return (self.a, self.b) > (other.a, other.b)
...         else:
...             return NotImplemented
...
...     def __ge__(self, other):
...         if other.__class__ is self.__class__:
...             return (self.a, self.b) >= (other.a, other.b)
...         else:
...             return NotImplemented
...
...     def __hash__(self):
...         return hash((self.a, self.b))
>>> ArtisanalClass(a=1, b=2)
ArtisanalClass(a=1, b=2)
```



