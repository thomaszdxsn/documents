# Introduction To Ad-Hoc Commands

相面的例子展示了如何使用`/usr/bin/ansible`来运行ad-hoc任务。

什么叫做ad-hoc命令？

一个ad-hoc命令应该是能够很快得到结果的命令。

在这里你会理解到为什么Ansible并不一定需要学习使用playbooks - ad-hoc命令也可以作很多事情。

一般来说，Ansible最强大的功能是playbook。那么为什么还要存在ad-hoc命令呢？

举例来说，如果你想好好过一个圣诞假期，那么就可以快速写一行ad-hoc命令，而不是重写一个playbook。

对于配置管理和部署，你应该使用ansible-playbook。

## Parallelism and Shell Commands

让我们使用Ansible的命令行工具来重启Atlanta的web服务。首先我们建立起SSH-agent，它可以记住我们的证书:

```shell
$ ssh-agent bash
$ ssh-add ~/.ssh/id_rsa
```

如果你不想用ssh-agent，想要直接输入SSH密码，那么你可以加入`--ask-pass, -k`选项。

现在我们对一个group的所有server运行一个命令，并行运行10个命令：

`$ ansible atlanta -a "/sbin/reboot" -f 10`

`/usr/bin/ansible`默认会用你的账号来运行。如果你不喜欢这样，那么可以通过`-u`来指定用户名，比如:

`$ ansible atlanta -a "/usr/bin/foo" -u username`

如果你想要运行需要权限的命令：

`$ ansible atlanta -a "/usr/bin/foo" -u username --become [--ask-become-pass]`

become会默认变为root，如果想切换成其它用户，可以使用`--become-user`:

`$ ansible atlanta -a "/usr/bin/foo" -u username --become-user otheruser [--ask-become-pass]`

`-f 10`意味着会为你准备10个同时进行的进程。你可以通过配置文件设置默认的并行数量，初始的默认值为5。

你可以通过`-m`选择你要运行的Ansible模块，默认的模块是"command"，它不需要你指定。

使用`shell`模块，看起像下面这样：

`$ ansible raleigh -m shell -a 'echo $TERM'`

在使用Ansible Ad-Hoc运行任何命令时，需要注意shell的引号规则，不要让本地的shell将变量"吃掉"。例如，如果上面的例子使用双引号而不是单引号，结果就完全不对。

## File Transfer

Ansible可以使用SCP来并行地对多台机器进行文件传输。

想要直接把一个文件传输到多台server：

`$ ansible atlanta -m copy -a "src=/etc/hosts dest=/tmp/hosts"`

如果你使用playbooks，可以使用`template`模块。

`file`模块允许你修改文件的所属和权限。选项和传入`copy`模块的一样：

```shell
$ ansible webservers -m file -a "dest=/srv/foo/a.txt mode=600"
$ ansible webservers -m file -a "dest=/srv/foo/b.txt mode=600 group=mdehaan"
```

`file`模块也可以创建目录，类似与`mkdir -p`:

```shell
$ ansible webservers -m file -a "dest=/path/to/c mode=755 owner=mdehaan group=mdehaan state=directory"
```

以及删除目录(递归)和删除文件：

```shell
$ ansible webservers -m file -a "dest=/path/to/c state=absent"
```

## Managing Packages

软件包管理可以通过模块`yum`和`apt`来解决。

想要确定一个软件是否安装，但是不要更新它：

`$ ansible webservers -m yum -a "name=acme state=present"`

确定一个软件是一个特定的版本:

`$ ansible webservers -m yum -a "name=acme-1.5 state=present"`

确定一个软件是最新版本：

`$ ansible webservers -m yum -a "name=acme state=latest"`

## Users and Groups

`user`模块可以用来创建和操作现存的用户账号:

```shell
$ ansible all -m user -a "name=foo password=<加密密码>"

$ ansible all -m user -a "name=foo state=absent"
```

## Deploying From Srouce Control

可以直接通过git来部署你的webapp：

`$ ansible webservers -m git -a 'repo=https://foo.example.org/repo.git dest=/srv/myapp version=HEAD'`

## Managing Services

想要确认一个服务是否运行:

`$ ansible webservers -m service -a "name=httpd state=started"`

重启服务：

`$ ansible webservers -m service -a "name=httpd state=restarted"`

确定一个服务已经停止了：

`$ ansible webservers -m service -a "name=httpd state=stopped"`

## Time Limited Background Operations

长时间运行的操作可以在后台执行，可以选择在之后检查它们的状态。例如，在后台异步执行`long_runing_operation`，使用`-B`设定超时时间为3600，以及通过`-P`设置不用polling：

`$ ansible all -B 3600 -P 0 -a "/usr/bin/long_runing_operation --do-stuff"`

如果你希望在之后检查任务完成的情况，你可以使用`async_status`模块，将之前返回的任务id传入:

`$ ansible web1.example.com -m async_status -a "jid=488359678239.2844"`

Polling是内置的，看起来像这样：

`$ ansible all -B 3600 -P 60 -a "/usr/bin/long_running_operation --do-stuff"`

上面的例子是说：“最多运行30分钟”，每60秒poll一下状态。

Poll模式是很智能的,在任何机器上都可以开启poll。

## Gathering Facts

你可以通过下面命令来查看facts：

`$ ansible all -m setup`


