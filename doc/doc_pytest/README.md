# pytest: helps you write better programs

`pytest`框架可以让你编写更小型的tests，不过仍然可以支持复杂性的功能性测试。

下面是一个简单test的示例:

```python
# test_sample.py
def inc(x):
    return x + 1


def test_answer():
    assert inc(3) == 5
```

执行它：

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
>       assert inc(3) == 5
E       assert 4 == 5
E        +  where 4 = inc(3)

test_sample.py:5: AssertionError
========================= 1 failed in 0.12 seconds =========================
```

## Features

- 直接使用`assert`语句(不需要记忆一堆`self.assert*`方法名);
- 自动发现test模块和函数;
- 可以使用**模块级fixture**来管理测试资源;
- 可以运行`unittest`和`nose`的测试单元；
- 支持插件架构，有超过315+的外部插件可以使用.

