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
    >> metaclass hint`metaclass`将会被剩余的类型机构(type machinery)消费，它不会被传入到`__init_subclass__`.真实的metaclass(而不是显式hint的那个)可以通过`type(cls)`来访问.


### Metaclasses

