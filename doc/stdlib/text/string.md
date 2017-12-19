[TOC]

## 官网文档: string -- 普通的字符串操作

### 字符串常量

在这个模块中定义的常量为：

- `string.ascii_letters`

    将下面的`ascii_lowercase`和`ascii_uppercase`变量串联起来。这个值不是locale-dependent的。

- `string.ascii_lowercase`

    小写字母`abcdefghijklmnopqrstuvwxyz`.这个值不是locale-dependent的，也不应该修改它。

- `string.ascii_uppercase`

    大写字母`ABCDEFGHIJKLMNOPQRSTUVWXYZ`.这个值不是locale-dependent的，也不应该修改它。

- `string.digits`

    字符串`0123456789`

- `string.hexdigits`

    字符串`0123456789abcdefABCDEF`

- `string.octdigits`

    字符串`01234567`

- `string.punctuation`

    考虑在C locale中为标点符号的ASCII字符。

- `string.printable`

    可以打印的ASCII字符串。这个字符串组合了`digits`, `ascii_letters`, `punctuation`, 和`whitespace`.

- `string.whitespace`

    考虑为空白字符的ASCII字符串。这个字符串包含空格，tab，linefeed，return，formfeed，和vertical tab。

## 源代码 

[github🔗](https://github.com/python/cpython/blob/3.6/Lib/string.py)



