# Skip and xfail: dealing with tests that cannot succed

你可以标记一个test函数，让它在某个特定平台中不会运行，或者根据一些其它情况来
跳过它，保持test suite为绿色。

`skip`意味着你自己明白这个test可以在一些条件下通过。


`xfail`意味着你可以让一个test在某些情况下错误。一个常见的例子就是，一个功能
还没有实现，或者一个bug还没有被修复。

## Skipping test functions

最简单的方式是使用`skip`装饰器来标记一个test应该被跳过:

```
@pytest.mark.skip(readon='no way of currently testing this')
def test_the_unkown():
    ...
```

另外，你可以在test函数中调用`pytest.skip`:

```
def test_function():
    if not valid_config():
        pytest.skip('unsupported configuration')
```

甚至，可以跳过整个模块:

```
import pytest

if not pytest.config.getoption('--custom-flag'):
    pytest.skip("--custom-flag is missing, skipping tests", allow_module_level=True)
```

### skipif

如果你想要在某些情况下被跳过，你可以使用`skipif`。

```
import sys


@pytest.mark.skipif(sys.version_info < (3, 6),
                    reason='requires python3.6')
def test_function():
    ...
```

如果这个表达式为True，这个test函数将会被跳过，如果要显示原因，那么就需要使用`-rs`.

你可以在一个模块中共享一个skipif标记:

```
import mymodule

minversion = pytest.market.skip(mymomdule.__versioninfo__ < (1, 1),
                                reason='at least mymodule-1.1 required')
@minversion
def test_function():
    ...
```

你可以引用这个market，在其它的test模块继续使用它：

```
from test_mymodule import minversion

@minversion
def test_anotherfunction():
    ...
```

### Skip all test functions of a class or module

你可以对一个class使用`skipif` marker.

```
@pytest.mark.skipif(sys.platform == 'win32',
                    reason='does not run on windows')
class TestPosixCalls(object):
    
    def test_function(self):
        "will not be setup or run under 'win32' platform"
```

### Skipping files or directories

...

### Skipping on a missing import dependency

你可以使用下面这个helper来确定是否有存在module缺失的情况.

```
docutils = pytest.importskip('docutils')
```

### Summary

下面是一个简单的总结：

1. 无条件地跳过一个module的所有tests：

    pytestmaker = pytest.mark.skip('all tests still WIP')

2. 根据某些条件，跳过一个模块的某些tests:

    pytestmarker = pytest.mark.skipif(sys.platform == 'win32', 'tests for linux only')

3. 如果import失败，则跳过一个模块的所有tests:

    pexpect = pytest.importskip('pexpect')


## XFail: mark test functions as expected to fail

你可以使用`xfail`标记，指明你期待一个test会失败:

```
@pytest.mark.xfail
def test_function():
    ...
```

另外，你也可以在test函数内部根据条件调用xfail.

```
def test_function():
    if not valid_config():
        pytest.xfail('failing configuration (but should work)')
```

### strict parameter

...

### reason 

...
