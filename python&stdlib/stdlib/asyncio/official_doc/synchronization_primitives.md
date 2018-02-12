# Synchronization primitives

源代码: [Lib/asyncio/locks.py](https://github.com/python/cpython/tree/3.6/Lib/asyncio/locks.py)

Locks:

- Lock
- Event
- Condition

Semaphores:

- Semaphore
- BoundedSemaphore

asyncio lock API设计于用来模仿`threading`模块的类(Lock, Event, Condition, Semaphore, BoundedSemaphore)，不过没有timeout参数。
`asyncio.wait_for()`函数可以在超时后取消一个task。

## Locks

### Lock

- class`asyncio.Lock(*, loop=None)`

    原语Lock对象.

    一个原语lock是一个同步原语，在上锁的时候它不属于任何一个特定的协程。原语lock由两种状态，"locked"或者"unlocked".

    在创建它的时候默认是"unlocked"状态。它有两个基础的方法：`acquire()`和`release()`.当状态是"unlocked"的时候，`acquire()`会改变状态为"locked"并立即返回。当状态为"locked"的时候，`acquire()`会堵塞，直到另一个协程调用`release()`把锁的状态改为"unlocked"，然后`acquire()`会重新将状态改为"locked"。`release()`应该只在"locked"状态调用；它会把状态改为"unlocked"并立即返回。如果在"unlocked"状态试图调用`release()`，则会抛出`RuntimeError`.

    如果有多个协程(多于1个)堵塞在`.acquire()`，等待锁的状态改为"unlocked"，只有一个协程会在状态改为"unlocked"的时候获取锁，并让`acquire()`继续堵塞。

    `.acquire()`是一个协程，应该以`yield from`来调用。

    `Lock`同样支持上下文管理器协议。`(yield from lock)`可以用在上下文管理器表达式。

    这个类不是线程安全的。

    用法：

    ```python
    lock = Lock()
    ...
    yield from lock
    try:
        ...
    finally:
        lock.release()
    ```

    上下文管理器的用法：

    ```python
    lock = Lock()
    ...
    with (yield from lcok):
        ...
    ```

    Lock对象可以查看当前的状态:

    ```python
    if not lock.locked():
        yield from lock
    else:
        # lock is acquired
        ...
    ```
    
    - `locked()`

        如果锁是"locked"，返回True.

    - 协程`acquire()`

        获取一个lock.

        这个方法会堵塞，直到锁的状态变为"unlocked"，然后将状态改为"locked"并返回True。

        这个方法是一个协程。

    - `release()`

        释放一个lock。

        在一个lock是“locked”状态的时候，将它重置为“unlocked”并返回。如果有任何其它的协程堵塞并等待这个lock变为“unlocked”，运行它们中的其中一个获取这个lock。

        如果在“unlocked”状态的时候调用这个方法，抛出`RuntimeError`错误.

        这个方法不会返回值。

### Event

- class`asyncio.Event(*, loop=None)`

    一个Event的实现，是`threading.Event`的异步形式。

    Event对象的类实现。一个event管理一个flag，可以通过`.set()`方法将它设置为True，使用`.clear()`方法将它重置为False。`.wait()`方法会堵塞直到flag为True。flag初始化状态为False.

    这个类不是线程安全的。

    - `clear()`

        将flag重置为False。随后，协程调用`.wait()`会堵塞，直到再次调用`.set()`让flag设置为True。

    - `is_set()`

        如果内部的flag为True，返回True。

    - `set()`

        将内部的flag设置为True。所用堵塞等待协程都会被唤醒。

    - 协程`wait()`

        堵塞，直到内部的flag变为True。


### Condition

- class`asyncio.Condition(lock=None, *, loop=None)`

    一个Condition的实现，是`threading.Condition`的异步形式。

    这个类实现了condition变量对象。一个condition变量可允许一个或多个协程等待，直到被另一个协程通知。

    如果给定了`lock`参数，它必须是一个`Lock`对象，将会把它用作是底层的锁。否则，会创建一个新的`Lock`对象。

    这个类不是线程安全的。

    - 协程`acquire()`

        获取底层的锁(lock).

        这个方法会堵塞直到锁变为"unlocked"状态，获取锁以后会把它变为“locked”状态并返回True。

        这个方法是一个协程。

    - `notify(n=1)`

        默认情况下，会唤醒一个等待这个condition的协程。如果没有协程想要获取锁，将会抛出一个`RuntimeError`.

        这个方法会唤醒最多`n`个等待condition的协程。

    - `locked()`

        如果底层的lock已被获取，返回True。

    - `notify_all()`

        唤醒所有等待这个condition的协程。这个方法类似于`notify()`，但是会唤醒所有等待的协程。

    - `release()`

        释放底层的锁。

    - 协程`wait()`

        等待，直到被通知。

        如果这个方法被调用的时候，没有其它协程获取了锁，会抛出`RuntimeError`.

        这个方法会释放底层的锁，然后堵塞直到被`notify()`或`notify_all()`唤醒。一旦被唤醒，它会重新唤醒锁并返回True。

    - 协程`wait_for(predicate)`

        等待，直到predicate变为True。

        predicate必须是一个可调用对象并返回布尔值。

## Semaphores

### Semaphores

- class`asyncio.Semaphore(value=1, *, loop=None)`

    一个Semaphore的实现。

    一个semaphore管理者内部的counter，它在调用`.acquire()`的时候会减量，在调用`.release()`的时候会增量。这个counter的值永远不会小于0。在`.acquire()`发现这个计数值为0的时候，它会堵塞并等待其它的协程调用`.release()`.

    Semaphore同样支持上下文管理协议。

    可选参数会作为counter值，默认为`1`。如果给定的参数小于0，会抛出`ValueError`。

    这个类不是线程安全的。

    - 协程`acquire()`

        获取一个semaphore。

        如果内部的counter大于0，减量这个值并立即返回True。如果counter为0，堵塞，等待另一个协程调用`release()`让counter大于0，然后返回True。
        
        这个方法是一个协程。

    - `locked()`

        如果semaphore不能立即被获取，返回True。

    - `release()`

        释放一个semaphore，增量内部的counter。如果counter为0并且另一个协程在堵塞等待，那么就唤醒这个协程。

### BoundedSemaphore

- class`asyncio.BoundedSemaphore(value=1, *, loop=None)`

    一个bounded semaphore的实现，继承自`Semaphore`.

    如果`release()`增量让值超过了原始的值，抛出`ValueError`.

    