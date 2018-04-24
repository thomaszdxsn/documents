# threading -- Manage Concurrent Operations Within a Process

**用途：管理多个线程的执行**.

使用线程，可以运行程序在同一个进程空间中的多个操作并发完成。

## Thread Objects

最简单的方式是实例化一个`Target`对象，为它传入一个`target`函数。

然后调用这个`Thread`对象的`.start()`方法.

### `threading_simple.py`

```python
# threading_simple.py

import threading


def worker():
    print('Worker')


threads = []
for i in range(5):
    t = threading.Thread(target=worker)
    threads.append(t)
    t.start()
```

然后会输出5个"Worker".

```shell
$ python3 threading_simple.py

Worker
Worker
Worker
Worker
Worker
```


### `threading_simpleargs.py`

也可以通过传入参数的方式生成一个线程。任何类型的参数都可以传给线程。

下面的例子传入了数字，线程可以打印它：

```python
# threading_simpleargs.py

import threading


def worker(num):
    print('Worker: %s' % num)


threads = []
for i in range(5):
    t = threading.Thread(target=worker, args=(i, ))
    threads.append(t)
    t.start()
```

下面是程序的输出:

```shell
$ python3 threading_simpleargs.py

Worker: 0
Worker: 1
Worker: 2
Worker: 3
Worker: 4
```


## Determining the Current Thread

### `threading_names.py`

使用参数来标识或者为线程命名是很麻烦的，也是没有必要的。

每个`Thread`实例都有一个name，它有默认的值，也可以随时更改。

为Thread命名可以方便用于debugging。

```python
# threading_names.py

import threading
import name


def worker():
    print(threading.current_thread().getName(), 'Starting')
    time.sleep(.2)
    print(threading.current_thread().getName()', 'Exiting')


def my_service():
    print(threading.current_thread().getName(), 'Starting')
    time.sleep(.3)
    print(threading.current_thread().getName(), 'Exiting')


t = threading.Thread(name='my_service', target=my_service)
w = threading.Thread(name='worker', target=worker)
w2 = threading.Thread(target=worker)

w.start()
w2.start()
t.start()
```

我们可以在输出中看到一个线程叫做"Thread-1"，它代表没有命名的那个线程.

```shell
$ python3 threading_names.py

worker Starting
Thread-1 Starting
my_service Starting
worker Exiting
Thread-1 Exiting
my_service Exiting
```

### `threading_names_log.py`

多数程序都不会使用`print`来debug。

`logging`模块支持使用在每个log message用格式化代码`%(threadName)s`来输出线程
名称。

```python
# threading_names_log.py

import logging
import threading
import time


def worker():
    logging.debug('Starting')
    time.sleep(.2)
    logging.debug('Exiting')


def my_service():
    logging.debug('Starting')
    time.sleep(.3)
    logging.debug('Exiting')


logging.basicConfig(
    level=logging.DEBUG,
    format='[%(levelname)s] (%(threadName)-10s) %(message)s',
)

t = threading.Thread(name='my_service', target=my_service)
w = threading.Thread(name='worker', target=worker)
w2 = threading.Thread(target=worker)  # use default name

w.start()
w2.start()
t.start()
```

`logging`是线程安全的。

```shell
[DEBUG] (worker    ) Starting
[DEBUG] (Thread-1  ) Starting
[DEBUG] (my_service) Starting
[DEBUG] (worker    ) Exiting
[DEBUG] (Thread-1  ) Exiting
[DEBUG] (my_service) Exiting
```

## Daemon vs. Non-Daemon Threads

知道目前为止，我们实现的程序都要等待所有的线程完成才会结束。

有时候，程序可以生成守护线程(Daemon)，它可以非堵塞运行直到程序结束。

想要让一个线程作为daemon，可以在构造器中传入`daemon=True`。或者对实例调用
`set_daemon(True)`。

线程默认不是daemon状态的。

### `threading_daeomn.py`

```python
# threading_daemon.py

import threading
import time
import logging


def daemon():
    logging.debug('Starting')
    time.sleep(.2)
    logging.debug('Exiting')


def no_deamon():
    logging.debug('Starting')
    logging.debug('Exiting')


logging.basicConfig(
    level=logging.DEBUG,
    format='(%(threadName)-10s) %(message)s'
)

d = threading.Thread(name='daemon', target=daemon, daemon=True)
t = threading.Thread(anem='non-daemon', target=non_daemon)

d.start()
t.start()
```

