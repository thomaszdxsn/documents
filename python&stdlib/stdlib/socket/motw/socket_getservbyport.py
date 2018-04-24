"""
当然，也可以通过端口号倒推服务名称
"""
import socket
from urllib.parse import urlunparse


for port in [80, 443, 21, 70, 25, 143, 993, 110, 995]:
    url = '{}://example.com/'.format(socket.getservbyport(port))
    print(url)
