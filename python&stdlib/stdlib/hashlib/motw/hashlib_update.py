"""
hash计算器的`update()`方法是可以调用多次的。

每次，digest都会基于额外加入的文本来更新。

使用递增式更新无疑可以更加节省内存。
"""

import hashlib

from hashlib_data import lorem

h = hashlib.md5()
h.update(lorem.encode('utf-8'))
all_at_once = h.hexdigest()


def chunkize(size, text):
    start = 0
    while start < len(text):
        chunk = text[start:start + size]
        yield chunk
        start += size
    return


h = hashlib.md5()
for chunk in chunkize(64, lorem.encode('utf-8')):
    h.update(chunk)
line_by_line = h.hexdigest()

print("All at once :", all_at_once)
print("Line by line:", line_by_line)
print("Same: ", (all_at_once == line_by_line))
