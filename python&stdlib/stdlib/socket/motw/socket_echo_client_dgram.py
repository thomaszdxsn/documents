"""
UDP的echo 客户端和服务器端很像。

只不过不需要使用`bind()`

它使用`sendto()`来递送它的消息，使用`recvfrom()`来接受消息
"""

import socket
import sys


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server_address = ('localhost', 10000)
message = b'This is the message. It will be repeated.'

try:
    print("sending {!r}".format(message))
    sent = sock.sendto(message, server_address)

    print('waiting to receive')
    data, server = sock.recvfrom(4096)
    print('received {!r}'.format(data))
finally:
    print('closing socket')
    sock.close()
