# Setuptools Integration

在编写命令行工具的时候，推荐使用setuptools来将它们distributed。

为什么你需要这样：

1. 传统的方法需要在命令行最开始的时候加入`python`

2. 不是所有平台都可以轻松的执行，在Unix/Linux/OS X你可以在文件的开始加入`#!/usr/bin/env python`，你的脚本因此可以直接执行。不过在Windows中无效。

    事实上如果类Unix系统你使用了virtualenv的话同样会有问题。

3. 如果你的脚本是一个Python的模块。如果你的应用变得越来越大，你想要使用这个脚本来运行一个package，同样会遇到问题。

## Introduce

想要将你的脚本和setuptools绑定，只需要在一个Python package中建立一个脚本以及一个`setup.py`文件。

想象下面这个目录结构：

```txt
yourscript.py
setup.py
```

`yourscript.py`的内容:

```python
import click


@click.command()
def cli():
    """Example script."""
    click.echo('Hello World!')
```

`setup.py`的内容:

```python
from setuptools import setup

setup(
    name='yourscript',
    version='0.1',
    py_modules=['yourscript'],
    install_requires=[
        'Click'
    ],
    entry_points="""
        [console_scripts]
        yourscript=yourscript:cli
    """
)
```

请注意`entry_points`参数。在`console_scripts`中，每一行都代表一个控制台脚本。`=`左边的部分代表应该生成的脚本名称，右边部分代表引入路径(import path)以及Click命令(`:`后面的部分)

## Testing The Script

想要测试这个脚本，你可以创建一个virtualenv然后安装你的package：

```shell
$ virtualenv venv
$ . venv/bin/activate
$ pip install --editable .
```

最终，你的命令就可以直接执行了：

```shell
$ yourscript
Hello World!
```

## Scripts in Packages

如果你的脚本变得越来越大，那么你可能想要把你的脚本变为一个Python package，并且尽可能的拆分成模块。让我们假定你拥有下面这个目录结构：

```txt
yourpackage/
    __init__.py
    main.py
    utils.py
    scripts/
        __init__.py
        yourscript.py
```

这是`setup.py`应该这么写:

```python
from setuptools import setup, find_packages

setup(
    name='yourpackage',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Click'
    ],
    entry_points='''
        [console_scripts]
        yourscript=yourpackage.scripts.yourscripts:cli
    '''
)
```