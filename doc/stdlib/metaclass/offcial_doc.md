[TOC]

本文链接: [https://docs.python.org/3/reference/datamodel.html#customizing-class-creation](https://docs.python.org/3/reference/datamodel.html#customizing-class-creation)

## Customizing class creation(自定义类的创建)

无论何时，在一个类调用另一个类的时候，这个类将会调用`__init_subclass__`。那么就可以编写一个类，来改变继承的行为。这种方式很像类装饰器(`class decorators`)，但是类装饰器只会应用到它指定的那些类，`__init__subclass__`可以应用于定义了这个类方法的所有未来子类上面。

- **classmethod**`object.__init_subclass__(cls)`

    无论何时，只要包含的类`cls`是一个子类时，这个方法就会被调用。`cls`是新定义的子类。如果将这个方法定义为普通的方法，这个方法也会内部转换为`classmethod`.

    传入新类的关键字参数也会传入到父类的`__init_subclass__`。为了和其它使用`__init_subclass__`的类相兼容，它可以拿走自己需要的关键字参数，并把其它(关键字参数)传给基类，比如:

    ```python
    class Philosopher:
        def __init_subclass__(cls, default_name, **kwargs):
            super().__init_subclass__(**kwargs)
            cls.default_name = default_name


    class AustralianPhilosopher(Philosopher, default_name='Bruce'):
        pass
    ```

    默认的`object.__init_subclass__`什么都没做，但是如果传入了任何参数，就会抛出一个错误。

    > 注意
    >
    >> metaclass hint`metaclass`将会被剩余的类型机制(type machinery)消费，它不会被传入到`__init_subclass__`.真实的metaclass(而不是显式hint的那个)可以通过`type(cls)`来访问.


### Metaclasses

默认情况下，class通过`type()`构建。这个class的body将会在一个新的命名空间(namespace)内执行，class name通过`type(name, base, namespace)`来局部绑定(bound locally)。

**类创建过程(class creation process)**可以通过在类定义时传入`metaclass`关键字参数来自定义，或者可以继承一个包含metaclass参数的类。在下面的例子中，`MyClass`和`MySubclass`都是`Meta`的实例：

```python
class Meta(type):
    pass


class MyClass(metaclass=Meta):
    pass


class MySubClass(MyClass):
    pass
```

任何在类定义时传入的其它关键字参数，都会传入下面描述的所有的metaclass操作。

当一个类定义被执行后，会执行以下步骤：

- 确定适当的metaclass
- 准备类的命名空间(namespace)
- 执行类的body
- 创建类对象

### Determing the appropriate metaclass(确定适当的元类)

一个类定义适当的metaclass通过如下步骤来确定：

- 如果没有基类，没有显式指定metaclass，那么就使用`type()`
- 如果显式给定一个metaclass，而且它还不是`type()`的实例，那么就直接使用它来作为metaclass
- 如果给定一个`type()`的实例作为metaclass，或者基类是一个`type()`实例，那么就使用尾部基类(most derived)作为metaclass

### Preparing the class namespace(准备类的命名空间)

一旦确认了合适的元类，接下来就是准备命名空间。如果metaclass有一个`__prepare__`属性(方法也是属性)，就会这样调用`namespace = metaclass.__prepare__(name, bases, **kwds)`(额外的关键字参数，如果存在，就是来自于类定义时传入的那些关键字参数)

如果metaclass没有`__prepare__`属性，那么类的命名空间将会以一个排序映射(OrderedDict?)的形式初始化.

> 参考
>
>> [PEP3115 -- Metaclasses in Python 3000](https://www.python.org/dev/peps/pep-3115)
>> 
>> 引入了`__prepare__`这个命名空间钩子.

### Executing the class body(执行类body)

这个类的body大约是以这样的方式被执行的：`exec(body, globals(), namespace)`.和平常调用`exec()`的一个关键不同之处在于，在类定义出现在一个函数中的时候，词法域允许类body(包含任何方法)可以引用当前和外部的域(scope)的名称(names).

不过，即使类定义出现在函数中，类中的方法仍然类域中的名称(names).类变量必须通过实例或者类方法的第一个参数，或者通过隐式的词法域`__class__`来引用。

### Creating the class object(创建类对象)

一旦通过执行类body构成了类的命名空间，这个类对象将会通过调用`metaclass(name, bases, namespace, **kwds)`(在这里额外的关键字参数都是传入到`__prepare__`的关键字参数)来创建.

这个类对象也是通过**零参数形式的`super()`**引用的对象之一.如果类body中的任何方法引用了`__class__`或者`super`时，编译器将会创建一个隐式的闭包(closure)引用，即`__class__`.这种机制可以允许**零参数形式的`super()`**可以根据词法域识别出正确的被定义类，类或实例用此来识别出传入方法的第一个参数(`self`).

**CPython implementation detail(CPython实现细节)**：在CPython3.6及以后，`__class__`cell将会以类命名空间中的`__classcell__`entry形式传入到metaclass.如果出现(present)，为了类的正确初始化，它将会传播到`type.__new__`的调用中。在Python3.6以后，如果这个过程失败，将会导致一个`DeprecationWarning`，并且可能在未来导致一个`RuntimeWarning`.

当使用默认的metaclass`type`时，或者任何最终调用`type.__new__`的元类时，在创建了类对象之后，下面的一些额外定制化步骤都将会被调用：

- 首先，`type.__new__`收集类命名空间中所有定义了`__set_name__()`方法的描述符.
- 然后，所有的`__set_name__`方法都会被通过指定描述符赋予的名称调用.
- 最后，通过MRO(method resolution order)调用新类的最接近的父类(immediate parent)的钩子:`__init_subclass__()`.

在类对象被创建后，它将会传入到类定义中存在的类描述符，返回的结果将会绑定局部的命名空间。

当一个新类通过`type.__new__`被创建后，对象提供的namespace参数会被拷贝到一个新的有序映射(ordered mapping)，之后原始的对象会被丢弃。这个新的拷贝将会封装到一个**只读**的proxy，它会变为类对象的`__dict__`属性。

> 参考
>
>> [PEP3135 -- New super]
>>
>> 描述隐式的`__class__`闭包引用.

### Metaclass example(元类例子)

元类的潜在使用场景是数不清的。一些使用的想法包括enum, logging，接口检查，自动化分发(automatic delegation)，自动化的property创建，proxies，框架以及自动化的资源锁/同步化(resouce locking/synchronization).

下面是一个metaclass的例子，它使用`collections.OrderedDict`来记住类变量定义的顺序：

```python
class OrderedClass(type):

    @classmethod
    def __prepare__(metacls, name, bases, **kwds):
        # 这个返回将会等于__new__.namespace参数
        return collections.OrderedDict()

    def __new__(cls, name, bases, namespace, **kwds):
        result = type.__new__(cls, name, base, dict(namespace))
        result.members = tuple(namespace)
        return result

        
class A(metaclass=OrderedClass):
    def one(self): pass
    def two(self): pass
    def three(self): pass
    def four(self): pass


>>> A.members
('__module__', 'one', 'two', 'three', 'four')
```

当类定义`A`被执行后，进程将会从调用元类的`__prepare__()`方法开始，这个方法返回一个空的`collections.OrderedDict`.这个映射对象记录了A的属性，这些属性通过类body中的语句定义。一旦这些定义被执行后，这个有序字典完全组构完成，然后元类的`__new__()`方法被调用。这个方法定义了一个新的type，它将有序字典的键保存到了一个属性(`.members`)中。
