# Overview of Docker Compose

Compose是一个定义和运行多容器Docker应用的工具。

通过Compose，你可以使用YAML文件来配置你的应用服务。

然后，通过一个简单的命令，你就可以通过配置来创建并启动服务。

Compose可以运行在所有的环境中：生产环境，staging，开发，测试，以及CI工作流中。

使用Compose基本只需要以下三个步骤：

1. 通过Dockerfile来定义你的app环境
2. 在`docker-compose.yml`中定义service，让它们可以在一个隔离的环境中运行
3. 运行`docker-compose up`

`docker-compose.yml`看起来像下面这样:

```yml
version: '3'
services:
  web:
    build: .
    ports:
      - '5000:5000'
    volumes:
      - .:/code
      - logvolume01:/var/log
    links:
    - redis
  redis:
    image: redis
volumes:
  logvolume01: {}
```

## Feature

Compose包含的特性有:

- 在单个机器上的多个隔离环境
- 在容器创建后保留volume数据
- 只会重新创建改动过的容器
- 变量在环境中可以混合使用

### Multiple isolated environments on a single host

Compose使用一个项目名称来将环境相互隔离。你可以在很多不同的地方使用这个项目名称：

- 在一个dev host中，可以创建一个环境的多个拷贝
- 在一个CI server，可以保持相互之间的干涉构建，你可以将项目名设置一个唯一的构建数字
- 在一个分享的host或者dev host，可以使用相同的service名称

默认的项目名称是项目目录的basename。你可以通过`-p`来指定一个项目名称。

### Perserve volume data when containers are created

Compose保留你的service使用过的所有volumes。

在使用`docker-compose up`运行的时候，如果它返现任何容器已经运行过，它会将旧容器
的volumes拷贝到新的这个容器。

### Only recreate containers that have changed

Compose可以缓存创建容器的配置。

在你重启一个service的时候，如果没有任何改动，Compose会重新使用现存的容器

### Variables and moving a composition between environments

Compose支持在Compose文件中放入变量。

## Common use cases

### Development environments

在你开发应用的时候，可以将应用运行在一个隔离的环境中。Compose命令行工具可以用来
创建环境并与之交互。

### Automated testing enviroments

任何CI/CD的最重要一部分就是自动化的单元测试。自动化的端到端测试要求配置环境。
Compose可以方便地为自动化测试创建环境。

比如通过下面这几条命令：

```
$ docker-compose up -d
$ ./run_tests
$ docker-compose down
```

### Single host deployments

Compose一般用于开发和测试，但是也可以用于单机的部署。


