"""
除了MD5,  还可以使用SHA1算法
"""

import hmac
import hashlib


# 这里的new()接受了三个参数
# 第一个参数是 secret key
# 第二个参数是 initial message
# 第三个参数是hash算法函数
digest_maker = hmac.new(
    b"secret-shared-key-goes-here",
    b"",
    hashlib.sha1
)

with open('hmac_sha.py', 'rb') as f:
    while True:
        block = f.read(1024)
        if not block:
            break
        digest_maker.update(block)


digest = digest_maker.hexdigest()
print(digest)
