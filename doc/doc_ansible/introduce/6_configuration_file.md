# Configuration file

Ansible的一些settings是通过配置文件来调整的。默认的配置应该足够大多数用户，但是有时你也会想要修改一下。

配置文件解析通过下面的顺序决定：

```
* ANSIBLE_CONFIG (一个环境变量)
* ansible.cfg(当前目录的配置文件)
* .ansible.cfg(home目录下的配置文件)
* /etc/ansible/ansible.cfg
```

文件的setting不会合并。

> 配置文件中的`#`和`;`都是注释标记。

## Getting the latest configuration

如果ansible是通过包管理器下载的，最新的`ansible.cfg`应该在`/etc/ansible`.

如果你通过pip安装或者源码安装，你可以手动创建这个文件来覆盖默认配置。

你可以[在线](https://raw.github.com/ansible/ansible/devel/examples/ansible.cfg)看到所有的最新配置。

## Environment configuration

Ansible支持通过环境变量来配置。如果设置了环境变量，它们会是最高解析优先级。这些变量定义在[`constants.py`](https://github.com/ansible/ansible/blob/devel/lib/ansible/constants.py)

## Explanation of values by section

配置文件可以划分不同的区块。最常用的是"general".

### General defaults

在`[defaults]`块中，下面的这些变量可以设置

#### action_plugins

Action是ansible的一块代码，它可以决定模块执行，模版等等。

这是一个开发者使用的特性，允许Ansible从不同的地方读取一些底层扩展。

`action_plugins = ~/.ansible/plugins/action_plugins/:/usr/share/ansible_plugins/action_plugins`

#### allow_unsafe_lookups

在激活后，这个选项会允许查询插件返回的数据不会标记为"unsafe"。默认情况下，这些数据会被标记为不安全来语法模版引擎的eval，这可能会造成安全隐患。

这个选项主要是为了向后兼容性问题而存在的，用户应该优先考虑在使用模版的时候加入`allow_unsafe=True`:

`{{lookup('pipe', '/path/to/some/command', allow_unsafe=True)}}`

#### allow_world_readable_tmpfiles

如果机器创建了一个临时文件没有设置任何权限，这个配置可以让这个临时文件成功创建。

`allow_world_readable_tmpfiles=True`

#### ansible_managed

`ansible_managed`字符串可以插入由Ansible模版系统写的文件中：

`{{ ansible_managed }}`

默认值代表Ansible管理一个文件：

`ansible_managed = Ansible managed`

...

#### ask_pass

这个选项用来控制Ansible playbook是否会弹出提示界面让用户输入密码。默认为否：

`ask_pass = False`

如果使用SSH key来访问，不需要修改这个配置。

#### ask_sudo_pass

和*ask_pass*类似.

#### ask_vault_pass

控制Ansible playbook是否应该提示用户输入vault密码。默认为否:

`ask_vault_pass = False`

#### bin_ansible_callbacks

控制是否在运行`/usr/bin/ansible`的时候读取callback插件。可以用它来记录命令行日志，发送通知等等。如果使用`/usr/bin/ansible-playbook`，那么总是会读取callback插件:

`bin_ansible_callbacks = False`

#### callback_plugins

callback是一段代码，在一些特定的事件后被调用，允许用来触发通知。

`callback_plugins = ~/.ansible/plugins/callback:/usr/share/ansible/plugins/callback`

#### callback_whitelist

Ansible现在内置了很多的callback。这个setting允许你激活一些额外的callback：

`callback_whitelist = timer,mail`

#### command_warnings

从Ansible1.8开始，如果一个命令和某个ansible模块很像，ansible会发出警告。这个选项用来控制是否发出警告：

`command_warnings = True`

#### connection_plugins

connection plugins允许用来扩展ansible现在的连接方式。

`connection_plugins = ~/.ansible/plugins/connection_plugins/:/usr/share/ansible_plugins/connection_plugins`

#### deprecation_warnings

这个选项用来控制在碰到启用的命令/模块时是否发出弃用警告：

`deprecation_warnings = True`

#### display_args_to_stdout

默认情况下，ansible-playbook会打印每个任务的header到stdout上面。header一般包括你指定的name等字段。如果这个选项设置为True，也会打印任务的参数。

这个setting默认为False，因为参数中很可能有敏感信息:

`display_args_to_stdout = False`

#### display_skipped_hosts

如果设置为False，ansible不会显示已跳过的任务的状态。默认是True。

`display_skipped_hosts = True`

#### error_on_undefined_vars

在碰到未定义变量是会报错

`error_on_undefined_vars = True`

如果设置为False，{{ template_expression }}如果包含未定义变量则直接将它打印到模版。

#### executable

这个选项指定命令使用的shell。一般不需要改动：

`executable = /bin/bash`

#### filter_plugins

Filter是模版系统可以使用的类函数对象。

`filter_plugins = ~/.ansible/plugins/filter_plugins/:/usr/share/ansible_plugins/filter_plugins`

#### force_color

这个选项会强制开启颜色模式，即使不是在TTY也会：

`force_color = 1`

#### force_handlers

这个选项可以让host运行一个通知handler，即使host发生错误也一样：

`force_handlers = True`

#### forks

这个配置可以设置在与远程host通讯时的最大并行数量。从Ansible1.3开始，fork数量自动限制为可能运行的host数量，所以你只需要担心你的机器可以承载多大的网络和CPU开销。默认值很保守:

`forks = 5`

#### fact_caching

这个配置可以让你使用fact缓存。

目前可以使用redis和jsonfile两种缓存.

`fact_caching = jsonfile`

#### fact_caching_connection

对于jsonfile，需要指定存放路径。对于redis，需要指定`host:port:database`:

`fact_caching_connection = localhost:6379:0`

#### fact_caching_timeout

fact缓存超时时间

`fact_caching_timeout = 86400`

#### fact_path

...

#### gathering

...

#### hash_behavior

...

#### hostfile

...已经弃用

#### host_key_checking

是否检查host key.

#### internal_poll_interval

Ansible内部进程的poll间隔(秒)。

`internal_poll_interval=0.001`

#### inventory

`inventory = /etc/ansible/hosts`

#### inventory_ignore_extensions

`inventory_ignore_extensions = ~, .orig, .bak, .ini, .cfg, .retry, .pyc, .pyo`

#### jinja2_extendsions

`jinja2_extensions = jinja2.ext.do,jinja2.ext.i18n`

#### library

`library = /usr/share/ansible`

#### local_tmp

...

#### log_path

`log_path=/var/log/ansible.log`

#### lookup_plugin

...

#### mege_multiple_cli_tags

...

#### module_lang

...

#### module_name

默认使用的module.

`module_name = command`

#### module_set_locale

...

#### module_utils

...

#### nocolor

...

#### nocows

...

#### pattern

...

#### poll_interval

...

#### private_key_file

指定一个默认的秘钥.

#### remote_port

默认的ssh端口，默认为22.

#### remote_tmp

...

#### remote_user

...

#### retry_files_enabled

...

#### retry_files_save_path

...

#### roles_path

...

#### squash_actions

...

#### stdout_callback

...

#### strategy_plugins

...

#### strategy

...

#### sudo_exe

...

#### sudo_flags

...

#### sudo_user

...

#### system_warnings

...

#### timeout

默认的ssh超时时间

#### transport

...

#### vars_plugins

...

#### vault_password_file

...


pass...




