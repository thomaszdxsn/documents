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

pass
