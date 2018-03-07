# Inventory

Ansible可以在同一个时间内同时让你底层设施的多个系统一起工作。它会从列入Ansible inventory的系统中挑选一部分，inventory默认放在`/etc/ansible/hosts`。你可以通过命令行的`-i <path>`来指定另一个存放路径。

另外不只是这个inventory配置，你可以同时使用多个inventory文件，动态拉取inventory或者云资源，甚至使用不同的格式(比如YAML).

## Hosts and Groups

Inventory文件可以有很多格式。例如，`/etc/ansible/hosts`文件的格式类似INI：

```python
mail.example.com

[webservers]
foo.example.com
bar.example.com

[dbservers]
one.example.com
two.example.com
three.example.com
```

头部在方括号中的是组名，它用来划分系统。

YAML格式如下：

```yaml
all:
    hosts:
        mail.example.com
    children:
        webservers:
        hosts:
            foo.example.com
            bar.example.com
        dbservers:
        hosts:
            one.example.com
            two.example.com
            three.example.com
```

可以将系统放在多个group中。

如果你有的host运行在非标准的SSH端口，你可以将端口号码放在host后面以冒号分隔。

```yaml
badwolf.example.com:5309
```

假设你只有静态IP，但是想为你的host设定一些alias.

在INI中：

`jumper ansible_port=5555 ansible_host=192.0.2.50`

在YAML中：

```yaml
hosts:
    jumper:
        ansible_port: 5555
        ansible_host: 192.0.2.50
```

在上面的例子中，我们为这个host取了一个alias叫做`jumper`，可以连接`192.0.2.50:5555`。一般来说，这不是推荐的方式。

如果很多host都有相同的模式，你不必将他们每个都列出来：

```ini
[webservers]
www[01:50].example.com
```

开头的0可以选择移除。另外你可以定义字母表:

```ini
[databases]
db-[a:f].example.com
```

另外你可以在每个host的基础上面选择连接的类型:

```ini
[targets]

localhost  ansible_connection=local
other1.exmaple.com  ansible_connection=ssh  ansible_user=mpdehaan
other2.example.com  ansible_connection=ssh  ansible_user=mdehaan
```

上面提到过，将这些设置在inventory只是一个快捷方式。我们在之后会讨论怎么把它们作为单独文件保存在`host_vars`文件夹。

## Host Variables

上面提到过，为host赋值变量很简单，这些变量之后在playbooks会用到：

```ini
[atlanta]
host1 http_port=80 maxRequestsPerChild=808
host2 http_port=303 maxRequestsPerChild=909 
```

## Group Variables

变量也可以应用到整个组上面.

INI的方式:

```ini
[atlanta]
host1
host2

[atlanta:vars]
ntp_server=ntp.atlanta.example.com
proxy=proxy.atlanta.example.com
```

YAML版本:

```yaml
atlanta
    hosts:
        host1:
        host2:
    vars:
        ntp_server: ntp.atlanta.example.com
        proxy: proxy.atlanta.example.com
```

## Groups of Groups, and Group Variables

可以在INI中使用`:children`后缀，或者YAML使用`children:`来获取嵌套的group。

```ini
[atlanta]
host1
host2

[raleigh]
host2
host3

[southeast:children]
atlanta
raleigh

[southeast:vars]
some_server=foo.southeast.example.com
halon_system_timeout=30
self_destruct_countdown=60
escape_pods=2

[usa:children]
southeast
northeast
southwest
northwest
```

```yaml
all:
  children:
    usa:
      children:
        southeast:
          children:
            atlanta:
              hosts:
                host1:
                host2:
            raleigh:
              hosts:
                host2:
                host3:
          vars:
            some_server: foo.southeast.example.com
            halon_system_timeout: 30
            self_destruct_countdown: 60
            escape_pods: 2
        northeast:
        northwest:
        southwest:
```

如果你需要存储list或者hash数据，请看下章节的内容。子group有几个特点需要注意：

- 子group中的任何成员都会自动成为父group的成员
- 子group的变量优先级比父group更高
- group可以多个父或子，但是不能有循环问题
- host可以存在于多个group中，但是每个host只有一个实例

## Default groups

有两个默认group: `all`和`ungrouped`。`all`包含每个host，`ungrouped`包含除了`all`之外没有所属group的host。每个host都最少属于两个group。

## Splitting Out Host and Group Specific Data

Ansible的最佳实践是不要把变量存储在主inventory文件中。

除了直接把变量存储在inventory文件，host和group变量可以存储在独立的文件(放在inventory同目录下)。

合法的文件后缀是`.yml`, `.yaml`, `.json`，或者无后缀。

