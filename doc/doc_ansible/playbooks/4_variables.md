# Variables

因为自动化的存在，所用可重复的事情都可以很轻松完成。

在同样的系统你可能想要设置一样的行为，或者将它们和其它系统稍微有些区别对待。

另外，一些观察行为或者远程服务器的状态会影响到你如何配置这些系统。

你可能有一个配置文件模版很类似，只有其中的变量有差别。

Ansible中的变量就是用来处理不同系统的。

要理解变量你首先要理解条件和循环。一些有用的模块，比如`group_by`使用`when`条件来使用变量，可以用来管理不同系统之间的差别。

高度推荐你去`ansible-examples`这个github仓库看一下变量的使用例子。

## What Makes A Valid Varialbe Name

在开始使用变量之前，你需要知道怎样才是一个合法的变量名。

变量名应该是字母，数组和下划线组成。变量名应该总是以字母开始。

`foo_part`是一个合法的变量名，`foo5`也是。

`foo-port`,`foo port`和`12`都不是合法的变量名。

YAML支持字典来映射键和值:

```yaml
foo:
  field1: one
  field2: two
```

你可以只用方括号或者点式记号法来引用一个指定的字段:

```yaml
foo['field1']
foo.field1
```

## Variable Defined in Inventory

有时你像根据机器所在的分组来定义变量。可以通过在inventory定义变量来实现。

## Variable Defined in a Playbook

在一个playbook，可以直接定义变量:

```yaml
- hosts: webservers
    vars:
        http_port: 80
```

## Variable defined from included files and roles

变量可以通过其它文件，通过include来引入。

## Using Variables: About Jinja2

现在我们已经知道怎么定义变量了，那么如何使用变量呢？

Ansible允许你在playbooks中使用Jinja2模版系统来使用变量。你可以在Jinja中作一些
很复杂的事情。

例如，一个简单的模版，你可以这样作:

`my amp goes to {{ max_amp_value }}`

这也是变量最直接的使用方式。

在playbooks中的示例:

`template: src=foo.cfg dest{{ remote_instance_path }}/foo.cfg`

## Jinja2 Filters

Jinja2的filter可以理解为是某种形式的函数。Jinja2内置了很多种filter。

## Hey Wait, A YAML Gotcha

YAML语法要求，如果你的一个值以`{{ foo }}`的形式开始，你必须把整行都加上引号，
因为YAML需要确认你不是在输入一个字典。

下面这个写法是错误的：

```yaml
- hosts: app_servers
    vars:
        app_path: {{ base_path }}/22
```

你必须这么作:

```yaml
- hosts: app_servers
    vars:
        app_path: "{{ base_path }}/22"
```

## Information disconvered from systems: Facts

还有一些其它地方可以放置变量，但是这种类型的变量是发现得来的，不是用户定义的。

Fact是你的远程机器的一些信息。

比如机器的ip地址，或者操作系统。

想要看看这些信息，可以试一下下面这个命令:

`ansible hostname -m setup`

这个命令会返回很多变量数据。

我们可以用下面这个变量来代表第一个硬件的model:

`{{ ansbile_devices.sda.model }}`

同样的，系统的hostname可以这样引用

`{{ ansible_nodename }}`

Facts一般用于条件性情况。

Facts还可以用来创建host的动态分组。

## Turning Off Facts

如果你知道你不需要fact数据，知道你的系统的一切信息，你可以关闭fact收集。
这可以增进Ansible的性能。

```yaml
- hosts: whatever
  gather_facts: no
```

## Local Facts(Facts.d)

在playbooks章节中有过讨论，Ansible的facts是一种获得远程系统数据的方式，
可以用来当作playbook的变量。

通常，fact会使用Ansible的`setup`模块自动获取。用户也可以编写自定义facts模块，
这在API Guide中有描述。不过，如果你想有一个简单的方式获取系统信息，何必写
一个fact模块呢。

例如，如果你想要控制系统被管理的某些方面，可以使用"Facts.d".

如果一个远程被管理系统有一个`/etc/ansible/facts.d`目录，这个目录下的任何文件
都会以`.fact`结尾，可以是JSON，INI或者其它文件格式。

例如假设有一个`/etc/ansible/facts.d/preferences.fact`:

```ini
[general]
asdf=1
bar=2
```

这将会生成一个hash变量，名叫`general`，`asdf`和`bar`都是它的元素。你可以验证一下:

`ansible <hostname> -m setup -a "filter=ansbile_local"`

你可以看到下面这些fact输出:

```json
"ansible_local": {
        "preferences": {
            "general": {
                "asdf" : "1",
                "bar"  : "2"
            }
        }
 }
```

这些数据可以在`template/playbook`中访问:

```txt
{{ ansible_local.preferences.general.asdf }}
```

## Ansible version

想要让playbook符合特定ansible的版本，可以使用ansible_version变量:

```json
"ansible_version": {
    "full": "2.0.0.2",
    "major": 2,
    "minor": 0,
    "revision": 0,
    "string": "2.0.0.2"
}
```

## Fact Caching

一个server可以引用另一个server的变量：

`{{ hostvars['asdf.example.com']['ansible_os_family'] }}`


