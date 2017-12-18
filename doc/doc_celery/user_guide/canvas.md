## Signature

你在之前的一篇"task calling"学到了如何使用`delay()`方法调用一个任务，大多数时候你知道这个就行了！但是有时你会想把一个函数调用的签名传入到其它进程，或干脆传入一个其它函数中作为参数使用。

`signature()`封装了参数，关键字参数，以及执行选项。

- 你可以像这样创建一个add()的签名(使用`signature()`函数)

    ```python
    >>> from celery import signature
    >>> signature('tasks.add', args=(2, 2), countdonw=10)
    tasks.add(2, 2)
    ```

    这个任务有一个签名:2个参数（２，２）以及设置了countdown=10.

- 或者可以通过`.signature()`方法来创建:

    ```python
    >>> add.signature((2, 2), countdown=10)
    tasks.add(2, 2)
    ```

-  对于`.signature()`，还有一个快捷方式:

    ```python
    >>> add.s(2, 2)
    tasks.add(2, 2)
    ```

- 这个快捷方式也支持关键字参数:

    ```python
    >>> add.s(2, 2, debug=True)
    tasks.add(2, 2, debug=True)
    ```

- 对于任何signature实例，你都可以查看它的不同字段:

    ```python
    >>> s = add.signature((2, 2), {"debug": True}, countdown=10)
    >>> s.args
    (2, 2)
    >>> s.kwargs
    {'debug': True}
    >>> s.options
    {"countdown": 10}
    ```

- 它也支持所有的"calling API":

    直接调用:

    ```python
    >>> add(2, 2)
    4
    >>> add.s(2, 2)()
    4
    ```

    可以对它使用`apply_async()`

    ```python
    >>> add.apply_async(args, kwargs, **options)
    >>> add.signature(args, kwargs, **options).apply_async()
    
    >>> add.apply_async((2, 2), countdown=1)
    >>> add.signature((2, 2), countdown=1).apply_async()
    ```

- 也可以在`.s()`的时候设置选项，但是链式操作的时候需要小心:

    ```python
    >>> add.s(2, 2).set(countdown=1)
    proj.tasks.add(2, 2)
    ```

### Partial

对于一个Signature，你可以将它作为一个任务让worker执行：

```python
>>> add.s(2, 2).delay()
>>> add.s(2, 2).apply_async(countdown=1)
```

或者你可以直接将它在当前进程中执行:

```python
>>> add.s(2, 2)()
4
```

在`apply_async`/`delay`中指定额外的参数，关键字参数，选项。这种方式叫做`partial`:

- 任何加入的位置参数都会prepend到签名的参数列表中:

    ```python
    >>> partial = add.s(2)          # 不完整的签名
    >>> partial.delay(4)            ＃　4 + 2
    >>> partial.apply_async((4,))   # 和上面一样(4 + 2)
    ```

- 任何加入的关键字参数都会和签名的kwargs合并，新加入的参数将会有更高的优先级:

    ```python
    >>> s = add.s(2, 2)
    >>> s.delay(debug=True)         # -> add(2, 2, debug=True)
    >>> s.apply_partial(kwargs={'debug': True}) # 和上面一样
    ```

- 任何加入的options都会和签名的options合并，新加入的options将会具有更高的优先级:

    ```python
    >>> s = add.signature((2, 2), countdown=10)
    >>> s.apply_async(countdown=1)          # countdown现在是1
    ```

另外你可以克隆一个签名，来创建一个衍生体:

```python
>>> s = add.s(2)
proj.tasks.add(2)

>>> s.clone(args=(4,), kwargs={'debug': True})
proj.tasks.add(4, 2, debug=True)
```

### Immutability(不可变性)

Partial可以用于callback, 任何的任务links，或者chord callback.有时你想要设定一个不接受任何额外参数的callback，对于这种情况你可以讲签名设置为不可变:

```python
>>> add.apply_async((2, 2), link=reset_buffers.signature(immutable=True))
```

