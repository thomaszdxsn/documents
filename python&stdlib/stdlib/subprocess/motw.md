# subprocess -- Spawning Additional Processes

**用途：开启一个额外的进程，并和它通信**

`subprocess`模块提供三个API，可以用于操作进程。

`run()`函数，在Python3.5加入，是一个高级别的API，可以用来运行一个进程并且收集
它的输出。

函数`call()`， `check_call()`和`check_output()`都是之前的Python2以来的高级API。
仍然会支持这些API，因为它们已经广泛用于现存的程序/项目里。

类`Popen`是一个低级的API，用于构建其它的(更高级的)API，并可以用于复杂的进程交互。

`Popen`的构造器接受参数用来构建新的进程，所以父进程可以使用管道和它通讯。这个类
提供了进程交互的完整功能。

`subprocess`是作为`os.system()`, `os.spawnv()`以及`os.popen()`，`popen2`模块和
`commands()`模块的替代品而产生的。`subprocess`相比其它所有的模块都更加简单。

> 运行在Unix和Windows的API大致相同，但是底层的实现是不同的，因为操作系统的进程
模型是有区别的。下面的所有例子都经过了Mac OS X的测试。

## Running External Command

### `subprocess_os_system.py`

想要运行一个外部的命令，就像使用`os.system()`的功能一样。你可以使用`run`函数.

```python
# subprocess_os_system.py

import subprocess

completed = subprocess.run(['ls', '-l'])
print('returncode:', completed.returncode])
```

命令行参数是以字符串list的形式传入的，可以避免引号的转义以及shell上面特殊字符的
干扰。`run()`会返回一个`CompletedProcess`实例，包含进程的信息，比如退出码，进程
的输出。

```shell
$ python3 subprocess_os_system.py

index.rst
interaction.py
repeater.py
signal_child.py
signal_parent.py
subprocess_check_output_error_trap_output.py
subprocess_os_system.py
subprocess_pipes.py
subprocess_popen2.py
subprocess_popen3.py
subprocess_popen4.py
subprocess_popen_read.py
subprocess_popen_write.py
subprocess_run_check.py
subprocess_run_output.py
subprocess_run_output_error.py
subprocess_run_output_error_suppress.py
subprocess_run_output_error_trap.py
subprocess_shell_variables.py
subprocess_signal_parent_shell.py
subprocess_signal_setpgrp.py
returncode: 0
```

### `subprocess_shell_variables.py`

设置`shell`关键字参数为`True`，可以让`subprocess`开启一个中间的shell进程来运行
命令。默认情况下是直接运行命令的。

```python
$ subprocess_shell_variables.py

import subprocess

completed = subprocess.run('echo $HOME', shell=True)
print('returncode:', completed.returncode)
```

运行中间的shell进程意味着环境变量，glob模式，以及其它的命令行特性都可以使用了.

```shell
$ python3 subprocess_shell_variables.py

/Users/dhellmann
returncode: 0
```

> 执行`run()`但是没有传入`check=True`，等同于调用`call()`，它只会返回进程的退出码。

## Error Handling

`CompletedProcess`的returncode属性代表程序的退出码。

调用者需要负责截取错误。如果为`run()`传入`check=True`，退出码会被检查，如果
退出码代表一个错误，将会抛出`CalledProcessError`异常。

### `subprocess_run_check.py`

```python
# subprocess_run_check.py

import subprocess

try:
    subprocess.run(['false'], check=True)
except subprocess.CalledProcessError as err:
    print('ERROR:', error)
```

`false`命令总是会返回一个非0的退出码，`run()`会把它看作是一个错误。

```shell
$ python3 subprocess_run_check.py

ERROR: Command '['false']' returned non-zero exit status 1
```

> `run(..., check=True)`等同于`check_call()`.

## Capturing Output

在运行`run()`的时候这个进程的标准输入和标准输出就会绑定父进程的标准输入和输出。

这意味着调用程序的时候并不会补货命令的输出。

### `subprocess_run_output.py`

可以为`stdout`和`stdin`传入一个`PIPE`对象，可以捕获命令的输出供之后处理。

```python
# subprocess_run_output.py

import subprocess

completed = subprocess.run(
    ['ls', '-l'],
    stdout=subprocess.PIPE,
)
print('returncode:', completed.returncode)
print('Have {} bytes in stdout:\n{}'.format(
    len(completed.stdout),
    completed.stdout.decode('utf-8'))
)
```

`ls -l`命令成功运行，所以它打印的输出可以被补货并返回。

```shell
$ python3 subprocess_run_output.py

returncode: 0
Have 522 bytes in stdout:
index.rst
interaction.py
repeater.py
signal_child.py
signal_parent.py
subprocess_check_output_error_trap_output.py
subprocess_os_system.py
subprocess_pipes.py
subprocess_popen2.py
subprocess_popen3.py
subprocess_popen4.py
subprocess_popen_read.py
subprocess_popen_write.py
subprocess_run_check.py
subprocess_run_output.py
subprocess_run_output_error.py
subprocess_run_output_error_suppress.py
subprocess_run_output_error_trap.py
subprocess_shell_variables.py
subprocess_signal_parent_shell.py
subprocess_signal_setpgrp.py
```

