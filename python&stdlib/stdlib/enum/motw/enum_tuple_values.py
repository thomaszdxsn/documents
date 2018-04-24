"""
Enum成员的值并没有限制必须是整数。

事实上，任何类型的对象都可以关联一个enum对象。

如果值是一个元祖，这个成员将会作为一个整体参数传入给`__init__()`.
"""

import enum


class BugStatus(enum.Enum):

    new = (7, ['incomplete',
               'invalid',
               'wont_fix',
               'in_progress'])
    incomplete = (6, ['new', 'wont_fix'])
    invalid = (5, ['new'])
    wont_fix = (4, ['new'])
    in_progress = (3, ['new', 'fix_committed'])
    fix_commited = (2, ['in_progress', 'fix_released'])
    fix_released = (1, ['new'])

    def __init__(self, num, transitions):
        self.num = num
        self.transitions = transitions

    def can_transition(self, new_state):
        return new_state.name in self.transitions


print("Name:", BugStatus.in_progress)
print("Value:", BugStatus.in_progress.value)
print("Custom attribute:", BugStatus.in_progress.transitions)
print("Using attribute:", BugStatus.in_progress.can_transition(BugStatus.new))
