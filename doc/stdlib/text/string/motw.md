## PyMOTW-3: string -- 文本变量和模版

### 常量

`string`模块包含一组关于ASCII字符和数字字符集的常量.

#### string_constants.py

```python
import inspect
import string


def is_str(value):
    return isinstance(value, str)


for name, value in inspect.getmembers(string, is_str):
    if name.startswith('_'):
        continue
    print("{0!s}={1!r}\n".format(name, value))
```

在处理ASCII数据时这些常量会很有用，但是由于现在会更常碰到非ASCII即Unicode字符，这些常量的作用也受到了限制：

```python
$ python3 string_constants.py

ascii_letters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVW
XYZ'

ascii_lowercase = 'abcdefghijklmnopqrstuvwxyz'

ascii_uppercase = 'ABCDEFGHIJKLMNOPQRSTUVW
XYZ'

digits = '0123456789'

hexdigits = '0123456789abcdefABCDEF'

octdigits = '01234567'

printable = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQ
RSTUVWXYZ!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~ \t\n\r\x0b\x0c'

punctuation = '!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~'

whitespace = ' \t\n\r\x0b\x0c'
```