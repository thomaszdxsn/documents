"""
Decimal()这个构造器还可以接受tuple作为参数：

索引0: 代表符号为(0为正数，1为负数)
索引1: 这是一个嵌套的元祖，代表数字
索引2: 代表正数的指数
"""

import decimal


t = (1, (1, 1), -2)
print('Input   ', t)
print('Decimal ', decimal.Decimal(t))
