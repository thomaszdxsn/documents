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


import _string      # string的helper模块   #TODO: 阅读这个模块??找不到

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


########################################################################
import re as _re
from collections import ChainMap as _ChainMap


#! 这个元类做的事情就是根据类属性来生成最后编译成正则对象的"pattern"属性
#! 如果覆盖了"pattern"类属性，则直接将它编译成正则对象
#! 如果没有，则讲"id_pattern", "delim"这两个属性插值到默认的pattern规则中并编译
#! 另外，不管"flag"设置了"VERBOSE"没有，最后都会加上这个flag
class _TemplateMetaclass(type):
    pattern = r"""
    %(delim)s(?:
        (?P<escaped>%(delim)s)  |   # 使用两个delimiters转义序列
        (?P<named>%(id)s)       |   # delimiter以及一个Python标识符
        {(?P<braced>%(id)s)}    |   # delimiter和一个braced标识符
        (?P<invalid>)           |   # 其它不规范的delimiter
    )
    """

    def __init__(cls, name, bases, dct):
        #! 使用super()完成类对象的创建(元类)
        super(_TemplateMetaclass, cls).__init__(name, bases, dict)
        #! 下面的代码是对类作一些额外的修改
        if 'pattern' in dct:
            pattern = cls.pattern
        else:
            pattern = _TemplateMetaclass.pattern %{
                'delim': _re.escape(cls.delimiter),
                'id': cls.idpattern,
            }
        cls.pattern = _re.compile(pattern, cls.flags | _re.VERBOSE)


class Template(metaclass=_TemplateMetaclass):
    """一个支持$-替换的字符串类"""

    delimiter = '$'
    # r'[a-z]'在使用re.IGNORECASE而不是用re.ASCII的时候可以匹配非ASCII字符
    # 因为向后兼容性的问题，我们不可以加入re.ASCII.
    # 所以我们使用了-i标识以及[a-zA-Z]模式
    # 请看 https://bugs.python.org/issue31672
    idpattern = r'(?-i:[_a-zA-Z][_a-zA-Z0-9]*)'
    flags = _re.IGNORECASE

    def __init__(self, template):
        self.template = template

    # 搜索$$, $identifier, ${identifier}, 以及任何单独的$

    def _invalid(self, mo):
        """!获取模版中出错的位置并抛出ValueError"""
        i = mo.start('invalid')
        lines = self.template[:i].splitlines(keepends=True)
        if not lines:
            colno = 1
            lineno = 1
        else:
            colno = i - len(''.join(lines[:-1]))
            lineno = len(lines)
        raise ValueError('Invalid placeholder in string: line %d, col %d' %
                         (lineno, colno))

    def substitute(*args, **kws):
        """!占位符替换方法"""
        if not args:
            raise TypeError("descriptor 'substitute' of 'Template' object"
                            "needs an argument")
        #! "self"包含在args中,这种写法好像很蠢
        #! 查看源码中的注释明白了， allow the "self" keyword be passed
        #! 意思就是允许在关键字参数中传入名称为self的参数
        #! 也就是说不让第一个参数占用任何参数命名
        self, *args = args
        if len(args) > 1:
            raise TypeError('Too many positional arguments')
        if not args:
            mapping = kws
        elif kws:                               #! 同时包含字典和关键字参数
            mapping = _ChainMap(kws, args[0])   #! 关键字参数将会优先使用
        else:
            #! 没有关键字参数的情况
            mapping = args[0]

        # .sub()的一个helper函数
        def convert(mo):
            """这个函数传入到re.sub()函数
            
            :return: 返回应该要替换的pattern
            """
            # 首先检查最常见的path
            named = mo.group('named') or mo.group('braced')
            if named is not None:
                return str(mapping[named])
            if mo.group('escaped') is not None:
                return self.delimiter
            if mo.group('invalid') is not None:
                #! 碰到invalid的情况，直接交给_invalid()方法处理
                #! 可以输出详细的出错位置
                self._invalid(mo)
            #! 如果抛出下面这个错误，大概率是是因为继承Template之后
            #! 没有安装规范覆盖.pattern属性
            raise ValueError('Unrecognized named group in pattern',
                             self.pattern)
        return self.pattern.sub(convert, self.template)

    def safe_substitute(*args, **kws):
        if not args:
            return TypeError("descriptor 'safe_substitute' of 'Template' object"
                             "needs an argument")
        self, *args = args
        if len(args) > 1:
            raise TypeError('Too many positional arguments')
        if not args:
            mapping = kws
        elif kws:
            mapping = _ChainMap(kws, args[0])   #! 记住args是一个元祖
        else:
            mapping = args[0]

        # .sub()的helper函数
        def convert(mo):
            named = mo.group('named') or mo.group('braced')
            if named is not None:
                #! 注意这里的代码是和.substitute()方法唯二的不同之处之一
                #! 在mapping没有待匹配的占位符时，不报错
                try:
                    return str(mapping[named])
                except KeyError:
                    return mo.group()
            if mo.group('escaped') is not None:
                return self.delimiter
            if mo.group('invalid') is not None:
                #! 这里的处理也和.substitute()不一样
                #! 在delimiter之后的字符不合法时，没有抛出错误，而是直接表示
                return mo.group()
            raise ValueError('Unrecognized named group in pattern',
                             self.pattern)
        return self.pattern.sub(convert, self.template)


