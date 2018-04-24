"""
想要计算一块数据(必须先转换为byte string)的MD5 hash, digest。

首先需要创建一个hash对象，

然后将数据加入到这个对象中，

对后调用`digest()`或者`hexdigest()`
"""
import hashlib

from hashlib_data import lorem


h = hashlib.md5()
h.update(lorem.encode('utf-8'))
print(h.hexdigest())
