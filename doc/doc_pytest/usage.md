# Usage and Invocations

## Calling pytest through `python -m pytest`

你可以通过python解释器来调用test：

`python -m pytest [...]`

这等同于直接调用`pytest [...]`，除了通过`python`调用时会把
当前目录加入到`sys.path`.

## Possible exit codes

运行`pytest`的退出码总共有6种：

0. 所有的tests都收集并且成功通过.
1. tests都被收集，不过一些tests失败.
2. test执行时被用户终端.
3. 在执行tests时发生了内部错误.
4. pytest命令行使用错误.
5. 没有收集到tests.

## Getting help on version, option names, environment variables

```python
pytest --version    # 展示当前的pytest版本
pytest --fixtures   # 展示内置的fitures
pytest -h | --help  # 展示命令行的帮助文本和配置文件选项
```

## Stopping after the first (or N) failures

想要在测试失败时中止继续测试:

```python
pytest -x           # 在首个失败时停止
pytest --maxfail=2  # 在两个失败时停止
```

## Specifying tests / selecting  tests

Pytest支持多种方式从命令行来运行和选择tests。

- 运行一个模块的tests

    `pytest test_mod.py`

- 运行一个目录的tests

    `pytest test_dir/`

- 运行一个关键字表达式tests

    `pytest -k "MyClass and not method"`

    这个命令会运行符合给定表达式的测试,可以包含Python操作符，使用的文件名，
    类名，函数名作为比那里。上面的例子将会运行`TestMyClass.test_something`
    而不会运行`TestMyClass.test_method_simple`.

- 通过node-id来运行tests

    每个收集来的test都有一个唯一的`nodeid`，它由库文件名，函数名来组成：

    `pytest test_mod.py::test_fun`

    运行一个方法tests:
    
    `pytest test_mod.py::TestClass::test_method`

- 运行带有标记marker表达式的tests

    `pytest -m slow`

    这个命令会运行装饰有`@pytest.mark.slow`的tests.

## Modifying Python traceback printing

修改traceback打印信息的示例：

```python
pytest --showlocals | -l     # 在tracebacks中显示局部变量

pytest --tb=auto             # [默认] 自动选择"long"或者"short"

pytest --tb=long             # 完整的traceback
pytest --tb=short            # 简短的traceback
pytest --tb=line             # 每个failure只显示一行
pytest --tb=native           # 使用Python标准库的格式
pytest --no                  # 不显示traceback
```

## Dropping to PDB(Python Debugger) on failures

Python有一个内置的debugger，叫做`PDB`，pytest允许将PDB插入到命令行中.

`pytest --pdb`

这会在每次失败的时候调用Python debugger。通常你会想把它和`-x`组合一起用:

```python
pytest -x -pdb
pytest --pdb --maxfail=3
```

## Setting breakpoints

想要在你的代码中设置断点，你需要使用`import pdb; pdb.set_trace()`.

## Profiling test execution duration

想要获取运行最慢的10个tests:

`pytest --durations=10`

## Creating JUnitXML format files

想要创建一个文件，让Jenkins或者其它的持续继承服务器可以阅读它，你可以这么来调用：

`pytest --junitxml=path`

这会在`path`中创建一个XML文件.

## Creating resultlog format files

已经废弃.

## Sending test report to online pastebin service

为每个失败的test都创建一个URL

`pytest --pastebin=failed`

## Disabling plugins

想要禁用特定的插件，可以使用`-p`选项，加上`no`前缀:

`pytest -p no:doctest`

## Calling pytest from Python code

你可以指甲在Python代码中调用`pytest`:

`pytest.main()`


