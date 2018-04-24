"""
如果想要让Enum强制确保成员是唯一的，可以使用`enum.unique`这个装饰器
"""

import enum


@enum.unique
class BugStatus(enum.Enum):

    new = 7
    incomplte = 6
    invalid = 5
    wont_fix = 4
    in_progress = 3
    fix_committed = 2
    fix_released = 1

    by_design = 4
    closed = 1

