"""
这个函数的后半段名称很熟悉，

没错，它就是调用了`base64.urlsafe_b64encode()`

所以它返回的值是base64编码
"""


import secrets


token_with_16bytes = secrets.token_urlsafe(16)
print(f"token with 16bytes == ${token_with_16bytes}")
print("It's length is {}".format(len(token_with_16bytes)))

token_with_32bytes = secrets.token_urlsafe(32)
print(f"token with 32bytes == ${token_with_32bytes}")
print("It's length is {}".format(len(token_with_32bytes)))
