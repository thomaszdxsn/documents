# Including and Importing

## Includes vs. Imports

include和import语句语义上非常类似，不过在Ansible中是完全不一样的概念。

- 所有的`import*`语句都会在playbooks被解析的时候被处理
- 所有的`include*`语句只有在执行playbooks的时候才会被处理。

## Importing Playbooks

可以使用这个语句来在一个playbook中引入另一个playbook:

```yaml
---
- import_playbook: databases.yml
- import_playbook: databases.yml
...
```

play和task的执行顺序会按照它们的定义顺序来决定。

## Including and Importing Task Files

下面是一个task文件

```yaml
# common_tasks.py
---
- name: placeholder foo
  command: /bin/foo
- name: placeholder bar
  command: /bin/bar
```

你可以使用`import_tasks`或者`include_tasks`来将这个task文件引入你的主playbook：

```yaml
tasks:
  - import_tasks: common_tasks.yml
  # 或者
  - include_tasks: common_task.yml
```

你可以为import和include传入变量:

```yaml
tasks:
- import_tasks: wordpress.yml wp_user=timmy
- import_tasks: wordpress.yml wp_user=alice
- import_tasks: wordpress.yml wp_user=bob
```

inluce传入变量的方式是：

```yaml
tasks:
- include_tasks: wordpress.yml
  vars:
    wp_user: timmy
    ssh_keys:
    - "{{ lookup('file', 'keys/one.pub') }}"
    - "{{ lookup('file', 'keys/two.pub') }}"
```

include和import可以放在`handlers:`结块下：

```yaml
# more_handlers.yml
---
- name: restart apache
  service: name=apache state=restarted
...
```

你的主playbook文件：

```yaml
---
handlers:
- include_tasks: more_handlers.yml
# 或者
- import_tasks: more_handlers.yml
...
```


