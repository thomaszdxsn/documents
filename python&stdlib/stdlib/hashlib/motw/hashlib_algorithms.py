"""
这个脚本会列出hashlib模块所有可用的算法
"""

import hashlib


print("Guaranteed:\n{}\n".format(
     ", ".join(sorted(hashlib.algorithms_guaranteed))))
print("Available:\n{}".format(
    ", ".join(sorted(hashlib.algorithms_available))))

