# Overview of docker-compose CLI

## Command options overview and help

## Compose CLI environment variables

一些环境变量可以影响Docker compose的命令行行为。

以`DOCKER_`开头的变量可以用来配置Docker CLI。

### `COMPOSE_PROJECT_NAME`

设置项目名称。

这个项目名称会前置到service名称和容器名称中。

例如，如果你的项目名称为`myapp`，拥有两个service：`db`, `web`。那么compose启动
的容器就会是`myapp_db_1`和`myapp_web_1`.

这个变量是可选的。如果你没有设置，那么就会默认使用项目目录的`basename`来作为项目
名称。

### `COMPOSE_FILE`

指定Compose file的路径。

如果没有提供，Compose将会在当前目录查找`docker-compose.yml`文件，如果没找到
会向上递归，在父目录中进行查找，知道找到为止。

这个变量支持多个Compose文件，通过路径分隔符来分割(在类unix系统中以`:`作为分隔符，
在windows中以`;`作为分隔符).

### `COMPOSE_API_VERSION`

Docker API接受的请求必须指定version。

如果你在使用`docker-compose`的时候出现错误:`client and server don't have same version`.
你就知道是这个环境变量的问题了。

### `DOCKER_HOST`

设置`docker` daemon的URL。默认为`unix:///var/run/docker.sock`

### `DOCKER_CERT_PATH`

配置用于TLS验证的`ca.pem`, `cert.pem`以及`key.pem`文件路径。默认为`~/.docker`.

### `COMPOSE_HTTP_TIMEOUT`

配置对Docker daemon请求的超时时间。默认为60s。

### `COMPOSE_TLS_VERSION`

配置TLS版本.默认为`TLSv1`，支持的值包括: `TLSv1`, `TLSv1_1`和`TLSv1_2`.

### `COMPOSE_CONVERT_WINDOWS_PATHS`

...

### `COMPOSE_PATH_SEPERATOR`

如果设置了这个变量，将会用它的值作为路径分隔符。

### `COMPOSE_FORCE_WINDOWS_HOST`

...

### `COMPOSE_IGNORE_ORPHANS`

如果设置为true(1)，那么compose不会试图探测项目的“孤儿”容器。

### `COMPOSE_PARALLEL_LIMIT`

设置并行的compose操作限制。默认为64。

### `COMPOSE_INTERACTIVE_NO_CLI`

...


## build

## bundle

通过compose file生成分布式应用捆束(Distributed Application Bundle, DAB).

## config

...
    
