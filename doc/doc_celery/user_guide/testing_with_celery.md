## Testing with Celery

### Tasks and unit tests

想要在单元测试中测试task的行为，最推荐的方式是使用mocking.

> 贪婪模式
>
>> `task_always_eager`设置开启的贪婪模式并不适用于单元测试.
>>
>> 在贪婪模式中测试时，仅仅是仿真了一个worker执行环境。真实世界的情况和仿真的环境有较大差异.

Celery task很像web view，在调用一个任务后应该定义在当前上下文中如何执行动作。

这意味着task最好只处理序列化，消息头，重试...真实的业务逻辑实现在其它地方.

比如，我们有一个这样的任务:

```python
from .models import Product

@app.task(bind=True)
def send_order(self, product_pk, quantity, price):
    price = Decimal(price)
    
    # model通过id传入，而不是直接传入序列化的对象
    product = Product.objects.get(product_pk)

    try:
        product.order(quantity, price)
    except OperationalError as exc:
        raise self.retry(exc=exc)
```

你可以使用mocking来为这个task写一个单元测试：

```python
from pytest import raises

from celery.exceptins import Retry

# 对于Python2，使用unnitest.mock.patch 需要安装: pip install mock
from unittest.mock import patch

from proj.models import Product
from proj.tasks import send_order


class test_send_order:

    @patch('proj.tasks.Product.order')
    def test_success(self, product_order):
        product = Product.objects.create(
            name='Foo'
        )
        send_order(product.pk, 3, Decimal(30.3))
        product_order.assert_called_with(3, Decimal(30.3))

    @patch('proj.tasks.Product.order')
    @patch('proj.tasks.send_order.retry')
    def test_failutre(self, send_order_retry, product_order):
        product = Product.objects.create(
            name='Foo'
        )

        # 将patched方法加上一个side effect
        # 让它可以抛出我们想要的错误
        send_order_retry.side_effect = Retry()
        product_order.side_effect = OperationError()
        
        with raises(Retry):
            send_order(product.pk, 3, Decimal(30.3))
```

### Py.test

Celery有一个`pytest`插件，并且加入了fixture。可以将它继承到你的测试集(test suite)中。

#### Marks

##### Celery - Set test app configuration

`celery mark`让你可以覆盖默认配置，这个配置可以应用于单个测试集:

```python
@pytest.mark.celery(result_backend='redis://')
def test_something():
    ...
```

后者可以应用于测试用例:

```python
@pytest.mark.celery(result_backen='redis://')
class TestSomething:

    def test_one(self):
        ...

    def test_two(self):
        ...
```

#### Fixture

##### Function scope

- `celery_app` －－　用于测试的Celery app

    这个fixture返回一个Celery app，可以将它用于测试.

    例子：

    ```python
    def test_create_task(celery_app, celery_worker):
        @celery_app.task
        def mul(x, y):
            return x * y

        assert mul.delay(4, 4).get(timeout=10) == 16
    ```

- `celery-worker` -- 嵌入激活的worker

    这个fixture开启一个worker实例，你可以将它继承到测试中.这个worker会另外开启一个线程，在测试结束后即关闭.

    例子:

    ```python
    @pytest.fixture(scope='session')
    def celery_config():
        return {
            "broker_url": "amqp://",
            "result_backend": "redis://"
        }


    def test_add(celery_worker):
        mytask.delay()


    @pytest.mark.celery(result_backend='rpc')
    def test_other(celery_worker):
        # ...
    ```

##### Session scope

- `celery_config` -- 覆盖测试worker的配置

    你可以重新定义这个fixture来配置Celery app.

    这个fixture返回的配置将会用来配置`celery_app()`和`celery_session_app()`这些fixtures.

    例子：

    ```python
    @pytest.fixture(scope='session')
    def celery_config():
        return {
            'broker_url': 'amqp://',
            'result_backend': 'rpc'
        }
    ```

    # ...略去，都是关于fixtures的内容