# Cache: working with cross-testrun state

## Usage

这个插件可以提供两个命令行选项，可以返回最后一次调用`pytest`时候发生的错误.

- `--if`, `--last-failed`: 重新运行这个错误
- `--ff`, `--failed-first`: 运行第一个错误，一起之后的tests.

## Returnning only failures or failures first

首先，我们创建50个test调用，有两个或失败:

```
# test_50.py

import pytest

@pytest.mark.parametrize('i', range(50))
def test_num(i):
    if i in (17, 25):
        pytest.fail('bad luck')
```

然后在你首次运行测试的时候会看到如下输出:

```
$ pytest -q
.................F.......F........................                   [100%]
================================= FAILURES =================================
_______________________________ test_num[17] _______________________________

i = 17

    @pytest.mark.parametrize("i", range(50))
    def test_num(i):
        if i in (17, 25):
>          pytest.fail("bad luck")
E          Failed: bad luck

test_50.py:6: Failed
_______________________________ test_num[25] _______________________________

i = 25

    @pytest.mark.parametrize("i", range(50))
    def test_num(i):
        if i in (17, 25):
>          pytest.fail("bad luck")
E          Failed: bad luck

test_50.py:6: Failed
2 failed, 48 passed in 0.12 seconds
```

然后，你通过`--if`来再次运行测试:

```
$ pytest --lf
=========================== test session starts ============================
platform linux -- Python 3.x.y, pytest-3.x.y, py-1.x.y, pluggy-0.x.y
rootdir: $REGENDOC_TMPDIR, inifile:
collected 50 items / 48 deselected
run-last-failure: rerun previous 2 failures

test_50.py FF                                                        [100%]

================================= FAILURES =================================
_______________________________ test_num[17] _______________________________

i = 17

    @pytest.mark.parametrize("i", range(50))
    def test_num(i):
        if i in (17, 25):
>          pytest.fail("bad luck")
E          Failed: bad luck

test_50.py:6: Failed
_______________________________ test_num[25] _______________________________

i = 25

    @pytest.mark.parametrize("i", range(50))
    def test_num(i):
        if i in (17, 25):
>          pytest.fail("bad luck")
E          Failed: bad luck

test_50.py:6: Failed
================= 2 failed, 48 deselected in 0.12 seconds ==================
```

你只会最后一次运行时候发生的两个错误，其它的48个tests都不会运行。





