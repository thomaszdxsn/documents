# How Ansible Works

Ansible是一个简单地要死的IT自动换引擎，它可以自动进行云监控，配置管理，应用部署，服务协调等工作。

Ansible的通过描述你的系统来构建你的IT底层架构模型。

它使用无agent，无额外的自定义安全设施的架构，所以可以轻松部署 - 最重要的是，它使用了一种简单的语言(YAML，Ansible Playbooks使用的语言)，允许你用其来描述自动化任务。

在本章中，我们带你快速浏览一遍Ansible的强大功能。更多细节请看文档。

## Efficient Architecture

Ansible是通过连接结点然后推送小程序来工作的，这些小程序叫做"Ansible modules"。这些程序用来获取系统的资源状态。Ansible会默认通过SSH执行这些模块，并在结束以后移除它们。

你的模块库可以放在任何系统上面，不要求服务器，守护进程，数据库。一般你可以使用你喜欢的终端，文本编辑器来写模块。

## SSH Key Are Your Friends

Ansible支持使用密码，但是最好是使用SSH秘钥。不要求使用root登陆，你可以以任何用户登陆，然后使用`su`或者`sudo`切换成其它用户。

Ansible的`authorized_key`模块是ansible用来控制哪个机器访问哪个host的。

## Manage Your Inventory In Simple Text Files

默认情况下，Ansible使用一个简单的`INI`文件来代表机器被怎样管理。

想要加入额外的机器，不需要额外的SSL签名server。

如果你的IT设施中有其它可信赖的用户，Ansible也可以管理，比如划出一个目录，group，以及一些变量信息。

下面是一个inventory文件的样子:

```ini
[webservers]
www1.example.com
www2.example.com

[dbservers]
db0.example.com
db1.example.com
```

一个inventory host列入后，变量可以通过一个简单的文本文件来赋予(在`group_vars/`或者`host_vars/`的子目录中).

## The Basics: Using Ansible For AD HOC Parallel Task Execution

一旦你可以使用实例了，你就可以和它通信了，不需要任何额外的步骤：

```shell
ansible all -m ping
ansible foo.example -m yum -a "name=httpd state=installed"
ansible foo.example -a "/usr/sbin/reboot"
```

## Playbooks: A Simple+Powerful Automation Language

Playbooks可以协调你的设施，可以很详细的控制一次性有多少机器参与处理。

```txt
---
- hosts: webservers
serial: 5 # 一次性更新5台机器
roles:
- common
- webapp
```

```txt
- hosts: content_servers
roles:
- common
- content
```

## Extend Ansible: Modules, Plugins and APIs

Ansible module可以使用任何语言编写，只要返回JSON就可以了。