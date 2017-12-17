## 基础

这篇文档介绍了Celery的"Calling API"风格，用于任务实例和Canvas中。

这个API定义了一套执行的选项，包含以下三个方法：

- `apply_asnyc(args[, kwargs[, ...]])`

    发送一个任务消息

- `delay(*args, **kwargs)`

    发送一个任务消息的快捷方式。但是不支持额外的任务执行选项。

- 直接(同步)调用(`__call__`)

    直接调用一个任务意味着这个任务不会由worker执行，而是由当前进程直接同步执行(也就不会发送任务消息了)。

> 速查表
> - `T.delay(arg, kwargs=value)`
>   
>   `T.apply_async()`的快捷方式.
>
> - `T.apply_async((arg,), {'kwarg': value})`
>   
> - `T.apply_async(countdown10)`
>   
>   在１０秒以后开始执行这个任务
>
> - `T.apply_async(countdown=60, expires=120)`
> 
>   在1分钟以后开始执行，但是在设定了2分钟以后任务过期.
> 
> - `T.apply_async(expires=now + timedealta(days=2))`
>
>   在两天以后过期.

### 例子

`delay()`方法是一个方便的用法，因为看起来就像调用一个普通函数一样：

`task.delay(arg1, arg2, kwarg1='x', kwarg2='y')`

如果使用`apply_async()`，你需要这么来写:

`task.apply_async((arg1, arg2), {"kwarg1": "x", "kwarg2": "y"})`

所以`delay()`是更加清晰易读的，但是如果你想要加入额外的执行选项，那么你不得不使用`apply_async`.

这篇文档的剩余部分会详细的探讨执行选项。所有的例子都是用一个`add()`的任务：

```python
@app.task
def add(x, y):
    return x + y
```

### Linking(callbacks/errbacks)

Celery支持讲任务链接在一起，所以可以让一个任务紧随着另一个任务执行。callback任务将会把父任务的返回结果当做自己的一个partial参数.

`add.apply_async((2, 3), link=add.s(16))`

第一个任务的结果是**4**，这个结果将会发送给新任务(`link`参数）,上面的表达式形式为`(2+2)+16 = 20`.

如果任务抛出一个异常你也可以调用一个callback(errback)，但是这个场景的处理方式稍有不同。

下面是一个使用errback的例子:

```python
@app.task
def error_handler(uuid):
    result = AsyncResult(uuid)
    exc = result.get(propagate=False)
    print("Task {0} raise exception: {1!r}\n{2!r}".format(uuid, exc, result.traceback))
```

可以使用`link_error`这个选项加入到一个任务的执行中：

`add.apply_async((2, 2), link_error=error.handler.s())`

另外，`link`和`link_error`可以以列表形式传入多个：

`add.apply_async((2, 2), link=[add.s(16), other_task.s()])`

callback/errbacks将会按顺序调用，所有的callback都将会把父对象的返回值当做一个partial参数来执行。

### On message

pass