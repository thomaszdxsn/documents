# Descriptor HowTo Guide

-- | --
-- | --
Author | Raymond Hettinger
Contact | python@rcn.dom

## Abstract

定义描述符，总结描述符协议，然后展示描述符如何被调用。

检查自定义描述符和几个Python内置描述符，包括functions，properties, static method, class method...

展示这些描述符是怎么通过纯pyhton实现的。

## Definition and Introduce

一般来说，**描述符是一个对象属性，具有"绑定行为(binding behavior)"**，访问这个属性
的时候会被描述符协议的方法所覆盖。这些方法分别是`__get__()`, `__set__()`,以及
`__delete__()`。如果有一个对象定义了这些方法，那么就可以说它是一个描述符了。

属性默认的形式就是可以对一个对象的字典进行get，set和delete。

对于实例来说，`a.x`的查询链将会从`a.__dict__['x']`开始，然后是`type(a).__dict__['a']`，
然后是基类的基类....

如果你查询的值是定义了描述符方法，Python会覆盖默认的行为，直接调用这个描述符方法。

优先级链条去取决于描述符方法定义在哪里。

描述符是一个强大的，用途广泛的协议。这个协议是properties, method, static method, class method
和`super()`之后的机制。Python2.2以后定义新式类就是通过它来实现的。描述符简化了底层的C代码，
提供了一套弹性的接口供程序员使用。

## Descriptor Protocol

`descr.__get__(self, obj, type=None) --> value`

`descr.__set__(self, obj, value) --> None`

`descr.__delete__(self, obj) --> None`

描述符协议就这三个方法。一个对象只要定义了它们中的任一一个方法，就是一个描述符。
在查询属性行为发生的时候，就会优先查找描述符。

如果一个对象同时定义了`__get__()`和`__set__()`，那么就可以认为它是一个数据描述符。
只定义了`__get__()`方法的对象叫做非数据描述符.

数据描述符和非数据描述符之间的区别就在于它们实例字典的覆盖和计算方法不同：

- 如果一个数据描述符和实例字典的值存在名称一样的情况，那么数据描述符优先级更高
- 如果一个非数据描述符和实例字典的值存在名称一眼的情况，那么实例字典的优先级更高

如果想要创建一个只读的数据描述符，可以同时定义`__get__()`和`__set__()`，在
调用`__set__()`的时候抛出一个`AttributeError`.

定义`__set__()`方法但是只抛出异常，同样可以让它成为一个数据描述符。

## Invoking Descriptors

描述符可以直接通过它的方法名来调用。例如: `d.__get__(obj)`.

但是描述符最常见的方法方式是把它直接当作属性访问。例如`obj.d`将会查询`obj`的
字典。如果`d`定义了方法`__get__()`，然后就会按照描述符的优先级规则调用`d.__get__(obj)`.

调用的细节取决于`obj`是一个对象还是一个类。

对于对象来说，这个机制就和`object.__getattribute__()`一样，将会把`b.x`转换为
`type(b).__dict__['x'].__get__(b, type(b))`.这个实现的优先级是按照数据描述符优先
实例变量，实例变量优先于非数据描述符的规则的.最低的优先级是`__getattr__()`.

