"""
getaddrinfo()还可以接受额外的参数，用来过滤最后的结果

host, port是必须的参数。

可选的参数包括family, proto和flags。可选参数必须是socket模块的常量
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

responses = socket.getaddrinfo(
    host='www.python.com',
    port='http',        # http会自动转换为80
    family=socket.AF_INET,
    type=socket.SOCK_STREAM,
    proto=socket.IPPROTO_TCP,
    flags=socket.AI_CANONNAME,
)

for response in responses:
    family, socktype, proto, canonname, sockaddr = response

    print('Family       :', families[family])
    print('Type         :', types[socktype])
    print('Protocol     :', protocols[proto])
    print('Canonical name:', canonname)
    print('Socket address:', sockaddr)
    print()



