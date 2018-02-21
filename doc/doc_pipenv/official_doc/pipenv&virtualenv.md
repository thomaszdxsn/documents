## Pipenv & Virtual Environments

这篇教程带你安装和使用Python的软件包。

它会告诉你如何安装和使用一些必须的工具以及推荐给你一套最佳实践。记住，Python可以做很多事情，你想要如何管理你的依赖通常基于你想要怎么发布你的软件。这篇教程更适用于网络应用的开发和部署，但是也适用于任何其它应用项目的管理和测试。

### Make sure you've got Python & pip

在继续读下去之前，取保你可以通过命令行来访问Python：

`$ python --version`

你应该看到一些输出，比如`3.6.2`。否则，你应该去[https://python.org/](https://python.org/)下载安装Python发布版。

另外，你应该确保安装了`pip`，你可以这样来检查:

```shell
$ pip --version
pip 9.0.1
```

如果你从https://python.org/下载的Python，那么这个软件包应该已经自动安装了。否则你应该试一下:

`$ python -m ensurepip`

### Installing Pipenv

**Pipenv**是Python项目的依赖管理器。如果你熟悉Node.js的`npm`或者Ruby的`bundler`，你会发现pipenv的设计哲学和它们类似。pip可以安装Python软件包，而更推荐使用pipenv作为一个更高层面的依赖管理。

使用`pip`来安装`pipenv`:

`$ pip install pipenv`

### Installing packages for your project

Pipenv基于每个项目的基础来管理依赖。想要安装软件包，那么可以进入你的项目目录并执行：

```shell
$ cd myproject
$ pipenv install requests
```

pipenv会帮你安装`requests`并且在这个项目目录中为你创建一个`Pipfile`。Pipfile文件用来追踪依赖的改动，让你可以将这个项目分享给别人的时候让他可以轻松的重新安装这些依赖。你应该看到类似以下的输出：

```shell
Creating a Pipfile for this project...
Creating a virtualenv for this project...
Using base prefix '/usr/local/Cellar/python3/3.6.2/Frameworks/Python.framework/Versions/3.6'
New python executable in ~/.local/share/virtualenvs/tmp-agwWamBd/bin/python3.6
Also creating executable in ~/.local/share/virtualenvs/tmp-agwWamBd/bin/python
Installing setuptools, pip, wheel...done.

Virtualenv location: ~/.local/share/virtualenvs/tmp-agwWamBd
Installing requests...
Collecting requests
  Using cached requests-2.18.4-py2.py3-none-any.whl
Collecting idna<2.7,>=2.5 (from requests)
  Using cached idna-2.6-py2.py3-none-any.whl
Collecting urllib3<1.23,>=1.21.1 (from requests)
  Using cached urllib3-1.22-py2.py3-none-any.whl
Collecting chardet<3.1.0,>=3.0.2 (from requests)
  Using cached chardet-3.0.4-py2.py3-none-any.whl
Collecting certifi>=2017.4.17 (from requests)
  Using cached certifi-2017.7.27.1-py2.py3-none-any.whl
Installing collected packages: idna, urllib3, chardet, certifi, requests
Successfully installed certifi-2017.7.27.1 chardet-3.0.4 idna-2.6 requests-2.18.4 urllib3-1.22

Adding requests to Pipfile's [packages]...
P.S. You have excellent taste! ✨ 🍰 ✨
```

### Using installed packages

现在你已经安装了`requests`了，你可以创建一个简单的`main.py`文件并执行它：

```python
import requests

response = requests.get('https://httpbin.org/ip')

print('You IP is {0}'.format(response.json()['origin']))
```

然后你应该使用`pipenv run`来执行这个脚本:

`$ pipenv run python main.py`

你应该获得类似下面的输出：

`Your IP is 8.8.8.8`

使用`$ pipenv run`，确保你的脚本可以使用你安装的软件包。另外可以使用`$ pipenv shell`来生成一个新的shell，让所有的命令都可以使用你安装的软件包。

### Next steps

恭喜，你现在知道怎么安装和使用Python软件包了。

## Fancy Installation of Pipenv

pass

### Referentially Transparent Installation of Pipenv

pass

### Pragmatic Installation of Pipenv

pass

### Crude Installation of Pipenv

pass