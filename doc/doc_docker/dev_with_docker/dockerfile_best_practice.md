# Best practives for writing Dockerfiles

Docker可以通过读取一个`Dockerfile`的指令来自动创建image，Dockerfile是一个包含命令
的文本文件，根据命令的顺序来创建一个image。Dockerfile有一个特殊的格式，并且使用
一组特殊的指令。你可以在[Dockerfile reference](https://docs.docker.com/engine/reference/builder/)
学习它的基础知识。如果你刚开始编写Dockerfile，你应该先看完这篇文章。

这篇文档介绍了Docker推荐的best practice和方法论。

## General guidelines and recommendations

### Containers should be ephemeral

container应该尽可能的ephemeral(短暂的)。"ephemeral"，这里是指它可以以最小时间
停止，销毁和重新创建。

你可能需要看以下[这篇文章](https://12factor.net/processes)

### Use a .dockerignore file

在你使用命令`docker build`的时候，将会根据当前的工作目录来进行image的创建，
Dockerfile必须存在于这个工作目录下面。默认情况下，它假定是当前目录，但是
你可以通过`-f`选项来指定另一个位置。

不管Dockerfile存在于何处，这个目录下的所有内容都会发送到Dcoker daemon，作为
build context。

但是一些不需要加入的文件会增加image的大小。

你可以使用一个`dockerignore`文件来注明不需要加入的文件，就像`.gitignore`一样。

### Use multi-stage builds

如果你使用Docker17.05或者更高版本，你可以使用`multi-stage builds`来减少最终image
的大小。

image是直接建立在最终stage上面的，你可以利用build缓存来减少image的层数。

你的build stage可能包含多个层次:

- 安装建立你应用所需的工具
- 安装或更新库依赖
- 生成你的应用

建立一个go应用的Dockerfile可能看起来像这样:

```python
FROM golang:1.9.2-alpine3.6 AS build

# 安装创建项目所需的工具
# 我们需要运行`docker build --no-cache .`来更新这些依赖
RUN apk add --no-cache git
RUN go get github.com/golang/dep/cmd/dep

# Gopkg.toml和Gopkg.lock列出了项目的依赖
# 这些层是在Gopkg文件更新时需要重新build的
COPY Gopkg.lock Gopkg.toml /go/src/project/
WORKDIR /go/src/project/

# 安装库依赖
RUN dep ensure -vendor-only

# 复制整个项目并build它
# 这一层在项目文件发生改动时会重新built
COPY . /go/src/project/
RUN go build -o /bin/project

# 这是一个单层image的结果
FROM scratch
COPY --from=build /bin/project /biin/project
ENTRYPOINT ["/bin/project"]
CMD ["--help"]
```

### Avoid installing unnecessary packages

为了减少复杂性，依赖，文件大小以及创建时间，你应该避免安装不必要的软件包。
例如，你不应该在一个数据库image中包含一个文本编辑器。

### Each container should have only one concern

将应用解耦到多个container，可以让它更容易删除水平scale，以及可以利于container的重用。

例如，一个web应用栈可能由三个单独的container组成，每个都有它自己的image，用来
管理web应用，数据库，和内存缓存。

你可能听说过“每个进程一个container”的说法。这可能是一个好习惯，但是并不是硬性规定。

如果container之间互相依赖，你可以使用`Docker container networks`来确保container
之间可以通信。

### Minimize the number of layers

在Docker17.05之前，减少你image的层数是很重要的。

你可能需要以下建议

- 在Docker1.10以上的版本，只用`RUN`， `COPY`, `ADD`指令会创建层。其它的指令
会创建临时的中间images，不会增加image的大小。

- Docker17.05之后的版本支持了`multi-stage builds`，允许你只拷贝需要的artifacts
到你最终的image。这允许你包含在中间的build stage中包含一些debug工具，而不会影响
最终image的大小。

### Sort multi-line arguments

尽可能将多行参数以字母表顺序排序。这可以帮助你避免软件包的重复，并且视觉上也
更加清楚。另外建议在`\`前面加上一个空格。

下面是`buildpack-deps` image的示例：

```txt
RUN apt-get update && apt-get install -y \
    bzr \
    cvs \
    git \
    mercurial \
    subversion
```

### Build cache

在创建image的过程中，Docker会按照顺序执行`Dockerfile`的指令。每个指令执行前，
Docker都会查询现存的image是否已经存在缓存可以重用。如果你不想使用缓存，可以
在命令`docker build`中使用`--no-cache=true`选项.

不过，如果你让Docker使用它的缓存，你需要理解它是怎么匹配image的。Docker主要遵循
以下的规则:

- 如果一个父image已经在缓存中了，下一个指令将会比较所有的子image是否基于同一个
base image。如果不是，这个缓存就是无效的。

- 多数情况下只是把Dockerfile的指令和子image对比是不够的。一些指令需要一些额外的
检查。

- 对于`ADD`和`COPY`指令，将会检查image的文件内容(checksum)。在缓存查询期间，
将会对比checksum。如果文件发生了改动，不如内容或者元数据改动，那么这个缓存就
失效了。

- 除了`ADD`和`COPY`命令，缓存检查不会通过container中的文件来决定缓存是否匹配。

## The Dockerfile instructions

下面的介绍可以帮助你编写Dockerfile.

### FROM

只用可能，都应该使用一个官方仓库的image作为基础image。我们推荐使用`Alpine image`，
因为它们很成熟，并且保持了最小化。

### LABEL

你可以为image加入label来帮助你组织项目中的images，记录licensing信息，帮助自动化的过程，
或者一些其它原因。使用方法是，使用`LABEL`指令，然后加上一个键值对。下面的示例
介绍了不同的LABEL格式。

> 如果你的字符串包含空格，必须加上引号或者将空格转义.

```txt
LABEL com.example.version='0.0.1-beta'
LABEL vendor='ACME Incorporated'
LABEL com.exmaple.release-date='2015-02-12'
LABEL com.exmaple.version.is-production=''
```

一个image可以有多个label.可以将所有的LABEL放在一行来声明.

```txt
LABEL vendor=ACME\ Incorporated \
      com.example.is-beta= \
      com.example.is-production="" \
      com.example.version="0.0.1-beta" \
      com.example.release-date="2015-02-12"
```

### RUN

为了把易读性，应该将复杂的`RUN`语句分隔成多行.

#### APT-GET

`RUN`最常用的就是`apt-get`，可以用它来安装软件包。

你应该避免使用`RUN apt-get upgrade`或者`dist-upgrade`，因为在一个unprivileged的container中，
parent images的很多软件包是不能更新的。

如果一个parent image的软件包过时了，你应该联系它的维护者。如果你有一个特殊的包，比如`foo`，必须
立即更新，可以使用`apt-get install -y foo`来单独更新它。

应该将`RUN apt-get update`和`apt-get install`组合在同一个RUN语句中:

```txt
RUN apt-get update && apt-get install -y \
    package-bar \
    package-baz \
    package-foo
```

如果单独使用`apt-get update`会造成缓存问题，之后的`apt-get install`就会失败。

在创建image之后，所有的层都存在于Docker缓存中。假设你之后修改了`apt-get install`
，追加了一些额外的package:

```txt
FROM ubuntu:14.04
RUN apt-get update
RUN apt-get install -y curl nginx
```

Docker会查看之前步骤的缓存，而`apt-get update`不会被执行因为会使用它的缓存版本。
因为`apt-get update`没有运行，你的image可能会使用旧版本的`curl`或者`nginx`.

请确保将它们放在一行：`RUN apt-get update && apt-get install -y`

#### USING PIPES

一些`RUN`命令基于管道符号：

`RUN wget -0 https://some.site | wc -l > number`

Docker使用`/bin/sh -c`解释器来执行这些命令，它只会eval管道最后一次操作的退出码。

如果你想要让命令在首次失败的时候停止，需要加入前缀`set -o pipefail &&`

`RUN set -o pipefail && wget -O - https://some.site | wc -l > /number
`

### CMD

`CMD`指令应该用于允许你的image中包含的软件，以及其它的任意参数，它的语法是
`CMD ['executable', 'param1', 'param2'...]`。

### EXPOSE

`EXPOSE`指令可以指定连接容器所监听的端口。你应该为应用设置一个传统的端口号码，
比如Apache web server使用`EXPOSE 80`， MongoDB使用`EXPOSE 27017`.

对于外部访问，你可以在执行`docker run`的时候加上选项指定端口的映射。

### ENV

要让一个新的软件可以轻松运行，你可以使用`ENV`来更新`PATH`环境变量。

比如: `ENV PATH /usr/local/nginx/bin:$PATH`可以确保`CMD ['nginx']`生效。

`ENV`还可以用来指定应用所需的环境变量，比如Postgresql的`PGDATA`.

最后，`ENV`通常用于设置版本好吗:

```txt
ENV PG_MAJOR 9.3
ENV PG_VERSION 9.3.4
RUN curl -SL http://example.com/postgres-$PG_VERSION.tar.xz | tar -xJC /usr/src/postgress && …
ENV PATH /usr/local/postgres-$PG_MAJOR/bin:$PATH
```

### ADD or COPY

虽然`ADD`和`COPY`的功能类似，但是一般来说，更加推荐使用`COPY`。这是应为它相比
`ADD`更加透明。`COPY`只支持将本地文件复制到container中的基础功能，`ADD`还有一些其它
特性(比如本地的tar解压缩，远程URL)。使用`ADD`最好的方式是将一个本地的tar文件
自动解压缩放到image中，比如`ADD rootfs.tar.xz /`

因为image的大小很重要，使用`ADD`来获取远程文件的方式是不提倡的，你应该使用curl或者wget:

### ENTRYPOINT

`ENTRYPOINT`最佳使用场景是设置为image的主命令，允许将image当作命令使用。

```txt
ENTRYPOINT ['s3cmd']
CMD ['--help']
```

现在运行这个image会显示命令行的help:

`$ docker run s3cmd`

或者你可以使用正确的参数来执行这个命令:

`$ docker run s3cmd ls s3://mybucket`

ENTRYPOINT还可以设置为脚本.

举例来说，Postgres官方image使用下列的脚本作为`ENTRYPOINT`

```bash
#!/bin/bash
set -e

if ["s1" = "postgres" ]; then
    chown -R postgres "$PGDATA"

    if [ -z "$(ls -A "$PGDATA")" ]; then
        gosu postgres initdb
    fi

    exec gosu postgres "$@"
fi

exec "$@"
```

### VOLUME

`VOLUME`指令应该用于为数据库暴露一份存储空间，配置存储，或者你的docker container创建的文件/文件夹。

我们提倡在image中任何可变的用户服务文件都应该使用`VOLUME`.

### USER

如果service以无privileges方式与性能，使用`USER`可以更改为非root用户。

但是你应该首先增加user和group:

`RUN gruopadd -r postgres && useradd --no-log-init -r -g postgres postgres`

### WORKDIR

处于清晰和易读性的原因；你应该对`WORKDIR`总是使用绝对路径。另外你应该使用
`WORKDIR`代替命令中的`cd ...`.

### ONBUILD

`ONBUILD`命令会在Dockerfile build完成以后被执行。可以把它看作是一个子Dockerfile.


