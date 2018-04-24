"""
虽然这个模块叫做base64，
但是它还提供了base85, base32, base16(hex)的编码方式
"""

import base64


original_data = b'This is the data, in the clear.'
print("Original:", original_data)

encoded_data = base64.b32encode(original_data)
print("Encoded :", encoded_data)

decoded_data = base64.b32decode(encoded_data)
print("Decoded :", decoded_data)
