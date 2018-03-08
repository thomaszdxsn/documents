# unittest.mock -- mock object library

`unittest.mock`是Python中用来测试的一个库。它允许你替换测试中的一部分对象为模拟对象。

`unittest`提供了一个核心的`Mock`类。在执行一个动作后，你可以断言某个属性/方法应该用哪些参数来调用。你可以指定返回的值并设定属性。

另外，mock提供了一个`patch()`装饰器来在一个作用域中处理要打补丁的模块级和类级属性，以及提供`sentinel`用来创建唯一对象。

Mock非常容易使用，它设计为和unittest一起使用。Mock基于`"动作" -> "断言"`模式。

## Quick Guide

`Mock`和`MagicMock`对象用来创建所有的属性和方法。你可以配置它们，指定返回值，限定哪些对象可以访问，然后对它们断言：

```python
>>> from unittest.mock import MagicMock
>>> thing = ProductionClass()
>>> thing.method = MagicMock(return_value=3)
>>> thing.method(3, 4, 5, key='value')
3
>>> thing.method.assert_called_with(3, 4, 5, key='value')
```

`sinde_effect`允许你执行一些副作用，包括在调用mock的时候抛出一个异常:

```python
>>> mock = Mock(side_effect=KeyError('foo'))
>>> mock()
Traceback (most recent call last):
 ...
KeyError: 'foo'
```

```python
>>> values = {'a': 1, 'b': 2, 'c': 3}
>>> def side_effect(arg):
...     return values(arg)
...
>>> mock.side_effect = side_effect
>>> mock('a'), mock('b'), mock('c')
(1, 2, 3)
>>> mock.side_effect = [5, 4, 3, 2, 1]
>>> mock(), mock(), mock()
(5, 4, 3)
```

Mock还有很多其它方式让你可以对它进行配置和控制它的行为。例如，`spec`参数可以配置mock从另一个对象拿到它的它的属性说明。如果访问一个mock不存在于spec的属性会抛出`AttributeError`.

`patch()`装饰器/上下文管理器，可以用来在一个测试中模拟一个类或者一个模块的对象。这个对象将会被替换成一个mock(或者其它对象):

```python
>>> from unittest.mock import patch
@patch('module.ClassName2')
@patch('module.ClassName1')
def test(MockClass1, MockClass2):
...     module.ClassName1()
...     module.ClassName2()
...     assert MockClass1 is module.ClassName1
...     assert MockClass2 is module.ClassName2
...     assert MockClass1.called
...     assert MockClass2.called
...
>>> test()
```

> 当你嵌套`patch`装饰器的时候，mock会按照装饰器定义的顺序(自下而上)传入函数.

`patch()`虽然说是一个装饰器，其实你可以将它作为上下文管理器来使用：

```python
>>> with patch.object(ProductionClass, 'method', return_value=None) as mock_method:
...     thing = ProductionClass()
...     thing.method(1, 2, 3)
...
>>> mock_method.assert_called_once_with(1, 2, 3)
```

另外还有一个`patch_dict()`可以用来设置字典的值:

```python
>>> foo = {'key': 'value'}
>>> original = foo.copy()
>>> with patch.dict(foo, {'new_key': 'newvalue'}, clear=True):
...     assert foo == {'newkey': 'newvalue'}
...
>>> assert foo == original
```

Mock支持模拟Python的魔术方法。可以通过`MagicMock`类来实现:

```python
>>> mock = MagicMock()
>>> mock.__str__.return_value = 'foobarbaz'
>>> str(mock)
'foobarbaz'
>>> mock.__str__.assert_called_with()
```

Mock允许你将一个函数(或者其它的Mock实例)赋值给一个魔术方法。

```python
>>> mock = Mock()
>>> mock.__str__ = Mock(return_value='wheeeeee')
>>> str(mock)
'wheeeeee'
```

如果你没有正常使用，mock也会报错:

```python
>>> from unittest.mock import create_autospec
>>> def function(a, b, c):
...     pass
...
>>> mock_function = create_autospec(function, return_value='fishy')
>>> mock_function(1, 2, 3)
'fishy'
>>> mock_function.assert_called_once_with(1, 2, 3)
>>> mock_function('wrong arguments')
Traceback (most recent call last):
 ...
TypeError: <lambda>() takes exactly 3 arguments (1 given)
```

`create_autospec()`可以用在类上面，它会拷贝类的`__init__`方法的签名，如果是一个callable对象，还会拷贝它的`__call__`方法的签名。

## The Mock Class

Mock是一个作用为模拟对象的对象，一般用于测试。MOck可以是可调用的。访问相同的属性总是会返回相同的mock。mock会记录你如何使用它，允许你在之后作一个断言，判断之前是怎么被使用的。

