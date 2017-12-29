# Tornado项目编码规范

可能本项目并没有按照这个规范~~~不过向着这方向努力

## 项目结构

- app/
    - module1/
        - \_\_init\_\_.py
        - forms.py
        - handlers.py
    - module2/
        - \_\_init\_\_.py
        - forms.py
        - handlers.py
    - libs/
        - base.py
        - decorators.py
        - utils.py
        - exceptions.py
        - middleware.py
    - models/
        - model1.py
        - model2.py
    - static/
    - templates/
    - \_\_init\_\_.py
    - urls.py
- requirements/
    - common.txt
    - dev.txt
    - prod.txt
- tests/
    - \_\_init\_\_.py
    - test_api.py    
    - test_client.py
    - ...
- alembic/`(option)`
    - ...
- alembic.ini`(option)`
- requirements.txt
- Dockerfile
- config.py
- manager.py

其中，在`app/__init__.py`中编写项目的初始化代码.最好以函数的形式编写生成`Appilication`实例
和`HTTPServer`启动的代码.

外层的`manager.py`定义命令行参数，通过它来开启测试，启动服务器...

## config.py文件的结构

以类继承的结构定义`Config`:

```python
class Config:
    DATABASE_NAME = ''
    MAIL_SERVER = ''
    SETTINGS = {
        'debug': False
        # ...
    }
    # ...
    

class DevelopmentConfig(Config):
    DATABASE_NAME = ""
    SETTINGS = {
        'debug': True
        # ...
    }
    # ...
    

class ProductionConfig(Config):
    DATABASE_NAME = ''
    SETTINGS = {
        'debug': False
        # ...
    }
    # ...
    
    
config = {
    'development': DevelopmentConfig,
    'product': ProductionConfig,
    'testing': '...'
}
```
