# Basic Usage of Pipenv

## Example: Pipfile & Pipfile.lock

下面是`Pipfile`以及`Pipfile.lock`的示例。

### Exmaple: Pipfile

```txt
[[source]]
url = 'https://pypi.python.org/simple'
verify_ssl = true
name = 'pypi'

[packages]
requests = '*'

[dev-packages]
pytest = '*'
```

### Example: Pipfile.lock

```txt
{
    "_meta": {
        "hash": {
            "sha256": "8d14434df45e0ef884d6c3f6e8048ba72335637a8631cc44792f52fd20b6f97a"
        },
        "host-environment-markers": {
            "implementation_name": "cpython",
            "implementation_version": "3.6.1",
            "os_name": "posix",
            "platform_machine": "x86_64",
            "platform_python_implementation": "CPython",
            "platform_release": "16.7.0",
            "platform_system": "Darwin",
            "platform_version": "Darwin Kernel Version 16.7.0: Thu Jun 15 17:36:27 PDT 2017; root:xnu-3789.70.16~2/RELEASE_X86_64",
            "python_full_version": "3.6.1",
            "python_version": "3.6",
            "sys_platform": "darwin"
        },
        "pipfile-spec": 5,
        "requires": {},
        "sources": [
            {
                "name": "pypi",
                "url": "https://pypi.python.org/simple",
                "verify_ssl": true
            }
        ]
    },
    "default": {
        "certifi": {
            "hashes": [
                "sha256:54a07c09c586b0e4c619f02a5e94e36619da8e2b053e20f594348c0611803704",
                "sha256:40523d2efb60523e113b44602298f0960e900388cf3bb6043f645cf57ea9e3f5"
            ],
            "version": "==2017.7.27.1"
        },
        "chardet": {
            "hashes": [
                "sha256:fc323ffcaeaed0e0a02bf4d117757b98aed530d9ed4531e3e15460124c106691",
                "sha256:84ab92ed1c4d4f16916e05906b6b75a6c0fb5db821cc65e70cbd64a3e2a5eaae"
            ],
            "version": "==3.0.4"
        },
        "idna": {
            "hashes": [
                "sha256:8c7309c718f94b3a625cb648ace320157ad16ff131ae0af362c9f21b80ef6ec4",
                "sha256:2c6a5de3089009e3da7c5dde64a141dbc8551d5b7f6cf4ed7c2568d0cc520a8f"
            ],
            "version": "==2.6"
        },
        "requests": {
            "hashes": [
                "sha256:6a1b267aa90cac58ac3a765d067950e7dbbf75b1da07e895d1f594193a40a38b",
                "sha256:9c443e7324ba5b85070c4a818ade28bfabedf16ea10206da1132edaa6dda237e"
            ],
            "version": "==2.18.4"
        },
        "urllib3": {
            "hashes": [
                "sha256:06330f386d6e4b195fbfc736b297f58c5a892e4440e54d294d7004e3a9bbea1b",
                "sha256:cc44da8e1145637334317feebd728bd869a35285b93cbb4cca2577da7e62db4f"
            ],
            "version": "==1.22"
        }
    },
    "develop": {
        "py": {
            "hashes": [
                "sha256:2ccb79b01769d99115aa600d7eed99f524bf752bba8f041dc1c184853514655a",
                "sha256:0f2d585d22050e90c7d293b6451c83db097df77871974d90efd5a30dc12fcde3"
            ],
            "version": "==1.4.34"
        },
        "pytest": {
            "hashes": [
                "sha256:b84f554f8ddc23add65c411bf112b2d88e2489fd45f753b1cae5936358bdf314",
                "sha256:f46e49e0340a532764991c498244a60e3a37d7424a532b3ff1a6a7653f1a403a"
            ],
            "version": "==3.2.2"
        }
    }
}
```

## Example: Pipenv workflow

使用Pipfile来安装:

`$ pipenv install`

增加一个模块:

`$ pipenv install <module>`

根据已经安装的版本来创建一个`Pipfile.lock`:

`$ pipenv lock`

根据`Pipfile.lock`来安装：

`$ pipenv install --ignore-pipfile`

## Importing from requirements.txt

如果在执行`$ pipenv install`的时候你的项目目前只有一个`requirements.txt`文件，pipenv将会自动引入这个文件的内容并且帮你创建一个`Pipfile`.

你也可以使用命令`$ pipenv install -r path/to/requirements.txt`来引入指定的文件。

注意，在你引入一个requirements文件的时候，它通常会包含一个版本号码，如果你不想它出现在你的`Pipfile`中，那么需要手动将它移除。

