"""
迄今为止，我们的式例都是使用`decimal`模块的默认行为.

不过有些配置是可以覆盖的，比如:维持的精度，怎么执行约数，
错误的处理，等等。

可以使用`context`完成。

context可以用于线程或者local。
"""

import decimal


context = decimal.getcontext()

print("Emax      =", context.Emax)
print("Emin      =", context.Emin)
print("capitals  =", context.capitals)
print("prec      =", context.prec)
print("rounding  =", context.rounding)
print("flags     =")
for f, v in context.flags.items():
    print("  {}: {}".format(f, v))
print("traps     =")
for t, v in context.traps.items():
    print("  {}: {}".format(t, v))
