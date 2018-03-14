# Installlation and Getting Started

## Install pytest

1. 在你的命令行运行下面这条命令

`pip install -U pytest`

2. 检查你是否安装了正确版本

```python
$ pytest --version
This is pytest version 3.x.y, imported from $PYTHON_PREFIX/lib/python3.5/site-packages/pytest.py
```

## Create your first test

创建一个简单的test函数:

```python
def func(x):
    return x + 1


def test_answer():
    assert func(3) == 5
```

然后你可以执行这个测试函数:

```python
$ pytest
=========================== test session starts ============================
platform linux -- Python 3.x.y, pytest-3.x.y, py-1.x.y, pluggy-0.x.y
rootdir: $REGENDOC_TMPDIR, inifile:
collected 1 item

test_sample.py F                                                     [100%]

================================= FAILURES =================================
_______________________________ test_answer ________________________________

    def test_answer():
>       assert func(3) == 5
E       assert 4 == 5
E        +  where 4 = func(3)

test_sample.py:5: AssertionError
========================= 1 failed in 0.12 seconds =========================
```

返回了错误报告，因为`func(3)`不会返回5.

## Run multiple tests

`pytest`将会运行所有当前目录/子目录的`test_*.py`或者`*_test.py`文件。

## Assert that a certain exception is raised

使用`raises`可以帮助你断言代码会抛出异常:

```python
import pytest


def f():
    raise SystemExit(1)


def test_mytest():
    with pytest.raises(SystemExit):
        f()
```

执行这个测试函数，测试会通过:

```python
$ pytest -q test_sysexit.py
.                                                                    [100%]
1 passed in 0.12 seconds
```

## Group multiple tests in a class

如果你开发了多个tests，你可能想要把它们分组放到一个类中。`pytest`可以很轻松地
实现:

```python
class TestClass(object):
    def test_one(self):
        x = 'this'
        assert 'h' in x
    
    def test_two(self):
        x = 'hello'
        assert hasattr(x, 'check')
```

`pytest`会找到所有遵循Python test命名习惯的test。

```python
$ pytest -q test_class.py
.F                                                                   [100%]
================================= FAILURES =================================
____________________________ TestClass.test_two ____________________________

self = <test_class.TestClass object at 0xdeadbeef>

    def test_two(self):
        x = "hello"
>       assert hasattr(x, 'check')
E       AssertionError: assert False
E        +  where False = hasattr('hello', 'check')

test_class.py:8: AssertionError
1 failed, 1 passed in 0.12 seconds
```

## Request a unique temporary directory for functional tests

`pytests`提供**内置fixture/函数参数**，可以请求任意的资源，比如一个唯一的
临时文件夹。

```python
# content of test_tmpdir.py
def test_needsfiles(tmpdir):
    print(tmpdir)
    assert 0
```

只要将`tmpdir`放在测试函数签名中，pytest会查找并调用一个fixture工厂来创建
资源。

```python
$ pytest -q test_tmpdir.py
F                                                                    [100%]
================================= FAILURES =================================
_____________________________ test_needsfiles ______________________________

tmpdir = local('PYTEST_TMPDIR/test_needsfiles0')

    def test_needsfiles(tmpdir):
        print (tmpdir)
>       assert 0
E       assert 0

test_tmpdir.py:3: AssertionError
--------------------------- Captured stdout call ---------------------------
PYTEST_TMPDIR/test_needsfiles0
1 failed in 0.12 seconds
```

想要查找所有内置的`pytest fixtures`，可以通过这条命令:

`pytest --fixtures`


