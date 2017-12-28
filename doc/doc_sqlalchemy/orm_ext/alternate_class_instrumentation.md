## Alternate Class Instrumentation

扩展类的指令。

`sqlalchemy.ext.instrumentation`包提供了ORM类指令(instrumentation)的一种替代方法。类指令是指ORM如何将属性放置入类并且追踪／维护数据的改动，以及在类中安装事件钩子。

### API

- `sqlalchemy.ext.instrumentation.INSTUMENTATION_MANAGER = '__sa_instrumentation_manager__'`

    属性，代表选择的自定义的instrumentation.
    
    允许类定义一个轻微改动，或者完全不同的技术来追踪映射属性和映射集合的改动。

    在一个继承结构中只可以指定一个instrumentation.

    这个属性的值必须是一个可调用对象，并会传入一个类对象。这个可以调用对象必须返回下面中的一个:

    - 一个`InstrumentationManager`／它的子类的实例
    - 一个`ClassManager`/它的子类的实例

- class`sqlalchemy.orm.instrumentation.InstrumentationFactory`

    新`ClassManager`实例的工厂

- class`sqlalchemy.ext.instrumentation.InstrumentationManager(class_)`

    用户定义类instrumentation扩展.

    这个类的接口还不是稳定版，可能在之后的SA发布版中有变动.

- `sqlalchemy.ext.instrumentation.instrumentation_finders = [<function find_native_user_instrumentation_hook>]`

- class`sqlalchemy.ext.instrumentation.ExtendedInstrumentationRegistry`

    ...