无论在官方文档还是pyMOTW，`string`都是第一个介绍的标准库。如果是python老兵可能对这个库有很多回忆，因为很久之前，现在`str`中的大部分方法都是`string`库的独立函数.

另外这个库引入了`format`语法，这种迷你DSL(Domain Specific Language)语言比C的`%`占位符无疑更加可读.

## 摘要

首先，`string`模块现在对使用者的意义几乎只剩**常量**部分.

`Template`在Python历史上面昙花一现，它标榜自己相比Ｃ的%插值"simpler(更简单)"，
但是“更简单”还不够，C语言的插值语法已经深入人心，而且大多数人都学过并掌握，所以也没有学习成本.

学习`Template`一部分最有用的是通过看它的源码，我又去学了一遍`metaclass`，这次大概理解了元类
6-7成的样子。另外这个`Template`源码基本就是通过正则实现的，使用的正则方法包括`re.escape()`,
`re.sub()`...

`Template`源码中有两个重要的细节:

1. `substitute(*args, **kwargs)`方法把`self`包含到了`*args`中，所以可以将`self`这个名称
让出来供关键字参数使用.
2. `re.sub()`可以接受函数作为第一个参数，这样使用明显更加弹性化.

`Formatter`重不重要？重要，但是多数时候并不需要`import string`，使用`str.method()`这个接口即可。

还有个辅助函数: `capwords`，有句讲句没多少人会记得这个函数吧，大多数碰到使用场景的时候也是自己写一行表达式搞定.

## 参考

- [string库的官方文档](https://docs.python.org/3.5/library/string.html)

- [pyMOTW3的text/string](https://pymotw.com/3/string/index.html)

- [str的方法 - 这些str方法替换了string模块中的函数](https://docs.python.org/3/library/stdtypes.html#string-methods)

- [PEP292 - 简单的字符串替换](https://www.python.org/dev/peps/pep-0292)

    定义了一个`Template`类，存放在`string`模块.这个提案很古老，提供了一种除C语言printf()以外的新的字符串插值思路.

- [PEP3101 - 高级字符串格式化](https://www.python.org/dev/peps/pep-3101)

    定义了`str.format()`，`format()`，`string.Formatter`这些代码。定义了更复杂，更弹性的字符串格式化方式.

- [PEP378 - 格式化标识符中的千位分割符号](https://www.python.org/dev/peps/pep-0378/)

- [PEP515 - 数值中的下划线](https://www.python.org/dev/peps/pep-0515/)

- [格式化字符串语法 - `Formatter`和`str.format()`的DSL语言](https://docs.python.org/3.5/library/string.html#format-string-syntax)

## 源代码 

[github](https://github.com/python/cpython/blob/3.6/Lib/string.py)