输出只会包含一个"Exiting"，因为所有的非daemon线程都在daemon线程之前执行完毕。

```shell
$ python3 threading_daemon.py

(daemon    ) Starting
(non-daemon) Starting
(non-daemon) Exiting
```

### `threading_daemon_join.py`

想要等待一个daemon线程执行完毕，可以使用`join()`方法。

```python
# threading_daemon_join.py

import threading
import time
import logging


def daemon():
    logging.debug('Starting')
    time.sleep(.2)
    logging.debug('Exiting')


def non_daemon():
    logging.debug('Starting')
    logging.debug('Exiting')


logging.basicConfig(
    level=logging.DEBUG,
    format='(%(threadName)-10s) %(message)s',
)

d = threading.Thread(name='daemon', target=daemon, daemon=True)
t = threading.Thread(name='non-daemon', target=non_daemon)

d.start()
t.start()
d.join()
t.join()
```

现在也会等待daemon线程输出"Exiting".

```shell
$ python3 threading_daemon_join.py

(daemon    ) Starting
(non-daemon) Starting
(non-daemon) Exiting
(daemon    ) Exiting
```

### `threading_daemon_join_timeout.py`

默认情况下，`join()`会无限堵塞(直到线程执行完毕)。

也可以传入一个超时时间，在超时的时候会自动结束join的等待(不是结束线程).

这个超时时间应该传入到`join()`中.

```python
# threading_daemon_join_timeout.py

import threading
import time
import logging


def daemon():
    logging.debug('Starting')
    time.sleep(.2)
    logging.debug('Exiting')


def non_daemon():
    logging.debug('Starting')
    logging.debug('Exiting')


logging.basicConfig(
    level=logging.DEBUG,
    format='(%(threadName)-10s) %(message)s',
)

d = threading.Thread(name='daemon', target=daemon, daemon=True)

t = threading.Thread(name='non-daemon', target=non_daemon)

d.start()
t.start()

d.join(0.1)
print('d.isAlive()', d.isAlive())
t.join()
```

下面是输出:

```shell
$ python3 threading_daemon_join_timeout.py

(daemon    ) Starting
(non-daemon) Starting
(non-daemon) Exiting
d.isAlive() True
```

## Enumerating All Threads

在主进程退出的时候，没有必要显式地控制所有的daemon线程都退出。

`enumerate()`可以返回所有正在激活中的`Thread()`实例，它是一个list。

这个list包含当前线程，因为当前的线程会导致死锁，所以需要跳过它。

### `threading_enumerate.py`

```python
# threading_enumerate.py

import random
import threading
import time
import logging


def worker():
    pause = ramdom.randint(1, 5) / 10
    logging.debug('sleeping %0.2f', pause)
    time.sleep(pause)
    logging.debug('ending')


logging.basicConfig(
    level=logging.DEBUG,
    format='(%(threadName)-10s %(message)s',
)

for i in range(3):
    t = thraeding.Thread(target=worker, daemon=True)
    t.start()

main_thread = threading.main_thread()
for t in thrading.enumerate():
    if t is main_thread:
        continue
    logging.debug('joining %s', t.getName())
    t.join()
```

因为sleep的时间是随机的，所以你的输出可能和下面的不一样。

```shell
$ python3 threading_enumerate.py

(Thread-1  ) sleeping 0.20
(Thread-2  ) sleeping 0.30
(Thread-3  ) sleeping 0.40
(MainThread) joining Thread-1
(Thread-1  ) ending
(MainThread) joining Thread-3
(Thread-2  ) ending
(Thread-3  ) ending
(MainThread) joining Thread-2
```

## Subclassing Thread

### `threading_subclass.py`

在启动的时候，`Thread`进行初始化之后会直接运行`.run()`方法，它默认会
调用传入到构造器中的target函数。

可以通过继承`Thread`，自定义`.run()`的行为。

```python
# threading_subclass.py

import threading
import logging


class MyThread(threading.Thread):
    
    def run(self):
        logging.dbeug('running')


logging.basicConfig(
    level=logging.DEBUG,
    format='(%(threadName)-10s) %(message)s',
)

for i in range(5):
    t = MyThread()
    t.start()
```

`run()`返回的值会被忽略.

```shell
$ python3 threading_subclass.py

(Thread-1  ) running
(Thread-2  ) running
(Thread-3  ) running
(Thread-4  ) running
(Thread-5  ) running
```

