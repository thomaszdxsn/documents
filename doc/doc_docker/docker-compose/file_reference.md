# Compose file version 3 reference

## Service configuration references

Compose文件是一个`YAML`文件，用来定义services, networks以及volumes。

Compose文件的默认路径为`./docker-compose.yml`.

service定义中包含的配置很像`docker container create`中的参数。network和volume的
定义很像`docker network create`和`docker volume create`.

至于`docker container create`, 可以选择通过Dockerfile来指定，比如`CMD`, `EXPOSE`,
`VOLUME`, `ENV`。你不需要把它们定义在`docker-compose.yml`中。

你可以在配置中使用环境变量，语法为`${VARIABLE}`.

## build

`build`可以传入一个字符串，包含要创建上下文的路径:

```yml
version: '3'
services:
  webapp:
    build: ./dir
```

或者可以另行指定Dockerfile和args:

```yml
version: '3'
services:
  webapp:
    build:
      context: ./dir
      dockerfile: Dockerfile-alternate
      args:
        buildno: 1
```

如果你同时指定了`image`和`build`，结果就是会以image的名称作为命名，仍然以
`build`的上下文作为基础来构建:

```yml
build: ./dir
image: webapp:tag
```

### context

可以是一个包含Dockerfile的目录，亦或者是一个git仓库。

如果这个值是一个相对路径，那么它是相对于Composite文件的位置的：

```yml
build:
  context: ./dir
```

### dockerfile

可以另外选择一个文件作为Dockerfile：

```yml
build:
  context: .
  dockerfile: Dockerfile-alternate
```

### args

加入build参数，它们属于在build过程中可以使用的环境变量。

首先，在你的Dockerfile定义参数：

```
ARG buildno
ARG gitcommithash

RUN echo "Build number: $buildno"
RUN echo "Based on commit: $gitcommithash"
```

在compose阶段，你可以指定参数的值:

```python
build:
  context: .
  args:
    buildno: 1
    gitcommithash: cdc3b19
build:
  context: x
  args:
    - buildno=1
    - gitcommithash=cdc3b19
```

你也可以不传入参数值。在这种情况下，会选择使用同名的环境变量。

### cache_from

可以传入一组images，docker engine用它们来决定缓存:

```yml
build:
  context: .
  cache_from:
    - alpine:latest
    - corp/web_app:3.14
```

### labels

为image加入元数据。可以使用数组或者字典形式。

推荐使用reverse-DNS记号法，避免label有命名冲突:

```yml
build:
  context: .
  labels:
    com.example.description: "Accounting webapp"
    com.example.department: "Finance"
    com.example.label-with-empty-value: ""

  build:
  label:
    - "com.example.description=Account webapp"
    - "com.example.department=Finance"
    - "com.example.label-with-empty-value"
```

### shm_size

设置这个容器的`/dev/shm`分区大小。

```yml
build:
  context: .
  shm_size: '2gb'


build:
  context: .
  shm_size: 10000000
```

### target

构建Dockerfile定义的指定阶段(stage).

```yml
build:
  context: .
  target: prod
```

### `cap_add`, `cap_drop`

增加或减少容器的性能(capabilities).

```yml
cap_add:
  - ALL

cap_drop:
  - NET_ADMIN
  - SYS_ADMIN
```

### command

覆盖默认的命令.

`command: bundle exec thin -p 3000`

这个命令可以是一个list，和dockerfile中的语法一样:

`command: ["bundle", "exec", "thin", "-p", "3000"]

### configs

...

#### short syntax

#### long syntax

```yml
version: "3.3"
services:
  redis:
    image: redis:latest
    deploy:
      replicas: 1
    configs:
      - my_config
      - my_other_config
configs:
  my_config:
    file: ./my_config.txt
  my_other_config:
    external: true
```

### cgroup_parent

为容器指定一个可选的父`cgroup`.

`cgroup_parent: m-executor-abcd`

### container_name

指定自定义的容器名称:

`container_name: my-web-container`

因为Docker的容器名称必须是唯一，所以你需要注意这一点。

### credential_spec

...

## depoly

指定部署时和运行服务时的配置。这些配置只对`swarm`或者`docker stack deploy`有用，
`docker-compose up`或者`docker-compose run`会忽略这些配置。

```yml
version: '3'
services:
  redis:
    image: redis:latest
    deploy:
      replicas: 6
      update_config:
        parallelism: 2
        delay: 10s
      restart_policy:
        condition: on-failure
```

## endpoint_mode

指定一个service作为外部client连接到一个swarm的发现方法。

- `endpoint_mode: vip`

    Docker赋值这个服务为一个虚拟IP(Virtual IP, VIP)，它可以作为客户端的前端来
    访问网络。Docker在客户端和可用的服务节点之间进行路由，客户端不需要知道服务
    中有多少节点，也不需要知道它们的IP地址和端口.（这是默认的选项).

- `endpoint_mode: dnsrr`

    DNS round-robin(DNSRR)方式的服务发现，它并不使用单个虚拟IP。Docker对服务建立
    起DNS入口，然后通过名称进行DNS查询，返回一组IP地址，客户端可以连接到它们中
    的一个。

    如果你想要使用自己的负载均衡，那么就有必要用DNS round-robin.