同样提供了一种快捷方式`.si()`:

```python
>>> add.apply_async((2, 2), link=reset_buffers.si())
```

当一个签名是不可变的(immutable)，只可以对它加入执行选项，不能再加入其它的额外参数.

> 注意
>
>> 在这篇教程里面有时可能会发现对一个签名使用了`~`操作符作为前缀(实际这是一个重载的操作符).你可能不会在生产代码中使用这种代码，但是在Shell中做试验会很方便.
>> ```python
>> >>> ~sig
>> 
>> >>> # 上面的操作符和下面的代码等同
>> >>> sig.delay().get()
>> ```

### Callbacks

使用`apply_async()`的`link`参数，可以将callback加入到任何的任务中:

```python
add.apply_async((2, 2), link=other_task.s())
```

callback只有在任务成功执行后才会被调用,并且它会讲父任务的返回值作为参数.

就像我们前面提到的那样，任何加入到signature的参数，都会被prepend到参数列表中。

比如你有一个这样的signature:

```python
>>> sig = add.s(10)
```

然后`sig.delay(result)`将会别为:

```python
>>> add.apply_async(args=(result, 10))
```

现在让我们在调用`add`的时候加入一个callback,并使用不完整的签名:

```python
>>> add.apply_async((2, 2), link=add.s(8))
```

第一个任务期待的结果是2 + 2 = 4，然后第二个任务将会计算4 + 8.


## The Primitive

>　概览
>
>> - gruop
>>    
>>     group是一个接收一组任务的签名,应该被并行运行.
>>
>> - chain
>>
>>     chain允许我们可以把任务链接在一起，让任务可以在一个完成后调用另一个，本质上是构成了一个callback的链条。
>>
>> - chord
>>
>>      chord就像group一样，但是多了一个callback。chord通过一个header group和body组成,body是一个任务,将会在header中所有的任务完成后被执行。
>>
>> - map
>>
>>      map就像普通的`map()`函数一样,但是在参数应用到task时将会创建一个临时任务.例如`task.map([1, 2])`的结果是单个任务,按顺序讲参数应用到这个任务上面:
>>
>>      `res = [task(1), task(2)]`
>>
>> - startmap
>>
>>      和map差不多,除了参数是以*args形式被应用.例如`add.starmap([(2, 2), (4, 4)])`的结果是调用下面这样一个单任务
>>      
>>      `res = [task(2, 2), task(4, 4)]`
>>
>> - chunks
>>
>>      chunksk可以分割一个长列表,比如如下的操作:
>>
>>      ```python
>>      >>> items = zip(xrange(1000), xrange(1000))     # 1000个items
>>      >>> add.chunks(items, 10)
>>      ```
>>
>>      我们讲items分割成每块１０份,结果就是1００个任务.

primitives本身都是signature对象，所以可以任意组合使用。

这里是一些例子：

- simple chain

    下面是一个简单的chain,第一个任务执行后将会把它的返回值传入链条的下一个任务...

    ```python
    >>> from celery import chain
    
    >>> # 2 + 2 + 4 + 8
    >>> res = chain(add.s(2, 2), add.s(4), add.s(8))()
    >>> res.get()
    16
    ```

    其实可以使用管道符来写:

    ```python
    >>> (add.s(2, 2) | add.s(4) | add.s(8))().get()
    16
    ```

- immutable signatures

    Signature可以是partial，所以可以追加参数，但是你有时候可能不想这样，比如在一个chain里面你不想把上一个任务的结果当做下一个任务的参数.

    在这种情况下,你需要把signature标记未immutable,这时参数不能被修改:

    `>>> add.signature((2, 2), immutable=True)`

    可以使用快捷方式`.si()`，也更推荐使用它来创建签名:

    `>>> add.si(2, 2)`

    现在你可以创建一个独立任务的chain:

    ```python
    >>> res = (add.si(2, 2) | add.si(4, 4) | add.s(8, 8))()
    >>> res.get()
    16

    >>> res.parent.get()
    8

    >>> res.parent.parent.get()
    4
    ```

