"""
继承`IntEnum`可以让枚举元素像数字一样 -- 例如，可以支持比对
"""
import enum


class BugStatus(enum.IntEnum):

    new = 7
    incomplete = 6
    invalid = 5
    wont_fix = 4
    in_progress = 3
    fix_committed = 2
    fix_released = 1


print("Ordered by value:")
print("\n".join(" " + s.name for s in sorted(BugStatus)))
