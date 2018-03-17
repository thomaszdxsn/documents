# Manage data in Docker

可以将数据存储在container的可写层中，但是有若干缺点:

- 在container不再运行的时候，数据也不再持久化，其它进程的container很难拿到其中的数据。

- 在container运行的时候，它的可写层和宿主机紧密耦合。你不可以在这个时候将数据移动。

- 将数据写入container的可写层需要storage驱动来管理文件系统。storage驱动使用Linux内核
提供了一个统一的文件系统。相比使用data volumes它的性能有损失，因为它需要额外的抽象。

Docker提供了三种方式，可以让container将数据挂载到宿主机:

- volumes
- bind mounts
- tmpfs

## Choose the right type of mount

无论你选择使用哪种类型的mount，在container看来都一样。

不同之处在于数据到底存放在哪里。

- `volumes`把数据存储在宿主机的一个部分，这部分叫做Docker area(`/var/lib/docker/volumes/`)。
非Docker进程不应该修改这个地方的文件，文件结构。volumes是Docker存放持久化数据的最佳方式。

- `bind mounts`可以将数据存储在宿主机的任意位置。

- `tmpfs`将数据存储在宿主机的内存中.

### More details about mount types

- volumes

    Docker自己创建并管理。你可以使用`docker volume create`命令来手动创建。

    可以通过`docker voume prune`命令来删除没有使用的volumes.

- bind mounts

    只是Docker之前使用的方式.

- tmpfs mounts

    tmpfs不会将数据持久化到硬盘中。

## Good use cases for volumes

Volumes推荐在需要把container或service数据持久化的时候使用，包括下面一些使用场景：

- 多个containers之间需要共享数据的时候.

- 在一个Docker host不保证存在指定的文件或者目录的时候

- 在你想要把container数据存储在一个远程的host或者云提供商提供的地方的时候.

- 当你需要备份，恢复或者迁移数据的时候.

## Good use cases for bind mounts

一般来说，你应该尽可能使用volumes。bind mounts适用于下面的场景：

- 想要通过宿主机为container分享配置文件.这是Docker为container提供DNS解析
的默认方式，它会把`/etc/resolv.conf`分享给宿主机下的每一个container。

- 在开发环境中分享源代码或者artifacts。

- 在需要为数据指定存放目录的时候.

## Good use cases for tmpfs mounts

在你不想要把数据持久化存储的时候，可能是因为安全原因，或者想要提升container的性能.

## Tips for using bind mounts or volumes

- 如果你挂载一个空的`volume`到一个容器目录，但是容器的目录存在文件，这些文件将会
传播到volume中。


