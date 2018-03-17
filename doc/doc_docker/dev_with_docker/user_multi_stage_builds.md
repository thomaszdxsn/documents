# Use multi-stage builds

Multi-stage builds是Docker17.05版本加入的新特性。

## Before multi-stage builds

建立一个image最重要的事情就是要让它保持尽可能的小。每个Dockerfile的指令都会为
image加入一层，你需要在进入下一层之前清除吊你不需要的artifacts。

想要编写一个搞笑的Dockerfile，你以前一般需要一些shell技巧来让每一层尽可能小。

这是Dockerfile用于开发常见的问题，在部署到生产环境时，应该只安装你的应用需要的
东西。这也叫做"builder模式".

下面是一个`Dockerfile.build`和`Dockerfile`的示例，它们解释了之前提到的builder模式：

```
# Dockerfile.build
FROM golang: 1.7.3
WORKDIR: /go/src/github.com/alexellis/href-counter/
COPY app.go .
RUN go get -d -v golang.org/x/net/html \
    && CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o app
```

下面是Dockerfile:

```
# Dockerfile
FROM alpine:latest
RUN apk --no-cache add ca-certificates
WORKDIR /root/
COPY app .
CMD ["./app"]
```

```
# build.sh
echo Building alexellis2/href-counter:build

docker build --build-arg https_proxy=$https_proxy --build-arg http_proxy=$http_proxy \  
    -t alexellis2/href-counter:build . -f Dockerfile.build

docker container create --name extract alexellis2/href-counter:build  
docker container cp extract:/go/src/github.com/alexellis/href-counter/app ./app  
docker container rm -f extract

echo Building alexellis2/href-counter:latest

docker build --no-cache -t alexellis2/href-counter:latest .
rm ./app
```

在你运行`build.sh`脚本的时候，它需要创建首个image，根据它的artifact拷贝到container,
然后创建第二个image。

## Use multi-stage builds

在使用multi-stage builds之后，你可以在Dockerfile中使用多个`FROM`语句。

每个`FROM`指令都可以使用一个完全不同的base image，它们中的每一个都会开启build的一个新的stage.

```
# Dockerfile
FROM golang:1.7.3
WORKDIR /go/src/github.com/alexellis/href-counter/
RUN go get -d -v golang.org/x/net/html
COPY app.go .
RUN CGO_ENABLED=0 GOOS=linux go build a -installsuffix cgo -o app .

FROM alpine:latest  
RUN apk --no-cache add ca-certificates
WORKDIR /root/
COPY --from=0 /go/src/github.com/alexellis/href-counter/app .
CMD ["./app"]  
```

## Name your build stages

默认情况下，stage没有名称，你可以通过数字来指代它们，一个FROM指令为0...

不过你也可以在`FROM`指令后面加上`as <NAME>`来为它们命名

```
FROM golang:1.7.3 as builder
WORKDIR /go/src/github.com/alexellis/href-counter/
RUN go get -d -v golang.org/x/net/html  
COPY app.go    .
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o app .

FROM alpine:latest  
RUN apk --no-cache add ca-certificates
WORKDIR /root/
COPY --from=builder /go/src/github.com/alexellis/href-counter/app .
CMD ["./app"]  
```

