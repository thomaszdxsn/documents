"""
new()函数创建一个新的对象，用来计算一个消息的签名。

这个脚本使用默认的MD5 hash算法
"""

import hmac


digest_maker = hmac.new(b'secret-shared-key-goes-here')

with open('hmac_simple.py', 'rb') as f:
    while True:
        block = f.read(1024)
        if not block:
            break
        digest_maker.update(block)

digest = digest_maker.hexdigest()
print(digest)