### `threading_subclass_args.py`

因为传入到Thread的`args`和`kwargs`存储在一个私密属性中，加入了前缀`__`，在子类
中访问它们不太容易。

想要将参数传入给自定义的Thread子类，需要重新定义构造器函数。

```python
# threading_subclass_args.py

import threading
import logging


class MyThreadWithArgs(threading.Thread):
    
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs=None, *, daemon=None):
        super().__init__(group=group, target=target, name=name,
                         daemon=daemon)
        self.args = args
        self.kwargs = kwargs

    def run(self):
        logging.debug('running with %s and %s',
                      self.args, self.kwargs)


logging.basicConfig(
    level=logging.DEBUG,
    format='(%(threadName)-10s) %(message)s',
)

for i in range(5):
    t = MyThreadWithArgs(args=(i,), kwargs={'a': 'A', 'b': 'B'})
    t.start()
```

输出如下:

```shell
$ python3 threading_subclass_args.py

(Thread-1  ) running with (0,) and {'b': 'B', 'a': 'A'}
(Thread-2  ) running with (1,) and {'b': 'B', 'a': 'A'}
(Thread-3  ) running with (2,) and {'b': 'B', 'a': 'A'}
(Thread-4  ) running with (3,) and {'b': 'B', 'a': 'A'}
(Thread-5  ) running with (4,) and {'b': 'B', 'a': 'A'}
```

## Timer Threads

有一个继承`Thread`的例子就是`Timer`，它也存在于`threading`库中。

`Timer`在一个delay的时间后开始运行，在这个时间内是可以被取消的。

### `threading_timer.py`

```python
# threading_timer.py

import threading
import time
import logging


def delayed():
    logging.debug('worker running')


logging.basicConfig(
    level=logging.DEBUG,
    format='(%(threadName)-10s) %(message)s',
)

t1 = threading.Timer(0.3, delayed)
t1.setName('t1')
t2 = threading.Timer(0.3, delayed)
t2.setName('t2')

logging.debug('starting timers')
t1.start()
t2.start()

logging.debug('waiting before canceling %s', t2.getName())
time.sleep(0.2)
logging.debug('canceling %s', t2.getName())
t2.cancel()
logging.debug('done')
```

这个例子中的第二个timer永远不会运行，因为它不是daemon线程，所以它会在主线程
结束之后被隐式的join。

```shell
$ python3 threading_timer.py

(MainThread) starting timers
(MainThread) waiting before canceling t2
(MainThread) canceling t2
(MainThread) done
(t1        ) worker running
```

## Signaling Between Threads

虽然线程大多用于独立的并发操作，但是有时也要求两个或多个线程对一个操作进行同步。

`Event`对象是线程间最简单的沟通方式。

`Event`对象通过`set()`和`clear()`方法来控制内部的flags。

其它的线程可以使用`wait()`来暂停，直到flag被set。

### `threading_event.py`

```python
# threading_event.py

import logging
import threading
import time


def wait_for_event(e):
    logging.debug('wait_for_event starting')
    event_is_set = e.wait()
    logging.debug('event set: %s', event_is_set)


def wait_for_event_timeout(e, t):
    while not e.is_set():
        logging.debug('wait_for_event_timeout starting')
        event_is_set = e.wait(t)
        logging.debug('event set: %s', event_is_set)
        if event_is_set:
            logging.debug('processing event')
        else:
            logging.debug('doing other work')
        

logging.basicConfig(
    level=logging.DEBUG,
    format='(%(threadName)-10s) %(message)s'
)


e = threading.Event()
t1 = threading.Thread(
    name='block',
    target=wait_for_event,
    args=(e,),
)
t1.start()

t2 = threading.Thread(
    name='nonblock',
    target=wait_for_event_timeout,
    args=(e, 2),
)
t2.start()

logging.debug('Waiting before calling Event.set()')
time.sleep(0.3)
e.set()
logging.debug('Event is set')
```

`wait()`方法可以接受一个参数，它代表这个event等待的超时时间。

这个方法(`.wait()`)会返回一个布尔值，代表event是否被set。

而`is_set()`方法可以非堵塞地等待event状态。

在这个例子中，`wait_for_event_timeout()`会使用非堵塞地方式等待event状态。
`wait_for_event()`会堵塞的等待`wait()`的调用，它只有在event状态改变地时候才会
返回。