完整的C实现可以查看[PyObject\_GenericGetAttr()](https://docs.python.org/3/c-api/object.html#c.PyObject_GenericGetAttr).

对于类来说，`type.__getattribute__()`将会把`B.x`转换为`B.__dict__['x'].__get__(None, B)`.
用纯Python来描述:

```python
def __getattribute__(self, key):
    "Emulate type_getattro() in Objects/typeobject.c"
    v = object.__getattribute__(self, key)
    if hasattr(v, '__get__'):
        return v.__get__(None, self)
    return v
```

最值得记住的几点包括:

- 描述符通过`__getattribute__()`方法调用
- 覆盖`__getattribute__()`将会妨碍描述符的自动调用
- `object.__getattribute__()`和`type.__getattribute__()`调用`__get__()`的方式不同。
- 数据描述符的优先级高于实例字典.
- 非数据描述符的优先级低于实例字典.

`super()`返回的对象同样有一个自定义的`__getattribute__()`方法用来调用描述符。
调用`super(B, obj).m()`将会理解搜索到`obj.__class__.__mro__`中在B前面的基类A，
然后返回`A.__dict__['m'].__get__(obj, B)`。如果没有一个描述符，`m`会无修改返回。
如果不在字典中，`m`将会转而使用`object.__getattribute__()`进行搜索。

`super_getattro()`的实现细节可以在[`Objects/typeobject.c`](https://github.com/python/cpython/tree/3.6/Objects/typeobject.c)找到.

上面描述的细节展示了描述符的机制写在了`object`, `type`和`super()`的`__getattribute__()`方法中。如果覆盖这个方法就会关闭描述符。

## Descriptor Exmaple

下面的代码创建了一个class，它有一个数据描述符，在每次get/set的时候都会打印一条消息。

直接覆盖`__getattribute__()`也可以达到这个目的。不过，描述符可以用来监控某几个属性：

```python
class RevealAccess(object):
    
    def __init__(self, initval=None, name='var'):
        self.val = initval
        self.name = name

    def __get__(self, obj, objtype):
        print('Retrieving', self.name)
        return self.val

    def __set__(self, obj, val):
        print('Updating', self.name)
        self.val = val


>>> class MyClass(object):
...     x = RevealAccess(10, 'var "x"')
...     y = 5
...
>>> m = MyClass()
>>> m.x
Retrieving var "x"
10
>>> m.x = 20
Updating var "x"
>>> m.x
Retrieving var "x"
20
>>> m.y
5
```

这个协议很简单，但是提供了很多可能性。最常见的使用例子就是function, property,
bound method, static method 以及 class method. 它们都是基于描述符协议.

## Properties

调用`property`是创建数据描述符的一个简洁方式：

`property(fget=None, fset=None, fdel=None, doc=None) -> property attribute`

下面的例子使用property来管理属性x:

```python
class C(object):
    def getx(self): return self.__x
    def setx(self, value): self.__x = value
    def delx(self): del self.__x
    x = property(getx, setx, delx, "I'm the 'x' property.")
```

下面是`property`纯Python语言的实现细节:

```python
class Property(object):
    """模仿PyProperty_Type() in Objects/descrobject.c"""

    def __init__(self, fget=None, fset=None, fdel=None, doc=None):
        self.fget = fget
        self.fset = fset
        self.fdel = fdel
        if doc is None and fget is not None:
            doc = fget.__doc__
        self.__doc__ = doc

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        if self.fget is None:
            raise AttributeError('unreachble attribute')
        return self.fget(obj)

    def __set__(self, obj, value):
        if self.fset is None:
            raise AttributeError("can't set attribute")
        self.fset(obj, value)

    def __delete__(self, obj):
        if self.fdel is None:
            raise AttributeError("can't delete attribute")
        self.fdel(obj)

    def getter(self, fget):
        return type(self)(fget, self.fset, self.fdel, self.__doc__)

    def setter(self, fset):
        return type(self)(self.fget, fset, self.fdel, self.__doc__)

    def deleter(self, fdel):
        return type(self)(self.fget, self.fset, fdel, self.__doc__)
```

`property()`这个内置的描述符可以允许一个用户接口像访问属性一样地访问。

例如，一个数据表格类可以通过`Cell('b10').value`来访问一个cell的值:

```python
class Cell(object):
    ...

    def getvalue(self):
        self.recalc()
        return self._value

    value = property(getvalue)
```

## Functions and Methods

Python的面向对象特性都是基于函数。使用非数据描述符可以让它们两者无缝衔接.

Class字典将方法当作函数来存储。在一个class的定义中，方法使用`def`或者`lambda`
来编写。Methods和一般函数不同之处在于它会保留对象实例作为自己的第一个参数。
Python的命名惯例把这个参数叫做`self`，但其实可以为它取任何的名称。

为了支持方法调用，函数会包含`__get__()`方法，在访问属性的时候调用绑定的方法。
这意味着函数是非数据描述符，在通过一个对象调用它们的时候会返回绑定方法。

使用纯Python来表达它:

```pyhton
class Function(object):
    ...
    def __get__(self, obj, objtype=None):
        """模仿 func_descr_get() in Objects/funcobject.c"""
        if obj is None:
            return self
        return types.MethodType(self, obj)
```

运行解释器，让我们看看函数描述符在实际中是如何运转的：

```python
>>> class D(object):
...     def f(self, x):
...         return x
...
>>> d = D()

# 通过类字典来访问函数不会调用`__get__`.
# 只会返回底层的函数对象.
>>> D.__dict__['f']
<function D.f at 0x00C45070>

# 使用点式记号法调用`__get__()`也只会返回底层的函数
>>> D.f
<function D.f at 0x00C45070>

# 这个函数拥有一个`__qualname__`属性，可以支持内窥
>>> D.f.__qualname__
'D.f'

# 对实例进行点式记号法访问将会返回一个bound method对象
>>> d.f
<bound method D.f of <__main__.D object at 0x00B18C90>>

# 在内部，绑定的方法都存储在底层函数，绑定的实例，以及绑定方法的类
>>> d.f.__func__
<function D.f at 0x1012e5ae8>
>>> d.f.__self__
<__main__.D object at 0x1012e1f98>
>>> d.f.__class__
<class 'method'>
```

## Static Methods and Class Methods

非数据描述符提供了一种简单的机制，可以实现多种函数绑定方法的模式。

总结来说，函数有一个`__get__()`方法，所以在访问属性的时候都会被转换为方法。
非数据描述符会把`obj.f(*args)`调用转换为`f(obj, *args)`，调用`klass.f(*args)`将会
变为`f(*args)`.

下面的表格总结了绑定的两种常见变种：

变形 | 从对象中调用 | 从类中调用
-- | -- | --
function | f(obj, \*args) | f(\*args) 
staticmethod | f(\*args) | f(\*args)
classmethod | f(type(obj), \*args) | f(klass, \*args)

静态方法会直接返回底层的函数。调用`c.f`和`C.f`是等价的。

静态方法适用那些不需要self的方法。

例如，一个统计模块可能包含一个包含实验数据的容器类。这个类提供普通方法来计算average,
mean, median和其它的统计数据。但是这些方法其实是可以独立的，可以认为它们是纯函数。
所以可以使用静态方法定义。

由于静态方法直接返回底层的函数，下面这个例子就不新鲜了:

```python
>>> class E(object):
...     def f(x):
...         print(x)
...     f = staticmethod(f)
...
>>> print(E.f(3))
3
>>> print(E().f(3))
3
```

使用非数据描述符协议，一个纯python版本的staticmethod实现：

```python
class StaticMethod(object):
    
    def __init__(self, f):
        self.f = f

    def __get__(self, obj, objtype=None):
        return self.f
```

和静态方法不一样，类方法将会把class的引用作为第一个参数传入到函数中：

```python
>>> class E(object):
...     def f(klass, x):
...         return klass.__name__, x
...     f = classmethod(f)
...
>>> print(E.f(3))
('E', 3)
>>> print(E().f(3))
('E', 3)
```

可以拿Python内置对象的dict举例子，`dict.fromkeys()`根据一个keys lists创建一个新的字典，
纯Python语言的描述如下：

```python
class Dict(object):
    ...
    def fromkeys(klass, iterable, value=None):
        d = klass()
        for key in iterable:
            d[key] = value
        return d
    fromkeys = classmethod(fromkeys)
```

使用非数据描述符协议，一个纯Python版本的`classmethod()`看起来像下面这样:

```python
class ClassMethod(object):
    
    def __init__(self, f):
        self.f = f

    def __get__(self, obj, klass=None):
        if klass is None:
            klass = type(obj)
        def newfunc(*args):
            return self.f(klass, *args)
        return newfunc
```
