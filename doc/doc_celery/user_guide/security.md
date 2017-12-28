## Security

### Introduce

在写Celery程序时不要忘了安全问题，应该将它看做是一个不安全组件。

### Area of Concern

#### Broker

- 在broker签名设置防火墙，只允许指定机器访问.
- 记住防火墙有它自己的问题，应该对防火墙保持监控
- 如果使用RabbitMQ，请看[这篇文章](http://www.rabbitmq.com/access-control.html)
- 如果broker支持，可以使用SSL加密

#### Client

在Celery中, "客户端“是指任何发送消息到broker的东西，比如使用了任务的web服务器.

#### Worker

### Serializers

可以在`accept_content`设置中禁用不信任的内容.

### Message Siging

Celery可以使用`pyOpenSSL`库，使用公钥加密技术来让消息加密.

### Intrusion Detection

#### Logs

日志通常是首先用来发现安全漏洞的地方.

#### Tripwire