- simple group

    你可以简单的创建一组任务,让它们并行执行：

    ```python
    >>> from celery import group
    >>> res = group(add.s(i, i) for i in range(10))()
    >>> res.get(timeout=1)
    [0, 2, 4, 6, 8, 10, 12, 14, 16, 18]
    ```

- simple chord

    chord可以让我们加入一个会回调，在一个group的所有任务完成后执行。

    ```python
    >>> from celery import chord
    >>> res = chord((add.s(i, i) for i in range(10)), xsum.s())()
    >>> res.get()
    90
    ```

    上面的例子创建了１０个任务并且并行启动，在所有任务完成后，会讲返回值组合进一个列表然后发送给`xsum`任务.

    chord的body同样可以是immutable,这种情况group的返回值不会传入callback:

    ```python
    >>> chord((import_contact.s(c) for c in contacts),
    ...         notify_complete.si(importe_id)).apply_async()
    ```

    注意上面`si()`的使用;这将会创建一个immutable的signature,意味着任何传入的新参数都会被忽略。

- 通过组合使用来扩展思维

    Chains也可以是partial:

    ```python
    >>> c1 = (add.s(4) | mul.s(8))
    
    # (16 + 4) * 8
    >>> res = c1(16)
    >>> res.get()
    160
    ```

    这意味着你也可以组合chains:

    ```python
    # ((4 + 16) * 2 + 4) * 8
    >>> c2 = (add.s(4, 16) | mul.s(2) | (add.s(4)) | mul.s(8))
    
    >>> res = c2()
    >>> res.get()
    352
    ```

    讲一个group和一个其它任务chain在一起，将会自动生成一个chord:

    ```python
    >>> c3 = (group(add.s(i, i) for i in range(10)) | xsum.s())
    >>> res = c3()
    >>> res.get()
    90
    ```

    group和chord同样可以接受partial参数:

    ```python
    >>> new_user_workflow = (create_user.s() | group(
    ...                     import_contacts.s(),
    ...                     send_welcome_email.s()))
    >>> new_user_workflow.delay(username='artv',
    ...                         first='Art',
    ...                         last='Vandelay',
    ...                         email='art@vandelay.com')
    ```

    如果你不想讲参数导入group,那么你需要让你的group编程immutable:

    ```python
    >> res = (add.s(4, 4) | group(add.si(i, i) for i in range(10)))
    >>> res.get()
    <GroupResult: de44df8c-821d-4c84-9a6a-44769c738f98 [
    bc01831b-9486-4e51-b046-480d7c9b78de,
    2650a1b8-32bf-4771-a645-b0a35dcc791b,
    dcbee2a5-e92d-4b03-b6eb-7aec60fd30cf,
    59f92e0a-23ea-41ce-9fad-8645a0e7759c,
    26e1e707-eccf-4bf4-bbd8-1e1729c3cce3,
    2d10a5f4-37f0-41b2-96ac-a973b1df024d,
    e13d3bdb-7ae3-4101-81a4-6f17ee21df2d,
    104b2be0-7b75-44eb-ac8e-f9220bdfa140,
    c5c551a5-0386-4973-aa37-b65cbeb2624b,
    83f72d71-4b71-428e-b604-6f16599a9f37]>

    >>> res.parent.get()
    8
    ```

### Chain

任务可以连接在一起:被连接的任务会在父任务成功执行以后才被调用：

```python
>>> res = add.apply_async((2, 2), link=mul.s(16))
>>> res.get()
4
```

被连接任务将会把父任务的返回值作为第一个参数.在上面例子中结果为４，将会再次调用`mul(4, 16)`

最终结果可以通过初始任务的子任务来调用：

```python
>>> res.children
[<AsyncResult: 8c350acf-519d-4553-8a53-4ad3a5c5aeb4>]

>>> res.children[0].get()
64
```   

结果实例有一个`collect()`方法可以讲结果看做是一个graph,让你可以迭代结果:

