"""
这个函数生产一个文本，以hexdecimal的形式返回

注意它首先是有token_bytes生成一个n_bytes的随机bytes，
然后转换为hex, 解码为unicode
"""

import secrets


hex_with_16bytes = secrets.token_hex(16)
print(f"hex_with_16bytes: {hex_with_16bytes}")
print("It's length is {}".format(len(hex_with_16bytes)))

hex_with_32bytes = secrets.token_hex()
print(f"hex_with_32bytes: {hex_with_32bytes}")
print("It's length is {}".format(len(hex_with_32bytes)))
