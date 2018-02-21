# Get Started, Part 1: Orientation and setup

## Docker concepts

Docker是为开发者和系统管理提供**用容器**来开发、部署和运行应用的一个平台。使用Linux容器来部署应用也叫做容器化(containerization)。容器不是一个新概念，不过使用它确实可以轻松的部署。

容器化变得越来越流行了，因为容器:

- 弹性: 不管多么复杂的应用都可以被容器化.
- 轻量级: 容器可以利用和共享host的内核。
- 可交换性: 你可以部署更新或者热更新。
- 可移植性: 你可以在本地建立，部署在云上，在任何地方运行。
- Stackable: 你可以垂直堆栈服务。

### Image and containters

一个容器(container)是通过运行一个镜像(image)来发布的。镜像是一个可执行的软件打包，里面可以包含任何应用所需的库，环境变量，配置文件等...

容器是镜像的运行时实例-镜像在内存运行后即是容器。你可以通过`docker ps`来查看你正在运行的容器。

## Containers and virtual machines

容器天然可以运行在Linux，并且可以和宿主机器中的其它容器分享kernal。它运行一个隔离的进程，使用极少的内存。

而虚拟机器(virtual machine, VM)运行一个成熟的“guest”操作系统，可以访问宿主机器的资源。不过一般来说，VM提供环境的资源大多数超出应用所需。

![container.png](./Container.png)
![vm.png](./VM.png)

## Prepare your Docker environment

请访问[链接](https://docs.docker.com/get-started/#prepare-your-docker-environment)

### Test Docker version

通过下列命令可以查看docker版本：

```shell
$ docker --version
Docker version 17.12.0-ce, build c97c6d6
```

运行`docker version`(没有`--`)或者`docker info`可以看到你的docker安装的更细节的信息：

```shell
$ docker info
Containers: 0
 Running: 0
 Paused: 0
 Stopped: 0
Images: 0
Server Version: 17.12.0-ce
Storage Driver: overlay2
...
```

### Test Docker installation

下面通过运行一个简单的Docker image: `hello-world`来测试你的docker是否正常安装:

```shell
$ docker run hello-world

Unable to find image 'hello-world:latest' locally
latest: Pulling from library/hello-world
ca4f61b1923c: Pull complete
Digest: sha256:ca0eeb6fb05351dfc8759c20733c91def84cb8007aa89a5bf606bc8b315b9fc7
Status: Downloaded newer image for hello-world:latest

Hello from Docker!
This message show that your installation appears to be working correctly.
...
```

下面命令可以列出你机器中下载的`hello-world`image:

```shell
$ docker image ls
```

下面命令列出`hello-world`容器：

```shell
$ docker container ls --all
CONTAINER ID     IMAGE           COMMAND      CREATED            STATUS
54f4984ed6a8     hello-world     "/hello"     20 seconds ago     Exited (0) 19 seconds ago
```

## Recap and cheat sheet

```shell
## List Docker CLI commands
docker
docker container --help

## Display Docker version and info
docker --version
docker version
docker info

## Execute Docker image
docker run hello-world

## List Docker images
docker image ls

## List Docker containers (running, all, all in quiet mode)
docker container ls
docker container ls -all
docker container ls -a -q
```

## Conclusion of part one

容器化可以无缝CI/CD(持续集成/持续开发)。例如:

- 应用没有系统依赖。
- 更新可以push到分布式应用的任何部分。
- 资源密度可以优化。

