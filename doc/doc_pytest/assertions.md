# The writing and reporting of assertions in tests

## Assertiing with `assert` statement

`pytest`允许你使用python标准语句`assert`来验证表达式和python tests的值:

```python
# test_assert1.py
def f():
    return 3


def test_function():
    assert f() == 4
```


如果失败了，你将会看到下面这些输出:

```
$ pytest test_assert1.py
=========================== test session starts ============================
platform linux -- Python 3.x.y, pytest-3.x.y, py-1.x.y, pluggy-0.x.y
rootdir: $REGENDOC_TMPDIR, inifile:
collected 1 item

test_assert1.py F                                                    [100%]

================================= FAILURES =================================
______________________________ test_function _______________________________

    def test_function():
>       assert f() == 4
E       assert 3 == 4
E        +  where 3 = f()

test_assert1.py:5: AssertionError
========================= 1 failed in 0.12 seconds =========================
```

`pytest`支持展示出错前的几个表达式，如calls，attributes，comparison...

不过，如果你使用了assert语句的message特性，就不会显示这些帮助信息了，只会
把你填的message显示出来.

## Assertions about expected exceptions

为了编写抛出异常的assertions，你必须使用`pytest.raises`作为上下文管理器:

```python
import pytest


def test_zero_division():
    with pytest.raises(ZeroDivisionError):
        1 / 0
```

如果你想要知道确切的异常信息:

```python
def test_recursion_depth():
    with pytest.raises(RuntimeError) as excinfo:
        def f():
            f()
        f()
    assert 'maximum recursion' in str(excinfo.value)
```

`excinfo`是一个`ExceptionInfo`的实例，它是Exception对象的封装。

它的主要属性包括`.type`, `.value`和`.traceback`.

在上下文管理器中，你可以使用关键字参数`message`来指定自定义的错误message：

```python
>>> with raises(ZeroDivisionError, message='Expecting ZeroDivisionError'):
...     pass
... Failed: Expecting ZeroDivisionError
```

另外，这个上下文管理器还接受一个`match`关键字参数，它可以接受正则表达式pattern
作为参数，匹配ExceptionInfo.value的值:

```python
import pytest


def myfunc():
    raise ValueError("Exception 123 raised")


def test_match():
    with pytest.raises(ValueError, match=r".* 123 .*"):
        myfunc()
```

## Assertions about expected warnings

你可以通过`pytest.warns`来检查是否抛出特定的警告。

## Making use of context-sensitive comparisons

`pytest`在碰到比较的时候支持提供比较上下文敏感的信息:

```python
# test_assert2.py

def test_set_comparison():
    set1 = set('1308')
    set2 = set('8035')
    assert set1 == set2
```

运行的时候，将会抛出如下错误:

```python
$ pytest test_assert2.py
=========================== test session starts ============================
platform linux -- Python 3.x.y, pytest-3.x.y, py-1.x.y, pluggy-0.x.y
rootdir: $REGENDOC_TMPDIR, inifile:
collected 1 item

test_assert2.py F                                                    [100%]

================================= FAILURES =================================
___________________________ test_set_comparison ____________________________

    def test_set_comparison():
        set1 = set("1308")
        set2 = set("8035")
>       assert set1 == set2
E       AssertionError: assert {'0', '1', '3', '8'} == {'0', '3', '5', '8'}
E         Extra items in the left set:
E         '1'
E         Extra items in the right set:
E         '5'
E         Use -v to get the full diff

test_assert2.py:5: AssertionError
========================= 1 failed in 0.12 seconds =========================
```


## Defining your own assertion comparison

...


## Advanced assertion introspection

...
