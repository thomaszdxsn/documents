# addict - The Python Dict that's better than heroin

addict是一个Python模块，可以给你一个字典结构，除了标准的item访问方式，还可以通过对属性的访问方式来get/set它。

这意味着你不需要将字典写成下面这样:

```python
body = {
    'query': {
        'filtered': {
            'query': {
                'match': {'description': 'addictive'}
            },
            'filter': {
                'term': {'created_by': 'Mats'}
            }
        }
    }
}
```

你可以将它简化成下面这三行代码:

```python
body = Dict()
body.query.filterd.query.match.description = 'addictive'
body.query.filterd.query.term.created_by = 'Mats'
```

## Installing

你可以通过`pip`来安装:

`pip install addict`

## Usage

addict继承自`dict`，但是它的get/set方式更加的弹性。可以让你很开心的写字典！

```python
>>> from addict import Dict
>>> mapping = Dict()
>>> mapping.a.b.c.d.e = 2
>>> mapping
{'a': {'b': {'c': {'d': {'e': 2}}}}}
```

如果`Dict`使用任何可迭代对象来实例化，它的构造器会迭代这个对象并且克隆它的值:

```python
>>> mapping = {'a': [{'b': 3}, {'b': 3}]}
>>> dictionary = Dict(mapping)
>>> dictionary.a[0].b
3
```

不过`mapping['a']`不再和`dictionary['a']`是相同的对象了：

```python
>>> mapping['a'] is dictionary['a']
False
```

上面的限制是构造器施加的，如果你通过属性赋值或者item赋值的方式设定，list仍然会保持
一份相同的引用:

```python
>>> a = Dict()
>>> b = [1, 2, 3]
>>> a.b = b
>>> a.b is b
True
```

## Stuff to keep in mind

请记住`int`不是和合法的属性名(但是是合法的键名)，所以必须使用item的方式:

```python
>>> addicted = Dict()
>>> addicted.a.b.c.d.e = 2
>>> addicted[2] = [1, 2, 3]
>>> addicted
{2: [1, 2, 3], 'a': {'b': {'c': {'d': {'e': 2}}}}}
```

两种语法是可以混合在一起的:

```python
>>> addctied.a.b['c'].d.e
2
```

## Attibutes like keys, items etc.

addict不允许你覆盖`dict`的原生属性，所以下面这些情况都会失败:

```python
>>> mapping = Dict()
>>> mapping.keys = 2
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "addict/addict.py", line 53, in __setattr__
    raise AttributeError("'Dict' object attribute '%s' is read-only" % name)
AttributeError: 'Dict' object attribute 'keys' is read-only
```

不过，下面这种情况是可以的:

```python
>>> a = Dict()
>>> a['keys'] = 2
>>> a
{'keys': 2}
>>> a['keys']
2
```

## Recursive Fallback to dict

如果你不想在其它模块使用`addict`对象，可以使用`to_dict()`方法，它会返回一个普通
的dict。

```python
>>> regurlar_dict = my_addict.to_dict()
>>> regurlar_dict.a = 2
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
AttributeError: 'dict' object has no attribute 'a'
```

如果你想通过寥寥几行来创建一个嵌套字典:

```python
body = Dict()
body.query.filtered.query.match.description = 'addictive'
body.query.filtered.filter.term.created_by = 'Mats'
thrid_party_module.search(query=body.to_dict())
```

## Couting

`Dict`可以简单的访问深嵌套的属性，让它也可以很轻松的进行counting。
它的counting和`collections.Count`不一样，它可以counting不同的层级。

```python
# 考虑有下面这些数据
data = [
    {'born': 1980, 'gender': 'M', 'eyes': 'green'},
    {'born': 1980, 'gender': 'F', 'eyes': 'green'},
    {'born': 1980, 'gender': 'M', 'eyes': 'blue'},
    {'born': 1980, 'gender': 'M', 'eyes': 'green'},
    {'born': 1980, 'gender': 'M', 'eyes': 'green'},
    {'born': 1980, 'gender': 'F', 'eyes': 'blue'},
    {'born': 1981, 'gender': 'M', 'eyes': 'blue'},
    {'born': 1981, 'gender': 'F', 'eyes': 'green'},
    {'born': 1981, 'gender': 'M', 'eyes': 'blue'},
    {'born': 1981, 'gender': 'F', 'eyes': 'blue'},
    {'born': 1981, 'gender': 'M', 'eyes': 'green'},
    {'born': 1981, 'gender': 'F', 'eyes': 'blue'}
]

# 如果你想根据三个条件(born, gender, eyes)来进行分类计数
counter = Dict()
for row in data:
    born = row['born']
    gender = row['gender']
    eyes = row['eyes']
    
    counter[born][gender][eyes] += 1

print(counter)
# 打印结果如下
# {1980: {'M': {'blue': 1, 'green': 3}, 'F': {'blue': 1, 'green': 1}}, 1981: {'M': {'blue': 2, 'green': 1}, 'F': {'blue': 2, 'green': 1}}}
```

## Update

`addict`的`update`做了些改动, 下面是普通的dict：

```python
>>> d = {'a': {'b': 3}}
>>> d.update({'a': {'c': 4}})
>>> print(d)
{'a': {'c': 4}}
```

而`addict`会进行递归更新:

```python
>>> D = Dict({'a': {'b': 3}})
>>> D.update({'a': {'c': 4}})
>>> print(D)
{'a': {'b': 3, 'c': 4}}
```

## When is this especially useful?

这个模块对于创建Elasticsearch查询很有用。如果你发现你需要编写多嵌套的字典，
都可以选择使用`addict`.

## Perks

和`dict`一样，它也可以完美地转换为JSON(通过`to_dict()`).

## Testing, Development and CI

...
