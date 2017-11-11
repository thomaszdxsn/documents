## tornado.gen -- 简化异步代码

`tornado.gen`是一个以生成器为基础的接口，它可以让异步环境更简单的实现。使用`gen`模块的代码，在技术上可以称为异步性代码，但是只需要编写一个简单的生成器而不需要使用一组(回调)函数。

例如，假定有如下的异步代码：

```python
class AsyncHandler(web.RequestHandler):
    @asynchronous
    def get(self):
        http_client = AsyncHTTPClient()
        http_clietn.fetch("http://example.com", 
                          callback=self.on_fetch)

    def on_fetch(self, response):
        do_something_with_response(response)
        self.render("template.html")
```

可以使用`gen`模块改写为:

```python
class GenAsyncHandler(RequestHandler):
    @gen.coroutine
    def get(self):
        http_client = AsyncHTTPClient()
        response = yield http_client.fetch("http://example.com")
        do_something_with_response(response)
        self.render("template.html")
```

Tornado多数异步函数都会返回`Future`，对这个Future对象使用`yield`，将会返回这个对象的`.result`属性。

你可以yield一个`Future`列表或者字典，它们将会在同时并且并行运行；在所有对象都完成时才会返回一个结果列表或者字典：

```python
@gen.coroutine
def get(self):
    http_client = AsyncHTTPClient()
    response1, response2 = yield [http_client.fetch(url1),
                                http_client.fetch(url2)]
    response_dict = yield dict(response3=http_client.fetch(url3),
                               response4=http_client.fetch(url4))
    response3 = response_dict['response3']
    response4 = response_dict['response4']
```

如果可以获取`singdispatch`库(在Python3.4以后变成标准库，之前都是第三方库，需要通过pip等安装)，其它类型的对象也可以yield。Tornado支持yield的对象包括: 在import了`tornado.platform.asyncio`和`tornado.platform.twisted`时，`asyncio.Future`和`twisted.Deferred`类可以被yield。可以查看`convert_yielded`函数来扩展这个机制。

### 装饰器

- `tornado.gen.coroutine(func, replace_callback=True)`

    用于异步生成器的装饰器。

    任何yield这个模块中对象的对象，都必须使用这个装饰器(`coroutine`)或者`engine`。

    协程可以通过一个特殊的“异常”(`Return(value)`)来返回。在python3.3以后，生成器可以简单的使用`return value`语句来返回(之前的版本并不支持在生成器中直接返回值)。在Python所有版本中，如果想要一个协程提前结束，那么只要简单使用一个没有值的return就可以了。

    使用这个装饰器的函数如果返回一个`Future`。它将会通过一个callback关键字参数来调用。如果一个协程失败，callback不会运行，一个异常将会抛出到`StackContext`环境中。`callback`参数在协程函数中是不可见的，装饰器本身能够处理它。

    从调用的视角来看，`@gen.coroutine`类似于`@return_future`和`@gen.engine`的组合。



    > 警告
    > 
    >> 当一个协程内出现一个异常，异常的信息将会存入到`Future`对象中。你必须检查Future对象，否则这个异常将不会被你的代码捕捉到。意思就是yield一个函数如果通过另一个协程来调用，在顶层中使用类似`IOLoop.run_sync()`来调用，或者将`Future`传入到`IOLoop.add_future`。

- `tornado.gen.engine(func)`

    用于异步生成器以callback为基础的装饰器。

    这是一个旧的接口；新的代码不需要兼容这种Tornado3.0以前的代码风格，推荐使用`@coroutine`。

    这个装饰器类似于`@coroutine`，除了它不会返回一个Future，以及它不会特殊处理callback参数。

    在大多数时候，装饰了`@engine`的函数应该接收一个`callback`参数，并在它的结果完成时调用它。一个明显的例外情况就是`RequestHandler`中的HTTP动词方法，它们使用`self.finish()`而不是callback参数。

### 工具函数

- `tornado.gen.Return(value=None)`

    一个特殊的异常，可以让一个协程可以返回值。

    如果这个异常被抛出，它的值将会被看作为协程的结果。

    ```python
    @gen.coroutine
    def fetch_json(url):
        response = yield AsyncHTTPClient().fetch(url)
        raise gen.Return(json.decode(response.body))
    ```
    