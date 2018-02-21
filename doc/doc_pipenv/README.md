# Pipenv: Python Development Workflow for Humans

**Pipenv -- Python官方推荐的打包工具。**

Pipenv是一个目标为把最好的软件打包思想(如bundler, composer, npm, cargo...)带入到Python世界的一个工具。

它会为你的项目自动创建并管理一个virtualenv，以及在你安装/卸载软件包的时候自动修改`Pipfile`。而且它会生产一个`Pipfile.lock`.

![pyenv.gif](./pipenv.gif)

使用pipenv之后：

- 你不需要再单独的使用`pip`和`virtualenv`了.
- 管理一个`requirements.txt`文件会有很多(潜在的)问题，所以pipenv使用`Pipfile`和`Pipfile.lock`来管理软件包.
- 出于安全等因素，到处都用到了hash.
- 你可以观察你项目的依赖图(`pipenv graph`).
- 通过读取`.env`文件来实现流线型的开发工作流.

## Installation

`$ pip install pipenv`

## User Testimonials

- Jannis Leidel, former pip maintainer

    Pipenv is the porcelain I always wanted to build for pip. It fits my brain and mostly replaces virtualenvwrapper and manual pip calls for me. Use it.

- Justin Myles Holmes

    Pipenv is finally an abstraction meant to engage the mind instead of merely the filesystem.


- Isaac Sanders
    
    Pipenv is literally the best thing about my day today. Thanks, Kenneth!

## Features

- 使用完全确定性的构件，可以指定你需要的东西.
- 为上锁的依赖生成和检查文件hash
- 如果使用了`pyenv`，自动安装要求的Python
- 通过查看`Pipfile`，自动查找你的项目主目录
- 如果不存在，自动创建一个`Pipfile`
- 在一个标准位置自动创建一个virtualenv
- 在安装/卸载软件包的时候，自动将它从Pipfile中添加/移除
- 如果存在，自动读取`.env`文件

主要的命令是`install`, `uninstall`，以及`lock`(它会生成一个`Pipfile.lock`文件)。主要目的是为了代替`$ pip install`的用法，和手动创建virtualenv的用法。(想要激活一个virtualenv，可以执行命令`$ pipenv shell`)

### Basic concepts

- 如果不存在，会自动创建一个virtualenv
- 如果没有为`install`传入参数，将会把`[packages]`中的所有软件包都给安装
- 想要初始化一个Python3虚拟环境，执行`$ pipenv --three`
- 想要初始化一个Python2虚拟环境，执行`$ pipenv --two`
- 否则，将会使用默认的`virtualenv`

### Other Commands

- `shell`：可以使用激活的virtualenv来生产一个shell
- `run`: 将会用给定的virtualenv来运行一个命令
- `check`: 断言当前环境下是否有`PEP508`的requirements
- `graph`: 将会把你所有安装的依赖打印出来

### Shell Completion

例如，可以将它放到你的`~/.config/fish/completions/pipenv.fish`:

`eval (pipenv --completion)`

另外也可以将它放到你的`.bashrc`或者`.bash_profile`:

`eval "$(pipenv --completion)"`

现在开启了shell补全。另外还有一个[fish plugin](https://github.com/fisherman/pipenv)(需要安装fish shell)

## Usage

```shell
$ pipenv
Usage: pipenv [OPTIONS] COMMAND [ARGS]...

Options:
    --update        Update Pipenv & pip to latest.
    --where         Output project home information.
    --venv          Output virtualenv information.
    --py            Output Python interpreter information.
    --envs          Output Environment Variable options.
    --rm            Remove the virtualenv.
    --bare          Minimal output.
    --completion    Ouput cmpletion (to be eval'd).
    --man           Display manpage.
    --three / --two Use Python3/2 when creating virtualenv.
    --python TEXT   Specify which version of Python virtualenv should use.
    --site-packages Enable site-packages for the virtualenv.
    --jumbotron     An easter egg, effectively.
    --version       Show the version and text.
    -h, --help      Show this message and exit.


Usage Examples:
    Create a new project using Python3.6, specifically:
    $ pipenv --python3.6

    Install all dependencies for a project (including dev):
    $ pipenv install --dev
    
    Create a lockfile containing pre-releases:
    $ pipenv lock --pre

    Show a graph of your installed dependencies:
    $ pipenv graph

    Check your installed dependencies for security vulnerabilities:
    $ pipenv check

    Install a local setup.py into your virtual environment/Pipfile:
    $ pipenv install -e .

Commands:
  check      Checks for security vulnerabilities and...
  graph      Displays currently–installed dependency graph...
  install    Installs provided packages and adds them to...
  lock       Generates Pipfile.lock.
  open       View a given module in your editor.
  run        Spawns a command installed into the...
  shell      Spawns a shell within the virtualenv.
  uninstall  Un-installs a provided package and removes it...
  update     Uninstalls all packages, and re-installs...
```

定位一个项目:

```shell
$ pipenv --where
/Users/kennethreitz/Library/Mobile Documents/com~apple~CloudDocs/repos/kr/pipenv/test
```

定位virtualenv：

```shell
$ pipenv --venv
/Users/kennethreitz/.local/share/virtualenvs/test-Skyy4vre
```

定位Python解释器：

```shell
$ pipenv --py
/Users/kennethreitz/.local/share/virtualenvs/test-Skyy4vre/bin/python
```

安装软件包：

```shell
$ pipenv install
Creating a virtualenv for this project...
...
No package provided, installing all dependencies.
Virtualenv location: /Users/kennethreitz/.local/share/virtualenvs/test-EJkjoYts
Installing dependencies from Pipfile.lock...
...

To activate this project's virtualenv, run the following:
$ pipenv shell
```

安装一个dev的依赖：

```shell
$ pipenv install pytest --dev
Installing pytest...
...
Adding pytest to Pipfile's [dev-packages]...
```

查看依赖图:

```shell
$ pipenv graph
requests==2.18.4
  - certifi [required: >=2017.4.17, installed: 2017.7.27.1]
  - chardet [required: >=3.0.2,<3.1.0, installed: 3.0.4]
  - idna [required: >=2.5,<2.7, installed: 2.6]
  - urllib3 [required: <1.23,>=1.21.1, installed: 1.22]
```

生成一个lockfile：

```shell
$ pipenv lock
Assuring all dependencies from Pipfile are installed...
Locking [dev-packages] dependencies...
Locking [packages] dependencies...
Note: your project now has only default [packages] installed.
To install [dev-packages], run: $ pipenv install --dev
```

安装所有的dev依赖：

```shell
$ pipenv install --dev
Pipfile found at /Users/kennethreitz/repos/kr/pip2/test/Pipfile. Considering this to be the project home.
Pipfile.lock out of date, updating...
Assuring all dependencies from Pipfile are installed...
Locking [dev-packages] dependencies...
Locking [packages] dependencies...
```

卸载一切:

```shell
$ pipenv uninstall --all
No package provided, un-installing all dependencies.
Found 25 installed package(s), purging...
...
Environment now purged and fresh!
```

使用shell

```shell
$ pipenv shell
Loading .env environment variables…
Launching subshell in virtual environment. Type 'exit' or 'Ctrl+D' to return.
$ ▯
```

## Documentation

[http://pipenv.org/](http://pipenv.org/)