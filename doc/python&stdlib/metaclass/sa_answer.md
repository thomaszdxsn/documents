## StackOverflow's Answer

### Votes 5000+ 

**回答链接**: [https://stackoverflow.com/questions/100003/what-is-a-metaclass-in-python#answer-6581949](https://stackoverflow.com/questions/100003/what-is-a-metaclass-in-python#answer-6581949)

### Classes as objects(类即对象)

在理解metaclass之前，你需要熟悉Python中的class。Python对什么是类有一个独特的想法，借鉴自Smalltalk.

在大多数语言中，类只是一个用来生成对象的一段代码。Python的类中大部分时候也是这样:

```python
class ObjectCreator(object):
...     pass
...

>>> my_object = ObjectCreator()
>>> print(my_object)
<__main__.ObjectCreator object at 0x8974f2c>
```

但是Python中的类还能做的更多。类也是对象!

是的，对象。

一旦你使用了关键字`class`.Python解释器会找到并执行和这个类，最后创建了这个**类对象**(连起来读)。指令如下：

```python
>>> class ObjectCreator(object):
...     pass
...
```

在内存中创建了一个对象，名字叫做`ObjectCreator`.

**这个对象(类本身)是一个能够创建对象(类实例)的对象，也就是它之所以能够叫做类(class)的原因。**

但是它仍然还是一个对象，因此:

- 你可以将它赋值给一个变量
- 你可以copy它
- 你可以为它添加属性
- 你可以将它当做参数传递给可调用对象

例如：

```python
>>> print(ObjectCreator)        # 因为类是一个对象，所以你可以打印它
<class '__main__.ObjectCreator'>
>>> def echo(o):
...     print(o)
...
>>> echo(ObjectCreator)         # 你可以将一个类当做参数来传递
<class '__main__.ObjectCreator'>
>>> print(hasattr(ObjectCreator, 'new_attribute'))  
False
>>> ObjectCreator.new_attribute = 'foo' # 你可以为一个类添加属性
>>> print(ObjectCreator.new_attribute)
foo
>>> ObjectCreatorMirror = ObjectCreator # 你可以讲一个类赋值给一个变量
>>> print(ObjectCreatorMirror.new_attribute)
foo
>>> print(ObjectCreatorMirror())
<__main__.ObjectCreator object at 0x8997b4c>
```

### Creating classes dynamically

由于类即对象，你可以在运行时(on the fly)创建它们，就像创建对象一样。

首先，你可以在一个函数中使用`class`创建一个类:

```python
>>> def choose_class(name):
...     if name == 'foo':
...         class Foo(object):
...             pass
...         return Foo
...     else:
...         class Bar(object):
...             pass
...         return Bar
...
>>> MyClass = choose_class('foo')
>>> print(MyClass)      # 这个函数返回一个类，而不是一个实例
<class '__main__.Foo'>
>>> print(MyClass())    # 你可以通过这个类来创建一个实例
<__main__.Foo object at 0x89c6d4c>
```

但是这还不算真正的动态(dynamically)创建，因为你还是需要手写整个类。

由于类即对象，所以它们必须通过一些东西来生成.

当你使用`class`关键字时，Python会自动创建这个对象。但是就像Python中的很多东西一样，它允许你手动干涉这个类对象的创建过程。

记得函数`type`吗？这个古老的函数能够告诉你对象的类型是什么：

```python
>>> print(type(1))
<type 'int'>
>>> print(type('1'))
<type 'str'>
>>> print(type(ObjectCreator))
<type 'type'>
>>> print(type(ObjectCreator()))
<class '__main__.ObjectCreator'>
```

不过`type`还有一种完全不同的能力,它可以在运行时(on the fly)创建一个类.`type`可接受若干对类的描述参数,然后返回一个类。

(一样的函数因为不同的参数而完全不一样，看起来有点蠢。但是这是由于Python为了保证向后兼容性不得已为之)

`type`可以这样调用：

```python
type(类名:str,
     父类:tuple(用于继承，可以为空),
     属性:dict(对应属性的名称和值))
```

例如:

```python
>>> MyShinyClass = type('MyShinyClass', (), {})     # 返回一个类对象
>>> print(MyShinyClass)
<class __main__.MyShinyClass>
>>> print(MyShinyClass())                           # 创建一个类实例
<__main__.MyShinyClass object at 0x8997cec>
```

你注意到我们使用的类名*MyShinyClass*和绑定类引用的名字一样.两者可以取不同名字，但是没有必要把事情搞复杂。

`type`接受的第三个参数是一个字典,用于定义类的属性，所以:

```python
>>> class Foo(object):
...     bar = True
```

可以这样来创建：

```python
>>> Foo = type('Foo', (), {'bar': True})
```

可以当做普通类使用:

```python
>>> print(Foo)
<class '__main__.Foo'>
>>> print(Foo.bar)
True
>>> f = Foo()
>>> print(f)
<__main__.Foo object at 0x8a9b84c>
>>> print(f.bar)
True
```

当然，你也可以继承它.比如：

```python
>>> class FooChild(Foo):
...     pass
```

可以由`type()`这样来创建:

```python
>>> FooChild = type('FooChild', (Foo,), {})
>>> print(FooChild)
<class '__main__.FooChild'>
>>> print(FooChild.bar)
True
```

最后，如果你想为`type()`创建的类添加方法.只需要定义一个具有合适签名的函数,然后把当做属性赋值即可:

```python
>>> def echo_bar(self):
...     print(self.bar)
...
>>> FooChild = type('FooChild', (Foo,), {'echo_bar': echo_bar})
>>> hasattr(Foo, 'echo_bar')
False
>>> hasattr(FooChild, 'echo_bar')
True
>>> my_foo = FooChild()
>>> my_foo.echo_bar()
True
```

并且你可以通过**monkey patch**来动态创建方法:

```python
>>> def echo_bar_more(self):
...     print('yet another method')
...
>>> FooChild.echo_bar_more = echo_bar_more
>>> hasattr(FooChild, 'echo_bar_more')
True
```

相比到此你应该明白了：在Python中，类即对象，你可以动态(on the fly)地创建一个类.

这些事情(类对象的创建)就是在你使用关键字`class`以后Python做的事情，使用元类后一样。

### What are metaclasses(finally)

Metaclass是创建类的东西("stuff").

你定义类是为了创建对象，不是吗？

但是我们刚才明白了Python的类也是对象。

Metaclass就是用来创建这些对象的(类).它们是类的类，你可以把它们想象成这样:

```python
MyClass = MetaClass()
MyObject = MyClass()
```

你已经知道了`type()`可以这么做:

```python
MyClass = type("MyClass", (), {})
```

这是因为，`type`事实上也是一个元类.`type`是Python用来在幕后创建所有类的一个元类。

现在你会奇怪为什么它是小写形式，而不是`Type`?

我猜是为了保持和`str`的一致性,`str`类创建字符串对象,`int`类创建整数对象,`type`这个类当然是用来创建类对象。

你可以通过`__class__`属性来检查.

一切，我是说一切，Python中一切皆对象.包括int, string, function, class.它们都是对象.它们都是通过一个类来创建的:

```python
>>> age = 35
>>> age.__class__
<type 'int'>
>>> name = 'bob'
>>> name.__class__
<type 'str'>
>>> def foo(): pass
>>> foo.__class__
<type 'function'>
>>> class Bar(object): pass
>>> b = Bar()
>>> b.__class__
<class '__main__.Bar'>
```

那么，每个`__class__`的`__class__`是什么呢?

```python
>>> age.__class__.__class__
<type 'type'>
>>> name.__class__.__class__
<type 'type'>
>>> foo.__class__.__class__
<type 'type'>
>>> b.__class__.__class__
<type 'type'>
```

所以，metaclass是用来创建类的东西.

如果你愿意，你可以把它叫做**类工厂(class factory)**.

`type`是Python中的内置元类，你当然也可以创建你自己的元类。

### The __metaclass__ attribute

当你写一个类的时候可以加入一个`__metaclass__`属性(在Py3中是直接传入类定义那一行，以关键字`metaclass`的形式).

```python
class Foo(object):
    __metaclass__ = something...
    [...]
```

如果你这样做了，Python将会使用这个元类来创建类`Foo`。

小心，这里很容易出问题。

你编写了`class Foo(object)`，但是这个时候类对象`Foo`还没有在内存中被创建。

Python将会在类定义中查找`__metaclass__`.如果找到了，它会使用这个元类来创建类`Foo`.如果没找到，仍然会使用`type`来创建类。

请反复阅读上面这句话。

当你这样做的时候：

```python
class Foo(Bar):
    pass
```

Python做了下面这些事:

- `Foo`里面有`__metaclass__`属性吗？
- 如果有，在使用`__metaclass__`这个属性在内存中创建一个类对象，将它和`Foo`这个名称绑定.
- 如果没有找到`__metaclass__`，它会查找模块级别(模块级全局变量)的`__metaclass__`，然后用它来创建类对象(但是只针对没有继承任何类的旧式类。在Python中默认是新式类也就是说这个规则没有用了？)
- 最后如果你仍然没有找到`__metaclass__`，将会使用`Bar`(第一个父类)拥有的元类(可能是默认的`type`)来创建类对象.
- 注意`__metaclass__`属性不会被继承，只会继承父类的元类(在这个例子中是`Bar.__class__`).如果Bar使用的`__metaclass__`属性通过`type`(而不是`type.__new__()`)创建的`Bar`，那么自类不会继承这个行为。

现在最大的问题来了，你可以在`__metaclass__`中放什么东东？

答案是：可以创建一个类的东西。

什么可以创建类呢？`type`，或者任何继承使用`type`的东西.

### Custom metaclasses

只用元类的**最大作用就是，可以在类创建的时候自动修改它**。

你一般可以在需要创建一个符合当前上下文的API时使用元类。

想象一个很傻的例子，如果你决定让一个模块中所有定义的类的属性都以大写形式表示。有很多方法可以做到，其中的一种就是在模块级(全局变量)设置一个`__metaclass`.

通过这个方法，模块中所有类的创建都要使用这个元类，我们只要告诉元类将所有属性名改为大写。

`__metaclass__`可以是任何可调用对象，没有要求必须是一个常规类。(虽然metaclass中有一个class，但是并不意味着它就是类呀！)

所以我们通过一个函数的例子开始:

```python
# 这个元类可以自动接收你传入到type()-构造器用法中的参数
def upper_attr(future_class_name, future_class_parents, future_class_attr):
    """返回一个类对象，它的属性名称将会改为大写"""

    # 挑选出所有不以"__"开头的属性名，并将它改为大写
    uppercase_attr = {}
    for name, value in future_class_attr.items():
        if not name.startswith("__"):
            uppercase_attr[name.upper()] = value
        else:
            uppercase_attr[name] = value
    
    # 让type来创建一个类
    return type(future_class_name, future_class_parents, uppercase_attr)


__metaclass__ = upper_attr      # 这个变量将会影响到整个模块的类


# 注意这全是Python2的用法
class Foo():    # 全局的__metaclass__不会影响到新式类，即继承了"object"的类
    # 如果是新式类，我们可以讲__metaclass__定义在这个地方
    bar = 'bip'
    
print(hasattr(Foo, 'bar'))
# out: False
print(hasattr(Foo, 'BAR'))
# out: True

f = Foo()
print(f.BAR)
# out: 'bip'
```

然后，我们通过一个属于class的元类，来做相同的事情：

```python
# 记住type像str和int一样，也是一个类。所以你可以继承它
class UpperAttrMetaClass(type):
    # __new__ 是 __init__ 之前调用的一个方法
    # 它是一个创建对象并返回的方法
    # __init__只是为对象把传入的参数初始化
    # 你一般很少需要使用__new__，除非你想要控制对象的创建过程
    # 这里我们想要创建的对象是类，我们要自定义这个创建过程，所以我们需要重写__new__
    # 如果你想的话，你也可以继续在__init__中做些事情
    # 一些高级用法涉及到覆盖__call__方法，但是我们现在还没必要明白这些
    def __new__(upperattr_metaclass, future_class_name, 
                future_class_parents, future_class_attr):
        uppercase_attr = {}
        for name, val in future_class_attr.items():
            if not name.startswith("__"):
                uppercase_attr[name.upper()] = val
            else:
                uppsercase_attr[name] = val

        return type.(upperattr_class, future_class_name,
                        future_class_parents, uppercase_attr)
```

但是这不够OOP。我们直接调用了`type`，我们并没有覆盖或调用父类的`__new__`:

```python

```class UpperAttrMetaclass(type): 

    def __new__(upperattr_metaclass, future_class_name, 
                future_class_parents, future_class_attr):

        uppercase_attr = {}
        for name, val in future_class_attr.items():
            if not name.startswith('__'):
                uppercase_attr[name.upper()] = val
            else:
                uppercase_attr[name] = val

        # 重用了type.__new__()方法
        # 这就是基础的OOP思想，没什么特殊的
        return type.__new__(upperattr_metaclass, future_class_name, 
                            future_class_parents, uppercase_attr)
        # 或者可以这样写
        # return super().__new__(upperattr_metaclass, future_class_name, 
        #                 future_class_parents, uppercase_attr)
```

你可能主要到了，有一个额外的参数`upperattr_metaclass`。它本身没什么特殊的：`__new__`总是在第一个参数接受定义类的本身。就像一般方法的`self`，或者类方法的`cls`一样。
(`__new__`其实是个`classmethod`，即使你定义时没有显式使用`@classmethod`来声明，它仍然会在内部将自己转换为一个`classmethod`)。

当然，我在这里使用的命名主要是由于想要清晰地阐述，第一个参数可以随意取名，但是就像`self`一样，很多参数都有一个惯例。所以一个正在的产品级元类应该像这样：

```python
class UpperAttrMetaclass(type): 

    def __new__(cls, clsname, bases, dct):

        uppercase_attr = {}
        for name, val in dct.items():
            if not name.startswith('__'):
                uppercase_attr[name.upper()] = val
            else:
                uppercase_attr[name] = val

        return type.__new__(cls, clsname, bases, uppercase_attr)
```

我们可以使用`super()`让它开起来更加清晰，`super()`函数可以更加简单地实现继承：

```python
class UpperAttrMetaclass(type): 

    def __new__(cls, clsname, bases, dct):

        uppercase_attr = {}
        for name, val in dct.items():
            if not name.startswith('__'):
                uppercase_attr[name.upper()] = val
            else:
                uppercase_attr[name] = val
        
        return super(UpperAttrMetaclass, cls).__new__(cls, clsname, bases, dct)
```

OK，关于元类没有更多的东西了。

使用元类的代码看起来很复杂一般不是因为元类，是因为你使用元类来完成*根据观察改变对象*， *操纵继承*， *操纵变量，比如__dict__*,等等一些复杂的事情。

事实上，元类特别适合用来做黑魔法(black magic)，因此也往往充满了复杂性。但是就元类本身而言，它很简单：

- 拦截了类的创建
- 修改类
- 返回修改后的类

### Why would you use metaclasses classes instead of functions?(为什么要用元类class代替元类function？)

由于`__metaclass__`可以接受任何可调用对象，为什么要用一个看起来更加复杂的class当作元类呢？

因为有以下若干原因：

- 让目的清晰。当你阅读`UpperAttrMetaclass(type)`的时候，你就大概明白它是什么了。
- 你可以使用OOP。元类可以继承元类，覆盖父类的方法。元类甚至可以使用元类。
- 如果你指定一个元类class，它的子类都将是元类的实例，但是使用元类function的时候就不行。
- 你可以把你的代码结构更加优化。你不可能只用元类做类似例子中的这点小事情。通常会使用它来做更加复杂的事情。能够在一个类中定义一组方法先让会让代码更加易读。
- 你可以使用`__new__`, `__init__`和`__call__`这些钩子。它们可以让你做一些额外的事情。虽然大多数时候单独的使用`__new__`就够了，但总有一些家伙偏爱使用`__init__`.
- 它原名就叫做元类(metaclass).总得让这个名字有点意义吧？

### Why would you use metaclasses?

现在问题来了，为什么你要使用这个容易导致bug的特性？

好吧，大多数时候你不需要使用它：

> 元类是一个高深的技巧，99%的用户并不需要明白它。如果你好奇自己需不需要使用元类，那么你就不需要(真正需要它的人明白需要它的地方，不需要解释为什么)
>
> -- Python专家Tim Peters

使用元类的主要场景就是创建一个API。一个典型的例子就是Django ORM。

它让你可以这样写代码：

```python
class Person(models.Model):
    name = models.CharField(max_length=30)
    age = models.IntegerField()
```

但是如果你这样写：

```python
guy = Person(name='bob', age='35')
print(guy.age)
```

它并不会返回一个`IntegerField`对象给你。它会返回一个`int`，甚至可以将它从数据库中取回。

这种代码可行是因为`models.Model`定义了`__metaclass__`，它会使用一些技巧让你定义的`Person`中的简单语句(`age = models.IntegerField()`)转换为一个数据库字典的复杂钩子(complex hook).

Django通过元类让一个复杂的东西看起来很简单，并将它暴露成一个简单的API，在幕后会对这个API做的一些重建代码才重要。

### The last word

首先，你知道类即对象，类可以用来创建实例。

好吧，类也是实例，元类的实例：

```python
>>> class Foo(object): pass
>>> id(Foo)
142630324
```

在Python中一切皆对象，它们都是类的实例或者元类的实例。

除了`type`!

`type`事实上是它自己的元类。在纯Python中你不可能再造出这么一个东西，它是在语言实现层创建的。

其次，元类是复杂的。在一些简单的类修改上面不应该使用它们。你可以使用两个稍简单的技术来修改类：

- monkey patch
- class decorator

在需要修改类的99%的情况下，你只需要上面两种方式就能修改。

但是在98%的情况下，你并不需要修改类。

