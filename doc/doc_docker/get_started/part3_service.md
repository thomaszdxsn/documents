# Get Started, Part 3: Services

## Introduce

在part3，我们scale我们应用，并且运行一个负载均衡。我们将到容器的上一层来做这件事 -- `Service`:

- Stack
- Service(本章的内容)
- Container

## About services

在一个分布式应用中，app的不同部分叫做“service”。例如，想象一个视频分享网站，你可能想加入一个服务来把应用中的数据存储到数据库;加入一个服务可以转码用户上传的痛惜，在后台运行;一个前端的服务；等等。

Service其实就是产品化的容器。一个服务只运行一个镜像，不过可以用代码来规划镜像的运行 -- 使用哪个端口，这个服务应该运行多少容器副本，等等。

幸运的是通过Docker平台可以简单的定义、运行和scale服务 - 编写`docker-compose.yml`文件即可。

## Your first `docker-compose.yml` file

`docker-compose.yml`是一个YAML文件，它定义了一个容器在生产环境中应该是怎么样的。

### `docker-compose.yml`

将下面的内容保存到文件`docker-compose.yml`中，随便放在哪里。确认你已经把part2中的镜像推送到了repository，然后把`.yml`文件中的`username/repository:tag`改为你的tagged镜像名。

```yml
version: "3"
services:
    web:
        image: thomaszdxsn/get-started:part2
        deploy:
            replicas: 5
            resources:
                limits:
                    cpus: "0.1"
                    memory: 50M
            restart_policy:
                condition: on-failure
        ports:
            - "80:80"
        networks:
            - webnet
networks:
    webnet:
```

这个`docker-compose.yml`告诉Docker应该这么做：

- 拉取part2中上传的镜像
- 运行这个镜像的5个实例，可以将它必做一个叫做“web”的service，限制每个实例使用的CPU(10%)，以及50M的内存
- 如果容器错误，立即重启
- 映射端口80到宿主机的端口80
- 命令`web`的容器通过一个叫做“webnet”的负载均衡来共享端口80
- 使用默认配置来运行`webnet`网络(它是一个负载均衡层的网络)

## Run your new load-balanced app

在我们使用`docker stack depoly`之前，我们首先需要：

`docker swarm init`

现在让我们运行它。你需要给你的app一个名称，我们把它叫做`getstartedlab`:

`docker stack deploy -c docker-compose.yml getstartedlab`

我们的单服务栈运行了5个容器实例。让我们调研一下这个栈。

首先获取我们的这个service：

`docer service ls`

请看`web`服务的输出，如果你使用上面的名称`getstartedlab`，那么服务的名称为`getstartedlab_web`。service的ID也列出来了，以及副本的数量，镜像名称和暴露的端口号。

service运行的每个容器都叫做`task`。Task使用一个递增、唯一的数字作为ID，使用你`docker-compose.yml`定义的副本数量。下面命令可以列出你服务中的tasks：

`docker service ps getstartedlab_web`

也可以列出本机运行的所有的容器，它没有被筛选服务器：

`docker container ls -q`

你可以在一行命令中运行多次`curl -4 http://localhost`。

## Scale the app

你可以修改`docker-compose.yml`中的`replicas`值来规划app的规模，保存更改然后重新运行`docker stack depoly`命令即可：

`docker stack depoly -c docker-compose.yml getstartedlab`

Docker会执行原地更新，不需要关闭stack或者杀死很多容器。

现在，可以运行`docker container ls -q`来看你重新配置的部署实例。

### Take down the app and the swarm

- 可以通过`docker stack rm`来关闭这个app:

    `docker stack rm getstartedlab`

- 关闭swarm可以：

    `docker swarm leave --force`

操作很简单。你已经学会了如何在生产环境中运行容器。之后，你会学到如何将这个app当作一个真正的swarm，运行在一个Docker机器蔟群中。

## Recap and cheat sheet[optional]

```shell
# 列出所有的stack
docker stack ls

# 运行指定的Compose文件
docker stack deploy -c <composefile> <appname>

# 列出一个app运行的所有service
docker service ls

# 列出一个app关联的task
docker service ps <service>

# 观察一个task或者container
docker inspect <task or container>

# 列出所有容器的ID
docker container ls -q

# 关闭一个应用
docker stack rm <appname>

# 关闭manager swarm的一个节点
docker swarm leave --force
```

