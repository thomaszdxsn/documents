"""
想要忽略一个信号，可以将SIG_IGN作为handler注册。

这个脚本将默认的handler -- SIGINT替换为SIG_IGN，为SIGUSR1注册另一个handler。

然后它使用`signal.pause()`来等待信号接收
"""
import signal
import os
import time


def do_exit(sig, stack):
   raise SystemExit('Exiting')


signal.signal(signal.SIGINT, signal.SIG_IGN)
signal.signal(signal.SIGUSR1, do_exit)

print("My PID:", os.getpid())

signal.pause()

