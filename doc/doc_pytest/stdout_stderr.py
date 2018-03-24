# Capturing of the stdout/stderr output

## Default stdout/stderr/stdin capturing behaviour

在测试期间，发送到`stdout`和`stderr`的输出都会被捕获。

如果一个测试或者一个setup方法失败了，可以根据捕获的输出来判断是什么原因。这个
行为可以通过`--show-capture`来激活。

除此之外，`stdin`可以设置为`null`对象，对它的读取操作都会失败。

默认捕获是通过写入一个底层的文件描述符来实现的。这可以允许你捕获简单的print
语句，以及subprocess的输出。

## Setting capturing methods or disabling cpaturing

在`pytest`中，有两种方式可以执行捕获:

- 文件描述符级别的捕获(默认): 所有的写操作都会被操作系统的文件描述符1和2给捕获
- `sys`级别的捕获：只有写入到`Python`文件`sys.stdout`和`sys.stderr`会被捕获。

你可以通过下面的命令行来进行指定：

```python
pytest -s
pytest --capture=sys
pytest --capture=fd
```

## Using print statements for debugging

默认的捕获是可以直接打印它们的:

```python
# test_module.py

def setup_function(function):
    print("setting up %s" % function)


def test_func1():
    assert True


def test_func2():
    assert False
```

运行这个模块，你会看到：

```
$ pytest
=========================== test session starts ============================
platform linux -- Python 3.x.y, pytest-3.x.y, py-1.x.y, pluggy-0.x.y
rootdir: $REGENDOC_TMPDIR, inifile:
collected 2 items

test_module.py .F                                                    [100%]

================================= FAILURES =================================
________________________________ test_func2 ________________________________

    def test_func2():
>       assert False
E       assert False

test_module.py:9: AssertionError
-------------------------- Captured stdout setup ---------------------------
setting up <function test_func2 at 0xdeadbeef>
==================== 1 failed, 1 passed in 0.12 seconds ====================
```

## Accessing captured output from a test function

`capsys`, `capsysbinary`, `capfd` 和 `capfdbinary` 这些fixture可以运行test函数
访问stdout/stderr的输出。

```python
def test_myoutput(capsys):
    print('hello')
    sys.stderr.write('world\n')
    captured = capsys.readouterr()
    assert captured.out == 'hello\n'
    assert captured.err == 'world\n'
    print('next')
    captured = capsys.readouterr()
    assert captured.out = 'next\n'
```


