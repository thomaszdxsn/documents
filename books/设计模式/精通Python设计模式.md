[TOC]

书名: mastering python design pattern
出版社: packt
作者: Sakis Kasampalis
作者简介: 作者是一名荷兰的工程师，自称是一名实用主义编程语言/工具的忠实信徒．他的格言"是正确的工具应该用在正确的地方"．他最爱的语言是Python因为它发现这个语言的生产能力很强.
书籍简介: 本书共16个章节，分别对应16个设计模式．在书里大量使用论文式reference，可以看出作者是一个有着丰富经验，大量阅读的工程师．每一章节中，作者都会从上到下，从模式的定义到具体实例／使用场景来讲解，章节的末尾再次进行归纳．通俗易懂，阅读体验极佳．推荐配合万星github仓库[python-patterns](https://github.com/faif/python-patterns)一起食用，风味更佳． 

## 章节及内容

### 1.工厂模式(factory)
*通过把"创建对象"的代码和"使用对象"的代码解耦，来减少应用维护的复杂度*

这个章节主要介绍了一种模式的两个变种:`factory method`和`abstract factory`．
    
`factory method`是实现一个函数，负责根据参数来创建一种类型的对象(或者一种形式,一个接入点...等等)．
    
`abstract facotry`是指实现一个拥有若干`factory method`的一个类．它可以用来(根据需求)创建一大堆相关对象．

应用实例:
- `django`使用`factory method`模式来创建表单的字段.
- `django_factory`实现了`abstract factory`模式，用来为测试创建model.
    
工厂模式的作用:
1. 追踪对象的创建
2. 将对象的创建从类中解耦出来
3. 可以提升应用中的性能和资源的使用.

参考:
- github
    - [https://github.com/faif/python-patterns/blob/master/creational/factory_method.py](https://github.com/faif/python-patterns/blob/master/creational/factory_method.py) 
    - [https://github.com/faif/python-patterns/blob/master/creational/abstract_factory.py](https://github.com/faif/python-patterns/blob/master/creational/abstract_factory.py)
- `factory method`
    - [http://ginstrom.com/scribbles/2007/10/08/design-patterns-python-style/](http://ginstrom.com/scribbles/2007/10/08/design-patterns-python-style/)
    - [https://fkromer.github.io/python-pattern-references/design/#factory-method](https://fkromer.github.io/python-pattern-references/design/#factory-method)
    - [https://sourcemaking.com/design_patterns/factory_method](https://sourcemaking.com/design_patterns/factory_method) 
- `abstract factory`
    - [https://sourcemaking.com/design_patterns/abstract_factory](https://sourcemaking.com/design_patterns/abstract_factory)
    - [http://ginstrom.com/scribbles/2007/10/08/design-patterns-python-style/](http://ginstrom.com/scribbles/2007/10/08/design-patterns-python-style/) 
 
### 2.建造者模式(builder)

*通过将构造(construction)和表达形式(representation)分离，同样的一个构造可以创建若干不同的表达形式*

这个章节主要介绍了bulder模式，以及它和factory模式的比较，前者适合一些复杂，需要多步骤构建的对象的构建．另外本章节的实例介绍了一个有意思的第三方库`django-widgy`：通过django实现的CMS系统，它有一个很有吸引力的特性即**Page Builder**，可以在浏览器通过编辑器修改，设计页面的样式．


在这个模式中，一般有两个主要的成员，即`builder`和`director`．builder负责创建一个复杂对象的不同部分．director通过使用builder实例来控制创建过程．

可能这个模式和factory很难区分，只要记住builder模式和factory模式的不同之处，首先factory模式只需通过一步完成对象的创建，而builder模式需要多个步骤而且总是需要通过使用director来完成(但有时可以不用director, 参见java的`StringBuilder`).

再就是factory模式立即返回创建的对象，builder模式只有client在需要时请求director才会返回最终的对象.

在以下的情况更加推荐使用builder模式而不是factory模式:
- 我们想要创建一个复杂的对象(一个对象混合了不同的部分，需要根据制定顺序的步骤(对象的步骤可能是不同的)来创建).
- 需要为一个对象提供不同的表现形式，以及需要把一个对象的构建和它的表达形式解耦.
- 我们想要在某个时候创建一个对象，再稍后访问它.

一个有趣的地方是，可以将builder模式稍微变化，让它可以链式操作(Effective Java (2nd edition)).即在builder中实现`build()`方法，它会返回最终的对象，这种模式叫做`fluent builder`.

应用实例:

- `django-widgy`库实现了builder模式，通过它来创建生成HTML．django-widgy的编辑器包含一个页面builder，可以创建不同样式的HTML页面.
- `django-query-builder`库依靠builder模式来动态生成SQL查询.    

参考：
- [https://github.com/faif/python-patterns/blob/master/creational/builder.py](https://github.com/faif/python-patterns/blob/master/creational/builder.py)
- [https://sourcemaking.com/design_patterns/builder](https://sourcemaking.com/design_patterns/builder) 

### 3.原型模式(prototype)

*原型模式帮助我们创建一个对象的拷贝*

原型模式在Python中的最常见的表现即`copy`标准库．

原型模式的另一个用处是避免了**telescopic constructor problem**.

应用实例:

- Python应用一般不会提及自己使用了原型模式，因为这是一个内置标准库.
- `Visualization Toolkit (VTK)`使用原型模式来负责克隆地理元素．
- `Music 21`使用原型模式来拷贝音乐评注和评分.

python文档中关于**浅拷贝**和**深拷贝**的区分:

- `shallow copy`构建了一个新的混合(compound)对象，然后把将原始对象的引用(reference)插入其中.
- `deep copy`构建了一个新的混合(compound)对象，然后递归地将原始对象的拷贝(copy)插入其中.

### 4.适配器模式(adapter)

*一个结构化设计模式，聚焦于提供一个简单的方式来为一个复杂对象增加功能*

`Adapter`是一个结构化设计模式，用来帮助我们让两个原本不兼容的接口兼容．

常用于数据转换，但是也可以函数/可调用对象的接口转换.

我们一般使用继承来实现Adapter模式，但是通过一个中间的`Adapter`来实现也未尝不可(语义更清晰).

应用实例:

- `Grok`(一个基于Zope3的web框架, 聚焦于敏捷开发)．这个框架使用了Adapter模式，可以使用Zope3的接口而不需要修改它.
- `Traits`(用来为一个类增加类型定义)第三方库同样使用了Adapter模式来将一个对象变形而不需要实现制定的接口.
- `Tornado`实现了若干Adapter，可以让tornado和asyncio及twisted相互交换使用底层事件循环.

参考：
 - [http://ginstrom.com/scribbles/2008/11/06/generic-adapter-class-in-python/](http://ginstrom.com/scribbles/2008/11/06/generic-adapter-class-in-python/)
 - [https://sourcemaking.com/design_patterns/adapter](https://sourcemaking.com/design_patterns/adapter)
 - [http://python-3-patterns-idioms-test.readthedocs.io/en/latest/ChangeInterface.html#adapter](http://python-3-patterns-idioms-test.readthedocs.io/en/latest/ChangeInterface.html#adapter) 

### 5.装饰器模式(decorator)

*相比继承，应该优先选择使用混合(composite)，因为继承让代码很难复用，它是静态的，作用于整个类所有的实例*
*装饰器模式可以为一个对象动态地增加职责(responsibilities)，并且是通过一个透明的方式实现*

Python的装饰器和装饰器模式并不是一对一的关系．Python的装饰器比装饰器模式能做的更多(其中之一就是实现装饰器模式).

装饰器模式的一般用途就是为一个对象扩展功能

应用实例:

- `Django`的`View`装饰器, 用来控制访问权限和缓存.
- `Gork`使用装饰器实现Adapter模式,注册函数作为事件订阅者...等等

参考：

- [https://sourcemaking.com/design_patterns/decorator](https://sourcemaking.com/design_patterns/decorator) 

### 6.外观模式(facade)

*外观设计模式帮助我们隐藏系统的内部复杂性，只暴露应该让客户端简单使用的接口.*

本质上，外观模式是一个复杂系统的抽象层．多数使用外观模式的理由是：想为一个复杂系统提供了一个单独的，简单的入口．

不暴露系统内部的功能还有一个好处，即我们可以随意改动系统，只要传入参数,返回结果不变，就不影响客户端的调用.

如果你的系统包含很多层，也可以使用外观模式．为你的每一层都增加一个外观模式入口点，让层与层之间通过facade来通信．这种方式将会帮助你实现代码解耦，让每个层尽可能独立．

应用实例:

- `django-oscar-datacash`: 这个模块是Django的一个第三方库，它整合了`DataCash`支付接口.
- `Caliendo`: 模仿Python API的接口.

参考:

- [https://sourcemaking.com/design_patterns/facade](https://sourcemaking.com/design_patterns/facade)
- [https://fkromer.github.io/python-pattern-references/design/#facade](https://fkromer.github.io/python-pattern-references/design/#facade)
- [http://python-3-patterns-idioms-test.readthedocs.io/en/latest/ChangeInterface.html#facade](http://python-3-patterns-idioms-test.readthedocs.io/en/latest/ChangeInterface.html#facade)

### 7.轻量级模式(flyweight)

*轻量级(flyweight)设计模式是一个用来最小化内存用量的数据，通过在类似对象间分享数据来提升性能.*

flyweight是一个分享的对象，应该包含独立状态(state-independent)，不可变(immutable, 也称为intrinsic)数据．依靠状态，可变(mutable, 也成为extrinsic)的数据不应该是flyweight，因为这种数据是因对象而异的，是不可分享的．如果flyweight需要extrinct数据，应该由客户端的代码来提供.

GoF书列举了使用Flyweight模式需要满足的条件:

- 应用需要使用大量的对象.
- 很多对象的存储/渲染开销巨大.
- 应用中的对象标识不是那么重要.

应用实例:

- `Exaile`音乐播放器使用fiyweight模式来复用对象.
- `Peppy`一个使用Python实现的类EXmacs编辑器.使用flyweight模式来存储"major mode"状态栏的状态.

参考：

- [http://codesnipers.com/?q=python-flyweights](http://codesnipers.com/?q=python-flyweights)

### 8.MVC模式(model-view-controller)

*软件设计的原则之一就是关注分离(Seperation of Concerns), 即解耦．使用这个原则可以简化应用的开发和维护．*


MVC可以说是更加像一个架构模式而不是设计模式．架构模式和设计模式的区别是前者适用范围比后者更广．
model是核心组件，它代表knowledge, 它包含／管理（业务）逻辑，数据，状态和一个应用的规则．view代表model的表现形式．controller是model和view之间的连接/胶水，model和view之间所有的通信通信都是通过controller来完成．



能否忽略controller组件？可以，但是会丧失MVC模式的一大好处：在不修改model的情况下，能够使用多个view．想要完成model和它表现形式的解藕，每个view一般都需要有它自己的controller.如果一个model直接和特定的view通信,我们就不能再使用多个view了.



*当你凑巧实现了MVC模式时，确保你创建了聪明(smart)的models，瘦(thin)的controllers，以及愚蠢(dumb)的views.*



- model因该是聪明的(smart)，因为：

    - 包含所有的验证/业务的规则/逻辑.

    - 处理应用的状态

    - 可以访问应用的数据(数据库，云等等...)

    - 不需要依靠UI

- controller应该是瘦的(thin)，因为：

    - 当用户通过view交互时更新model

    - 在model修改时更新view

    - 如果需要，在数据发送到model/view之前处理它们

    - 不需要显示数据

    - 不需要直接访问应用数据

    - 不包含验证/业务的规则/逻辑

- view应该是愚蠢的(dumb), 因为:

    - 需要显示数据

    - 需要用户交互

    - 只需要最小量的(逻辑)处理，通常通过模板语言来实现

    - 不需要存储任何数据

    - 不需要直接访问应用数据

    - 不包含验证/业务的规则/逻辑



如果你实现了MVC模式，想要知道你实现的对不对，可以问自己两个问题:



1. 如果你的应用包含一个GUI，是否可以切换皮肤?可以在运行时让用户切换皮肤吗?如果不能简单的实现切换皮肤，那么可能你实现的MVC模式就有点问题．

2. 如果你的应用没有GUI，那么在加入GUI的时候会不会很难？如果加入展示功能很难，可能你实现的MVC模式就有点问题了.



应用实例:



- `web2py`

- `django`使用了MVC模式，但是它使用的是一个变种，即django的view代表controller,template代表view, 也叫做`Model-Template-View`(MTV).



### 9.代理模式(proxy)



*代理模式用来在访问真正对象之前，执行一个重要的步骤(可能是为了安全,性能...)*



有4种不同的代理类型：



1. `remote proxy`，它扮演一个存在于另外的地址空间对象的本地代理(例如，一个网络服务器).

2. `virtual proxy`，它用于惰性初始化，直到一个高计算消耗对象真正需要时才执行.

3. `protection/protection proxy`，用来对敏感对象的访问控制.

4. `smart(reference) proxy`，当一个对象被访问时执行额外的操作。比如作引用计数和线程安全检查.



在OOP(面向对象编程)中，有两种不同的惰性初始化:



1. **实例级别**：意味着一个对象的property是惰性初始化的，但是这个property是有对象域的.相同类中的每个对象都有自己的property拷贝.

2. **类或者模块级别**：在这种情况下，我们不需要为每个实例准备不同的拷贝，所有的实例都共享同一个property，这个property是惰性初始化的.



应用实例:



- `weakref`模块包含一个`proxy()`方法，它接受一个输入对象并返回一个`smart proxy`

- `ZeroMQ`是一个FOSS项目，聚焦于去中心化计算.



### 10.责任链模式(chain of responsebility)

*责任链模式用于我们想要多个对象满足单个请求的情况，或者用于我们事先不知道(链条中)的哪个对象用来处理特定请求的情况。*

责任链的原则如下:

1. 存在一个对象链条(链表，树或者其它方便的数据结构)
2. 从把一个请求发送给链条中的第一个对象开始
3. 这个对象决定是否满足请求
4. 对象将请求交给下一个对象
5. 这个程序将会重复，知道抵达链条的末端

应用实例:

- Java的servlet filters(类似Django的中间件)
- Apple的Cocoa和Cocoa Touch框架

参考：

- [http://www.dabeaz.com/coroutines/](http://www.dabeaz.com/coroutines/)


### 11.命令模式(command)

*命令模式帮助我们把一个操作(undo, redo, copy...)封装成一个对象*

使用命令模式的好处在于：

- 我们不需要直接执行命令.
- 调用命令的对象和执行命令的对象解藕.调用者不需要知道命令实现的细节.
- 如果有必要，可以将多条命令按顺序执行.

命令模式常见的使用场景:

- `GUI按钮和菜单选项`
- `众多动作操作`: 比如剪切，拷贝，粘帖...
- `事务行为和记录日志`
- `宏`: 宏在这里意味着一连串的命令

应用实例:

- `PyQt`,QT工具包的Python接口.其中有一个`QAction`类，使用了命令模式.
- `git-cola`,Python编写的一个Git GUI.


### 12.解释器模式(interpreter)

*解释器模式只对应用中的高级用户有用，因为这个模式的背后思想是给非新手用户使用一个简单的语言来达到它们的想法*

对于应用来说，一般有两种类型的用户:

- 基础用户: 这类用户不原因花太多时间去学习应用的内部或者花时间去搞一些繁杂的配置．基本的使用对它们来说已经足够了.
- 高级用户: 这类用户通常属于少数，它们不介意花时间去学习应用的高级特性，它们甚至愿意为此学习一个配置(脚本)语言，应该:
    - 让他们能够对应用有更好的控制能力
    - 让他们用更好的方式完成自己的想法
    - 让他们的生产能力更高

通常"简单的语言"是指**DSL(Domain Specific Language)**.

DSL的性能通常不是需要担心的.DSL的重点应该放在提供一个负责特定功能的迷你语言，并且为这个迷你语言提供易读的语法.

这章介绍了一个Python(3.0+)标准库`Pyparsing`，使用这个库可以轻松的定义一套自己的DSL.

应用实例:

- `PyT`是一个Python的DSL，用于生成(X)HTML.一般拿来和Jinja2相比.因为它是一个DSL，所以当然使用的也是解释器模式.
- `Chromium`是一个受chrome影响创建的开源软件(FOSS)浏览器,它的内部使用解释器模式把C模型参数转译为Python对象并执行相关的命令.


### 13.观察者模式(observer)

*想象一下在MVC架构里面我们想要一个model对应两个view,只要model发生变动，那么view也会自动更新．这就是观察者模式, 也叫做发布－订阅模型*

观察者者模式背后的理论和MVC一样，都是关于软件工程的**分离关注点(seperation of concern)**, 在观察者模式中也就是增加＂发布者＂和＂订阅者＂之间的解藕程度，让订阅者可以在任何时候加入/移除对某个发布者的关注.另外，发布者也不需要在意谁在观察自己,它只需要通知它所有的关注者就可以了.

应用实例:

- `django-observer`是一个Django第三方包．可以用来注册一个回调函数，在一些Django字段发生变动时自动调用这个函数.
- `RabbitMQ`是一个erlang开源库.可以用它来为应用加入异步消息队列系统.RabbitMQ可以被Python应用使用，用来实现发布－订阅模型.

参考:

- [http://code.activestate.com/recipes/131499-observer-pattern/](http://code.activestate.com/recipes/131499-observer-pattern/)


### 14.状态模式(state)

*状态模式说到底不过是一个应用于特定软件工程问题的有限状态机*

*状态设计模式允许为一个上下文封装无限数量的状态,目的是易于维护和扩展*

用来作状态过渡的工作的一个常见工具即**有限状态机会(finite-state machine)**.有限状态机是一个抽象的机器，它具有两个关键的组件:状态(state)和过渡(transision).状态(state)即系统当前(激活)的状态(status).过渡即从一个状态改为另一个.通常在一个过渡出现之前，会先执行一堆动作.

需要记住的就是有限状态机在一个时间里面只能存在一个激活的状态．

良好的运用有限状态机(比如`state_machine`)可以改善条件逻辑代码,就是说不需要再写那些愚蠢的`if-else`语句.

应用实例:

- `django-fsm`是一个Django的第三方包，这个包为Django框架简化了有限状态机的实现．
- `State Machine Compiler(SMC)`, 使用它的DSL可以为你自动生成有限状态机的代码.

参考:

- [http://ginstrom.com/scribbles/2007/10/08/design-patterns-python-style/](http://ginstrom.com/scribbles/2007/10/08/design-patterns-python-style/)


### 15.策略模式(strategy)

*策略模式让一个问题的解决方案可选多种算法(中的一个),这是一个杀手级特性，可以让运行时的程序转变使用的代码.*

Python的`list.sort()`和`sorted()`都是策略模式的例子.它们都接受一个`key`参数,这个参数就是实现排序策略的名称.

参考：

- [http://stackoverflow.com/questions/963965/how-is-this-strategy-pattern
](http://stackoverflow.com/questions/963965/how-is-this-strategy-pattern
)

- [http://en.wikipedia.org/wiki/Strategy_pattern](http://en.wikipedia.org/wiki/Strategy_pattern)


### 16.模板模式(template)

*好代码的一个关键要素就是避免多余，模板模式就是用来消除多余代码的*

应用实例: 

- `cmd`是Python的一个标准模块，用来作为内置命令行解释器.
- `asyncore`用于实现异步的socket C/S服务．
- `cowpy`一个有趣的格式化输出库

参考:

- [http://ginstrom.com/scribbles/2007/10/08/design-patterns-python-style/](http://ginstrom.com/scribbles/2007/10/08/design-patterns-python-style/)