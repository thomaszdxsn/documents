# YAML Syntax

这篇文档主要介绍正确的YAML语法，它是Ansible playbook的表达方式。

我们使用YAML是因为它非常利于人类阅读。另外，多数编程语言都可以处理YAML。

## YAML Basics

对于Ansible来说，几乎每个YAML文件都从一个list开始。list中每个item都是一个键值对，通常叫做“hash”或者“字典”。所以我们需要知道在YAML中怎么编写list和dict。

所有的YAML文件都可以选择开始处写入`---`，结尾处写入`...`。这是YAML格式的一部分，代表文档的开始和结束。

list中的所有成员都有着相同的缩进，并且以`"- "`开头(一个横杆和一个空格):

```yaml
---
# 一组水果的list
fruits:
    - Apple
    - Orange
    - Strawberry
    - Mango
...
```

字典以简单的`key: value`形式(冒号后面通常跟着一个空格)表示:

```yaml
martin:
    name: Martin D'vloper
    job: Developer
    skill: Elite
```

也可以组合得到更复杂的结构，比如一组dict的list:

```yaml
- martin:
    name: Martin D'vloper
    job: Developer
    skills:
        - python
        - perl
        - pascal
- tabitha:
    name: Tabitha Bitumen
    job: Developer
    skills:
        - lisp
        - fortan
        - erlang
```

如果你想的话，list和dict都可以使用缩写形式:

```yaml
---
marin: {name: Martin D'vloper, job: Developer, skill: Elite}
fruits: 
...
```

虽然Ansible用的不多，但是你可以指定布尔值：

```yaml
create_key: yes
needs_agent: no
knows_oop: True
likes_emacs: TRUE
uses_csv: false
```

值可以通过`|`或者`>`符号来跨多行。使用`|`可以包含换行符，使用`>`会忽略换行符.

```yaml
include_newlines: |
            exactly as you see
            will appear these three
            lines of poetry

ignore_newlines: >
            this is really a
            single line of text
            despite appearances
```

让我们将上面的例子组合起来：

```yaml
---
name: Martin D'vloper
job: Developer
skill: Elite
employed: True
foods:
    - Apple
    - Orange
    - Starwberry
    - Mango
languages:
    perl: Elite
    python: Elite
    pascal: Lame
education: |
    4 GCSEs
    3 A-Levels
    BSc in the Internet of Things
```

## Gotchas

虽然YAML对用户友好，下面这种仍然是语法错误:

```yaml
foo: somebody said I should put a colon here: so I did

windows_drive: c:
```

但是下面这种可以:

```yaml
windows_path: c:\windows
```

如果你想保留冒号，可以使用引号：

```yaml
foo: "somebody said I should put a colon here: so I did"

windows_drive: "c:"
```

另外，Ansible使用`{{ var }}`作为变量。如果一个逗号以后的值以`{`开始，YAML会认为它是一个字典，所以必须加上引号：

```yaml
foo: "{{ varaible }}"
```

值要么全引号包裹起来，要么就不用:

```yaml
foo: "{{ variable }}/additional/string/literal"
foo2: "{{ variable }}\\backslashes\\are\\also\\special\\characters"
foo3: "even if it's just a string literal it must all be quoted"
```

下面这种是不合法的:

```yaml
foo: "E:\\path\\"rest\\of\\path
```

布尔值转换很有用。不过如果你只想要字符串值，那么就需要加上引号了：

```yaml
non_boolean: "yes"
other_string: "False"
```

YAML可以把一些字符串转换为浮点数，比如1.0:

```yaml
version: "1.0"
``