`MagicMock`是`Mock`的一个子类，可以用它来模拟对象的魔术方法。

`patch()`装饰器让你可以临时地替换一个指定模块的一个类变为一个Mock对象。默认情况下，`patch()`会为你创建一个`MagicMock`。你可以通过`new_callble`切换会`Mock`。

- class`unittest.mock.Mock(spec=None, side_effect=None, return_value=DEFAULT, wraps=None, name=None, spec_set=None, unsafe=False, **kwargs)`

    创建一个新的Mock对象。Mock接受若干选项参数，可以指定这个对象的行为。

    - spec:

        可以是一组字符串list，或者一个已经存在的对象(一个类或者实例).将会作为mock对象的spec规范而存在。

    - spec_set:

        spec参数的一个严格版本。如果使用它，试图访问任何不存在的属性都会抛出`AttributeErro`.

    - side_effect:

        可以是一个函数，在Mock被调用的时候调用它。可以用来抛出异常或者动态修改返回值。

        可以是一个异常类或者实例。

        可以是一个可迭代对象，每次调用mock都会迭代这个对象一次并返回值。

        可以通过将`side_effect`设置为None来清除它。

    - return_value

        在mock被调用时返回的值。

    - unsafe

        默认情况下，任何属性以`assert`开头都会抛出`AttributeError`错误。传入`unsafe=True`可以访问这些属性。

    - wraps

        mock要封装的对象。

    - name

        如果一个mock有name，那么会在它的repr中显示出来。可以用于DEBUG.


    方法:

    - `assert_called(*args, **kwargs)`

        断言这个mock上一次的调用情况:

        ```python
        >>> mock = Mock()
        >>> mock.method()
        <Mock name='mock.method()' id='...'>
        >>> mock.method.assert_called()
        ```

    - `assert_called_once(*args, **kwargs)`

        断言这个mock只被调用了一次。

        ```python
        >>> mock = Mock()
        >>> mock.method()
        <Mock name='mock.method()' id='...'>
        >>> mock.method.assert_called_once()
        >>> mock.method()
        <Mock name='mock.method()' id='...'>
        >>> mock.method.assert_called_once()
        Traceback (most recent call last):
        ...
        AssertionError: Expected 'method' to have been called once. Called 2 times.
        ```

    - `assert_called_with(*args, **kwargs)`

        这个方法是一个方便的方式，可以断言是否是一个特定的调用：

        ```python
        >>> mock = Mock()
        >>> mock.method(1, 2, 3, test='wow')
        <Mock name='mock.method()' id='...'>
        >>> mock.method.assert_called_with(1, 2, 3, test='wow')
        ```

    - `assert_called_once_with(*args, **kwags)`

        断言mock只被调用了一次，并且是以指定的方式调用的.

        ```python
        >>> mock = Mock(return_value=None)
        >>> mock('foo', bar='baz')
        >>> mock.assert_called_once_with('foo', bar='baz')
        >>> mock('other', bar='values')
        >>> mock.assert_called_once_with('other', bar='values')
        Traceback (most recent call last):
        ...
        AssertionError: Expected 'mock' to be called once. Called 2 times.
        ```

    - `assert_any_call(*args, **kwargs)`

        断言mock是通过指定的参数调用的。

        ```python
        >>> mock = Mock(return_value=None)
        >>> mock(1, 2, arg='thing')
        >>> mock('some', 'thing', 'else')
        >>> mock.assert_any_call(1, 2, arg='thing')
        ```

    - `assert_has_calls(calls, any_order=False)`

        断言mock被调用了指定的次数，calls是mock调用后返回对象的list。

        ```python
        >>> mock = Mock(return_value=None)
        >>> mock(1)
        >>> mock(2)
        >>> mock(3)
        >>> mock(4)
        >>> calls = [call(2), call(3)]
        >>> mock.assert_has_calls(calls)
        >>> calls = [call(4), call(2), call(3)]
        >>> mock.assert_has_calls(calls, any_order=True)
        ```

    - `assert_not_called()`

        断言一个mock没有被调用：

        ```python
        >>> m = Mock()
        >>> m.hello.assert_not_called()
        >>> obj = m.hello()
        >>> m.hello.assert_not_called()
        Traceback (most recent call last):
        ...
        AssertionError: Expected 'hello' to not have been called. Called 1 times.
        ```

    - `reset_mock(*, return_value=False, side_effect=False)`

        可以重置一些mock对象的调用属性:

        ```python
        >>> mock = Mock(return_value=None)
        >>> mock('hello')
        >>> mock.called
        True
        >>> mock.reset_mock()
        >>> mock.called
        False
        ```

    - `mock_add_spec(spec, spec_set=False)`

    - `attach_mock(mock, attribute)`

    - `configu`