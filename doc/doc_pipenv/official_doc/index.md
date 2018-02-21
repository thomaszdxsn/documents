# Pipenv: Python Dev Workflow for Humans

**Pipenv -- Python.org官方推荐用来作为Python包管理的工具，free.**

Pipenv是一个目标为把最好的软件打包思想(如bundler, composer, npm, cargo...)带入到Python世界的一个工具。

它会为你的项目自动创建并管理一个virtualenv，以及在你安装/卸载软件包的时候自动修改`Pipfile`。而且它会生产一个`Pipfile.lock`.

使用pipenv之后：

- 你不需要再单独的使用`pip`和`virtualenv`了.
- 管理一个`requirements.txt`文件会有很多(潜在的)问题，所以pipenv使用`Pipfile`和`Pipfile.lock`来管理软件包.
- 出于安全等因素，到处都用到了hash.
- 你可以观察你项目的依赖图(`pipenv graph`).
- 通过读取`.env`文件来实现流线型的开发工作流.

## Install Pipenv Today!

> 注意
>
>> 在安装pipenv的时候，推荐使用Python3。使用Python3作为安装目标可以增进three虚拟环境的兼容性.
>> 
>> --Kenneth Reitz

Pipenv是一个python软件包，所以你可以使用`pip`来安装它：

`$ pip install pipenv`

