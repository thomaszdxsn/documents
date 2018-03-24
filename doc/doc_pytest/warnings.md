# Warnings Capture

从pytest3.1开始，pytest可以自动捕获warnings，将它们展示在session的末尾.

```python
# test_show_warnings.py
import warnings


def api_v1():
    warnings.warn(UserWarning('api v1, should use function from v2'))
    return 1


def test_one():
    assert api_v1() == 1
```

下面是输出的结果:

```
$ pytest test_show_warnings.py
=========================== test session starts ============================
platform linux -- Python 3.x.y, pytest-3.x.y, py-1.x.y, pluggy-0.x.y
rootdir: $REGENDOC_TMPDIR, inifile:
collected 1 item

test_show_warnings.py .                                              [100%]

============================= warnings summary =============================
test_show_warnings.py::test_one
  $REGENDOC_TMPDIR/test_show_warnings.py:4: UserWarning: api v1, should use functions from v2
    warnings.warn(UserWarning("api v1, should use functions from v2"))

-- Docs: http://doc.pytest.org/en/latest/warnings.html
=================== 1 passed, 1 warnings in 0.12 seconds ===================
```

Pytest默认会捕获除了`DeprecatiionWarning`和`PendingDeprecationWarning`之外的所有
warnings。

`-W`这个flag可以控制某个warnings是否应该显示，或者直接转为错误：

```
$ pytest -q test_show_warnings.py -W error::UserWarning
F                                                                    [100%]
================================= FAILURES =================================
_________________________________ test_one _________________________________

    def test_one():
>       assert api_v1() == 1

test_show_warnings.py:8:
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

    def api_v1():
>       warnings.warn(UserWarning("api v1, should use functions from v2"))
E       UserWarning: api v1, should use functions from v2

test_show_warnings.py:4: UserWarning
1 failed in 0.12 seconds
```

另外可以通过配置文件来指定选项，配置文件名为`pytest.int`

```
[pytest]
filterwarnings =
    error
    ignore::UserWarning
```



