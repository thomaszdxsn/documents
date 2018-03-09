# Getting Started With Botocore

`botocore`软件包提供了AWC的底层接口。它主要负责：

- 提供访问所有可用服务
- 提供访问对一个服务执行所有可用操作
- 将一个特定操作的参数转换为正确的格式
- 使用正确的验证签名来签名请求
- 接受aws返回的响应，并且以Python原生数据结构的方式返回。

`botocore`并不提供服务的高级抽象接口，以及response响应的操作。这些留给应用层来解决。`botocore`的目标是处理所有的底层细节，让请求可以从服务中获取结果。

`botocore`是数据驱动的。

## Using Botocore

第一步就是使用botocore来创建一个`Session`对象。`Session`对象运行你创建一个单独的客户端：

```python
import botocore.session
session = botocore.session.get_session()
client = session.create_client('ec2', region_name='us-west-2')
```

一旦你创建了一个客户端，每个服务的操作都会映射为一个方法。每个方法接受的`**kwargs`参数将会映射为服务接受的参数。例如，可以使用上面创建的client对象：

```python
for reservation in client.describe_instances()['Reservations']:
	for instance in reservation['Instances']:
		print(instance['InstanceId'])

reservations = client.describe_instances(
	Filters=[{'Name': 'instance-state-name', 'Values': ['pending']}]
)
```