```python
>>> list(res.collect())
[(<AsyncResult: 7b720856-dc5f-4415-9134-5c89def5664e>, 4),
 (<AsyncResult: 8c350acf-519d-4553-8a53-4ad3a5c5aeb4>, 64)]
```

如果任务还完成，`collect()`将会抛出`IncompleteStream`异常,但是你可以获取这个graph的intermediate representation:

```python
>>> for result , value in res.collect(intermediate=True):
...
```

你尽可以凭喜好连接多个任务,signature也可以被连接：

```python
>>> s = add.s(2, 2)
>>> s.link(mul.s(4))
>>> s.link(log_result.s())
```

另外你可以使用`on_error`方法连接一个error callback:

```python
>>> add.s(2, 2).on_error(log.error.s()).delay()
```

之前提到过，error callback也可以定义在apply_async, apply_async的signature中：

```python
>>> add.apply_async((2, 2), link_error=log_error.s())
```

下面是一个errback的例子:

```python
from __future__ import absolute_import 

import os

from proj.celery import app


@app.task
def log_error(request, exc, traceback):
    with open(os.path.join("/var/errors", request.id), "a") as fh:
        print("--\n\n{0} {1} {2}".format(
            task_id, exc, traceback, file=fh
        ))
```

为了能更加简单的讲任务连接在一起，提供了一个特殊的签名`chain()`:

```python
>>> from celery import chain
>>> from proj.tasks import add, mul

>>> # (4 + 4) * 8 * 10
>>> res = chain(add.s(4, 4), mul.s(8), mul.s(10))
proj.tasks.add(4, 4) | proj.tasks.mul(8) | proj.tasks.mul(10)
```

调用chain将会在当前进程中直接运行任务,并返回chain中最后一个任务的返回结果：

```python
>>> res = chain(add.s(4, 4), mul.s(8), mul.s(10))()
>>> res.get()
640
```

它也有一个`.parent`属性可供查询中间的结果：

```python
>>> res.parent.get()
64

>>> res.parent.parent.get()
8

>>> res.parent.parent
<AsyncResult: eeaad925-6778-4ad1-88c8-b2a63d017933>
```

Chain可以支持管道操作符(`|`):

```python
>>> (add.s(2, 2) | mul.s(8) | mul.s(10)).apply_async()
```

### Graphs

另外你可以使用result graphn,比如`DependencyGraph`:

```python
>>> res = chain(add.s(4, 4), mul.s(8), mul.s(10))()

>>> res.parent.parent.graph
285fa253-fcf8-42ef-8b95-0078897e83e6(1)
    463afec2-5ed4-4036-b22d-ba067ec64f52(0)
872c3995-6fa0-46ca-98c2-5a19155afcf0(2)
    285fa253-fcf8-42ef-8b95-0078897e83e6(1)
        463afec2-5ed4-4036-b22d-ba067ec64f52(0)
```

你可以将这些graphz转换为dot格式：

```python
>>> with open('graph.dot', 'w') as fh:
...     res.parent.parent.graph.to_dot(fh)
```

并且可以创建一个图片:

`$ dot -Tpng graph.dot -o graph.png`

