[TOC]

## Daemonization

这篇文档主要介绍如何使用shell脚本来配置celery进程的后台运行。我们更倾向使用supervisor，所以这篇不准备翻译。


### Generic init-scripts

请看Celery官方发布包的`extra/generic-init.d/`目录


### init-script:celeryd

用法: `/etc/init.d/celeryd {start|stop|restart|status}`
配置文件: `etc/default/celeryd`

#### Superuser privileges required

#### Example configuration

#### Use a login shell

#### Example Django configuration

### init-script:celerybeat


用法: `/etc/init.d/celerybeat {start|stop|restart}`
配置文件: `etc/default/celeryd | etc/default/celearybeat`
