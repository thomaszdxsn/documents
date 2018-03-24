# pytest fixtures: explicit, modular, scalable

- fixtures有显式的名称，可以通过申明来使用，可以用在函数，模块，类，或者整个项目中.

- fixtures是通过模块来实现的，每个fixture name都会触发一个fixture function，fixture
本身也可以相互使用。

- fixture管理可以从简单的单元伸缩为复杂的功能测试，允许通过配置和组件选项来将
fixtures和tests进行参数化，或者在函数，模块之前重用fixtures。

## Fixtures as Function arguments

test函数可以接受fixture对象，将它们的名称作为参数传入。

对于每个参数名，都会提供与之相匹配的fixture对象。

Fixture函数可以通过`@pytest.fixture`装饰来被识别。

让我们来看一下一个简单的test模块，它包含了一个fixture，一个test函数使用这个fixture：

```python
# test_smtpsimple.py

import pytest


@pytest.fixture
def smtp():
    import smtplib
    return smtplib.SMTP('smtp.gmil.com', 587, timeout=5)

def test_ehlo(smtp):
    response, msg = smtp.ehlo()
    assert response == 250
    assert 0    # 只是处于demo需要
```

下面是这个test的输出:

```
$ pytest test_smtpsimple.py
=========================== test session starts ============================
platform linux -- Python 3.x.y, pytest-3.x.y, py-1.x.y, pluggy-0.x.y
rootdir: $REGENDOC_TMPDIR, inifile:
collected 1 item

test_smtpsimple.py F                                                 [100%]

================================= FAILURES =================================
________________________________ test_ehlo _________________________________

smtp = <smtplib.SMTP object at 0xdeadbeef>

    def test_ehlo(smtp):
        response, msg = smtp.ehlo()
        assert response == 250
>       assert 0 # for demo purposes
E       assert 0

test_smtpsimple.py:11: AssertionError
========================= 1 failed in 0.12 seconds =========================
```

## Fixtures: a prime example of dependency injection

使用pytest的fixture不需要操心import/setup/cleanup这些细节。

它是`依赖注入`的绝佳例子，fixture函数可以看作是injector，测试函数可以看作是
fixture对象的消耗者.

## conftest.py: sharing fixture function

如果你觉得你有多个test文件需要用到一个fixture函数，你可以将它放在一个`conftest.py`文件中。

你不需要将这个模块import到你需要使用的文件中。fixture函数的查找过程从test classes
开始，然后是test模块，然后是`conftest.py`文件，最后是第三方插件.

你同样可以使用`conftest.py`文件来实现本地插件.

## Sharing test data

如果你想要让你的test共享使用文件中的测试数据，一个很好的办法就是用一个fixture
函数来读取并返回它们。这其中可以用到pytest的缓存机制。

另一个方法就是把数据文件放到tests文件夹中，有很多插件可以处理这些数据文件。

## Scope: sharing a fixture instance across tests in a class, module or session

下面的示例中，将fixture函数放在一个单独的`conftest.py`文件，同个目录的多个
test模块都可以访问这个fixture函数:

```python
# conftest.py
import pytest
import smtpli


@pytest.fixture(scope='module')
def smtp():
    return smtplib.SMTP('smtp.gmail.com', 587, timeout=5)
```

这个fixture的名字`smtp`，让你可以作为参数传入到test函数，或其它fixture函数中:

```python
# text_module.py

def test_ehlo(smtp):
    response, msg = smtp.ehlo()
    assert response == 250
    assert b"smtp.gmail.com" in msg
    assert 0 


def test_noop(smtp):
    response, msg = smtp.noop()
    assert response == 250
    assert 0
```

## Higher-scoped fixtures are instantiated first

在一个函数请求fixtures的时候，高级域的fixture会相比低级域的fixture更快实例化。

考虑下面的代码：

```python
@pytest.fixture(scope='session')
def s1():
    pass


@pytest.fixture(scope='module')
def m1():
    pass


@pytest.fixture
def f1(tmpdir):
    pass


@pytest.fixture
def f2():
    pass


def test_foo(f1, m1, f2, s1):
    ...
```

`test_foo`对fixtures的请求将会遵循下列顺序:

1. `s1`: 最高域的fixture
2. `m1`: 第二高域的fixture
3. `tmpdir`: 是一个函数级fixture
4. `f1`: `test_foo`参数列表中的第一个函数域fixture
5. `f2`: `test_foo`参数列表中的最后一个函数域fixture

## Fixture finaliztion / executing teardown code

如果fixture不是session域级别的，pytest支持为这些fixture提供清理代码。

不过要使用`yield`来代替`return`，在`yield`之后的代码都会看作是清理代码。

```python
# conftest.py

import smtplib

import pytest


@pytest.fixture(scope='module')
def smtp():
    smtp = smtplib.SMTP('smtp.gmail.com', 587, timeout=5)
    yield smtp
    print('teardown smtp')
    smtp.close()
```

让我们执行它:

```
$ pytest -s -q --tb=no
FFteardown smtp

2 failed in 0.12 seconds
```

## Fixtures can introspect the requesting test context

Fixture函数可以接受request对象来监控请求的test函数，类或者模块context。

```python
# conftext.py

import pytest
import smtplib


@pytest.fixture(scope='module')
def smtp(request):
    server = getattr(request.module, 'smtpserver', 'smtp.gmail.com')
    smtp = smtplib.SMTP(server, 587, timeout=5)
    yield smtp
    print('finalizing %s (%s)' %(smtp, server))
    smtp.close()
```

`request.module`这个属性将会取决于请求fixture的对象，如果没有则使用默认值。

```
# content of test_anothersmtp.py

smtpserver = "mail.python.org"  # will be read by smtp fixture

def test_showhelo(smtp):
    assert 0, smtp.helo()
```

## Prametrizing fixtures

...