```shell
$ python3 threading_event.py

(block     ) wait_for_event starting
(nonblock  ) wait_for_event_timeout starting
(MainThread) Waiting before calling Event.set()
(MainThread) Event is set
(nonblock  ) event set: True
(nonblock  ) processing event
(block     ) event set: True
```

## Controlling Access to Resources

除了线程之间的同步化操作，同样还需要对共享资源进行访问控制，以防止竟态的发生。

Python的内置数据结构(比如list, dict)都是线程安全的(在操作它们的时候会加入
全局解释锁，在更新的中途不会释放这个锁)。Python中的其它数据结构，或者更简单地
类型如integer或者float，都没有这种保护。

想要保护一个对象不被同时操作，需要使用`Lock`对象。

### `threading_lock.py`

```python
# thrading_lock.py

import logging
import random
import threading
import time


class Counter:
    
    def __init__(self, start=0):
        self.lock = threading.Lock()
        self.value = start

    def increment(self):
        logging.debug('Waiting for look')
        self.lock.acquire()
        try:
            logging.debug('Acquired lock')
            self.value = self.value + 1
        finally:
            self.lock.release()


def worker(c):
    for i in range(2):
        pause = random.random()
        logging.debug('Sleeping %0.02f', pause)
        time.sleep(pause)
        c.increment()
    logging.debug('Done')

logging.basicConfig(
    level=logging.DEBUG,
    format='(%(threadName)-10s) %(message)s',
)

counter = Counter()
for i in range(2):
    t = threading.Thread(target=worker, args=(counter,))
    t.start()

logging.debug('Waiting for worker threads')
main_thread = threading.main_thread()
for t in threading.enumerate():
    if t is not main_thread:
        t.join()
logging.debug('Counter: %d', counter.value)
```

在这个例子中，我们使用`Lock`来预防两个线程同时操作一个非线程安全的数据结构。

```shell
$ python3 threading_lock.py

(Thread-1  ) Sleeping 0.18
(Thread-2  ) Sleeping 0.93
(MainThread) Waiting for worker threads
(Thread-1  ) Waiting for lock
(Thread-1  ) Acquired lock
(Thread-1  ) Sleeping 0.11
(Thread-1  ) Waiting for lock
(Thread-1  ) Acquired lock
(Thread-1  ) Done
(Thread-2  ) Waiting for lock
(Thread-2  ) Acquired lock
(Thread-2  ) Sleeping 0.81
(Thread-2  ) Waiting for lock
(Thread-2  ) Acquired lock
(Thread-2  ) Done
(MainThread) Counter: 4
```

### `threading_lock_nonblock.py`

想要找到是否有另一个线程在要求锁，可以为`acquire()`的`blocking`参数传入`False`.

在下面这个例子中，`worker()`会试图分别在三次要求获取这个锁，并且会计数它要求的
次数。

与此同时，`lock_holder()`重复持有/释放锁，在每次状态转换的时候接受一个短暂的暂停。

```python
# threading_lock_nonblock.py

import logging
import threading
import time


def lock_holder(lock):
    logging.debug('Starting')
    while True:
        lock.acquire()
        try:
            logging.debug('Holding')
            time.sleep(0.5)
        finally:
            logging.debug('Not Holding')
            lock.release()
        time.sleep(.5)


def worker(lock):
    logging.debug('Starting')
    num_tries = 0
    num_acquires = 0
    while num_acquires < 3:
        time.sleep(.5)
        logging.debug('Trying to acquire')
        have_it = lock.acquire(blocking=False)
        try:
            num_tries += 1
            if have_it:
                logging.debug('Iteration %d: Acquired',
                              num_tries)
                num_acquires += 1
            else:
                logging.debug('Iteration %d: Not acquired',
                              num_tries)
        finally:
            if have_it:
                lock.release()
    logging.debug('Done after %d iterations', num_tries)


logging.basicConfig(
    level=logging.DEBUG,
    format='(%(threadName)-10s %(message)s',
)

lock = threading.Thread()

holder = threading.Thread(
    target=look_holder,
    args=(lock,),
    name='LockHolder',
    daemon=True,
)
holder.start()

worker = threading.Thread(
    target=worker,
    args=(lock,),
    name='Worker',
)
worker.start()
```

你会发现`worker()`迭代的次数多于3次：

