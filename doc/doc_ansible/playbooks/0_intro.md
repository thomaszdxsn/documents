# Intro to Playbooks

## About Playbooks

Ansible的playbooks的使用方式和adhoc执行模式完全不同，playbook及其强大。

简单来说，playbook是一个很简单的配置管理和多机器部署系统，非常适合用来部署复杂的应用。

Playbook可以用来声明配置，但是也可以规划执行的步骤。任务可以以同步或者异步的方式发布。

你可以运行`/usr/bin/ansible`程序或者ad-hoc任务，playbooks更像资源控制，用来把你的配置推送或者确保你的远程系统使用指定配置。

## Playbook Language Example

Playbooks通过YAML格式来表达，保持语法的最小化，它是故意不使用编程语言或者脚本的形式。

每个playbook都是多个"plays"的混合。

play的主要目的是映射一组host，用之执行一组ansible任务。最简单来说，一个任务就是调用一个Ansbile模块。

通过在一个playbook中混合多个“plays”，可以用来规划多机器的部署，在所有的机器运行一组特定步骤的程序，等等。

“plays”看起来像一个运动方面的术语。你可以通过很多play来让你的系统做很多不同事情。

作为开胃菜，我们从一个单play的playbook开始:

```yaml
---
- hosts: webservers
  vars:
    http_port: 80
    max_clients: 200
  remote_user: root
  tasks:
  - name: ensure apace is at the latest version
    yum name=httpd state=latest
  -name: write the apache config file
    template: src=/srv/httpd.j2 dest=/etc/httpd.conf
    notify:
    - restart apache
- name: ensure apache is running (and enable it at boot)
  service: name=httpd state=started enabled=yes
handlers:
  - name: restart apache
    service: name=httpd state=restarted
...
```

在你的任务描述很长的时候，你可以将它写入多行。下面是上面例子的上一个版本，不过使用了YAML字典来支持模块的`key=value`参数:

```yaml
---
- hosts: webservers
  vars:
    http_port: 80
    max_clients: 200
  remote_user: root
  tasks:
  - name: ensure apache is at the latest version
    yum:
      name: httpd
      state: latest
  - name: write the apache config file
    template:
      src: /srv/httpd.j2
      dest: /etc/httpd.conf
    notify:
    - restart apache
  - name: ensure apache is running
    service:
      name: httpd
      stete: started
  handlers:
    - name: restart apache
      service:
        name: httpd
        state: restarted
...
```

Playbooks可以包含多个play。你可以针对上面的web服务器，另外提供一个数据库服务器：

```yaml
---
- hosts: webservers
  remote_user: root

  tasks:
  - name: ensure apache is at the latest version
    yum: name=httpd state=latest
  - name: write the apache config file
    template: src=/srv/httpd.j2 dest=/etc/httpd.cong

- hosts: databases
  remote_user: root

  tasks:
  - name: ensure postgresql is at the latest version
    yum name=postgresql state=latest
  - name: ensure that postgresql is started
    service: name=postgresql state=started
...
```

你可以使用这个方法来切换host组，切换登陆服务器的用户名，是否应该使用sudo等等。plays就像tasks，自上而下的运行。

下面，我们继续介绍playbook语言的一些其它特性。

## Basics

### Hosts and Users

对于playboo的每一个play，你可以选择机器和用户。

`host`行是一个或多个host模式的pattern或者group，通过分号分隔。`remote_user`是用户账号的名称。

```yaml
---
- hosts: webservers
  remote_user: root
...
```

> `remote_user`参数在以前叫做`user`。从Ansible1.4开始，为了将它和`user`模块进行区分而进行了改名。

远程用户可以在每个任务中单独设置：

```yaml
---
- hosts: webservers
  remote_user: root
  tasks:
    - name: test connection
      ping:
      remote_user: yourname
...
```

可以让你的任务在运行的时候切换成其它用户:

```yaml
---
- hosts: webservers
  remote_user: yourname
  become: yes
...
```

你可以在一个特定的task中使用`become`:

```yaml
---
- hosts: webservers
  remote_user: yourname
  tasks:
    - service: name=nginx state=started
      become: yes
      become_method: sudo
...
```

除了`become`切换为root，还可以切换为其它用户:

```yaml
---
- hosts: webservers
  remote_user: yourname
  become: yes
  become_user: postgres
...
```

你可以使用其它的privilege escaltion方法，比如`su`:

```yaml
---
- hosts: webservers
  remote_user: yourname
  become: yes
  become_method: su
...
```

如果你希望为`sudo`设定密码，可以在运行`ansible-playboo`的时候加上选项`--ask-become-pass`，或者使用以前的sudo语法`--ask-sudo-pass(-k)`。如果你运行一个带become的playbook但是它看起来卡住了，可能就是卡在privilege escaltion提示。这时候只要使用`Control-C`终止命令并重新执行命令就好了。