## Specifying Version of a Package

想要让pipenv安装一个指定版本的库：

`$ pipenv install requests==2.13.0`

## Specifying Version of Python

可以使用你已经安装的一个特定Python版本，来创建一个新的virtualenv。可以使用`--python VERSION`这个选项。

比如，使用Python3:

`$ pipenv --python 3`

想要使用Python3.6:

`$ pipenv --python 3.6`

想要使用Python2.7.14:

`$ pipenv --python 2.7.14`

在给定一个Python版本后，pipenv会自动扫面你的系统并查找匹配这个给定版本的Python位置。

如果还没有`Pipfile`文件，将会为你创建这个文件，它会类似下面这样:

```shell
[[source]]
url = "https://pypi.python.org/simple"
verify_ssl = true

[dev-packages]

[packages]

[requires]
python_version = "3.6"
```

注意`[requires] python_version = "3.6"`。这个指定你应用将使用的Python版本，在之后执行`pipenv install`的时候将会被自动使用。

如果你没有在命令行指定Python版本，pipenv将会根据`[requires]`的`python_full_version`或者`python_version`来自动选择一个，或者选择你系统默认的`python`.

## Editable Dependencies

你可以告诉Pipenv将一个安装路径变为可编辑：

```shell
$ pipenv install '-e .' --dev

$ cat Pipfile
[dev-packages]
"e1839a8" = {path = ".", editable = true}
```

## Environment Management with Pipenv

使用pipenv时的三个最主要命令为: `$ pipenv install`，`$ pipenv uninstall`以及`$ pipenv lock`.

### `$ pipenv install`

`$ pipenv install`用来将软件包安装到你的pipenv虚拟环境并且更新到Pipfile中。

基础用法为：

`$ pipenv insatll [package names]`

用户可以添加以下3个额外的参数:

- `--two` - 让一个virtualenv使用`python2`link来安装
- `--three` - 让一个virtualenv使用`python3`link来安装
- `--python` - 让一个virtualenv使用`python`link来安装

> 警告
>
>> 这三种选项不应该一起使用。因为它们包含毁坏性，在将它替换为合适的版本之前会删除当前的virtualenv。

- `--dev` - 将`Pipfile.lock`的`develop`和`default`都安装
- `--system` - 使用系统命令`pip`，而不是虚拟环境中的那一个
- `--ignore-pipfile` - 忽略`Pipfile`，从`Pipfile.lock`中安装
- `--skip-lock` - 忽略`Pipfile.lock`，从`Pipfile`中安装。另外，不会把`Pipfile`的变动映射到`Pipfile.lock`.

### `$ pipenv uninstall`

`$ pipenv uninstall`支持`pipenv install`中的所有选项参数，以及两个额外的选项，`--all`和`--all-dev`.

- `--all` - 这个参数将会清除当前虚拟环境中的所有文件，不过不会修改`Pipfile`.
- `--all-dev` - 这个参数将会清除虚拟环境中的所有dev软件包，并且将它从`Pipfile`中移除.

### `$ pipenv lock`

`$ pipenv lock`用来创建一个`Pipfile.lock`，它会为你的项目声明所有的依赖(以及所有的子依赖)，以及它们的最新可用版本，以及当前下载文件的hash值。

## About Shell Configuration

在子shell中使用的时候经常会出现误配置，所以`$ pipenv shell -fancy`可能生成一个意料之外的结果。可以试试`$ pipenv shell`，它使用“兼容模式”，并且会试图生成一个subshell。

一个适当的shell配置通常只会在登陆的session中设置环境变量`PATH`，而不是每次生成subshell都设置。在fish中可以这样：

```shell
if status --is-login
    set -gx PATH /usr/local/bin $PATH
end
```

你可以在你的shell的`~/.profile`或者`~/.bashrc`来适当配置。

## A Note about VCS Dependencies

pipenv可以可以解决VCS依赖的子依赖，但是只有在它可编辑的时候才行，例如:

```shell
[packages]
requests = {git = "https://github.com/requests/requests.git", editable=true}
```

## Pipfile.lock Security Features

`Pipfile.lock`利用了一些`pip`中的安全特性。默认情况下，`Pipfile.lock`将会为每个下载的软件包生成一个sha256
哈希值。这可以让`pip`可以确保你在一个未经官方验证站定下载时软件的安全性。

我们推荐的部署方法是将一个开发环境改为一个生成环境。你可以使用`pipenv lock`来编译你开发环境的依赖，然后将编译后的`Pipfile.lock`来部署。