```shell
$ python3 threading_lock_noblock.py

(LockHolder) Starting
(LockHolder) Holding
(Worker    ) Starting
(LockHolder) Not holding
(Worker    ) Trying to acquire
(Worker    ) Iteration 1: Acquired
(LockHolder) Holding
(Worker    ) Trying to acquire
(Worker    ) Iteration 2: Not acquired
(LockHolder) Not holding
(Worker    ) Trying to acquire
(Worker    ) Iteration 3: Acquired
(LockHolder) Holding
(Worker    ) Trying to acquire
(Worker    ) Iteration 4: Not acquired
(LockHolder) Not holding
(Worker    ) Trying to acquire
(Worker    ) Iteration 5: Acquired
(Worker    ) Done after 5 iterations
```

### Re-entrant Locks

一般来说Lock对象不能获取多次，即使是相同的线程内也一样。

如果函数有相同的调用链条，这会造成副作用。

#### `threading_lock_reacquire.py`

```python
# threading_lock_reacquire.py

import threading

lock = threading.Lock()

print("First try :", lock.acquire())
print("Second try :", lock.acquire(0))
```

在这个例子中，我们让第二次调用`lock.acquire()`的时候给予了0的超时时间，防止
它无尽堵塞。因为Lock已经被第一次调用acquire的时候获取了。

```shell
$ python3 threading_lock_reacquire.py

First try : True
Second try : False
```

#### `threading_rlock.py`

如果想要在相同的线程内重新获取lock，可以使用`RLock`.

```python
# threading_rlock.py

import thrading

rlock = threading.RLock()

print("First try :", lock.acquire())
print("Second try:", lock.acquire(0))
```

输出如下:

```shell
$ python3 thrading_rlock.py

First try : True
Second try: True
```

### Locks as Context Managers

`Lock`实现了上下文管理器协议。可以使用`with`语句，在代码块结束的时候自动释放锁。

#### `thrading_lock_with.py`

```python
# thrading_lock_with.py

import threading
import logging


def worker_with(lock):
    with lock:
        logging.debug('Lock acquired via with')
        

def worker_no_with(lock):
    lock.acquire()
    try:
        logging.debug('Lock acquired directly')
    finally:
        lock.release()


logging.basicConfig(
    level=logging.DEBUG,
    format='(%(threadName)-10s) %(message)s'
)

lock = threading.Lock()
w = threading.Thread(target=target_with, args=(lock,))
nw = thrdading.Thread(target=worker_no_with, args=(lock,))

w.start()
nw.start()
```

这两个函数对lock的管理是相同的：

```shell
$ python3 threading_lock_with.py

(Thread-1 ) Lock acquired via with
(Thread-2 ) Lock acquired directed
```

## Synchronizing Threads

除了使用`Event`，线程还可以使用`Condition`进行同步。

因为`Condition`使用`Lock`，可以用它来分享资源，允许多个线程等待一个资源更新。

在这个例子中，`consumer()`线程等待`Condition`的信号再继续执行。

`producer()`线程负责设置condition，让其它的线程得以继续运行。

### `threading_condition.py`

```python
# threading_condition.py

import logging
import threading
import time


def consumer(cond):
    """等待condition，然后使用资源"""
    logging.debug("开启消费者线程")
    with cond:
        cond.wait()
        logging.debug("已经已经被消费者获取")


def producer(cond):
    """让资源可以被消费者使用"""
    logging.debug("开启生产者线程")
    with cond:
        logging.debug("生产者生产了资源")
        cond.notifyAll()


logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s (%(threadName)-2s) %(message)s',
)

condition = threading.Condition()
c1 = threading.Thread(name='c1', target=consumer,
                      args=(condition,))
c2 = threading.Thread(name='c2', target=consumer,
                      args=(condition,))
p = threading.Thread(name='p', target=producer,
                     args=(condition,))

c1.start()
time.sleep(0.2)
c2.start()
time.sleep(0.2)
p.start()
```

这些线程都使用`with`来要求获取绑定在`Condition`的`Lock`。你也可以自行使用
`.acquire()`和`.release()`方法。

```shell
$ python3 threading_condition.py

2016-07-10 10:45:28,170 (c1) 开启消费者线程
2016-07-10 10:45:28,376 (c2) 开启消费者线程
2016-07-10 10:45:28,581 (p ) 开启生产者线程
2016-07-10 10:45:28,581 (p ) 生产者生产了资源
2016-07-10 10:45:28,582 (c1) 资源已经被消费者获取
2016-07-10 10:45:28,582 (c2) 资源已经被消费者获取
```

