"""
可以通过协议名称获取它对应的端口号码
"""

import socket


def get_constants(prefix):
    return {
        getattr(socket, n): n
        for n in dir(socket)
        if n.startswith(prefix)
    }

protocols = get_constants('IPPROTO_')
print(protocols)


for name in ['icmp', 'udp', 'tcp']:
    proto_num = socket.getprotobyname(name)
    const_name = protocols[proto_num]
    print('{:>4} -> {:2d} (socket.{:<12} = {:2d}'.format(
        name, proto_num, const_name,
        getattr(socket, const_name)))