你可以控制hosts运行的顺序。默认会根据inventory的顺序：

```yaml
---
- hosts: all
  order: sorted
  gather_facts: False
  tasks:
    - debug: var=inventory_hostname
...
```

`order`可选的值包括:

- inventory

	默认值。inventory提供的顺序。

- reverse_inventory

	inventory的逆序。

- sorted

	根据字母表顺序排序。

- reversed_sorted:

	字母表顺序的逆序。

- shuffle

	完全随机的顺序。

### Tasks list

每个play都包含一组task。Task按顺序执行，在所有的机器执行一个任务以后才会执行下一个任务。对于一个play来说，所有的host都会间接获取同一个task。它的目的是将paly映射到所选的host中。

在运行playbook时，它会自上而下的运行，执行task失败的host将会移除出整个playbook的执行环境。如果发生了错误，那么就请修改playbook文件再重新运行把。

每个task的目标就是使用指定的参数来执行一个模块。上面提到的变量可以用于当作模块的参数。

模块应该是幂等的，也就是说，同样参数运行一个模块多次应该每次的效果都是一样的。如果一个playbook使用的所有模块都是幂等的，那么这个playbook本身就是幂等的，这个playbook就可以反复运行。

`command`和`shell`模块可以重复执行相同的命令。

没有task都有一个`name`，它包含这个playbook运行时打印的输出。所以应该提供一些详细的描述文本。

推荐使用`module: options`来声明task。

下面是一个基础的task。大多数模块都可以以`key=value`格式传入参数:

```yaml
---
tasks:
  - name: make sure apache is running
    service: name=httpd state=started
...
```

`command`和`shell`是唯二的不实用`key=value`形式传入参数的模块：

```yaml
tasks:
  - name: enable selinus
    command: /sbin/setenforce 1
...
```

`command`, `shell`模块可以注意返回码。如果你想要忽略错误：

```yaml
---
tasks:
  - name: run this command and ignore the result
    shell: /usr/bin/somecommand || /bin/true
...
```

或者这样:

```yaml
---
tasks:
  - name: run this command and ignore the result
    shell: /usr/bin/somecommand
    ignore_errors: true
```

如果编写的代码太长了:

```yaml
---
- name: Copy ansible inventory file to client
  copy: src=/etc/ansible/hosts dest=/etc/ansible/hosts
          owner=root grouproot mode=0644
...
```

变量可以用来action行。假设你在`vars`节中有一个`vhost`变量：

```yaml
---
tasks:
  - name: create a virtual host file for {{ vhost }}
    template: src=somefile.j2 dest=/etc/httpd/conf.d/{{ vhost }}
...
```

## Action Shorthand

Ansible推荐使用这种方式调用模块:

`template: src=template/foo.j2 dest=/etc/foo.conf`

## Handlers: Running Operation On Change

我们之前提到过，模块应该是幂等的。Playbook有一个基本的事件系统，可以响应对远程机器的修改。

这些'notify'事件可以写在一个task的最后，不过只会被触发一次。

下面是一个例子，在文件改动的时候重启两个服务:

```yaml
- name: template configuration file
  template: src=template.j2 dest=/etc/foo.conf
  notify:
    - restart memcached
    - restart apache
```

一个task的notify列出的task部分叫做handlers。

handlers是一组task，和其它的task没什么不同。

下面是一个handlers的示例：

```yaml
---
handlers:
  - name: restart memcached
    service: name=memcached state=restarted
  - name: restart apache
	service: name=apache state=restarted
...
```

自Ansible2.2开始，handlers可以监听一些同样的事件：

```yaml
---
handlers:
  - name: restarted memcached
    service: name=memcached state=restarted
    listen "restart web services"
  - name: restarted apache
    service: name=apache state=restarted
    listen: "restart web services"

tasks:
  - name: restart anything
    commnet: echo "this task will restart the web services"
    notify: "restart web services"
...
```

注意:

- Notify handler会按照定义的顺序来运行，而不是通过notify语句的顺序。
- Handler名称和listen名都存在于全局命名空间
- 如果两个handler task有相同的名称，只有一个会被调用

## Executing A Playbook

现在你学会了playbook的语法，怎么运行一个playbook呢？很简单，让我们以并行数10个来运行playbook:

`ansible-playbook playbook.yml -f 10`

## Ansible-Pull

`ansible-pull`是一个小脚本，会检查一个git仓库，然后根据内容运行`ansible-playbook`.

## Tips and Tricks

想要检查playbook的语法是否正确，可以运行ansible-playbook并加上`--syntax-check`选项。


