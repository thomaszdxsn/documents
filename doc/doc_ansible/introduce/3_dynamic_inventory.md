# Dynamic Inventory

通常一个用户的配置管理系统想要把inventory放在不同的软件系统。Ansible提供了一个基础的文本系统叫做`inventory`，但是你想用其它方式怎么办呢？

一个常见的例子就是从一个云服务商(比如Cobbler)拉取inventory。

Ansible可以使用外部inventory系统来支持拉取所有这些inventory。发行包的`inventory`目录已经包含了它们中的一些 -- 包括EC2，Openstack...

Ansible Tower同样提供一个数据库来存储inventory的结果，可以通过web和REST来访问。

## Example：The Cobbler External Inventory Script

想要将Ansible的inventory和Cobbler绑定，可以将[这个脚本](https://raw.github.com/ansible/ansible/devel/contrib/inventory/cobbler.py)拷贝到`/etc/ansible`并修改文件权限`chomd +x`。在你使用anible和`-i`选项(比如`-i /etc/ansible/cobbler.py`)时，cobbler需要出于运行当中。这个特殊的脚本将会使用Cobbler的XMLRPC API和Cobbler进行通讯。

另外需要为`/etc/ansible`加入一个`cobbler.ini`文件，来开启缓存功能：

```ini
[cobbler]

# Set Cobbler's hostname or IP address
host = http://127.0.0.1/cobbler_api

# API calls to Cobbler can be slow. For this reason, we cache the results of an API
# call. Set this to the path you want cache files to be written to. Two files
# will be written to this directory:
#   - ansible-cobbler.cache
#   - ansible-cobbler.index

cache_path = /tmp

# The number of seconds a cache file is considered valid. After this many
# seconds, a new API call will be made, and the cache file will be updated.

cache_max_age = 900
```

可以直接运行`/etc/ansible/cobbler.py`来测试这个脚本。你应该会看到JSON数据输出。

...


## Example: AWS EC2 External Inventory Script

如果你使用AWS EC2，维持一个inventory文件可能不是好办法，因为host是变化的。所以你应该使用EC2外部inventory，使用[这个脚本](https://raw.github.com/ansible/ansible/devel/contrib/inventory/ec2.py)。

你可以以两种方式运行这个脚本。最简单的方式是使用Ansible的`-i`命令行选项，指定脚本的路径:

```shell
$ ansible -i ec2.py -u ubuntu us-east-1d -m ping
```

第二个选项是把脚本拷贝到`/etc/ansible/hosts`同目录下，并且将它修改权限为`chmod +x`。另外你也需要拷贝[ec2.ini](https://raw.githubusercontent.com/ansible/ansible/devel/contrib/inventory/ec2.ini)到`/etc/ansible/ec2.ini`

想要成功地对AWS发出API调用，你需要配置Boto(AWS的Python sdk)。你需要配置环境变量：

```shell
export AWS_ACCESS_KEY_ID='AK123'
export AWS_SECRET_ACCESS_KEY='abc123'
```

你可以测试脚本，看看是否配置正确:

```shell
cd contrib/inventory
./ec2.py --list
```

然后你应该看到JSON数据输出了。

如果你使用Boto管理多个AWS账号，你可以传入`--profile PROFILE`到`ec2.py`脚本.一个PROFILE可能看起来像这样:

```ini
[profile dev]
aws_access_key_id = <dev access key>
aws_secret_access_key = <dev secret key>

[profile prod]
aws_access_key_id = <prod access key>
aws_secret_access_key = <prod secret key>
```

然后你可以运行`ex2.py --profile prod`来获得prod账号的inventory。

...

## Example: OpenStack External Inventory Script

...

## Other inventory scripts

其它的inventory脚本包括：

```shell
BSD Jails
DigitalOcean
Google Compute Engine
Linode
OpenShift
OpenStack Nova
Ovirt
SpaceWalk
Vagrant (not to be confused with the provisioner in vagrant, which is preferred)
Zabbix
```



