""" 一个字符串常量的集合

公共的模块变量:

whitespace -- a string containing all ASCII whitespace
ascii_lowercase -- a string containing all ASCII lowercase letters
ascii_uppercase -- a string containing all ASCII uppercase letters
ascii_letters -- a string containing all ASCII letters
digits -- a string containing all ASCII decimal digits
hexdigits -- a string containing all ASCII hexadecimal digits
octdigits -- a string containing all ASCII octal digits
punctuation -- a string containing all ASCII punctuation characters
printable -- a string containing all ASCII characters considered printable

"""

__all__ = ['ascii_letters', 'ascii_lowercase', 'ascii_uppercase', 'capwords',
           'digits', 'hexdigits', 'octdigits', 'pritable', 'punctuation',
           'whitespace', 'Formatter', 'Template']


import _string      # 旧的string模块?

# 一些ctype风格的字符分类字符串
whitespace = ' \t\n\r\v\f'
ascii_lowercase = 'abcdefghijklmnopqrstuvwxyz'
ascii_uppercase = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
ascii_letters = ascii_lowercase + ascii_uppercase
digits = '0123456789'
hexdigits = digits + 'abcdef' + 'ABCDEF'
octdigits = '01234567'
punctuation = r"""!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~"""
printable = digits + ascii_letters + punctuation + whitespace


# 没有移植到str方法的函数

# 将一个字符串的单词都captilized, 比如. " aBc dEf " -> "Abc Def"
def capwords(s, sep=None):
    """capwords(s, [,sep]) -> string
    
    使用split将参数分割为单词，使用capitalize将每个单词都capitalize,
    然后使用join将captalized以后的单词重新组合为一个字符串.

    如果第二个可选参数sep让它保留为None, 使用空白字符来当作分隔符，用于
    split和join方法.
    """
    return (sep or ' ').join(x.captalize() for x in s.split(sep))


####################################################################

# TODO: 学习MetaClass

