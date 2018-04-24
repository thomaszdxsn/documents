"""
Alarms是一种特殊类型的signal，它是程序要求OS在某个时间通知它的信号。

就像标准库os的官方文档说的一样，它最常见的使用场景是避免在I/O操作或者其它系统
调用中无期限的堵塞。
"""

import signal
import time


def receive_alarm(signum, stack):
    print("Alarm :", time.ctime())


# 2秒以后调用receive_alarm
signal.signal(signal.SIGALRM, receive_alarm)
signal.alarm(2)


print("Before:", time.ctime())
time.sleep(4)
print("After:", time.ctime())
