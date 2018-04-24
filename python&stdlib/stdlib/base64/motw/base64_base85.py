"""
base85编码扩充了字母表，它相比base64，再处理空白符号的时候更加高校

base85在git, mercurial和PDF中的实现都不一样，

Python包含了两种base85的实现:

    - b85encode() 对应Mercurial和Git
    - a85encode() 对应PDF文件格式
"""

import base64


original_data = b'This is the data, in the clear.'
print("Orignal    : {} bytes {!r}".format(
    len(original_data), original_data))

b64_data = base64.b64encode(original_data)
print('b64 Encoded : {} bytes {!r}'.format(
    len(b64_data), b64_data))

b85_data = base64.b85encode(original_data)
print('b85 Encoded : {} bytes {!r}'.format(
    len(b85_data), b85_data))

a85_data = base64.a85encode(original_data)
print('a85 Encoded : {} bytes {!r}'.format(
    len(a85_data), a85_data))
