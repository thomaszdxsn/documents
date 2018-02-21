# Get Started, Part 4: Swarms

## Introduce

在part3中，你将part2写的镜像运行为一个产品级的app。

这里是part4，你可以将这个应用部署在一个cluster中，将它在多个机器中运行。多容器，多机器应用可以通过`swarm`来把多个机器连接起来运行在一个"Dockerized" cluster中。

## Understanding Swarm clusters

Swarm是一组运行Docker的机器，并且把它们连接到一个cluster中。在连接以后，你继续运行普通的Docker命令，但是这些命令运行在一个**swarm manager**中。swarm中的机器可以是物理机器或者虚拟机器。在连接到一个swarm中，它们都可以被叫做`nodes`.

**Swarm managers**可以以多种方式来运行容器，比如"emptiest node" - 它使用最近的一个机器来运行容器。或者"global" - 它确保每个机器都运行一个容器实例。你可以通过`compose file`来指定**swarm manager**使用的策略。

**Swarm managers**是一个swarm中唯一的一个可以执行你的命令的机器，授权加入到swarm的其它机器叫做**workers**。Worker不能授权其它机器加入swarm。

到目前为止，你都是在自己的机器上使用单主机模式来运行Docker。Docker可以转换为*swarm*模式，这可以让你使用swarm。激活swarm模式之后可以让当前的机器变为**swarm manager**。之后，这个机器可以运行swarm命令。

## Set up your swarm

一个Swarm是由多个nodes构成的，nodes可以是物理机器或者虚拟机器。基础概念很简单：运行`docker swarm init`来激活swarm模式，让你当前的机器变为**swarm manager**，在其它机器运行`docker swarm join`，让它们以*worker*的形式加入到swarm中。

### Create a cluster

使用`docker-machine`来创建一对虚拟机器，使用`VirtualBox`driver:

```shell
docker-machine create --driver virtualbox myvm1
docker-machine create --driver virtualbox myvm2
```

### List the VMs and get their ip addresses

你现在创建了两个VMs, `myvm1`和`myvm2`。

使用下条命令列出机器和它们的IP地址:

`docker-machine ls`

下面是这个命令的输出:

```shell
$ docker-machine ls
NAME    ACTIVE   DRIVER       STATE     URL                         SWARM   DOCKER        ERRORS
myvm1   -        virtualbox   Running   tcp://192.168.99.100:2376           v17.06.2-ce   
myvm2   -        virtualbox   Running   tcp://192.168.99.101:2376  
```

### Initialize the swarm and add nodes

第一个虚拟机作为**swarm manager**，它执行管理命令以及授权worker加入这个swarm，第二个虚拟机是一个worker。

你可以使用`docker-machine ssh`来对虚拟机发送命令。指令`myvm1`变为一个**swarm manager**：

```shell
$ docker-machine ssh myvm1 "docker swarm init --advertise-addr <myvm1 ip>"
Swarm initialized: current node <node ID> is now a manager.

To add a worker to this swarm, run the following command:

  docker swarm join \
  --token <token> \
  <myvm ip>:<port>

To add a manager to this swarm, run 'docker swarm join-token manager' and follow the instructions.
```

请将输出中提示你的那一段命令复制下来，然后让`myvm2`执行:

```shell
$ docker-machine ssh myvm2 "docker swarm join \
--token <token> \
<ip>:2377"

This node joined a swarm as a worker.
```

恭喜，你创建了你的第一个swarm！

在manager中运行`docker node ls`可以看到这个swarm中的节点：

```shell
$ docker-machine ssh myvm1 "docker node ls"
ID                            HOSTNAME            STATUS              AVAILABILITY        MANAGER STATUS
brtu9urxwfd5j0zrmkubhpkbd     myvm2               Ready               Active
rihwohkh3ph38fhillhhb84sk *   myvm1               Ready  
```

## Deploy your app on the swarm cluster

最难的部分已经过去了。现在你只需要重复part3中部署的步骤即可。只要记住需要使用`myvm1`来执行命令。

### Configure a `docker-machine` shell to the swarm manager

目前为止，你已经知道可以将Docker命令使用`docker-machine ssh`的方式告诉VMs执行。另一个方式是使用`docker-machine env <machine>`.这个方式对于下面的步骤更方便，它允许你使用本地的`docker-compose.yml`文件来“远程”部署app，而不用把它拷贝黏贴。

输入`docker-machine env myvm1`，然后赋值拷贝shell中提示你的命令。

#### Docker machine shell environment on Mac or Linux

运行`docker-machine env myvm1`可以获取和`myvm`shell通信的配置。

```shell
$ docker-machine env myvm1
export DOCKER_TLS_VERIFY="1"
export DOCKER_HOST="tcp://192.168.99.100:2376"
export DOCKER_CERT_PATH="/Users/sam/.docker/machine/machines/myvm1"
export DOCKER_MACHINE_NAME="myvm1"
# Run this command to configure your shell:
# eval $(docker-machine env myvm1)
```

运行这个给定的命令：

`eval $(docker-machine env myvm1)`

运行`docker-machine ls`来验证`myvm1`是否是正在激活的机器，那个星号代表是：

```shell
$ docker-machine ls
NAME    ACTIVE   DRIVER       STATE     URL                         SWARM   DOCKER        ERRORS
myvm1   *        virtualbox   Running   tcp://192.168.99.100:2376           v17.06.2-ce   
myvm2   -        virtualbox   Running   tcp://192.168.99.101:2376           v17.06.2-ce   
```

### Depoly the app on the swarm manager

现在你拥有了`myvm1`，你可以使用它作为**swarm manager**，使用`docker stack depoly`命令来部署你的app。这个命令可能需要一点时间来执行。使用`docker service ps <service_name>`可以验证这个服务是否已经成功部署。

你已经通过`docker-machine`的shell配置连接了`myvm1`，**但是你仍然可以访问宿主机的文件**。确认你仍然在app的目录下。

然后运行下面这条命令来部署：

`docker stack deploy -c docker-compose.yml getstartedlab
`

你的app已经部署到一个swarm cluster中了。

```shell
$ docker stack ps getstartedlab

ID            NAME                  IMAGE                   NODE   DESIRED STATE
jq2g3qp8nzwx  getstartedlab_web.1   john/get-started:part2  myvm1  Running
88wgshobzoxl  getstartedlab_web.2   john/get-started:part2  myvm2  Running
vbb1qbkb0o2z  getstartedlab_web.3   john/get-started:part2  myvm2  Running
ghii74p9budx  getstartedlab_web.4   john/get-started:part2  myvm1  Running
0prmarhavs87  getstartedlab_web.5   john/get-started:part2  myvm2  Running
```

### Accessing your cluster

你可以通过`myvm1`或者`myvm2`的IP地址来访问它们。

## Recap and cheat sheet[optional]

