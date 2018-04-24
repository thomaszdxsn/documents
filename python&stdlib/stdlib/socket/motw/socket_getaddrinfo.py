"""
getattrinfo()这个函数，可以把一个基本的地址转换为一组包含服务信息的tuple
"""

import socket


def get_constants(prefix):
    return {
        getattr(socket, n): n
        for n in dir(socket)
        if n.startswith(prefix)
    }


families = get_constants('AF_')
types = get_constants('SOCK_')
protocols = get_constants('IPPROTO_')


for response in socket.getaddrinfo('www.python.org', 'http'):

    family, socktype, proto, canonname, sockaddr = response

    print('Family       :', families[family])
    print('Type         :', types[socktype])
    print('Protocol     :', protocols[proto])
    print('Canonical name:', canonname)
    print('Socket address:', sockaddr)
    print()
