# Create a base image

多数Dockerfiles都从一个parent images开始。如果你需要完全控制你的image内容，你也可以
创建一个base image。

下面是它们之间的区别:

- `parent image`是你可以继承的image。它可以通过Dockerfile的`FROM`质量来引用。
Dockerfile随后的声明都是基于parent image的修改。多数Dockerfile都是基于一个parent images，
而不是直接作为base image.不过这两个词总是混淆在一起。

- `base image`没有`FROM`指令.

这篇文档告诉你怎么创建一个base image。

## Create a full image using tar

一般来说，要打包一个Linux发行版到images中，你需要一些工具，比如Debian的Debootstrap.

```shell
$ sudo debootstrap xenial xenial > /dev/null
$ sudo tar -C xenial -c . | docker import - xenial

a29c15f1bf7a

$ docker run xenial cat /etc/lsb-release

DISTRIB_ID=Ubuntu
DISTRIB_RELEASE=16.04
DISTRIB_CODENAME=xenial
DISTRIB_DESCRIPTION="Ubuntu 16.04 LTS"
```

## Create a simple parent image using scratch

你可以使用Docker保留最小化的image，使用`scratch`来开启建立container.

由于Scratch是Docker hub的一个仓库，你不可以pull它，运行它，或者将image命名为scratch。

你应该在Dockerfile中引用它：

```txt
FROM scratch
ADD hello /
CMD ['/hello']
```


