# Creating Reusable Playbooks

Playbook文件可能越写越大，最终你会想要重用文件以及组织它们。在Ansbile中，可以有三种方式来做这件事：`includes`, `imports`, `roles`.

`includes`和`imports`运行用户可以将一个大型的playbook拆分成一些小文件。

`roles`运行task打包并且可以包含变量，handler，或者其它模块和插件。roles还可以通过Ansible Galaxy来上传分享。

## Dynamic vs. Static

Ansible对于重用内容主要有两种操作模式：动态和静态。

在Ansible2.0中，引入了动态的概念。Ansible2.1引入静态的概念。

如果你使用`import*`任务(`import_playbook`, `import_task`等等)，它是静态的。如果你使用任何`include*`任务(`include_tasks`, `include_rol`等等)，它是动态的。

## Differences Between Static and Dynamic

这两个操作都很简单。

- Ansible在解析Playbook的时候会处理所有引入的static
- 动态包含会在实际运行时处理

当碰到Ansible选项如`tags`，条件语句`when:`时：

- 对于静态引入，父任务的选项将会拷贝到引入的子任务
- 对于动态包含，任务选项只有在动态任务被eval的时候应用，不会拷贝到子任务.

## Tradeoffs and Pitfalls Between Includes and Imports

使用`import`和`incude`各有有事，需要用户自己权衡选择。

使用`include`的最佳地方是在循环体中。在一个循环使用一个include，包含的任务或者roles将会在每次循环都被执行。

但是`include`相比`import`有下面这些限制.

- 存在于动态include的tag不会显示在输出中
- 存在于动态include的task不会显示在输出中
- 你不可以使用`notify`来触发一个handler
- 你不可以使用`--start-at-task`来开始一个任务的执行

使用`import`相比`include`有下面这些限制:

- 上面提到过，循环中不能使用import
- 在对目标文件或者role名称使用变量时，来自inventory的变量不能使用.

