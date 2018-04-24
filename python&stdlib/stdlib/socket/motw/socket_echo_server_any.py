"""
很多服务器都有多个网络接口，因此也有多个IP地址.

与其每次输入不同的地址，还可以使用一个特殊的地址，即`INADDR_ANY`。

这个特殊地址可以同时监听所有地址。

虽然socket定义了一个常量INADDR_ANY，也可以用空字符串或者`0.0.0.0`来标示
"""

import socket
import sys


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_address = ('', 10000)
sock.bind(server_address)
print('starting up on {} port {}'.format(*sock.getsockname()))
sock.listen(1)

while True:
    print('waiting for a connection')
    connection, client_address = sock.accept()
    try:
        print('client connected:', client_address)
        while True:
            data = connection.recv(16)
            print('received {!r}'.format(data))
            if data:
                connection.sendall(data)
            else:
                break
    finally:
        connection.close()