假定inventory文件的路径是:

`/etc/ansible/hosts`

如果hosts叫做'foosball'，group叫做'raleigh'和'webservers'，变量可以存储在下面位置:

```shell
/etc/ansible/group_vars/releigh
/etc/ansible/group_vars/webservers
/etc/ansible/host_vars/foosball
```

有一些高级的使用场景，你可以在接着向下创建目录，Ansible会递归获取这些目录：

```shell
/etc/ansible/group_vars/releigh/db_settings
/etc/ansible/group_vars/releigh/cluster_settings
```

## List of Behavioral Inventory Parameters

设置如下的变量可以控制ansible怎么和远程host通信：

Host连接:

- ansible_connection

    host的连接类型。

- ansible_host

    连接的host名称

- ansible_port

    连接host的端口号，默认为22

- ansible_user

    ssh使用的用户名，默认使用连接时本机的用户名.

SSH连接：

- ansible_ssh_pass

    要使用的ssh密码

- ansible_ssh_private_key_file

    连接ssh使用的秘钥文件

- ansible_ssh_commom_args

    这个settings会追加到`sftp`, `scp`和`ssh`命令后面。

- ansible_sftp_extra_args

    这个settings会追加到`sftp`命令后面。

- ansible_scp_extra_args

    这个settings会追加到`scp`命令后面。

- ansible_ssh_extra_args

    这个settings会追加到`ssh`命令后面。

- ansible_ssh_pipeline

    决定是否使用SSH pipeline。可以覆盖`ansible.cfg`的pipeline设置.

- ansible_ssh_executable

    这个配置可以覆盖系统默认的ssh可执行文件.


隐私设置：

- ansible_become

    等同于`ansible_sudo`, `ansible_su`，强制privilege escalation

- ansible_become_method

    允许设置privilege escalation方法.

- ansible_become_user

    等同于`ansible_sudo_user`或`ansible_su_user`，允许设置让用户通过privilege escalation.

- ansible_become_pass

    等同于`ansible_sudo_pass`或`ansible_su_pass`，允许用户设置privilege escalation密码

- ansible_become_exe

    等同于`ansbile_sudo_exe`或`ansible_su_exe`，允许用户设置选择的方法的可执行文件。

- ansible_become_flags

    等同于`ansible_sudo_flags`或者`ansible_su_flags`，允许你设置选择的escalation方法传入的flags。也可以在`ansible.cfg`中的`sudo_flags`选项进行全局设置.

远程host环境变量:

- ansible_shell_type

    目标系统的shell类型。你一般不要使用设置，除非你的系统不兼容Bource shell。

- ansible_python_interpreter

    如果系统中有多个Python，应该设置这个setting。

- ansible\_\*\_interpreter

    可以指定任何其它的解释器，比如ruby或者perl。

- ansible_shell_executable

    可以用来设置ansible controller，默认为`/bin/sh`.

一个INT host文件的示例：

```ini
some_host       ansible_port=2222  ansible_user=manager
aws_host        ansible_ssh_private_key=/home/example/.ssh/aws.pem
freebsd_host    ansible_python_interpreter=/usr/local/bin/python
ruby_module/host ansible_ruby_interpreter=/usr/bin/ruby.1.9.3
```

## Non-SSH connection types

可以使用下面的非SSH连接方式，即`ansible_connection=<connector>`的connector:

- local

    这个连接器可以用来部署playbook控制本机。

- docker

    这个连接器使用本地的Docker客户端直接为Docker容器部署playbook。可以为这个连接器指定下列参数:

    - ansible_host

        要连接的Docker容器名称

    - ansible_user

        操作容器的用户名。用户必须存在于容器中。

    - ansible_become

        如果设置为true，那么会使用`become_user`来操作容器

    - ansible_docker_extra_args

        可以是一个字符串，包含Docker可以理解的参数。这个参数主要用于配置要使用的远程Docker后台程序。

    下面的示例讲解了如何立即部署一个创建的容器(这是一个playbook):

    ```yaml
    - name: create jenkins container
      docker_container:
        docker_host: myserver.net:4243
        name: my_jenkins
        image: jenkins

    - name: add container to inventory
      add_host:
        name: my_jenkins
        ansible_connection: docker
        ansible_docker_extra_args: "--tlsverify --tlscacert=/path/to/ca.pem --tlscert=/path/to/client-cert.pem --tlskey=/path/to/client-key.pem -H=tcp://myserver.net:4243"
        ansible_user: jenkins
      change_when: false

    - name: create directory for ssh keys
      delegate_to: my_jenkins
      file:
        path: '/var/jenkins_home/.ssh/jupiter'
        state: directory
    ```

    