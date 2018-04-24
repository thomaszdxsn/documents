"""
除了获取IP地址，每个socket address还包含端口号码。

很多应用可以运行在同一个host，监听同一个IP地址，但是一个socket同时间只能使用
一个端口号码。

将IP地址、协议、端口号码组合起来就组成一个唯一的通讯频道标示，确保通过socket
发生的消息到达正确地目的地。

一些端口号码已经预先分配给了指定的协议。
比如: SMTP --> TCP:25
      HTTP --> TCP:80

想要获取网络服务的端口好，需要使用`getservbyname()`这个函数
"""

import socket
from urllib.parse import urlparse

URLS = [
  'http://www.python.org',
  'https://www.mybank.com',
  'ftp://prep.ai.mit.edu',
  'gopher://gopher.micro.umn.edu',
  'smtp://mail.example.com',
  'imap://mail.example.com',
  'imaps://mail.example.com',
  'pop3://pop.example.com',
  'pop3s://pop.example.com',
]

for url in URLS:
    parsed_url = urlparse(url)
    port = socket.getservbyname(parsed_url.scheme)
    print('{:>6} : {}'.format(parsed_url.scheme, port))
