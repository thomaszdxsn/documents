# Overview

为了满足重新找回编写class乐趣的目标，这个package给你一个class装饰器，可以让你声明式
地定义class的属性。

```
>>> import attr

>>> @attr.s
... class SomeClass(object):
...     a_number = attr.ib(default=42)
...     list_of_numbers = attr.ib(default=attr.Factory(list))
...
...     def hard_math(self, another_number):
...         return self.a_number + sum(self.list_of_numbers) * another_number


>>> sc = SomeClass(1, [1, 2, 3])
>>> sc
SomeClass(a_number=1, list_of_numbers=[1, 2, 3])

>>> sc.hard_math(3)
19
>>> sc == SomeClass(1, [1, 2, 3])
True
>>> sc != SomeClass(2, [3, 2, 1])
True

>>> attr.asdict(sc)
{'a_numer': 1, 'list_of_numbers': [1, 2, 3]}

>>> SomeClass()
SomeClass(a_numer=42, list_of_numbers=[])

>>> C = attr.make_class('C', ['a', 'b'])
>>> C('foo', 'bar')
C(a='foo', b='bar')
```

在声明属性以后，`attrs`可以让你:

- 让class属性看起来更简洁
- 友好的`__repr__`
- 一套完整的比较方法
- 一个initialnizer
- 等等

## Philosophy

- **It's about regular classes**

    `attrs`用来创建一个行为端正的类，带有属性，方法和一个类型，以及类能拥有的一切
    东西。它可以用于数据容器，就像`namedtuple`或者`types.SimpleNamespace`意义。

- **The class belongs to the users.**

    你定义一个类，然后`attrs`会根据你申明的属性为类增加静态方法。

    它不会增加元类。不会为你的类加入额外的继承关系。`attrs`类在运行时和普通的类
    没有任何区别：因为它就是一个普通类，但是带有一些防止重复输入的方法。

- **Be light on API impact.**

    它第一眼看上去就很方便。因为attrs模块中有很多工具函数，可以在示例级别进行操作。
    因为它们接受attrs示例作为它们的第一个参数，你可以只使用一行代码就把它们attched.

- **Performance matters.**

    `attrs`运行时的消耗接近于零，因为它的所有开销都是类定义的时候完成。

- **No surprises.**

    `attrs`创建类的方式对于Python新手来说都是显而易见的。它不会猜测你想要什么，
    因为explicit is better than implicit。它不会试图假装聪明，因为软件本身就
    不够聪明。

## What attrs is Not

`attrs`不能发明某种魔术系统，比如将类从它的元类中拉出来，运行时的inspection，
或者移除循环依赖。

attrs能做的事情就是:

1. 接受你的声明
2. 根据这心信息编写dunder方法
3. 将这些方法加入到你的class中

它不会在runtime的时候作任何事情，所以它在runtime的时候是零开销。

## On the attr.s and attr.ib Names

`attr.s`装饰器和`attr.ib`函数并不是任何晦涩的缩略语。

它们是让你编写`attrs`和`attrib`的简练和可读兼具的一种方式。

因此，下面的定义和之前的一样:

```
>>> from attr import attrs, attrib, Factory
>>> @attrs
... class SomeClass(object):
...     a_number = attrib(default=42)
...     list_of_numbers = attrib(default=Factory(list))
...
...     def hard_math(self, another_number):
...         return self.a_number + sum(self.list_of_numbers) * another_number
>>> SomeClass(1, [1, 2, 3])
SomeClass(a_number=1, list_of_numbers=[1, 2, 3])
```

使用哪种方式都随便你.

