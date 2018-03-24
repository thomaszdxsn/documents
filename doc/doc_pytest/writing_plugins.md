# Writing plugins

一个插件包含一个或多个钩子函数。

- 内部插件：读取pytest内部的`_pytest`目录.
- 外部插件：通过setuptools entry points发现的模块.
- conftest.py插件：在测试目录中自动发现的模块.

## Plugin discover order at tool startup

`pytest`按照如下顺序来读取plugin模块:

- 读取所有的内置plugin
- 读取所有通过setuptools entry point注册的插件.
- 通过`-p name`指定的插件
- 读取`conftest.py`文件中的所有插件.
- 递归读取`conftest.py`中指定的`pytest_plugins`变量

## conftest.py: local pre-directory plugins

本地的`conftest.py`，包含了目录级别的钩子。

下面是一个实现了`pytest_runtest_setup`钩子的示例:

```
a/conftest.py
    def pytest_runtest_setup(item):
        print('setting up', item)


a/test_sub.py
    def test_sub():
        pass


test_flat.py
    def test_flat():
        pass
```

下面是你运行的情况:

```
pytest test_flat.py   # 不会显示"setting up"
pytest a/test_sub.py  # 显示 "setting up"
```

## Writing your own plugin

如果你想要编写自定义plugin，那么最好的学习方式就是阅读别人写的代码.


