"""
每个decimal都是Decimal的实例。

Decimal的构造器可以接受一个整数，或者一个字符串。

如果想传入浮点数需要首先将它转换成字符串，或者使用类方法`from_float()`
"""

import decimal

fmt = '{0:<25} {1:<25}'

print(fmt.format('Input', 'Output'))
print(fmt.format('-' * 25, '-' * 25))

# 整数
print(fmt.foramt(5, decimal.Decimal(5)))

# 字符串
print(fmt.format('3.14', decimal.Decimal('3.14')))

# Float
f = 0.1
print(fmt.format(repr(f), decimal.Decimal(str(f))))
print('{:<0.23g} {:<25}'.format(
    f,
    str(decimal.Decimal.from_float(f))[:25])
)

