# Prametrizing fixtures and test functions

pytest可以让测试以几种level进行参数化:

- `pytest.fixture()`允许参数化fixture函数.
- `@pytest.mark.parametrize`允许定义多个参数set
- `pytest_generate_tests`允许定义自定义参数化.

## @pytest.mark.parametrize: parametrizing test functions

内置的`pytest.mark.parametrize`装饰器可以为一个test函数激活参数的参数化。

下面是一个典型例子:

```
# test_expectation.py

import pytest


@pytest.mark.parametrize('test_input,expected', [
    ('3+5', 8),
    ('2+4', 6),
    ('6*9', 42),
])
def test_eval(test_input, expected):
    assert eval(test_input) == expected
```

这里，`@parametrize`参数会定义三个不同的`(test_input, expected)`元祖，
所以会使用这些参数运行三次`test_eval`函数.

```
$ pytest
=========================== test session starts ============================
platform linux -- Python 3.x.y, pytest-3.x.y, py-1.x.y, pluggy-0.x.y
rootdir: $REGENDOC_TMPDIR, inifile:
collected 3 items

test_expectation.py ..F                                              [100%]

================================= FAILURES =================================
____________________________ test_eval[6*9-42] _____________________________

test_input = '6*9', expected = 42

    @pytest.mark.parametrize("test_input,expected", [
        ("3+5", 8),
        ("2+4", 6),
        ("6*9", 42),
    ])
    def test_eval(test_input, expected):
>       assert eval(test_input) == expected
E       AssertionError: assert 54 == 42
E        +  where 54 = eval('6*9')

test_expectation.py:8: AssertionError
==================== 1 failed, 2 passed in 0.12 seconds ====================
```

请记得，你可以为class或者module使用parametrize marker.

也可以使用另外一种写法，将装饰器堆在一起:

```
import pytest

@pytest.mark.parametrize('x', [0, 1])
@pytest.mark.parametrize('y', [2, 3])
def test_foo(x, y):
    pass
```

这个test将会通过参数`x=0/y=2`, `x=1/y=2`, `x=0/y=3`以及`x=1/y=3`来调用这个test
函数。

## Basic `pytest_generate_tests` example

...
