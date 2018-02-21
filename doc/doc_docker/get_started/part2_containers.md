# Get Started, Part 2: Containers

## Introduce

是时候使用Docker来构建一个APP了。我们从这个app的底层开始，它是一个容器。它上面的一层是一个service，它定义了容器在生产环境中的行为。最后，最上层是一个stack，定义了所有服务的交互。

- Stack
- Service
- Container(本章节内容)

## You new development environment

在过去，如果你要开始写一个Python app，那么首先要做的就是为你的机器安装一个Python运行环境。不过，下载的Python版本还要符合你应用的要求，也需要匹配生产环境。

在Docker角度来说，你可以将一个可移植的Python运行时当作一个镜像，不需要安装它。然后，你可以将这个Python镜像和你的代码包含在一起。

这些可移植的镜像通过所谓的`Dockerfile`来定义。

## Define a container with `Dockerfile`

`Dockerfile`定义你的容器中环境应该包含什么。在这个环境中可以访问类似网络的资源，这个环境和你的系统是隔离的，所以你应该将它的端口映射到外部世界，需要定义哪些文件应该“拷贝”入这个环境中。

### `Dockerfile`

创建一个空的文件。`cd`进入到这个文件，创建一个文件命名为`Dockerfile`，将下面的内容拷贝到文件中。

```text
# 使用一个官方的Python运行时环境作为一个父镜像
FROM python:2.7-slim

# 将工作目录切换到 /app
WORKDIR /app

# 将当前目录的内容拷贝到容器的 /app中
ADD . /app

# 安装requirements.txt中指定的Python packages
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# 将这个容器的端口80暴露出来
EXPOSE 80

# 定义环境变量
ENV NAME World

# 在容器发布的时候，运行app.py
CMD ["python", "app.py"]
```

## The app itself

再创建两个文件，`requirements.txt`和`app.py`，将它们放在和`Dockerfile`同一个目录下。然后我们的app就完成了，你可以看到它很简单。在上面的`Dockerfile`建立一个镜像之后，`app.py`和`requirements.py`因为`Dockerfile`中的`ADD`命令而加入到了镜像中，`app.py`的输出因为`EXPOSE`命令而可以通过HTTP来访问。

### `requirements.txt`

```text
Flask
Redis
```

### `app.py`

```python
from flask import Flask
from redis import Redis, RedisError
import os
import socket

# 链接Redis
redis = Redis(
    host='redis',
    db=0,
    socket_connect_timeout=2,
    socket_timeout=2
)

app = Flask(__name__)


@app.route('/')
def hello():
    try:
        visits = redis.incr('counter')
    except RedisError:
        visit = "<i>cannot connect to Redis, counter disabled</i>"
    
    html = "<h3>Hello {name}!</h3>" \
           "<b>Hostname:</b> {hostname}<br/>" \
           "<b>Visits:</b> {visits}"
    return html.format(
        name=os.getenv("NAME", "world"),
        hostname=socket.gethostname(),
        visits=visits
    )


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
```

我们可以看到`pip install -r requirements.txt`将会安装Python库`Flask`和`Redis`，这个app将会打打印环境变量`NAME`，以及调用`socket.gethostname()`的输出。最后，因为Redis没有运行(因为上面只安装了Python的redis库，而不是redis本身)，我们会看到redis访问发生了错误并且会打印一个提示信息。

这就醒了！你不需要在你的系统中安装Python运行环境和`requirements.txt`中的库。

## Build the app

我们已经搭建好了这个app。现在确保你出于这个app的目录下，运行`ls`命令:

```shell
$ ls
Dockerfile		app.py			requirements.txt
```

然后运行`build`命令。这将会创建一个Docker镜像，并且使用`-t`创建一个易读的tag名称：

```shell
$ docker build -t friendlyhello .
```

创建的镜像在哪里？它在你本地的Docker镜像registry中：

```shell
$ docker image ls

REPOSITORY            TAG                 IMAGE ID
friendlyhello         latest              326387cea398
```

## Run the app

运行这个app，使用`-p`选项，将你机器的端口号4000来映射发布的端口号80：

```shell
docker run -p 4000:80 friendlyhello
```

