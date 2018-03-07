# Installation

## Basic / What Will Be Instatlled

Ansible默认通过SSH协议来管理机器。

一但Ansible安装好了，它不会附带数据库，也不会启动守护进程。你只需要将它安装在一台机器上面，然后就可以以这台机器为中心点来管理整个机器群。在Ansible管理远方机器的时候，它不会运行某个软件，所以你唯一需要关心的就是在Ansible进入新版本的时候保持更新就好了。

## What Version To Pick?

因为Ansible可以轻松获得源码，不需要在远方机器安装其它软件，很多用户都选择使用开发版本。

Ansible的发布周期通常是以月算的。

如果你想要使用最新发布版本的Ansible并且你的系统是Redhat，CentOS，Fedora，Debian，Ubuntu，我们推荐你使用系统包管理器来进行安装。

其它的安装选项，我们推荐使用`pip`来安装。

如果你要使用开发版本，可以从Github拉取代码。

## Control Machine Requirement

目前Ansible可以运行在任何平台，只要安装了Python2.6，2.7或者Python3.5以上版本。

> As of version 2.0, Ansible uses a few more file handles to manage its forks. Mac OS X by default is configured for a small amount of file handles, so if you want to use 15 or more forks you’ll need to raise the ulimit with sudo launchctl limit maxfiles unlimited. This command can also fix any “Too many open files” error.

## Managed Node Requirements

在管理的节点中，你需要一种方式来通讯，通常是使用ssh。如果你想使用其它方式，可以修改`ansible.cfg`.

## Installing the Control Machine

### Latest Release Via Yum

```shell
$ git clone https://github.com/ansible/ansible.git
$ cd ./ansible
$ make rpm
$ sudo rpm -Uvh ./rpm-build/ansible-*.noarch.rpm
```

### Latest Releases Via Apt(Ubuntu)

```shell
$ sudo apt-get update
$ sudo apt-get install software-properties-common
$ sudo apt-get-repository ppa:ansible/ansible
$ sudo apt-get update
$ sudo apt-get install ansible
```

### Latest Releases Via Apt (Debian)

为`/etc/apt/souce.list`文件追加一行:

`deb http://ppa.launchpad.net/ansible/ansible/ubuntu trusty main`

然后执行下列命令:

```shell
$ sudo apt-key adv --keyserver keyserver .ubuntu.com --recv-keys 93C4A3FD7BB9C367
$ sudo apt-get update
$ sudo apt-get install ansible
```

### Latest Releases Via Protage(Gentoo)

`$ emerge -av app-admin/ansible`

### Latest Releases Via pkg (FreeBSD)

`$ sudo pkg install ansible`

### Latest Releases on Mac OSX

OS X系统推荐使用Pip进行ansible的安装。

### Latest Releases Via OpenCSW (Solaris)

```shell
# pkgadd -d http://get.opencsw.org/now
# /opt/csw/bin/pkgutil -i ansible
```

### Latest Releases Via Pip


```shell
$ sudo easy_install pip
$ sudo pip install ansible
```