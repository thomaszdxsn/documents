# Advanced Usage of Pipenv

## Specifying Package Indexes

如果你想通过一个特定的软件包站点来下载，可以这样:

```python
[[source]]
url = "https://pypi.python.org/simple"
verify_ssl = true
name = "pypi"

[[source]]
url = "http://pypi.home.kennethreitz.org/simple"
verify_ssl = false
name = "home"

[dev-packages]

[packages]
requests = {version="*", index="home"}
maya = {version="*", index="pypi"}
records = "*"
```

## Specifying Basically Anything

如果你想要让一个指定的软件包只在特定的系统中被安装，你可以使用[PEP508 specifiers](https://www.python.org/dev/peps/pep-0508/)来实现。

下面是一个`Pipfile`示例，它只会在Windos系统下面安装`pywinusb`:

```txt
[[source]]
url = "https://pypi.python.org/simple"
verify_ssl = true
name = "pypi"

[packages]
requests = "*"
pywinusb = {version = "*", os_name = "== 'windows'"}
```

下面是一个更复杂的例子：

```txt
[[source]]
url = "https://pypi.python.org/simple"
verify_ssl = true

[packages]
unittest2 = {version = ">=1.0,<3.0", markers="python_version < '2.7.9' or (python_version >= '3.0' and python_version < '3.4')"}
```

## Deploying System Dependencies

你可以告诉pipenv来将一个Pipfile的内容安装到父系统中(使用`--system`):

`$ pipenv install --system`

这对于Pass和Docker会很有用。

部署的时候可以使用`--deploy`:

`$ pipenv install --system --depoly`

如果`Pipfile.lock`过期会失败，而不是生成一个新的。

## pipenv and conda

想要将pipenv和conda绑定：

`$ pipenv install --python=/path/to/anaconda/python`

## Generating a requirements.txt

你可以将`Pipfile`和`Pipfile.lock`轻松的转换为一个`requirements.txt`文件。

让我们使用下面这个`Pipfile`:

```txt
[[source]]
url = "https://pypi.python.org/simple"
verify_ssl = true

[packages]
requests = {version="*"}
```

生成的`requirements.txt`文件为:

```shell
$ pipenv lock -r
chardet==3.0.4 --hash=sha256:fc323ffcaeaed0e0a02bf4d117757b98aed530d9ed4531e3e15460124c106691  --hash=sha256:84ab92ed1c4d4f16916e05906b6b75a6c0fb5db821cc65e70cbd64a3e2a5eaae
requests==2.18.4 --hash=sha256:6a1b267aa90cac58ac3a765d067950e7dbbf75b1da07e895d1f594193a40a38b  --hash=sha256:9c443e7324ba5b85070c4a818ade28bfabedf16ea10206da1132edaa6dda237e
certifi==2017.7.27.1 --hash=sha256:54a07c09c586b0e4c619f02a5e94e36619da8e2b053e20f594348c0611803704  --hash=sha256:40523d2efb60523e113b44602298f0960e900388cf3bb6043f645cf57ea9e3f5
idna==2.6 --hash=sha256:8c7309c718f94b3a625cb648ace320157ad16ff131ae0af362c9f21b80ef6ec4  --hash=sha256:2c6a5de3089009e3da7c5dde64a141dbc8551d5b7f6cf4ed7c2568d0cc520a8f
urllib3==1.22 --hash=sha256:06330f386d6e4b195fbfc736b297f58c5a892e4440e54d294d7004e3a9bbea1b  --hash=sha256:cc44da8e1145637334317feebd728bd869a35285b93cbb4cca2577da7e62db4f
```

如果你只想把dev的软件包来生成一个`requirements.txt`：

```txt
[[source]]
url = "https://pypi.python.org/simple"
verify_ssl = true

[dev-packages]
pytest = {version="*"}
```

生成一个`requirements.txt`:

```txt
$ pipenv lock -r -d
py==1.4.34 --hash=sha256:2ccb79b01769d99115aa600d7eed99f524bf752bba8f041dc1c184853514655a  --hash=sha256:0f2d585d22050e90c7d293b6451c83db097df77871974d90efd5a30dc12fcde3
pytest==3.2.3 --hash=sha256:81a25f36a97da3313e1125fce9e7bbbba565bc7fec3c5beb14c262ddab238ac1  --hash=sha256:27fa6617efc2869d3e969a3e75ec060375bfb28831ade8b5cdd68da3a741dc3c
```

## Detection of Security Vulnerabilities

pipenv包含安全的软件包，可以用它扫描你的依赖graph来获取安全漏洞。

例如：

```txt
$ cat Pipfile
[packages]
django = "==1.10.1"

$ pipenv check
Checking PEP 508 requirements…
Passed!
Checking installed package safety…

33075: django >=1.10,<1.10.3 resolved (1.10.1 installed)!
Django before 1.8.x before 1.8.16, 1.9.x before 1.9.11, and 1.10.x before 1.10.3, when settings.DEBUG is True, allow remote attackers to conduct DNS rebinding attacks by leveraging failure to validate the HTTP Host header against settings.ALLOWED_HOSTS.

33076: django >=1.10,<1.10.3 resolved (1.10.1 installed)!
Django 1.8.x before 1.8.16, 1.9.x before 1.9.11, and 1.10.x before 1.10.3 use a hardcoded password for a temporary database user created when running tests with an Oracle database, which makes it easier for remote attackers to obtain access to the database server by leveraging failure to manually specify a password in the database settings TEST dictionary.

33300: django >=1.10,<1.10.7 resolved (1.10.1 installed)!
CVE-2017-7233: Open redirect and possible XSS attack via user-supplied numeric redirect URLs
============================================================================================

Django relies on user input in some cases  (e.g.
:func:`django.contrib.auth.views.login` and :doc:`i18n </topics/i18n/index>`)
to redirect the user to an "on success" URL. The security check for these
redirects (namely ``django.utils.http.is_safe_url()``) considered some numeric
URLs (e.g. ``http:999999999``) "safe" when they shouldn't be.

Also, if a developer relies on ``is_safe_url()`` to provide safe redirect
targets and puts such a URL into a link, they could suffer from an XSS attack.

CVE-2017-7234: Open redirect vulnerability in ``django.views.static.serve()``
=============================================================================

A maliciously crafted URL to a Django site using the
:func:`~django.views.static.serve` view could redirect to any other domain. The
view no longer does any redirects as they don't provide any known, useful
functionality.

Note, however, that this view has always carried a warning that it is not
hardened for production use and should be used only as a development aid.
```

## Open a Module in Your Editor

pipenv允许你开启任何安装过的模块，可以使用`$ pipenv open`命令：

```shell
$ pipenv install -e git+https://github.com/kennethreitz/background.git#egg=background
Installing -e git+https://github.com/kennethreitz/background.git#egg=background…
...
Updated Pipfile.lock!

$ pipenv open background
Opening '/Users/kennethreitz/.local/share/virtualenvs/hmm-mGOawwm_/src/background/background.py' in your EDITOR.
```

这可以让你轻松的阅读源码(默认使用环境变量`EDITOR`来打开源码)，无需再去github阅读。

## Automatic Python Installation

如果你已经安装了`pyenv`，那么在你没有一个特定的Python版本时候，`pyenv`会自动询问你是否要安装这个版本。

这是一个牛X的特性，我们对这个实现的这个功能很骄傲：

```shell
$ cat Pipfile
[[source]]
url = "https://pypi.python.org/simple"
verify_ssl = true

[dev-packages]

[packages]
requests = "*"

[requires]
python_version = "3.6"

$ pipenv install
Warning: Python 3.6 was not found on your system…
Would you like us to install latest CPython 3.6 with pyenv? [Y/n]: y
Installing CPython 3.6.2 with pyenv (this may take a few minutes)…
...
Making Python installation global…
Creating a virtualenv for this project…
Using /Users/kennethreitz/.pyenv/shims/python3 to create virtualenv…
...
No package provided, installing all dependencies.
...
Installing dependencies from Pipfile.lock…
🐍   ❒❒❒❒❒❒❒❒❒❒❒❒❒❒❒❒❒❒❒❒❒❒❒❒❒❒❒❒❒❒❒❒ 5/5 — 00:00:03
To activate this project's virtualenv, run the following:
 $ pipenv shell
```

## Automatic Loading of `.env`

如果你的项目中有`.env`文件，`$ pipenv shell`和`$ pipenv run`将会自动读取它。

```shell
$ cat .env
HELLO=WORLD⏎

$ pipenv run python
Loading .env environment variables…
Python 2.7.13 (default, Jul 18 2017, 09:17:00)
[GCC 4.2.1 Compatible Apple LLVM 8.1.0 (clang-802.0.42)] on darwin
Type "help", "copyright", "credits" or "license" for more information.
>>> import os
>>> os.environ['HELLO']
'WORLD'
```

这个功能很有用，可以让一些生产级的验证信息脱离出代码库。我们不建议你将`.env`文件提交到版本控制。

如果你的`.env`文件在别的地方，你可以使用环境变量来指定它的位置:

`$ PIPENV_DOTENV_LOCATION=/path/to/.env pipenv shell`

## Configuration With Environment Variables

`pipenv`的很多选项都可以通过环境变量来设置：

- `PIPENV_DEFAULT_PYTHON_VERSION` - 创建一个新的virtualenv时默认使用的Python版本(默认为`3.6`)
- `PIPENV_SHELL_FANCY` - 在使用`pipenv shell`的时候是否使用fancy模式
- `PIPENV_VENV_IN_PROJECT` - 如果设置，在你项目目录中使用`.venv`存储virtualenv，而不是全局的virtualenv管理器`pew`
- `PIPENV_COLORBIND` - 关闭终端输出的颜色
- `PIPENV_NOSPIN` - 关闭终端的spinner，可以有更清楚的日志
- `PIPENV_MAX_DEPTH` - 设置搜索`Pipfile`文件的最大递归深度
- `PIPENV_TIMEOUT` - 设置pipenv创建virtualenv的超时时间
- `PIPENV_IGNORE_VIRTUALENVS` - 设置禁止默认使用virtualenv
- `PIPENV_PIPFILE` - 指定Pipfile的位置

## Custom Virtual Environment Location

`pipenv`依赖的`pew`会根据`WORKON_HOME`这个环境变量来决定virtuanenv存放的位置，例如：

`export WORKON_HOME=~/.venvs`






