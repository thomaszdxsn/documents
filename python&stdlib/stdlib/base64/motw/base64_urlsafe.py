"""
因为默认的base64字母表可能包含+和/，这两个字符是可以出现在URL中的,
所以有必要在转码的时候对这两个字符进行特殊处理，
让生成的base64字符不要和这两个字符相冲突
"""

import base64

encodes_with_pluses = b'\xfb\xef'
encodes_with_slashes = b'\xff\xff'


for original in [encodes_with_pluses, encodes_with_slashes]:
    print("Orignal              :", repr(original))
    print("Standard encoding    :",
          base64.standard_b64encode(original))
    print("URl-safe encoding    :",
          base64.urlsafe_b64encode(original))
    print()
