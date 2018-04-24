import sys
from types import MappiongProxyType, DynamicClassAttribute
from functools import reduce
from operator import or_ as _or_


try:
    from _collections import OrderedDict
except ImportError:
    from collections import OrderedDict


__all__ = [
        'EnumMeta',
        'Enum', 'IntEnum', 'Flag', 'IntFlag',
        'auto', 'unique',
        ]


def _is_descriptor(obj):
    return (
            hasattr(obj, '__get__') or
            hasattr(obj, '__set__') or
            hasattr(obj, '__delete__'))


def _is_dunder(name):
    return (name[:2] == name[-2:] == '__' and
            name[2:3] != '_' and
            name[-3:-2] != '_' and
            len(name) > 4)


def _is_sunder(name):
    return (name[0] == name[-1] == '_' and
            name[1:2] != '_' and
            name[-2:-1] != '_' and
            len(name) > 2)


def _make_class_unpickable(cls):
    def _break_on_call_reduce(self, proto):
        raise TypeError('%r cannot be pickled' % self)
    cls.__reduce_ex__ = _break_on_call_reduce
    cls.__module__ = '<unkown>'


_auto_null = object()
class auto:
    value = _auto_null


class _EnumDict(dict):
    """用来追踪所有的enum成员的顺序，并且确保成员名称不会重复使用

    EnumMeta会使用`self._member_names`来找到成员的名称
    """
    def __init__(self):
        super().__init__()
        self._member_names = []
        self._last_values = []

    def __setitem(self, key, value):
        if _is_sunder(key):
            if key not in (
                    '_order_', '_create_pseudo_member_',
                    '_generate_next_value_', '_missing_',
                    ):
                raise ValueError('_name_ are reserved for future Enum use')
            if key == '_generate_next_value_':
                setattr(self, '_generate_next_value', value)
        elif _is_dunder(key):
            if key == '__order__':
                key = '_order_'
        elif key in self._member_names:
            raise TypeError('Attempty to reuse key: %r' % key)
        elif not _is_descriptor(value):
            if key in self:
                raise TypeError('%r already defined as: %r' %(key, self[key]))
            if isinstance(value, auto):
                if value.value == _auto_null:
                    value.value = self._generate_next_value(key, 1, len(self._member_names, self._last_values[:])
                value = value.value
            self._member_names.append(key)
            self._last_values.append(value)
        super().__setitem(key, value)



# 这是一个伪造的Enum，主要目的是让EnumMeta可以找到它，
# 不过直到EnumMeta第一次运行之前，Enum类都是不存在的
# 这也是我们为什么在EnumMeta中写下`if Enum is not None`的原因
Enum = None


class EnumMeta(type):
    """Enum的元类"""
    @classmethod
    def __prepare__(metacls, cls, bases):
        # 创建一个命名空间字典
        enum_dict = _EnumDict()
        # 继承之前的flags和`_generate_next_value_`函数
        member_type, first_enum = metacls._get_mixins_(bases)   # first_enum是第一个为Enum的父类
        if first_enum is not None:
            enum_dict['_generate_next_value_'] = getattr(first_enum, '_generate_next_value_', None)
        return enum_dict

    def __new__(metacls, cls, bases, classdict):
        # Enum类在定义元素以后就是最终形态了；
        # 一般不可以将它混合其它类型使用(比如int, float...)
        # 除非重新定义了`__new__`
        member_type, first_enum = metacls._get_mixins_(bases)
        __new__, save_new, use_args = metacls._find_new_(classdict, member_type,
                                                         first_enum)
        # 将每个枚举元素保存到一个单独的字典中，将classdict的元素删除
        enum_members = {k: classdict[k] for k in classdict._member_names}
        for name in classdict._member_names:
            del classdict[name]

        # 调整sunders
        _order_ = classdict.pop('_order_', None)

        # 检查不合法enum名称，暂时只禁止取名为'mro'
        invalid_names = set(enum_members) & {'mro', }
        if invalid_names:
            raise ValueError('Invalid enum member name: {0}'.format(
                    ",".join(invalid_names)))

        # 如果没有提供docstring，创建一个默认的docstring
        if '__doc__' not in classdict:
            classdict['__doc__'] = 'An enumeration'

        # 创建我们自己的Enum类型
        enum_class = super().__new__(metacls, cls, bases, classdict)
        enum_class._member_names_ = []       # 名称需要按照定义时的顺序设置
        enum_class._member_map_ = OrderDict()
        enum_class._member_type_ = member_type

        # 从超类中拿到属性并保存
        base_attributes = {a for b in enum_class.mro() for a in b.__dict__}         # a只是属性名,所以这是一个属性名的集合

        # 逆向 value->name 的映射
        enum_class._value2member_map_ = {}

        # 如果一个自定义类型混合了Enum，它不知道如何pickle自己，
        # `pickle.dumps`是可以有效的，但是`pickle.loads`无效，所以我们要
        # 蓄意破坏，让`pickle.dumps`同样失效

        # 不过，如果这个类型定义了`__reduce_ex__`，就不要蓄意破坏了.
        if '__reduce_ex__' not in classdict:
            if member_type is not object:
                methods = ('__getnewargs_ex__', '__getnewargs__',
                           '__reduce_ex__', '__reduce__')
                if not any(m in member_type.__dict__ for m in methods):
                    _make_class_unpickable(enum_class)

        # 实例化它们... 
        
