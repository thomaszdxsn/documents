"""
很多web服务都是使用base64编码的二进制digest编码形式代替hexdigest
"""
import base64
import hmac
import hashlib


with open('lorem.txt', 'rb') as f:
    body = f.read()


hash = hmac.new(
    b'secret-shared-key-goes-here',
    body,
    hashlib.sha1
)

digest = hash.digest()
print(base64,encodestring(digest))