![image](http://docs.celeryproject.org/en/latest/_images/result_graph.png)


### Groups

group可以并行执行多个任务.

`group()`函数接受一个签名列表:

```python
>>> from celery import group
>>> from proj.tasks import add

>>> group(add.s(2, 2), add.s(4, 4))
(proj.tasks.add(2, 2), proj.tasks.add(4, 4))
```

如果你**调用**这个group,任务将会在当前进程中相继被调用,将会返回一个`GroupResult`实例，可以将之用于结果的追踪，或者告诉我们还有多少个任务在准备中：

```python
>>> g = group(add.s(2, 2), add.s(4, 4))
>>> res = g()
>>> res.get()
[4, 8]
```

Group也支持迭代器:

```python
>>> group(add.s(i, i) for i in range(100))()
```

group是一个signature对象,所以可以将它和其它signature组合使用。

#### Group Results

group任务同样也会返回特殊的结果,这个结果跟普通的任务结果差不多，除了它代表整个group的执行情况:

```python
>>> from celery import group
>>> from tasks import add

>>> job = group([
...     add.s(2, 2),
...     add.s(4, 4),
...     add.s(8, 8),
...     add.s(16, 16),
...     add.s(32, 32),
... ])

>>> result = job.apply_async()

>>> result.ready()            # 是否所有子任务都完成了?
True

>>> result.successful()       # 是否所有子任务都成功了?
True

>>> result.get()
[4, 8, 16, 32, 64]
```

`GroupResult`接受了一个`AsyncResult`列表,但是可以将它作为单个任务来操作。

它支持如下的操作:

- `successful()`

    如果所有的子任务都成功结束,则返回True.

- `failed()`

    如果有任何子任务失败，则返回True.

- `waiting()`

    如果有任何子任务还没有ready，则返回True.

- `ready()`

    如果所有的子任务都ready, 返回True

- `completed_count()`

    返回完成子任务的数量。

- `revoke()`

    取消所有的子任务.

- `join()`

    收集所有子任务的结果,将它们已调用时相同的顺序返回.

### Chord

chord是一个在group中所有任务执行完毕后才执行的任务，也可以算作是group的link callback.

让我们计算一下1 + 1 + 2 + 2 + 3 + 3...n + n知道１００个数字。

首先你需要两个任务，`add()`和`tsum()`:

```python
@app.task
def add(x, y):
    return x + y


@app.task
def tsum(numbers):
    return sum(numbers)
```

现在你可以使用chord并行计算每个步骤的结果,然后计算所有结果的sum:

```python
>>> from celery import chord
>>> from tasks import add, tsum

>>> chord(add.s(i, i) for i in range(100))(tsum.s())get()
9900
```

这个例子显然很不自然，消息传递和同步让它的速度远弱于Python的同步代码:

```python
>>> sum(i + i for i in range(100))
```

同步的步骤开销很高,所以你应该尽可能的避免使用chord.但是如果你的并行算法必须最后同步则chord会很有用.

让我们拆解一下chord表达式:

```python
>>> callback = tsum.s()
>>> header = [add.s(i, i) for i in range(100)]
>>> result = chord(header)(callback)
>>> result.get()
9900
```

记住，callback只有在header中所有的任务返回后才会被执行.`chord()`返回的任务id是这个callback的id,所以你可以等待它结束.

#### 错误处理

但是有一个任务抛出异常的话会发生什么呢？

chord callback的结果将会过渡`failure`状态,这个错误将会被抛出为`ChordError`:

```python
>>> c = chord([add.s(4, 4), raising_task.s(), add.s(8, 8)])
>>> result = c()
>>> result.get()
```

```python
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "*/celery/result.py", line 120, in get
    interval=interval)
  File "*/celery/backends/amqp.py", line 150, in wait_for
    raise meta['result']
celery.exceptions.ChordError: Dependency 97de6f3f-ea67-4517-a21c-d867c61fcb47
    raised ValueError('something something',)
```

根据result backend的不同，这个traceback返回的值也是不同的.你可以在字符串中找到最初的exception.也可以通过`result.traceback`来访问最开始的exception.

注意，**余下的任务仍然会被执行**,所有第3个任务`(add.s(8, 8))`仍然会被执行.`ChordError`也只会按照出现错误的时间显示错误，而不会按照group中的顺序显示。

想要在chord出现错误时执行一个动作，你可以加上一个errback:

```python
@app.task
def on_chord_error(request, exc, traceback):
    print("Task {0!r} raised Error: {1!r}".format(request.id, exc))
```

```python
>>> c = (group(add.s(i, i) for i in range(10)) | xsum.s().on_error(on_chord_error.s())).delat()
```

#### Important Notes

用于chord的任务不可以忽略它们的结果.也就是说你必须激活一个result backend才可以使用chord.另外，如果在你的配置中设置了`task_ignore_result = True`, 需要确保在chord中执行的任务必须单独设置`task_ignore_result = False`.

Task子类的例子：

```pyhton
class MyTask(Task):
    ignore_result = False
```

装饰任务的例子：

```python
@app.task(ignore_result=False)
def another_task(project):
    do_something()
```

默认情况下，同步步骤通过一个递归的任务poll实现，每秒执行一次.

实现例子：

```python
from celery import maybe_signature


@app.task(bind=True)
def unlock_chord(self, group, callback, interval=1, max_retries=None):
    if group.ready():
        return maybe_signature(callback).delay(group.join())
    raise self.retry(countdown=interval, max_retries=max_retries)
```

除了Redis和Memcached，都是使用这种方式来实现最后的同步:前面两者会在每个任务结束后递增一个counter，在counter超过任务设定的数量时执行callback.

Redis和Memcached的方案显然更好，但是实现在其它backend不那么容易。


### Map & Starmap

`map`和`starmap`都是内置的任务，可以调用一个序列中的每个任务。

它们和group的区别是:

- 只会发送一个任务消息
- 操作是接连的(group是并行的)

使用map的例子:

```python
>>> from proj.tasks import xsum

>>> ~xsum.map([range(10), range(100)])
[45, 4950]
```

它等同于有一个这样的临时任务:

```python
@app.task
def temp():
    return [xsum(range(10)), xsum(range(100))]
```

使用starmap需要这么写：

```python
>>> ~xsum.starmap(zip(range(10), range(10)))
[0, 2, 4, 8, 10, 12, 14, 16, 18]
```

它也等同于有下面这样一个临时任务:

```pyhton
@app.task
def temp():
    return [add(i, i) for i in range(10)]
```

`map`和`starmap`都是signature对象,所以它们可以和其它signature组合使用，也可以组合到group中:

```python
>>> add.starmap(zip(range(10), range(10))).apply_async(countdonw=10)
```

### Chunks

chunks可以把一个可迭代对象分割成小块,所以如果你有一百万个对象，你可以创建１０个任务，每个任务处理１０万个对象。

有人可能会觉得讲你的任务chunk化之后会降低并行效率，但这不是事实。实际上，由于你避免了消息的开销，反而会提升性能。

想要创建一个chunks signature,你可以使用`app.Task.chunks()`:

`>>> app.chunks(zip(range(100), range(100)), 10)`

它可以作为`group`使用:

```python
>>> from proj.tasks import add

>>> res = add.chunks(zip(range(100), range(100)), 10)()
>>> res.get()
[[0, 2, 4, 6, 8, 10, 12, 14, 16, 18],
 [20, 22, 24, 26, 28, 30, 32, 34, 36, 38],
 [40, 42, 44, 46, 48, 50, 52, 54, 56, 58],
 [60, 62, 64, 66, 68, 70, 72, 74, 76, 78],
 [80, 82, 84, 86, 88, 90, 92, 94, 96, 98],
 [100, 102, 104, 106, 108, 110, 112, 114, 116, 118],
 [120, 122, 124, 126, 128, 130, 132, 134, 136, 138],
 [140, 142, 144, 146, 148, 150, 152, 154, 156, 158],
 [160, 162, 164, 166, 168, 170, 172, 174, 176, 178],
 [180, 182, 184, 186, 188, 190, 192, 194, 196, 198]]
```

当调用`.apply_async()`时将会创建一个专门的任务,所以worker将会接受到一个独立的任务:

```python
>>> add.chunks(zip(range(100), range(100)), 10).apply_async()
```

你也可以把chunk转换为group:

```python
>>> group = add.chunks(zip(range(100), range(100)), 10).group()
```

对于group, 有一个`skew`方法可以获取递增的countdown值：

```python
>>> group.skew(start=1, stop10)()
```

这意味着group的第一个任务将会有１秒的countdown，第二个将会有2秒的countdown...