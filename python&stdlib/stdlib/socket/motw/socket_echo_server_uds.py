"""
在程序员的角度来开，Unix domain socket和TCP/IP的socket有两个主要的区别：

1. socket的地址是文件系统的路径，而不是一个包含host, port的元祖
2. socket创建的节点文件在socket被关闭后仍然存在，需要在每次服务器启动的时候
作清理。
"""
import socket
import sys
import os


server_address = './uds_socket'

# 首先要确保socket不存在
try:
    os.unlink(server_address)
except OSError:
    if os.path.exists(server_address):
        raise


# 创建一个UDS Socket
sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

# 将socket绑定到地址上面
print("Starting up on {}".format(server_address))
sock.bind(server_address)

sock.listen(1)

while True:
    print('Waiting for a connection')
    connection, client_address = sock.accept()

    try:
        print('connection from ', client_address)
        while True:
            data = connection.recv(16)
            if data:
                print('received {!r}'.format(data))
                connection.sendall(data)
            else:
                print('no data from ', client_address)
                break
    finally:
        connection.close()