> 调用`run()`并传入`check=True`以及`stdout=PIPE`，等同于调用`check_output()`.

### `subprocess_run_output_error.py`

下面这个例子在子shell中运行一系列命令。在命令退出之前消息就会被发送到标准输出和标准错误中。

```python
# import subprocess

try:
    completed = subprocess.run(
        'echo to stdout; echo to stderr 1>&2; exit1',
        check=True,
        shell=True,
        stdout=subprocess.PIPE
    )
except subprocess.CalledProcessError as err:
    print('ERROR', err)
else:
    print('returncode:', completed.returncode)
    print('Have {} byte in stdout {!r}'.format(
        len(completed.stdout),
        completed.stdout.decode('utf-8'))
    )
```

标准错误的消息会被打印，但是标准输出的消息被隐藏了:

```shell
$ python3 subprocess_run_output_error.py

to stderr
ERROR: Command 'echo to stdout; echo to stderr 1>&2; exit 1'
return non-zero exit status 1
```

### `subprocess_run_output_error_trap.py`

为了避免将标准错误打印到控制台，可以设置参数`stderr=PIPE`.

```python
# subprocess_run_output.py

import subprocess

try:
    completed = subprocess.run(
        'echo tot stdout; echo to stderr 1>&2; exit 1',
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
except subprocess.CalledProcessError as err:
    print("ERROR:", err)
else:
    print("returncode:", completed.returncode)
    print("Have {} bytes in stdout: {!r}".format(
        len(completed.stdout),
        completed.stdout.decode('utf-8'))
    )
    print('Have {} bytes in stderr: {!r}'.format(
        len(completed.stderr),
        completed.stderr.decode('utf-8'))
    )
```

这个例子没有设置`check=True`，所以命令的输出会同时被捕获和打印。

```shell
$ python subprocess_run_output_error_trap.py

returncode: 1
Have 10 bytes in stdout: 'to stdout\n'
Have 10 bytes in stderr: 'to stderr\n'
```

### `subproces_run_output_error_trap_output.py`

想要在使用`check_output()`的时候补货错误消息，可以将`stderr=STDOUT`，这个错误
详细将会合并到命令的输出中。

```python
# subprocess_check_output_error_trap_output.py
import subprocess

try:
    output = subprocess.check_output(
        'echo to stdout; echo to stderr 1>&2',
        shell=True,
        stderr=subprocess.STDOUT,
    )
except subprocess.CalledProcessError as err:
    print('ERROR:', err)
else:
    print('Have {} bytes in output: {!r}'.format(
        len(output),
        output.decode('utf-8'))
    )
```

输出的顺序可能和下面不一样，这是因为数据打印的顺序取决于标准输出流的缓冲空间。

```shell
$ python3 subprocess_check_output_error_trap_output.py

Have 20 bytes in output: 'to stdout\nto stderr\n'
```

## Suppressing Output

有些时候不需要看到输出，可以是将输出流导入`DEVNULL`.

### `subprocess_run_output_error_suppress.py`

```python
import subprocess

try:
    completed = subprocess.run(
        'echo to stdout; echo to stderr 1>&2; exit 1',
        shell=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
except subprocess.CalledProcessError as err:
    print('ERROR:', err)
else:
    print('returncode:', completed.returncode)
    print('stdout is {!r}'.format(completed.stdout))
    print('stderr is {!r}'.format(completed.stderr))
```

DEVNULL这个名称来自于Unix的一个特殊的设备文件，`/dev/null`，可以将它理解为一个
黑洞文件。

```shell
$ python3 subprocess_run_output_error_suppress.py

returncode: 1
stdout is None
stderr is None
```

## Working with Pipes Directly

函数`run()`，`call()`，`check_call()`和`check_output()`都是`Popen`类的封装。

直接使用`Popen`可以更加细地控制命令的运行，以及控制输入和输出流是如何处理的。

例如，通过为`stdin`, `stdout`和`stderr`传入不同的参数，可以用来模仿`os.popen()`
的不同变种。

### One-way Communication With a Process

#### `subprocess_popen_read.py`

想要运行一个进程并且完整地读取它的输出，可以设置`stdout`的值为`PIPE`，然后调用
`communicate()`.

```python
# subprocess_popen_read.py
import subprocess

print('read:')
proc = subprocess.Popen(
    ['echo', '"to stdout"'],
    stdout=subprocess.PIPE,
)
stdout_value = proc.communicate()[0].decode('utf-8')
print('stdout:', repr(stdout_value))
```

这个方式和`popen()`一样，除了读取操作是由`Popen`实例进行管理。

```shell
$ python3 subprocess_popen_read.py

read:
stdout: '"to stdout"\n'
```



