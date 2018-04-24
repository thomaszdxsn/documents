"""
TCP/IP的客户端可以通过`create_connection()`节省一些连接服务器的步骤。

这个函数接受一个参数，一个代表服务器地址的元祖
"""
import socket
import sys


def get_constants(prefix):
    return {
        getattr(socket, n): n
        for n in dir(socket)
        if n.startswith(prefix)
    }


families = get_constants("AF_")
types = get_constants("SOCK_")
protocols = get_constants("IPPROTO_")

# 创建一个TCP/IP的socket
# create_connection使用getaddrinfo()来找到适合的connection参数，
# 返回它首次连接的一个socket
sock = socket.create_connection(('localhost', 10000))

# family, type, protocol可以用来检查连接的状态
print('Family    :', families[sock.family])
print('Type      :', types[sock.type])
print('Protocol  :', protocols[sock.proto])
print()

try:
    message = b'This is the message. It will be repeated.'
    print('sending {!r}'.format(message))
    sock.sendall(message)

    amount_received = 0
    amount_expected = len(message)

    while amount_received < amount_expected:
        data = sock.recv(16)
        amount_received += len(data)
        print('received {!r}'.format(data))

finally:
    print('closing socket')
    sock.close()

