# Creating Reusable Playbooks

Playbook文件可能越写越大，最终你会想要重用文件以及组织它们。在Ansbile中，可以有三种方式来做这件事：`includes`, `imports`, `roles`.

`includes`和`imports`运行用户可以将一个大型的playbook拆分成一些小文件。

`roles`运行task打包并且可以包含变量，handler，或者其它模块和插件。roles还可以通过Ansible Galaxy来上传分享。

## Dynamic vs. Static

Ansible对于重用内容主要有两种操作模式：动态和静态。

在Ansible2.0中，引入了动态的概念。Ansible2.1引入静态的概念。

如果你使用`import*`任务(`import_playbook`, `import_task`等等)，它是静态的。如果你使用任何`include*`任务(`include_tasks`, `include_rol`等等)，它是动态的。

## Differences Between Static and Dynamic

pass
