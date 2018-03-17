# Docker development best proctices

下面的开发模式可以帮助用户用Docker构建应用。

## How to keep your images small

小的images可以更快速的推送到网络，在启动containers或者services的时候可以更加
快速的读取到内存中。

保持有一个小的image需要遵循以下规则:

- 从一个合适的基础image开始。例如，如果你需要一个JDK，考虑将你的image基于官方的
`openjdk` image来建立，而不是直接从`ubuntu` image开始，然后通过Dockerfile来下载
`openjdk`.

- 使用`multistage builds`。例如，你可以使用`maven` image来创建你的Java应用，
然后重置`tomcat`，将Java artifacts拷贝到你的app中，都放在Dockerfile进行。
这意味着你最终的image不会并不会包含这次build pull的所有库和依赖，而只需要artifacts
和环境。

- 如果你的很多image有一些相同之处，应该考虑创建你自己的`base image`。Docker只需要
读取这个通用层一次，然后会把它们缓存。

- 保持你的生产image瘦小但是可以允许调试，考虑使用产品image作为debug image的base image。
你可以为产品image加入调试/测试工具.

- 在你创建images的时候，应该总是为它们创建合适的tags。

## Where and how to persist application data

- **不要**把应用数据存储到你的container的可写层.你container不断增大会影响I/O效率.

- 应该不数据用`volumes`存储。

- 当你想要挂载你的源目录或者一个binary到你的container时，开发情况下可以使用`bind amounts`.
对于生产环境，应该使用volume。

- 对于生产环境，使用`secrets`来存储敏感数据，使用`configs`来存储非敏感数据如配置文件。
如果你现在使用单独的container，考虑将它迁移到单replica的service中，那么你就可以利用这些service的特性了。

## Use swarm services when possible

- 在可能的情况下，设计你的应用，让它可以利用swarm service来进行伸缩.
- 即使你只需要运行你的应用的单个实例，swarm service也相比单个container有多个优势。
service的配置是声明式的，Docker总是会同步保持这些状态。
- Swarm的网络和volumes可以连接和重连，Docker通过一个非腐蚀性的方式处理service的重新部署，
根据配置的更改来重新创建service。
- 有一些特性，比如能够存储`secrets`和`configs`，只可以通过services使用。这些特性
允许你保持image更通用，不需要把敏感数据存储在Docker images或者container中。
- 让`docker stack deploy`处理image的拉取，而不是使用`docker pull`。通过这种方式，
你不需要在nodes加入的时候再去手动拉取images，images会自动拉取并创建。

但是nodes之间的数据分享有些限制。如果你使用Docker for AWS或者Docker for Azure，
你可以使用Cloudstor插件来分享nodes之间的数据。你可以将你的应用数据放在一个单独的
数据库，来支持同步更新。

## Use CI/CD for testing and deployment

- 当你检查到源代码改动或者创建了一个pull request，可以使用Docker Cloud或者其它的
CI/CD pipeline来自动创建和tag一个image，并且测试它。

## Differences in development and production environments

开发 | 生产
-- | --
使用`bind mounts`，让你的container可以访问你的源文件 | 使用`volumes`来存储的container 数据
使用Docker for Mac 或者 Docker Windows | 尽可能使用Docker EE
不要担心time drift | 总是运行一个NTP客户端。如果你使用swarm services，应该确保每个Docker node的时钟同步
