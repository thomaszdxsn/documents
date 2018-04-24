"""
信号和线程一般不容易混淆，因为只有主线程会收到信号。

下面的例子建立了一个signal handler， 等待一个线程的信号，使用另一个线程来发送信号
"""

import signal
import threading
import os
import time


def signal_handler(num, stack):
    print("Received signal {}"
           " in {}".format(num, threading.currentThread().name))
signal.signal(signal.SIGUSR1, signal_handler)


def wait_for_signal():
    print("Waiting for signal in",
          threading.currentThread().name)
    signal.pause()
print("Done waiting")


# 启动一个线程，它不会收到信号
receiver = threading.Thread(
    target=wait_for_signal,
    name='receiver'
)
receiver.start()
time.sleep(.1)


def send_signal():
    print("Sending signal in", threading.currentThread().name)
    os.kill(os.getpid(), signal.SIGUSR1)


sender = threading.Thread(
    target=send_signal,
    name='sender'
)
sender.start()
sender.join()

# 等待线程接受这个信号(但是永远不会发生)
print("Waiting for ", receiver.name)
signal.alarm(2)
receiver.join()
