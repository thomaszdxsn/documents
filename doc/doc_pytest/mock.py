# Monkeypatching/mocking modules and environments

有一些测试需要访问全局配置，或者一些代码很难执行，因为需要网络访问。

这个时候，就需要`monkeypatch`这个fixture来帮助你安全的set/delete一个属性，
字典item或者环境变量，或者修改sys.path。

## Simple example: monkeypatching functions

如果你想要让`os.expanduser`返回一个确定的dict，你可以使用`monkeypatch.setattr()`
方法来为这个函数打上布丁，然后在调用它.

```python
# test_module.py

import os.path

def getssh():
    return os.path.join(os.path.expanduser('~admin'), '.ssh')


def test_mytest(monkeypatch):
    def mockreturn(path):
        return '/abc'
    monkeypatch.setattr(os.path, 'expanduser', mockreturn)
    x = getssh()
    assert x == '/abc/.ssh'
```

## example: preventing 'request' from remote operations

如果你不像让`requests`库在你的所有tests中执行http请求，你可以这样:

```pyhton
# conftest.py

import pytest


@pytest.fixture(autouse=True)
def no_requests(monkeypatch):
    monkeypatch.delattr('requests.sessions.Session.request')
```

这个autouse的fixture将会在每个test函数中执行，将会删除方法`request.session.Session.request`，
所以任何试图创建http请求的test都会失败.


