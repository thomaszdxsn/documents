# botocore.config

- class`botocore.config.Config(*args, **kwargs)`

	Botocore客户端的高级配置。

	参数：

	- region_name(str): 使用客户端的地区
	- signature_version(str): 签名请求使用的签名版本
	- user_agent(str): User-Agent头部
	- user_agent_extra(str): 这个值会追加到现在的User-Agent头部
	- connection_timeout(int): 超时时间，默认为60s。
	- read_timeout(int): 超市时间，默认为60s
	- parameter_validation(bool): 是否在序列化请求的时候验证参数。默认为True。
	- max_pool_connections(int): 连接池保持的最大链接数量，默认为10.
	- proxies(dict): 代理
	- s3(dict)

		- `use_accelerate_endpoint`: 是否使用S3加速端点。这个值必须是布尔值。
		- `payload_signing_enable`: 是否对payload加上签名
		- `addressing_style`: S3端点地址的风格，可用值包括:
			- auto
			- virtual
			- path

	- retries(dict)

		一个字典，用来设置retry.
		
		- `max_attempts`：最多尝试次数.

- `merge(other_config)`

	和另一个config对象合并。

	