########################################################################
# Formatter类
# 请看PEP 3101对这个类的提案和细节

# 最难的一部分是C扩展的重用。
# 暴露了一个"_"前缀方法供str使用

# 总体的parser实现于 _string.formatter_parser     # C实现
# field name parser 实现于 _string.formatter_field_name_split


class Formatter:
    
    def format(*args, **kwargs):
        if not args:
            raise TypeError("descriptor 'format' of 'Formatter' object "
                            "needs an object")
        self, *args = args      # 为了允许传入关键字参数'self'
        try:
            format_string, *args = args     # 允许传入关键字参数'format_string'
        except ValueError:      #! 如果args里面没有format_string，试着从kwargs中找找
            if 'format_string' in kwargs:
                format_string = kwargs.pop('format_string')
                import warnings
                warnings.warn("Passing 'format_string' as keyword argument is "
                              "deprecated", DeprecationWarning, stacklevel=2)
            else:
                raise TypeError("format() missing 1 required positional "
                                "argument: 'format_string'") from None
        return self.vformat(format_string, args, kwargs)

    def vformat(self, format_string, args, kwargs, used_args, recursion_depth,
                auto_arg_index=0):
        if recursion_depth < 0:
            raise ValueError("Max string recursion exceeded")
        result = []
        for literal_text, field_name, format_spec, conversion in \
                self.parse(format_string):
            
            # 输出literal_text
            if literal_text:
                result.append(literal_text)

            # 如果有一个field，输出它
            if field_name is not None:
                # 这是一种标记，找到对象并将它格式化

                # 在给定的field_name为空时，处理参数索引
                if field_name == '':
                    if auto_arg_index is False:
                        raise ValueError("cannot switch from manual field "
                                        "specification to automatic field "
                                        "numbering")
                    field_name = str(auto_arg_index)
                    auto_arg_index += 1
                elif field_name.isdigit():
                    if auto_arg_index:
                        raise ValueError("cannot switch from manual field "
                                         "specification to automatic field "
                                         "numbering")
                    # 禁用参数索引自增
                    auto_arg_index = False
                
                # 通过给定的field_name，找到它引用的对象
                obj, arg_used = self.get_field(field_name, args, kwargs)
                used_args.add(arg_used)

                # 在返回对象中做一些转换
                obj = self.convert_field(obj, conversion)

                # 如果需要的话，扩展format_spec
                format_spec, auto_arg_index = self._vformat(
                    format_spec, args, kwargs,
                    used_args, recursion_depth-1,
                    auto_arg_index=auto_arg_index
                )

                # 将对象格式化并追加到result中
                result.append(self.format_field(obj, format_spec))

        return "".join(result), auto_arg_index

    def get_value(self, key, args, kwargs):
        if isinstance(key, int):
            return args[key]
        else:
            return kwargs[key]

    def check_unused_args(self, used_args, args, kwargs):
        pass

    def format_field(self, value, format_spec):
        return format(value, format_spec)

    def convert_field(self, value, conversion):
        # 在结果对象中做一些转换(一般根据显式转义字符)
        if conversion is None:
            return value
        if conversion == 's':
            return str(value)
        elif conversion == 'r':
            return repr(value)
        elif conversion == 'a':
            return ascii(value)
        raise ValueError("Unknown conversion specifier {0!s}".format(conversion))

    # 返回一个可迭代对象，它包含下面形式的元祖:
    # (literal_text, field_name, format_spec, conversion)
    # literal_text可以长度为0(!空字符串
    # field_name可以是None,这个情况下对象不需要格式化输出
    # 如果field_name不是None，将会使用format_spec将它格式化，并且转换后再输出使用
    def parse(self, format_string):
        #! 这显然是一个C实现的解析函数
        return _string.formatter_parser(format_string)

    # 给定一个field_name，找到它引用的对象
    # field_name:   这个字段将会被查询，比如"0.name"
    #                   或者 "lookup[3]"
    # used_args:    一组已经使用过的参数集合
    # args, kwargs: 传入到`vformat`中的参数
    def get_field(self, field_name, args, kwargs):
        #! first是字段参数名称, rest是它属性的访问方式
        first, rest = _string.formatter_field_name_split(field_name)

        obj = self.get_value(first, args, kwargs)

        # 迭代field_name的rest, 按需使用getattr或者getitem
        for is_attr, i in rest:
            if is_attr:
                obj = getattr(obj, i)
            else:
                obj = obj[i]
        
        return obj, first
            
                    
