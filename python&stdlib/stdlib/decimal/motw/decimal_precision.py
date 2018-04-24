"""
context的`.prec`属性代表这个Decimal对象维持的精度
"""

import decimal


d = decimal.Decimal('0.123456')

for i in range(1, 5):
    decimal.getcontext().prec = i
    print(i, ':', d, d * 1)


