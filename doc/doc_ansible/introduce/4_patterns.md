# Patterns

Ansible的Pattern决定哪些host应该被管理。一般是说与哪些机器进行通信，但是对于Playbook来说，意味着应用某个特定的配置或者IT处理。

一般带pattern的命令是这样的：

```shell
$ ansible <pattern_goes_here> -m <module_name> -a <arguments>
```

比如:

```shell
ansible webservers -m service -a "name=httpd state=restarted"
```

一个pattern通常引用一组group。

使用Ansible，你首先要作的就是让Ansible知道你需要和inventory中的哪个host进行通讯。

下面两个pattern会将inventory中的所有host作为目标:

```shell
all
*
```

也可以通过名称来指定host或者一组host：

```shell
one.example.com
one.example.com:two.example.com
192.0.2.50
192.0.2.*
```

下面的pattern会匹配一个或多个group。Group以`:`号分隔意味着“OR”配置：

```shell
webservers
webservers:dbservers
```

你也可以排出group，例如，下面的pattern选中所有在webservers但是不在phoenix的机器：

```shell
webservers:!phoenix
```

你也可以交集两个group。下面的pattern意味着机器必须位于webservers group和staging group：

```shell
webservers:&staging
```

你可以将上面pattern作一个组合：

```shell
webservers:dbservers:&staging:!phoenix
```

也可以传入变量:

```shell
webservers:!{{excluded}}:&{{required}}
```

可以使用通配符:

```shell
*.example.com
*.com
```

可以同时混合通配符pattern和group：

```shell
one*.com:dbservers
```

可以通过Python的索引语法来选定group的一个子集，比如下面这个gruop:

```ini
[webservers]
cobweb
webbing
weber
```

可以用索引来访问:

```shell
webservers[0]       # == cobweb
webservers[-1]      # == weber
webservers[0:1]     # == webservers[0],webservers[1]
                    # == cobweb,webbing
webservers[1:]      # == webbing,weber
```

pattern以`~`开头可以将它指定为一个正则表达式:

```shell
~(web|db).*\.example\.com
```