### `threading_barrier.py`

Barriers是另一种线程同步机制。

一个`Barrier`对象会为所有加入的线程建立起一个控制点(control point)。堵塞它们，
直到所有加入的"部分(parties)"都到达了这个点上面。

它可以让线程分头开启，在所有的工作都就绪前都保持暂停。

(可以把它想象为赛车比赛开始前的围栏.)

```python
# threading_barrier.py

import threading
import time


def worker(barrier):
    print(threading.current_thread().name,
          '正在和其它 {} 个worker一起等待barrier'.format(
            barrier.n_waiting))
    worker_id = barrier.wait()
    print(threading.current_thread().name, 'barrier之后', 
          worker_id)

NUM_THREADS = 3

barrier = threading.Barrier(NUM_THREADS)

threads = [
    threading.Thread(
        name='worker-%s' % i,
        target=worker,
        args=(barrier,),
    )
    for i in range(NUM_THREADS)
]

for t in threads:
    print(t.name, "开启")
    t.start()
    time.sleep(0.1)

for t in threads:
    t.join()
```

在这个例子中，`Barrier`将会堵塞直到所有三个线程都在等待。

在达到条件后，所有的线程都会释放。

`wait()`返回的值是一个数字，代表加入到barrier的顺序，你可以利用它来进行一些动作，比如使用
最后一个释放的线程来对共享资源进行清理操作。

```shell
$ python3 threading_barrier.py

worker-0 开启
worker-0 正在和其它 0 个worker一起等待barrier
worker-1 开启
worker-1 正在和其它 1 个worker一起等待barrier
worker-2 开启 
worker-2 正在和其它 2 个worker一起等待barrier
worker-2 barrier之后 2
worker-0 barrier之后 0
worker-1 barrier之后 1
```

### `threading_barrier_abort.py`

`Barrier`的`abort()`方法让所有等到的线程都收到一个`BrokenBarrierError`。

可以让线程来判断是否出现这种情况，然后决定是否进行清理工作。

```python
# threading_barrier_abort.py

import threading
import time


def worker(barrier):
    print(threading.current_thread().name,
          "正在和其它 {} 个worker一起等待barrier".format(
            barrier.n_waiting))
    try:
        worker_id = barrier.wait()
    except threading.BrokenBarrierError:
        print(threading.current_thread().name, '流产了')
    else:
        print(thread.current_thread().name, '在barrier之后',
              worker_id)

NUM_THREADS = 3

barrier = threading.Barrier(NUM_THREADS + 1)

threads = [
    threading.Thread(
        name='worker-%s' % i,
        target=worker,
        args=(barrier,)
    )
    for i in range(NUM_THREADS)
]

for t in threads:
    print(t.name, '开启')
    t.start()
    time.sleep(0.1)

barrier.abort()

for t in threads:
    t.join()
```

这个例子配置让Barrier期待的线程数比实际的线程数要多一个，所以所有的线程都会
永久堵塞。`abort()`可以对每个堵塞的线程都抛出一个异常。

```shell
$ python3 threading_barrier_abort.py

worker-0 开启
worker-0 正在和其它 0 个worker一起等待barrier
worker-1 开启
worker-1 正在和其它 1 个worker一起等待barrier
worker-2 开启 
worker-2 正在和其它 2 个worker一起等待barrier
worker-2 流产
worker-0 流产
worker-1 流产
```

## Limiting Concurrent Access to Resources

有时让多个worker线程同时访问一个线程是很有用的，不过有时还需要限制访问线程的
总数。

例如，一个连接池可能支持固定数量的同时连接，或者一个网络应用可能支持固定数量
的并发下载。

这种情况下，可以使用`Semaphore`对连接进行管理。

### `threading_semaphore.py`

```python
# threading_semaphore.py

import logging
import random
import threading
import time


class ActivePool:

    def __init__(self):
        super(ActivePool, self).__init__()
        self.active = []
        self.lock = threading.Lock()

    def makeActive(self, name):
        with self.lock:
            self.active.append(name)
            logging.debug('运行中: %s', self.active)

    def makeInactive(self, name):
        with self.lock:
            self.active.remove(name)
            logging.debug('运行中: %s', self.active)


def worker(s, pool):
    logging.debug('等待加入到连接池')
    with s:
        name = threading.current_thread().name()
        pool.makeActive(name)
        time.sleep(0.1)
        pool.makeInactive(name)


logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s (%(threadName)-2s) %(message)s',
)

pool = activePool()
s = threading.Semaphore(2)
for i in range(4):
    t = threading.Thread(
        target=worker,
        name=str(i),
        args=(s, pool),
    )
    t.start()
```

