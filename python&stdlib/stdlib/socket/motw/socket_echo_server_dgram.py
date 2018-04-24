"""
UDP是一个以消息为导向的协议。

UDP不要求长连接，所以设定UDP socket很简单。

另一方面，UDP的消息必须包含在一个datagram中(在IPv4，一个电报可卡因包含65507bytes,
另外65535-65507bytes用来存储头部信息。

UDP并不保证消息能够传输。

因为没有连接，所以server也就不需要监听连接。

在socket模块中，只需要使用`bind()`来绑定到一个单独的端口就好
"""

import socket
import sys


# 创建一个UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# 将socket绑定到端口
server_address = ('localhost', 10000)
print('starting up on {} port {}'.format(*server_address))
sock.bind(server_address)

while True:
    print('\nwaiting to receiving message')
    data, address = sock.recvfrom(4096)

    print('received {} bytes from {}'.format(len(data), address))
    print(data)

    if data:
        sent = sock.sendto(data, address)
        print('sent {} bytes back to {}'.format(sock, address))
