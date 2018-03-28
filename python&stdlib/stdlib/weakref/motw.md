# weakref -- Impermanent references to Objects

`weakref`模块支持针对对象的弱引用。

一般的引用会增加对象的引用计数，防止它被垃圾回收。

这个方式并不总是人们想要的，特别是循环引用的情况，可能会让一个对象永远不能从
内存中被删除。

弱引用就是针对这种情况发明的，它不会保存一份引用。

## References

针对对象的弱引用由`ref`类来管理。想要取回最初的对象，可以调用这个引用对象.

### weakref_ref.py

```python
# weakref_ref.py

import weakref


class ExpensiveObject:

    def __del__(self):
        print("(Deleting {})".format(self))


obj = ExpensiveObject()
r = weakref.ref(obj)


print('obj:', obj)
print('ref:', r)
print('r():', r())


print('deleting obj')
del obj
print('r(): ', r())
```

在这个例子中，因为obj在第二次调用ref的时候被删除了，所以`r()`会返回None.

```shell
$ python3 weakref_ref.py

obj: <__main__.ExpensiveObject object at 0x1007bla58>
ref: <weakref at 0x1007a92c8; to 'ExpensiveObject' at 0x1007bla58>
r(): <__main__.ExpensiveObject object at 0x1007bla58>
deleting obj
(Deleting <__main__.ExpensiveObject object at 0x1007bla58>)
r(): None
```

## Reference Callbacks

`ref`构造器还可以接受一个可选的callback函数，它会在引用对象被删除的时候被调用.

```python
# weakref_ref_callback.py

import weakref


class ExpensiveObject:

    def __del__(self):
        print("(Deleting {})".format(self))


def callback(reference):
    print('callback({!r})'.format(reference))


obj = ExpensiveObject()
r = weakref.ref(obj, callback)


print('obj:', obj)
print('ref:', r)
print('r():', r())

print('deleting obj')
del obj
print('r():', r())
```

callback会接受ref对象作为它的参数。这个特性的用处？比如说可以在对象被删除的时候
把弱引用对象从缓存中移除。

```python
$ python weak_ref_callback.py

obj: <__main__.ExpensiveObject object at 0x1010b1978>
ref: <weakref at 0x1010a92c8; to 'ExpensiveObject' at
0x1010b1978>
r(): <__main__.ExpensiveObject object at 0x1010b1978>
deleting obj
(Deleting <__main__.ExpensiveObject object at 0x1010b1978>)
callback(<weakref at 0x1010a92c8; dead>)
r(): None
```

## Finalizing Objects

想要在弱引用被清除的时候对资源进行强管理，可以使用`finalize`让对象关联一个callback。

`finalize`对象会保留，直到关联的对象被删除。

### weakref_finalize.py

```python
# weakref_finalize.py

import weakref


class ExpensiveObject:
    
    def __del__(self):
        print("(Deleting {})".format(self))


def on_finalize(*args):
    print("on_finalizing({!r})".format(args))


obj = ExpensiveObject()
weakref.finalize(obj, on_finalize, 'extra argument')

del obj
```

这个callble会在对象被垃圾回收的时候被调用，后面的位置参数都会传入到这个callble：

```python
$ python3 weakref_finalize.py

(Deleting <__main__.ExpensiveObject object at 0x1019b10f0>)
on_finalize(('extra argument',))
```

`finalize`有一个属性叫做`atexit`，用来控制callback是否在程序退出的时候被调用，
而不是真正的被调用。

### `weakref_finalize_atexit.pt

```python
# weakref_finailize_atexit.py

import sys
import weakref


class ExpensiveObject:

    def __del__(self):
        print('(Deleting {})'.format(self))

def on_finalize(*args):
    print("on_finalize({!r})".format(args))


obj = ExpensiveObject()
f = weakref.finalize(obj, on_finalize, "extra_argument")
f.atexit = bool(int(sys.argv[1]))
```

默认会在程序退出的时候调用它，但是将`atexit`设置为False以后就不会被调用了。

```shell
$ python3 weakref_finalize_atexit.py 1

$ python3 weakref_finalize_atexit.py 1

on_finalize(('extra argument',))
(Deleting <__main__.ExpensiveObject object at 0x1007b10f0>)

$ python3 weakref_finalize_atexit.py 0
```

如果将对象的引用传入到`finalizing`的回调(作为参数)，那么这个对象永远不会被
垃圾回收：

### `weakref_finalize_reference.py`

```python
weakref_finalize_reference.py
import gc
import weakref


class ExpensiveObject:

    def __del__(self):
        print('(Deleting {})'.format(self))


def on_finalize(*args):
    print('on_finalize({!r})'.format(args))


obj = ExpensiveObject()
obj_id = id(obj)

f = weakref.finalize(obj, on_finalize, obj)
f.atexit = False

del obj

for o in gc.get_objects():
    if id(o) == obj_id:
        print('found uncollected object in gc')
```

在上面的例子中，即使对象看上去被删除了，实际上并没有被删除。

```shell
$ python3 weakref_finalize_reference.py

found uncollected object in gc
```

