"""
在动态创建Enum的时候，可以为`names`传入一个字典或者二维list，
更加细粒度地控制Enum成员的值
"""

import enum


BugStatus = enum.Enum(
    value='BugStatus',
    names=[
        ('new', 7),
        ('incomlete', 6),
        ('invalid', 5),
        ('wont_fix', 4),
        ('in_progress', 3),
        ('fix_committed', 2),
        ('fix_released', 1)
    ]
)

print("All memebers:")
for status in BugStatus:
    print("{:15} = {}".format(status.name, status.value))
