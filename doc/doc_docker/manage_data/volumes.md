# Use volumes

Volumes是Docker推荐用于容器作数据持久化的一种机制。`bind mounts`依赖于
宿主机的文件系统，volumes完全有Docker管理。

Volumes相比`bind mounts`有下面几种又是:

- Volumes更容易备份，迁移
- 你可以使用Docker CLI 或者 Docker API来管理volumes
- Volumes可以运行在Linux和Windows容器上面
- Volumes可以更安全地和其它容器分享
- Volume驱动允许你将volume放在一个远程host或者云上，可以加密volume的内容，或者为它加入功能
- 容器可以pre-populate一个新的volume内容

另外，voumes往往是容器写入层的最佳选择，因为使用volume不会增加容器的大小，
volume的内容存在于容器之外。

如果你的容器生产非持久化状态数据，考虑使用`tmpfs mount`。

Volumes使用`rprivate`来绑定传播(bind propagation)，这个属性是不能配置的。

## Choose the `-v` or `--mount` flag

从前，`-v`或者`--volume`用于独立的容器，而`--mount`用于swarm services。

不过从Docker17.06开始，你可以在独立的容器中使用`--mount`。

## Differences between `-v` and `--mount` behavior

在services使用volumes，只支持`--mount`.

## Create and manage volumes

Volumes可以直接创建，不一定要和容器或者service一起存在.

创建一个volume:

`$ docker volume create my-vol`

列出所有的volume:

`$ docker volume ls`

调查一个volume:

```shell
$ docker volume inspect my-vol

[
    {
        "Driver": "local",
        "Labels": {},
        "Mountpoint": "/var/lib/docker/volumes/my-vol/_data",
        "Name": "my-vol",
        "Options": {},
        "Scope": "local"
    }
]
```

移除一个volume:

`$ docker volume rm my-vol`

## Start a container with a volume

如果你通过一个volume来开启一个容器，但是volume还不存在，Docker会为你创建这个
volume。

下面的示例将`myvol2`volume挂载到容器的`/app/`中。

```
# --mount的示例
$ docker run -d \
    --name devtest \
    --mount source=myvol2, target=/app \
    nginx:latest

# -v/--volume的示例
$ docker run -d \
    --name devtest \
    -v myvol2:/app \
    nginx:latest
```

使用`docker instpect devtest`来验证voume是否正确创建和挂载.请看`Mount`部分:

```
"Mounts": [
    {
        "Type": "volume",
        "Name": "myvol2",
        "Source": "/var/lib/docker/volumes/myvol2/_data",
        "Destination": "/app",
        "Driver": "local",
        "Mode": "",
        "RW": true,
        "Propagation": ""
    }
],
```

停止container并移除volume:

```
$ docker container stop devtest
$ docker container rm devtest
$ docker volume rm myvol2
```

## Start a service with volumes

`docker service create`不支持选项`-v`或者`--volume`，你必须使用`--mount`.

## Populate a volume using a container

如果你像上面一样通过创建一个新的volume方式来开启一个container，那么这个container
就包含了挂载上的文件或者文件夹，这个文件夹的内容会被拷贝到volume中。container然后
挂载和使用volume，其它容器如果使用这个volume同样会访问到已经存在的内容。

通过例子来说明把，这个例子开启了一个`nginx`容器，创建了一个新的volume`nginx-vol`，
放在容器的`/usr/share/nginx/html`目录中，这也是ngixin默认存放HTML文件内容的地方。

```
$ docker run -d \
  --name=nginxtest \
  -v nginx-vol:/usr/share/nginx/html \
  nginx:latest
```

在运行这个示例之后，可以通过下面的命令来清除容器和volumes：

```
$ docker container stop nginxtest

$ docker container rm nginxtest

$ docker volume rm nginx-vol
```

## Use a read-only volume

可以为volumes的选项字段加入`ro`选项(为--mount加入`readonly`选项)

```
# --mount版本
$ docker run -d  \
    --name=nginxtest \
    --mount source=nginx-vol,target=/usr/share/nginx/html,readonly \
    nginx:latest

# -v/--volume版本
$ docker run -d \
  --name=nginxtest \
  -v nginx-vol:/usr/share/nginx/html:ro \
  nginx:latest
```

使用`docker insepect nginxtest`可以验证是否成功创建，请看`Mounts`部分:

```
"Mounts": [
    {
        "Type": "volume",
        "Name": "nginx-vol",
        "Source": "/var/lib/docker/volumes/nginx-vol/_data",
        "Destination": "/usr/share/nginx/html",
        "Driver": "local",
        "Mode": "",
        "RW": false,
        "Propagation": ""
    }
],
```

## Use a volume driver

在你使用`docker volume create`创建一个volume，或者启动一个container来创建一个
volume的时候，你可以指定volume driver。

下面的示例使用`vieus/sshfs`volume driver。

### Initial set-up

下面的示例假定你有两个节点，第一个是一个Docker host，可以通过SSH连接第二个节点。

在Docker host，安装`vieux/sshfs`插件：

`$ docker plugin install --grant-all-permissions vieus/sshfs`

### Create a volume using a volume driver

```
$ docker volume create --driver vieux/sshfs \
  -o sshcmd=test@node2:/home/test \
  -o password=testpassword \
  sshvolume
```

### Start a container which creates a volume using a volume driver

```
$ docker run -d \
  --name sshfs-container \
  --volume-driver vieux/sshfs \
  --mount src=sshvolume,target=/app,volume-opt=sshcmd=test@node2:/home/test,volume-opt=password=testpassword \
  nginx:latest
```
