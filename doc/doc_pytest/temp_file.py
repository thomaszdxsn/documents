# Temporary directories and files

## The 'tmpdir' fixture

你可以使用`tmpdir` fixture来提供一个临时目录，作为测试使用。

`tmpdir`是一个`py.path.local`对象，你可以对它使用`os.path`的方法。

下面是一些例子:

```python
# test_tmpdir.py
def test_create_file(tmpdir):
    p = tmpdir.mkdir('sub').join('hello.txt')
    p.write('content')
    assert p.readr() == 'content'
    assert len(tmpdir.listdir()) == 1
    assert 0
```

我们故意使用`assert 0`抛出了错误，所以你会看到下面的输出:

```
$ pytest test_tmpdir.py
=========================== test session starts ============================
platform linux -- Python 3.x.y, pytest-3.x.y, py-1.x.y, pluggy-0.x.y
rootdir: $REGENDOC_TMPDIR, inifile:
collected 1 item

test_tmpdir.py F                                                     [100%]

================================= FAILURES =================================
_____________________________ test_create_file _____________________________

tmpdir = local('PYTEST_TMPDIR/test_create_file0')

    def test_create_file(tmpdir):
        p = tmpdir.mkdir("sub").join("hello.txt")
        p.write("content")
        assert p.read() == "content"
        assert len(tmpdir.listdir()) == 1
>       assert 0
E       assert 0

test_tmpdir.py:7: AssertionError
========================= 1 failed in 0.12 seconds =========================
```

## The 'tmpdir_factory' fixture

`tmpdir_factory` 是一个session域级别的fixture，可以用来创建任意数量的临时文件。

例如，假设你的test需要在硬盘中又一个巨大的image，它需要若干步骤来创建。

如果你使用`tmpdir` fixture，那么你就必须在每个test之前都单独的创建它。

```python
# conftest.py
import pytest


@pytest.fxiture(scope='session')
def image_file(tmpdir_factory):
    img = compute_expensive_image()
    fn = impdir_factory_mktemp('data').join('img.png')
    img.save(str(fn))
    return fn


def test_histogram(image_file):
    img = load_image(image_file)
```

## The default base temporary directory

...
