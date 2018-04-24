"""
在C语言中进行网络编程，ip地址是用struct sockaddr来标示的

想要在Python中把IPv4的地址转换为C的形式，可以使用`inet_aton()`和
`inet_ntoa()`
"""

import binascii
import socket
import struct
import sys


for string_address in ['192.168.1.1', '127.0.0.1']:
    packed = socket.inet_aton(string_address)
    print('Orignal:', string_address)
    print('Packed :', binascii.hexlify(packed))
    print('Unpacked:', socket.inet_ntoa(packed))
    print()
