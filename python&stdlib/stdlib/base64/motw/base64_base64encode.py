"""
这个脚本描述了如何将文本转换为base64编码
"""

import base64
import textwrap


with open(__file__, 'r', encoding='utf-8') as input_:
    raw = input_.read()
    initial_data = raw.split('#end_pymotw_header')[1]


byte_string = initial_data.encode('utf-8')
encoded_data = base64.b64encode(byte_string)

num_initial = len(byte_string)

padding = 3 - (num_initial % 3)

print('{} bytes before encoding'.format(num_initial))
print('Expect {} padding bytes'.format(padding))
print('{} bytes after encoding\n'.format(len(encoded_data)))
print(encoded_data)
