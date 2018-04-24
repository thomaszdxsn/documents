# Socket Programming HOWTO

作者: Gordon McMillan

摘要：

现在到处都在使用Socket，但是它也几乎是最被误解的一项技术了。

这篇文章只是Socket的一篇概括，它不是教程 -- 你仍然需要从实践中学习。

这篇文章没有覆盖socket的方方面面，但是看完以后，你应该有使用socket的足够的背景
知识了。

## Sockets

我只准备讨论`INET`(也就是IPv4) sockets，它是当前使用率99%的一种sockets。

我只准备讨论`STREAM`(也就是TCP) sockets -- 大多数时候你使用STREAM就足够了。

我会试图清楚socket的神秘性，以及一些blocking和非blocking socket的提示。

但是，我会从blocking socket开始谈起。你需要知道blocking是怎样的，才能理解
非blocking。

理解socket的困难指出在于，根据语境的不同，很多概念也有一些偏差。

所以，我们首先需要区分"client" socket -- 它代表会话的一端；以及"server" socket
-- 它更像是一个电话总机的接线员。

客户端应用(比如浏览器），只会使用“client” socket。而web服务器，则会同时使用
"server" socket和"client" socket.

## Creating a Socket

粗略地来说，在你点击连接带你进入这个页面地时候，你的浏览器做了下面地事情：

```python
# 创建一个 INET, STREAMing socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# 连接到一个web服务器地80端口，web服务器最常用地一个端口
s.connect(('www.python.org', 80))
```

在连接完成后，socket`s`可以用来用来对请求页面地文本信息。

同样地一个socket可以读取回复，然后销毁。对，就是销毁。client exchange通常只
用来交换一次。

socket在服务器端发生地事情更复杂一些。

首先，web服务器创建一个"server socket":

```python
# 创建一个INET, STREAMing socket
serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# 将socket绑定到一个公共地host，port
serversocket.bind((socket.gethostname(), 80))
# 将它变为一个server端的socket
serversocket.listen(5)
```

有一些细节需要注意：

- 我们使用了`socket.gethostname()`，所以这个socket可以被外界看到
- 如果我们使用`s.bind(('localhost', 80))`, 或者`s.bind(('127.0.0.1', 80))`，
我们仍然可以创建一个“server socket”， 但是它只能被相同的机器发现并访问。
- `s.bind(('', 80))`，指定这个socket可以被任何其它地址的机器发现并访问。

- 一般数字比较小的端口号都叫做“众所周知”的端口号。如果你只是想实验，应该使用
四位数的端口号。

- `.listen()`说明我们想要入列最多5个连接的socket，剩余地会被拒绝。

现在，我们有了一个“server socket”，监听80端口，我们可以用一个死循环开启
web服务器，一般把这个循环叫做**主循环**:

```python
while True:
    # 从外部接受连接
    (clientsocket, address) = serversocket.accept()
    # 对这个clientsocket做一些事情，我们假设我们又一个线程型的web服务器
    ct = client_thread(clientsocket)
    ct.run()
```

在这个循环中一般可以有三种模式：

1. 分发一个线程来处理`clientsocket`
2. 创建一个新的进程来处理`clientsocket`
3. 重构app，让它使用非堵塞socket，使用`select`，对socket进行多路复用

更详细的细节在之后有介绍，只要明白这几种模式是“server socket”最常见的方式即可.

它不会发送任何数据，它也不会接受任何数据。它只是用来生产"client sockets"。

每个创建的`clientsocket`，都是为了负责连接到我们host：port的client。

一旦我们创建了`clientsocket`，我们就会回去监听更多的连接。

两个client可以相互“交谈” -- 它们使用了动态端口分配，在会话结束后会被回收。

## IPC

如果你需要在一个机器的两个进程间建立快速的IPC，你需要试一下PIPE，或者试试共享内存。

如果你决定使用`AF_INET` sockets, 将“server socket”绑定在'localhost'.在大多数平台
下，这种方式都更加快速。

> `multiprocessing`是集成了跨平台IPC的高级API。

## Using a Socket

首先需要注意的是，浏览器的"client sockets"和web服务器的"client socket"是相等的。

也就是说，这是一个p2p的会话。

在通讯中，有两组动词(verbs)可以使用。你可以使用`send`和`recv`，
或者可以将client socket变形为一个类文件对象，使用`read`或者`write`.

如果你不想关闭一个连接，最简单的方式是使用固定长度的message:

```python
class MySocket:
    
    def __init__(self, sock=None):
        if sock is None:
            self.sock = socket.socket(
                            socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.sock = sock

    def connect(self, host, port):
        self.sock.connect((host, port))

    def mysend(self, msg):
        totalsent = 0
        while totalsent < MSGLEN:
            sent = self.sock.send(msg[totalsent:])
            if sent == 0:
                raise RuntimeError('socket connection broken')
            totalsent = totalsent + sent

    def myreceive(self):
        chunks = []
        bytes_read = 0
        while bytes_read = MSGLEN:
            chunk = self.sock.recv(min(MSGLEN - btytes_read, 2048))
            if chunk == b'':
                raise RuntimeError('socket connection broken')
            chunks.append(chunk)
            bytes_recd = bytes_recd + len(chunk)
        return b''.join(chunks)
```
