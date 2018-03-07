# Getting Started

- `--private-key`
- `-u`
- `-m ping`
- `-a '/bin/echo'`

## Foreward

现在你已经在本机安装了Ansible，是时候开始使用一些ad-hoc命令了。

这章节主要介绍如何初始化Ansible的运行。一旦你理解了这些概念，可以阅读[Introduction To Ad-Hoc Commands](http://docs.ansible.com/ansible/latest/intro_adhoc.html)获取更多信息。

## Remote Connection Infomation

在我们开始之前，需要明白Ansible是怎么通过SSH和远程机器进行通讯的。

默认情况下，Ansible1.3以后会尽可能使用OpenSSH来进行远程通信。

在和远程机器通信时，Ansible默认假定你使用SSH key。虽然鼓励你使用SSH key，但是也可以用`--ask-pass`来传入密码。如果需要使用sudo，而sudo需要密码，那么需要使用`--ask-become-pass`.

虽然是常识，但是也有必要再提一下：任何管理系统都会更容易管理离自己更近的机器。如果你在一个云上运行Ansible，考虑在云上在运行一台机器。

有一些高级的情况，Ansible并不通过SSH来连接远方。传输层是可插拔的，有一些选项时可以本地管理的，比如管理`chroot`，`lxc`和`jail`容器。有一种模式叫做`ansible-pull`可以从一个中心仓库拉取配置目录。

## Your first commands

现在可以开始执行一些基础命令了。

编辑(或创建)`/etc/ansible/hosts`，放入一个或多个远程系统。你的公共SSH键应该位于这些系统的`authorized_keys`:

```shell
192.0.2.50
aserver.example.org
bserver.example.org
```

这是一个inventory文件。

我们假定你使用SSH key来进行验证。想要建立SSH agent来避免输入代码，你可以这样作：

```shell
$ ssh-agent bash
$ ssh-add ~/.ssh/id_rsa
```

根据你的情况，你可能需要使用`Ansible`的`--private-key`选项来指定一个pem文件。

现在可以ping一下你的节点：

`$ ansible all -m ping`

Ansible会使用你当前的用户名来链接机器，就像SSH做的一样。想要覆盖远程的用户名，可以使用`-u`选项.

如果你想要访问sudo模式，还需要是这下面这些flag：

```shell
# 以bruce登陆
$ ansible all -m ping -u bruce
# 以bruce登陆，sudoing切换为root
$ ansible all -m ping -u bruce --sudo
# 以bruce登陆，sudoing切换为batman
$ ansible all -m ping -u bruce --sudo --sudo-user batman

# 在最新版本的ansible中，`sudo`已经弃用
$ ansible all -m ping -u bruce -b
$ ansible all -m ping -u bruce -b --become-user batman
```

现在让你的节点运行一个live命令:

```shell
$ ansible all -a '/bin/echo hello'
```

恭喜！你使用Ansible和远程节点完成了通信。

Tips：

无论合适你运行一个命令，都可以指定一个本地服务器，使用"localhost"或者"127.0.0.1"作为服务器名称。

示例：

`$ ansible localhost -m ping -e 'ansible_python_interpreter="/usr/bin/env python"'`

你可以通过加入inventory文件来显式指定localhost：

```shell
localhost ansible_connection=local ansible_python_interpreter="/usr/bin/env python"
```

## Host Key Checking

在Ansible1.2.1以后，会默认开启host key检查。

如果一个host重新安装并且有一个不同的键，叫做"known_hosts"，这会导致一个错误消息。如果这个host没有以"known_hosts"来初始化，那么会有一个提示框让你确认key。

如果你想禁用这个行为，你可以编辑`/etc/ansible/ansible.cfg`或者`~/ansible.cfg`.

```ini
[defaults]
host_key_checking = False
```

另外你可以设置`ANSIBLE_HOST_KEY_CHECKING`环境变量：

`$ export ANSIBLE_HOST_KEY_CHECKING=False`


