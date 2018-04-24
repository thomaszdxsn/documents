# signal -- Asynchronous System Events

*用途: 异步的系统事件*

Signal是操作系统的一个特性，它能提供一个方法用来通知程序有事件发生，并且能够
通过异步处理。

Signal可以由系统自身生成，或者由其它进程发送。

因为signal会打断程序的正常运行流程，所以在进行一些操作的时候如果收到信号可能
会导致错误(尤其是I/O操作)。

Signal由整数来标示，它定义在操作系统的C头文件中。

Python在`signal`模块中暴露了这些系统信号的符号。例如本章使用的`SIGINT`和`SIGUSR1`。
它们在所有的Unix和类Unix系统中都有定义。

## Receiving Signals

和其它事件驱动编程模式一样，signal也是基于回调函数来建立的，这个回调函数叫做
`signal handler`。signal handler的参数是signal数字以及被signal打断的程序的当前栈帧(stack frame)。

### signal_signal.py

```python
# signal_signal.py

import signal
import os
import time


def receive_signal(signum, stack):
    print('Received:', signum)


signal.signal(signal.SIGUSR1, receive_signal)
signal.signal(signal.SIGUSR2, receive_signal)

print('My PID is:': os.getpid())

while True:
    print('Waiting...')
    time.sleep(3)
```

上面的脚本运行了一个死循环，每次会暂停若干秒。

在收到一个signal的时候，会打断`sleep()`，通过`receive_signal`来打印signal数字。
在signal handler返回之后，循环继续运行。

可以通过`os.kill()`或者Unix命令kill来发送signal:

```shell
$ python3 signal_signal.py

My PID is: 71387
Waiting...
Waiting...
Waiting...
Received: 30
Waiting...
Waiting...
Received: 31
Waiting...
Waiting...
Traceback (most recent call last):
  File "signal_signal.py", line 28, in <module>
    time.sleep(3)
KeyboardInterrupt
```

上面是一个窗口运行了`signal_signal.py`的输出，另一个窗口运行了如下命令:

```shell
$ kill -USR1 $pid
$ kill -USR2 $pid
$ kill -INT $pid
```

## Retrieving Registered Handlers

想要看一个signal注册了哪些handler，可以使用`getsignal()`，将signal number作为参数传入。

返回的值就是已经注册的handler，或者返回一些特殊值: `SIG_IGN`(应该忽略的信号)，
`SIG_DFL`(默认行为的信号)，`None`(信号handler已经通过C注册过了，而不是通过Python)。

### signal_getsignal.py

```python
# signal_getsignal.py

import signal


def alarm_received(n, stack):
    return

signal.signal(signal.SIGALRM, alarm_received)

signals_to_namse = {
    getattr(signal, n): n,
    for n in dir(signal)
    if n.startswith('SIG') and '_' not in n
}

for s, name in sorted(signals_to_names.items()):
    handler = signal.getsignal(s)
    if handler is signal.SIG_DFL:
        handler = 'SIG_DFL'
    elif handler is signal.SIG_IGN:
        handler = 'SIG_IGN'
    print(f"{name:<10} ({s:2d})", handler)
```

由于每个操作系统都可能有不同的信号定义，所以输出可能也不一样。

下面是OS X的输出:

```shell
$ python3 signal_getsignal.py

SIGHUP     ( 1): SIG_DFL
SIGINT     ( 2): <built-in function default_int_handler>
SIGQUIT    ( 3): SIG_DFL
SIGILL     ( 4): SIG_DFL
SIGTRAP    ( 5): SIG_DFL
SIGIOT     ( 6): SIG_DFL
SIGEMT     ( 7): SIG_DFL
SIGFPE     ( 8): SIG_DFL
SIGKILL    ( 9): None
SIGBUS     (10): SIG_DFL
SIGSEGV    (11): SIG_DFL
SIGSYS     (12): SIG_DFL
SIGPIPE    (13): SIG_IGN
SIGALRM    (14): <function alarm_received at 0x1019a6a60>
SIGTERM    (15): SIG_DFL
SIGURG     (16): SIG_DFL
SIGSTOP    (17): None
SIGTSTP    (18): SIG_DFL
SIGCONT    (19): SIG_DFL
SIGCHLD    (20): SIG_DFL
SIGTTIN    (21): SIG_DFL
SIGTTOU    (22): SIG_DFL
SIGIO      (23): SIG_DFL
SIGXCPU    (24): SIG_DFL
SIGXFSZ    (25): SIG_IGN
SIGVTALRM  (26): SIG_DFL
SIGPROF    (27): SIG_DFL
SIGWINCH   (28): SIG_DFL
SIGINFO    (29): SIG_DFL
SIGUSR1    (30): SIG_DFL
SIGUSR2    (31): SIG_DFL
```


