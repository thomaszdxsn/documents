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

    在Python3.3以后，这个异常就不需要再使用了：生成器函数已经能够原生支持`return`语句。

    类似于return语句，return后面的值也是可选的。如果没有传入值，意思就是`return None`。

- `tornado.gen.with_timeout(timeout, future, io_loop=None, quiet_exceptions=())`

    将一个Future对象(或者其它可yield的对象)封装，增加一个超时时间。

    如果在超时事件达到还没有结束，则抛出一个`TimeoutError`。

- 异常`tornado.gen.TimeoutError`

    `with_timeout`抛出的异常。

- `tornado.gen.sleep(duration)`

    返回一个Future，在给定的秒数后被完成。

    当在一个协程中使用时，这个函数类似是一个非堵塞的`time.sleep`：

    `yield gen.sleep(.5)`

    注意，直接调用这个函数并不会做什么事情，你必须yield它。

- `tornado.gen.moment`

    一个特殊的对象，可以yield它来让IOLoop进行一次迭代。

    一般并不常见使用这个对象，但是可以在一个长时间运行的协程中使用让它立即yield一个Future。

- `tornado.gen.WaitIterator(*args, **kwargs)`

    提供一个迭代器，在一组futures结束后yield它们。

    yield列表／字典使用下面这种语法：

    `results = yield [future1, future2]`

    直到`future1`和`future2`都返回时才会让协程解除暂停。如果其中的一个future抛出一个异常，这个异常将会让所有的结果丢失。

    但是，如果你想尽可能快的获取每个future结果，或者即使一些future发生错误你仍然想要其它future的结果，你可以使用`WaitIterator`:

    ```python
    wait_iterator = gen.WaitIterator(future1, future2)
    while not wait_iterator.done():
        try:
            result = yield wait_iterator.next()
        except Exception as e:
            print("Error {} from {}".format(e, wait_iterator.current_future))
        else:
            print("Result {} received from {} at {}".format(result, wait_iterator.current_future, wait_iterator.current_index))
    ```

    因为让结果尽可能快的获取，所以迭代器输出的顺序和输入参数的顺序并不会保持一样。如果你想知道生成当前结果的是那个future，你可以使用属性`WaitIterator.current_future`来获取, 或者使用`WaitIterator.current_index`来获取这个future在输入列表中的索引。如果在`WaitIterator`初始化时使用的是关键字参数形式(即字典形式)，`current_index`也会返回相符的键名。

    在Python3.5中，`WaitIterator`实现了`async`迭代器协议，所以它可以用于`async for`语句：

    ```python
    async for result in gen.WaitIterator(future1, future2):
        print("Result {} received from {} at ".format(result, wait_iterator.current_future, wait_iterator.current_index))
    ```

    - `done()`

        如果这个迭代器没有结果返回时，这个方法会返回True。

    - `next()`

        返回一个`Future`，将会生成下一个可获取的结果。

        注意这个`Future`对象和输入时的对象不是同一个。

- `tornado.gen.multi(children, quiet_exception=())`

    并行运行多个异步操作。

    `children`可以是一个列表或者字典，它的值必须是可以yield的对象。`multi()`返回一个新的可yield对象，它们在一个并行的结果中获取结果。如果`children`是一个列表，结果就是相同顺序的一个列表；如果它是一个字典，结果就是一个有着相同键的字典。

    也就是说，`results = yield multi(list_of_futures)`等同于：
    
    ```python
    results = []
    for future in list_of_futures:
        results.append(yield future)
    ```

    如果任何children抛出一个异常，`multi`将会抛出第一个异常。除非异常的类型包含在参数`quiet_exceptions`中，其它的都会被记录到日志。

    如果输入中有`YieldPoints`，返回的可yield对象也是一个`YieldPoint`。否则，返回一个`Future`。这意味着，`multi`的结果可以用于原生协程。

    在一个以`yield为基础`的协程中，没有必要直接调用这个函数，因为在yield一个列表或者字典时，协程runner会自动处理。但是，如果使用以`await为基础`的协程，或者需要传入`quiet_exceptions`参数时，这个函数就很有必要了。

    因为历史原因，这个函数有两个名称：`multi()`和`Multi()`。

- `tornado.gen.multi_future(children, quiet_exceptions=())`

    并行等待多个异步futures。

    这个函数类似于`multi`，但是并不支持`YieldPoint`。

- `tornado.gen.Task(func, *args, **kwargs)`

    在协程中使用`以callback为基础`的异步函数。

    接收一个函数(以及可选的额外参数)，然后对参数附加一个`callback`关键字参数来运行这个函数。

- `tornado.gen.Arguments`

    `Task`或者`Wait`的结果，它们的callback有一个以上的参数(或者关键字参数)。

    `Arguments`对象是一个`namedtuple`，可以当作元组`(args, kwargs)`来运行，或者可以访问这个对象的属性`args, kwargs`。

- `tornado.gen.convert_yielded(yielded)`

    将一个可yield对象转换为Future。

    默认的实现支持接受list, dict以及Future。

    如果可以获取`singledispatch`库，这个函数可以扩展支持额外的类型。例如：

    ```python
    @convert_yielded.register(asyncio.Future)
    def _(asyncio_future):
        return tornado.platform.asyncio.to_tornado_future(asyncio_future)
    ```

- `tornado.gen.maybe_future(x)`

    将`x`转换为Future。

    如果x已经是一个Future，那么它将会直接被返回；其它情况下，它将会被封装到一个新的Future。在你不知道`f()`返回的是否是一个`Future`时，使用类似`result = yield gen.maybe_future(f())`语法很有用。

- `tornado.gen.is_coroutine_function(func)`

    判断`func`是否为一个协程函数(是否使用`@coroutine`封装)。

###  旧式接口

在Python3.0支持Future之前，协程在yield表达式中使用`YieldPoint`的子类。这些类仍然支持，但是并不兼容其它的旧式接口。这些旧式的类都不支持原生协程(以`await`为基础)。

- `tornado.gen.YieldPoint`

    一个基类，可以在yield表达式中使用。

    - `start(runner)`

        在生成器yield以后被runner调用。

        在`start`之前不会有任何方法被调用。

    - `is_ready()`

        被runner调用，决定是否重启生成器。

        返回一个布尔值；可能会被调用一次以上。

    - `get_result()`

        返回yield表达式的结果值。

        这个方法只能被调用一次，只有在`is_ready()`返回True后才可以被调用。

- `tornado.gen.Callback(key)`

    返回一个可调用对象，可以允许一个匹配的`Wait`可以进行。

    参数`key`可以是任何适合作为字典键的值，它可以用于匹配`Waits`匹配的`Callback`。

- `tornado.gen.Wait(key)`

    返回之前Callback结果中传入的参数。

- `tornado.gen.WaitAll(keys)`

    返回多个`Callback`的结果。

    参数是一个`Callback`键的序列，返回的结果是一个相同顺序的列表。

    `WaitAll`等同于yield一个`Wait`对象的列表。

- `tornado.gen.MultiYieldPoint(children, quiet_exception=())`

    并行运行多个异步操作。

    这个类相似于`multi`,但即使没有children要求，它也会创建一个`stack context`。这个类并不支持原生协程。

    
