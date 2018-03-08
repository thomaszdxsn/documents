# aiobotocore's documentation!

这是一个aws的异步客户端，使用`botocore`和`aiohtto/asyncio`.

主要使用这个库来支持Amazon S3 API，但是其它的服务应该也可以支持。不过我们现在只测试了S3 API的上传和下载。

## Features

- AWS服务，botocore的异步支持
- 用户S3，SQS，Dynamo的库

## Basic Example

```python
import asyncio
import aiobotocore

AWS_ACCESS_KEY_ID = 'xxx'
AWS_SECRET_ACCESS_KEY = 'xxx'

async def go(loop):
	bucket = 'dataintake'
	filename = 'dummy.bin'
	folder = 'aiobotocore'
	key = '{}/{}'.format(folder, filename)

	session = aiobotocore.get_session(loop=loop)
	async with session.create_client('s3', region_name='us-west-2'，
									 aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
									 aws_access_key_id=AWS_ACCESS_KEY_ID):
		# 将对象上传到amazon s3
		data = b'\x01' * 1024
		resp = await client.put_object(Bucket=bucket, Key=key, Body=data)
		print(resp)

		# 从S3获取对象
		response = await client.get_object(Bucket=bucket, Key=key)
		# 下面这条语句可以确保连接能够正确的重用/关闭
		asnyc with response['Body'] as stream:
			assert await stream.read() == data

		# 使用paginator列出s3中的对象
		paginator = client.get_paginator('list_objects')
		async for result in paginator.paginate(Bucket=bucket, Prefix=folder):
			for c in result.get('Contents', []):
				print(c)

		# 从S3中删除对象
		resp = await client.delete_object(Bucket=bucket, Key=key)
		print(resp)

loop = asyncio.get_event_loop()
loop.run_until_complete(go(loop))
```

## awscli

awscli支持某个特定版本的botocore，不过aiobotocore支持多个botocore版本。

`pip install -U aiobotocore[awscli]`