你可能会看到一个消息，说FLask进程已经运行在`http://0.0.0.0:80`。但是这个消息来自于容器，它不知道你用4000端口映射了容器端口80，请访问正确的URL：`http://localhost:4000`.

将URL复制到web浏览器，你可以看到:

![app-in-browser](./app-in-browser.png)

## Share you image

为了给你展示可移植性，我们可以把刚才创建的镜像上传并在另一个地方运行它。在你想要把容器部署到生产环境的时候，你需要知道怎么把它推送到registry。

registry是一个仓库的集合，仓库是镜像的集合 -- 有几分像Github的仓库，除了代码是已经构建好的。registry的一个账号可以创建很多仓库，`docker`命名行工具默认使用公共的registry。

### Log in with your Docker ID

如果你还没有Docker ID，请到[https://cloud.docker.com/](https://cloud.docker.com/)进行注册。

请在你本机登陆Docker公共registry。

### Tag the image

关联一个本地镜像和一个仓库的记号法类似`username/repository:tag`。`tag`是可选的，但是推荐使用tag，因为这个机制可以让Docker镜像拥有版本特性。请给定一个有意义的仓库/tag名，比如`get-started:part2`。它会把镜像放到`get-started`仓库并且命名标签为`part2`.

现在，让我们把镜像放在一个仓库标签中。运行`docker tag image`以及你的用户名，仓库，和标签名称，让镜像上传到你指定的仓库。这个命令的语法为:

`docker tag image username/repository:tag`

例如：

`docker tag friendlyhello john/get-started:part2`

运行`docker image ls`可以看到你新创建的一个镜像：

```shell
$ docker image ls
REPOSITORY               TAG                 IMAGE ID            CREATED             SIZE
friendlyhello            latest              d9e555c53008        3 minutes ago       195MB
john/get-started         part2               d9e555c53008        3 minutes ago       195MB
python                   2.7-slim            1c7128a655f6        5 days ago          183MB
...
```

### Publish the image

将你的tagged镜像上传到仓库：

`docker push username/repository:tag`

### Pull and run the image from the remote repository

你可以使用`docker run`来运行本机中存在的镜像：

```shell
docker run -p 4000:80 username/repository:tag
```

如果镜像不在本机中，Docker会从仓库中拉取它：

```shell
$ docker run -p 4000:80 john/get-started:part2
Unable to find image 'john/get-started:part2' locally
part2: Pulling from john/get-started
10a267c67f42: Already exists
f68a39a6a5e4: Already exists
9beaffc0cf19: Already exists
3c1fe835fb6b: Already exists
4c9f1fa8fcb8: Already exists
ee7d8f576a14: Already exists
fbccdcced46e: Already exists
Digest: sha256:0601c866aab2adcc6498200efd0f754037e909e5fd42069adeff72d1e2439068
Status: Downloaded newer image for john/get-started:part2
 * Running on http://0.0.0.0:80/ (Press CTRL+C to quit)
```

## Recap and cheat sheet[optional]

```shell
# 使用这个文件夹中的Dockerfile来创建一个镜像
docker build -t friendlyhello . 

# 运行"friendlyhello", 将容器的端口80映射到本机的端口4000
docker run -p 4000:80 friendlyhello

# 和上面一条命令一样，不过是后台运行
docker run -d -p 4000:80 friendlyhello

# 列出所有运行中的容器
docker container ls 

# 累出所有容器，包括不在运行的
docker container ls -a

# 强制关闭一个特定的容器
docker container kill <hash>

# 从机器中移除指定的一个容器
docker container rm <hash>

# 移除所有的容器
docker container rm $(docker container ls -a -q)

# 列出机器中所有的镜像
docker image ls -a

# 从机器中移除指定的一个镜像
docker image rm <image id>

# 移除所有的镜像
docker image rm $(docker image ls -a -q)

# 登陆docker registry
docker login

# 将一个镜像tag，可以在之后上传到仓库
docker tag <image> username/repository:tag

# 将tagged的镜像上传到仓库
docker push username/repository:tag

# 运行一个仓库中的镜像
docker run username/repository:tag
```
