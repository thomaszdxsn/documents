"""
除了一般的小数值，Decimal还可以代表特殊值，
包含正数和负数形式的无穷尽，“非数字”(NaN)，以及零
"""

import decimal


for value in ['Infinity', 'NaN', '0']:
    print(decimal.Decimal(value), decimal.Decimal('-' + value))
print()


# 数学形式的无穷尽
print("Infinity + 1:", (decimal.Decimal('Infinity') + 1))
print("-Infinity + 1:", (decimal.Decimal('-Infinity') + 1))

# 打印NaN的对比
print(decimal.Decimal('NaN') == decimal.Decimal('Infinity'))
print(decimal.Decimal('NaN') != decimal.Decimal(1))
