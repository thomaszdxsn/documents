# Getting Started

## 1.1 Getting Started - Abount Version Control

### About Version Control

- Local Version Control Systems

    版本数据库, RCS...

- Centralized Version Control Systems

    CVS, Subversion, Perforce...

    这是可以多人协作一个代码库了。缺陷时代码有丢失的风险。

- Distributed Version Control Systems

## 1.2 Getting Started -- A Short History of Git

### A Short History of Git

Linux个人开发。有以下几个特性：

- 快速
- 设计简单
- 支持非线性开发(数以千计的并行分支)
- 完全分布式
- 可以处理大型项目，比如Linux内核

## 1.3 Gettings Started -- Git Basics

### Git Basics

理解三个事情就绷帮助你将Git和其它版本控制工具区分开来.

#### Snapshots, Not Differences

Git任务它的数据类似一个迷你文件系统的一系列快照。

#### Nearly Every Operation Is Local

Git几乎所有的操作都利用本地资源。

### Git Has Integrity

你对文件做的一切都应该让git知道。

Git使用SHA-1哈希算法来存储文件。

### Git Generally Only Adds Data

### The Three States

三种状态分别是:`committed`, `modified`和`staged`

- `committed`意味着数据已经安全的存储到你本地git数据库中。
- `modified`意味着你已经修改了文件，但是还未提交到本地git数据库中。
- `staged`意味着你标记一个modified文件，下次commit的时候将会提交它。

这三个状态可以让我们了解一个Git项目的三个主要分区：Git目录，working tree以及staging area.

Git目录存放你的项目的元数据以及对象数据库。这是Git最重要的一个部分，在你clone一个代码仓库到自己机器上的时候它指定拷贝什么。

working tree是项目的一个版本。这些文件从Git目录中的压缩数据库拉取出来，放在你的硬盘中以供使用。

staging area是一个文件，一般在你的Git目录中，它代表你下次要commit时包含的信息。它在Git术语中也叫作Index。

一个基本的Git工作流大概是：

1. 修改你的working tree中的文件
2. 选择你想要下次commit的一部分内容，将它加入到staging area.
3. 进行一次commit，这次操作会从staging area中拿取文件并当作snapshot永久存储在git目录中。

## 1.4 Getting Started - The Command Line

### The Command Line

有很多种方式可以使用Git。最原始的方式就是使用命令行，不过还有很多GUI应用可供选择。

## 1.5 Getting Started - Installing Git

pass

## 1.6 Getting Started - First-Time Git Setup

### First-Time Git Setup

Git有一个工具叫做`git config`，让你可以设置一些配置变量。这些变量存储在三个不同的地方：

- `/etc/gitconfig`

    系统级配置

- `~/.gitconfig`或者`~/.config/git/config`

    用户级配置

- Git目录中的`config`文件(也就是`.git/config`)

### Your Identity

在使用Git的时候应该设置你的用户名和邮箱：

```shell
$ git config --global user.name "John Doe"
$ git config --global user.email johndoe@example.com
```

### Your Editor

在Git需要你输入的时候，它会为你打开一个编辑器。默认会打开系统默认的编辑器。

如果你想要使用其它的文本编辑器：

`$ git config --global core.editor emacs`

### Checking Your Settings

如果你想要检查你的git配置，可以使用`git config --list`命令列出所有的配置。

也可以使用`git config <key>`来检查特定的配置：

```shell
$ git config user.name
John Doe
```

## 1.7 Getting Started - Getting Help

### Getting Help

如果你想要查看git的命令手册：

```shell
$ git help <verb>
$ man git-<verb>
```

也可以针对每个子命令使用`-h`选项来查看间断的命令描述.

## 1.8 Getting Started - Summary

你应该以及对Git有了基础的了解。现在正式开始学习把。

