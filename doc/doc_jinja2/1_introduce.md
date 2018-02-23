# Introduce

这是Jinja2的文档。Jinja2是Python的一个库，它设计于实现一种弹性、快速和安全的通用型模版语言。

如果你有其它文本型模版语言的基础，比如Smarty或者Django，你应该会对Jinja2很喜欢。它坚持了Python的一些准则，并设计于尽量对设计师和开发者都友好，另外为模版环境加入了一些强大的功能。

## Prerequisites

Jinja2可以运行在Python2.6, 2.7以及3.3以上版本。

如果你希望使用`PackageLoader`类，你需要安装`setuptools`和`distribute`.

## Installation

你可以通过很多方式来安装Jinja2。

### As a Python egg (via easy_install)

```shell
$ easy_install Jinja2
$ pip install Jinja2
```

### From the tarball release

1. 从[下载页面](https://pypi.python.org/pypi/Jinja2)下载最新的tar文件
2. 解包tarball
3. `python setup.py install`

### Installing the development version

1. 安装`git`
2. `git clone git://github.com/pallets/jinja.git`
3. `cd jinja2`
4. `ln -s jinja2 /usr/lib/pythonX.Y/site-packages`

## MarkupSafe Dependency

Jinja2依赖`MarkupSafe`模块，如果你使用`easy_install`或者`pip`来安装Jinja2，将会自动为你安装这个依赖。

## Basic API Usage

这章节为你间断的介绍Jinja2模版的Python API。

最基本的创建一个模版的方式是通过`Template`类。

```python
>>> from jinja2 import Template
>>> template = Template('Hello {{ name }}!')
>>> template.render(name='John Doe')
u'Hello John Doe!
```

在创建一个`Template`实例后，你可以使用它的方法`.render()`，以关键字或字典的形式传入变量到模版中。传入的变量也叫做模版的“context”。

你可以看到Jinja2内部使用Unicode并且返回的值也是Unicode字符串。

## Experimental Python 3 Support

Jinja2.7开始对Python3进行试验型支持。意味着它所有的unittest都更新到了新版本，不过可能仍然存在一些小BUG。如果你遇到了，请到[Jinja bug tracker](https://github.com/pallets/jinja/issues)反馈，谢谢。

另外记住这个文档是以Python2语法写的，如果要测试你需要自行将它转换为Python3.