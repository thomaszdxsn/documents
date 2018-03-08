# Roles

Roles是一种自动读取`vars_files`, `tasks`和`handlers`的方式。允许根据role来将内容分株。

## Role Directory Structure

一个项目目录的示例:

```yaml
site.yml
webservers.yml
fooservers.yml
roles/
  commom/
    tasks/
    handlers/
    files/
    templates/
    vars/
    defaults/
    meta/
  webservers/
    tasks/
    defaults/
    meta/
```

Role需要文件放在几个限定的目录中。Role必须包含至少一个这样的目录。

- tasks: 包含这个role执行的主要的task列表
- handlers: 包含handler，它可以被这个role使用或者被其它role使用
- defaults: 这个role的默认变量
- vars: 这个role的其它变量
- files: 这个role可以部署的文件
- templates: 这个role可以部署的模版
- meta: 定义这个role的一些元数据

```yaml
# roles/example/tasks/main.yml
- name: added in 2.4, previouslly you used 'include'
  import_tasks: redhat.yml
  when: ansible_os_platform|lower == 'redhat'
- import_tasks: debian.yml
  when: ansible_os_platform|lower == 'debian'

# roles/example/tasks/redhat.yml
- yum
  name: "httd"
  state: present

# roles/example/tasks/debian.yml
- apt:
  name: "apache2"
  state: present
```

## Using Roles

一般使用role的方法是通过一个paly的`role:`选项来使用：

```yaml
---
- hosts: webservers
  roles:
    - common
    - webservers
...
```

对于每个role'x'，有下面的行为设定：

- 如果`roles/x/tasks/main.yml`存在，列在其中的tasks将会加入到play中。
- 如果`roles/x/handlers/main.yml`存在，列在其中的handlers将会加入到play中。
- 如果`roles/x/vars/main.yml`存在，列在其中的变量将会加入到play中。
- 如果`roles/x/defaults/main.yml`存在，列在其中的变量将会加入到play中.
- 如果`roles/x/meta/main.yml`存在，其中的内容将会加入.

从Ansible2.4开始，你可以在其它的任务中使用`import_role`或者`include_role`:

```yaml
---
- hosts: webservers
  - debug:
     msg: "before we run our role"
  - import_role:
     name: example
  - include_role:
     name: example
  - debug:
     msg: "after we ran our role"
...
```

pass...