### `weakref_finalize_reference_method.py`

将对象的绑定方法传入到`finalize`，也会导致对象不能被正常垃圾回收:

```python
# weakref_finalize_reference_method.py
import gc
import weakref


class ExpensiveObject:

    def __del__(self):
        print('(Deleting {})'.format(self))

    def do_finalize(self):
        print('do_finalize')


obj = ExpensiveObject()
obj_id = id(obj)

f = weakref.finalize(obj, obj.do_finalize)
f.atexit = False

del obj

for o in gc.get_objects():
    if id(o) == obj_id:
        print('found uncollected object in gc')
```

```shell
$ python3 weakref_finalize_reference_method.py

found uncollected object in gc
```

## Proxies

很多时候为了方便都要使用代理，而不是弱引用。

可以将代理看作是原来的对象，在访问它的时候不需要先调用弱引用对象。

但是后果就是，代理对象可以传入一些callble，而这些callble并不知道它是代理还是
真正的对象。

### weakref_proxy.py

```python
# wekref_proxy.py

import weakref


class ExpensiveObject:

    def __init__(self, name):
        self.name = name


    def __del__(self):
        print("(Deleting {})".format(self))


obj = ExpensiveObject("object")
r = weakref.ref(obj)
p = weakref.proxy(obj)


print("via obj:", obj.name)
print("via ref:", r().name)
print("via proxy:", p.name)
del obj
print('via proxy:', p.name)
```

如果在引用对象被删除以后再次访问proxy，将会抛出`ReferenceError`异常.

```shell
$ python3 weakref_proxy.py

via obj: My Object
via ref: My Object
via proxy: My Object
(Deleting <__main__.ExpensiveObject object at 0x1007aa7b8>)
Traceback (most recent call last):
  File "weakref_proxy.py", line 30, in <module>
    print('via proxy:', p.name)
ReferenceError: weakly-referenced object no longer exists
```

## Caching Objects

`ref`和`proxy`可以认为是低级别的API。

通常我们需要的是对一个单独对象进行弱引用，允许它进入垃圾回收的循环。

`WeakKeyDictionary`和`WeakValueDictionary`类提供了一个更合适的API，
可以为对象创建缓存。

`WeakValueDictionary`持有它拥有的value的弱引用，允许在其它代码不持有它们的
时候让它进入垃圾回收。

### `weakref_valuedict.py`

下面的例子显式地调用了垃圾回收器，阐释了常规字典和`WeakValueDictionary`之间
内存处理的差异:

```python
# weakref_valuedict.py

import gc
from pprint import pprint
import weakref


gc.set_debug(gc.DEBUG_UNCOLLECTABLE)


class ExpensiveObject:

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "ExpensiveObject({})".format(self.name)

    def __del__(self):
        print("    (Deleting {})".format(self))


def demo(cache_factory):
    # 持有对象，所以任何弱引用都不会被立即移除
    all_refs = {}
    # 使用工厂创建缓存
    print("CACHE TYPE: ", cache_factory)
    cache = cache_factory()
    for name in ['one', 'two', 'three']:
        o = ExpensiveObject(name)
        cache[name] = o
        all_refs[name] = o
        del o

    print("  all_refs =", end=" ")
    pprint(all_refs)
    print("\ Before, cache contains:", list(cache.keys()))
    for name, value in cache.items():
        print("    {} = {}".format(name, value))
        del value  # 解除引用

    # 移除一个对象的所用引用，除了缓存
    print("\n Cleanup:")
    del all_refs
    gc.collect()

    print("\n After, cache contains:", list(cache.keys()))
    for name, value in cache.items():
        print('    {} = {}'.format(name, value))
    print('  demo returning')
    return

demo(dict)
print()

demo(weakref.WeakValueDictionary)
```

下面是输出:

```shell
$ python3 weakref_valuedict.py

CACHE TYPE: <class 'dict'>
  all_refs = {'one': ExpensiveObject(one),
 'three': ExpensiveObject(three),
 'two': ExpensiveObject(two)}

  Before, cache contains: ['one', 'three', 'two']
    one = ExpensiveObject(one)
    three = ExpensiveObject(three)
    two = ExpensiveObject(two)

  Cleanup:

  After, cache contains: ['one', 'three', 'two']
    one = ExpensiveObject(one)
    three = ExpensiveObject(three)
    two = ExpensiveObject(two)
  demo returning
    (Deleting ExpensiveObject(one))
    (Deleting ExpensiveObject(three))
    (Deleting ExpensiveObject(two))

CACHE TYPE: <class 'weakref.WeakValueDictionary'>
  all_refs = {'one': ExpensiveObject(one),
 'three': ExpensiveObject(three),
 'two': ExpensiveObject(two)}

  Before, cache contains: ['one', 'three', 'two']
    one = ExpensiveObject(one)
    three = ExpensiveObject(three)
    two = ExpensiveObject(two)

  Cleanup:
    (Deleting ExpensiveObject(one))
    (Deleting ExpensiveObject(three))
    (Deleting ExpensiveObject(two))

  After, cache contains: []
  demo returning
```


