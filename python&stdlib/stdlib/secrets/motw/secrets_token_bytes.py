"""
这个函数调用了`os.urandom()`，根据传入的参数`nbytes: int`，
来返回指定数量的随机bytes。

如果没有传入参数，默认会返回32位
"""


import secrets


rand_bytes_1 = secrets.token_bytes(16)
print(f"rand_bytes_1 == {rand_bytes_1}")
print("it's length is {}".format(len(rand_bytes_1)))

rand_bytes_2 = secrets.token_bytes()
print(f"rand_bytes_2 == {rand_bytes_2}")
print("it's length is {}".format(len(rand_bytes_2)))