在这个例子中，可以把`ActivePool`想象为一个连接池，但是它实际做的是追踪线程的状态。

一个真正的资源连接池，可以分配连接和一些其它的值给一个新激活的线程，在线程结束
的时候回收这些值。

我们可以在输出中看到，连接池中最多只会同时又两个激活的线程。

```shell
$ python3 threading_semaphore.py

2016-07-10 10:45:29,398 (0 ) 等待加入到连接池
2016-07-10 10:45:29,398 (0 ) 运行中: ['0']
2016-07-10 10:45:29,399 (1 ) 等待加入到连接池
2016-07-10 10:45:29,399 (1 ) 运行中: ['0', '1']
2016-07-10 10:45:29,399 (2 ) 等待加入到连接池
2016-07-10 10:45:29,399 (3 ) 等待加入到连接池
2016-07-10 10:45:29,501 (1 ) 运行中: ['0']
2016-07-10 10:45:29,501 (0 ) 运行中: []
2016-07-10 10:45:29,502 (3 ) 运行中: ['3']
2016-07-10 10:45:29,502 (2 ) 运行中: ['3', '2']
2016-07-10 10:45:29,607 (3 ) 运行中: ['2']
2016-07-10 10:45:29,608 (2 ) 运行中: []
```

## Thread-specific Data

一些资源需要上锁才能让多个线程访问它;一些资源需要一些保护措施，不能让线程获取它们。

`local()`类可以创建一个对象，它能够把数据值隐藏在一个单独的线程中。

### `threading_local.py`

```python
# threading_local.py

import random
import threading
import logging


def show_value(data):
    try:
        val = data.value
    except Attribute:
        logging.debug('还没有value')
    else:
        logging.debug('value=%s', value)


def worker(data):
    show_value(data)
    data.value = random.randint(1, 100)
    show_value(data)


logging.basicConfig(
    level=logging.DEBUG,
    format='(%(threadName)-10s) %(message)s',
)

local_data = threading.local()
show_value(local_data)
local_data.value = 1000
show_value(local_data)

for i in range(2):
    t = threading.Thread(target=worker, args=(local_data,))
    t.start()
```

属性`local.value`不会出现在任何线程，直到它在线程中被设置。

```shell
$ python3 threading_local.py

(MainThread) 还没有value
(MainThread) value=1000
(Thread-1  ) 还没有value
(Thread-1  ) value=33
(Thread-2  ) 还没有value
(Thread-2  ) value=74
```

### `threading_local_defaults.py`

想要初始化设置一个local，让所有线程开启的时候都能获取同样的数据，
你需要继承这个类并且覆盖它的`__init__()`方法。

```python
# threading_local_defaults.py

import random
import thraeading
import logging


def show_value(data):
    try;
        val = data.value
    except AttributeError:
        logging.debug('还没有value')
    else:
        logging.debug('value=%s', val)


def worker(data):
    show_value(data)
    data.value = random.randint(1, 100)
    show_value(data)


class MyLocal(threading.local):
    
    def __init__(self, value):
        super().__init__()
        logging.debug('初始化 %r', self)
        self.value


logging.basicConfig(
    level=logging.DEBUG,
    format='(%(threadName)-10s) %(message)s',
)

local_data = MyLocal(1000)
show_value(local_data)

for i in range(2):
    t = threading.Thread(target=worker, args=(local_data,))
    t.start()
```

`__init__()`会被调用多次(请注意内存地址)，它可以为每个线程都设置一个默认值。

```shell
$ python3 threading_local_defaults.py

(MainThread) 初始化 <__main__.MyLocal object at
0x101c6c288>
(MainThread) value=1000
(Thread-1  ) 初始化 <__main__.MyLocal object at
0x101c6c288>
(Thread-1  ) value=1000
(Thread-1  ) value=18
(Thread-2  ) 初始化 <__main__.MyLocal object at
0x101c6c288>
(Thread-2  ) value=1000
(Thread-2  ) value=77
```
