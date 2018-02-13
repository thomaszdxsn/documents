# Copyright 2009 Brian Quinlan. All Rights Reserved.
# Licensed to PSF under a Contributor Agreement.

"""Implements ProcessPoolExecutor

下面的图表用文本描述了流过系统的数据流:

|======================= In-process =====================|== Out-of-process ==|

+----------+     +----------+       +--------+     +-----------+    +---------+
|          |  => | Work Ids |    => |        |  => | Call Q    | => |         |
|          |     +----------+       |        |     +-----------+    |         |
|          |     | ...      |       |        |     | ...       |    |         |
|          |     | 6        |       |        |     | 5, call() |    |         |
|          |     | 7        |       |        |     | ...       |    |         |
| Process  |     | ...      |       | Local  |     +-----------+    | Process |
|  Pool    |     +----------+       | Worker |                      |  #1..n  |
| Executor |                        | Thread |                      |         |
|          |     +----------- +     |        |     +-----------+    |         |
|          | <=> | Work Items | <=> |        | <=  | Result Q  | <= |         |
|          |     +------------+     |        |     +-----------+    |         |
|          |     | 6: call()  |     |        |     | ...       |    |         |
|          |     |    future  |     |        |     | 4, result |    |         |
|          |     | ...        |     |        |     | 3, except |    |         |
+----------+     +------------+     +--------+     +-----------+    +---------+

Executor.submit()调用之后:
- 创建一个唯一的以数字标示的`_WorkerItem`并把它加入到"Work Items"字典
- 将`_WorkerItem`的ID加入到"Work Ids"队列中

本地的worker线程：
- 从"Work Ids"队列读取work id，然后从“Work Items“字典中查找相符的WorkItem:
  如果work item被取消，那么就会把它从字典中移除，否则将它封装为一个"_CallItem"
  并且将它放到"Call Q".新的"_CallItem"都会放到"Call Q"直到"Call Q"满了为止。
  注意：“Call Q”的大小会保持尽量的小，因为放到"Call Q"的call不能被取消.
- 从`Result Q"读取"_ResultItems"，更新存储在"Work Items"字典中的Future，
  然后删除字典的entry。

  Process #1..n:
  - 从"Call Q"中读取"_CallItems"，执行这个call，然后把结果放到"Result Q".
"""

__author__ = 'Brian Quinlan (brian@sweetapp.com)'

import atexit
import os
from concurrent.futures import _base
import queue
from queue import Full
import multiprocessing
from multiprocessing import SimpleQueue
from multiprocessing.connection import wait
import threading
import weakref
from functools import partial
import itertools
import traceback

# Worker以Deamon线程/进程的方式创建。允许解释器在退出的时候
# 把ThreadPoolExecutor的闲置线程关闭。不过，让worker线程
# 和解释器一起死亡有两个不好的属性：
#   - 在解释器关闭的时候worker仍然可能在运行，
#     意味着它们可能以不可预见的方式失败.
#   - 在eval一个worker item的时候这个worker可能被杀死，
#     如果worker有副作用的话这可能会造成糟糕的结果。比如：写入一个文件
#
# 为了解决这个问题，加入了一个`exit handler`，它会告诉worker在它们的
# worker队列清空时，且线程/进程结束的时候退出。

_threads_queues = weakref.WeakKeyDictionary()
_shutdown = False


def _python_exit():
    global _shutdown
    _shutdonw = True
    items = list(_threads_queues.items())
    for t, q in items:
        q.put(None)
    for t, q in items:
        t.join()


# 下面这个常量控制数量多于process多少的call将会入队“call queue”。
# 一个相对小的值会让process花费更多的时间去等待worker，
# 一个相对大的值会让调用`Future.cancel()`的频率更少
# （在call queue的Future不能被取消)
EXTRA_QUEUED_CALLS = 1

# 使用hack的方法把远程的traceback放到本地的traceback(字符串化)


class _RemoteTraceback(Exception):
    def __init__(self, tb):
        self.tb = tb
    def __str__(self):
        return self.tb


class _ExceptionWithTraceback:
    def __init__(self, exc, tb):
        tb = traceback.format_exception(type(exc), exc, tb)
        tb = "".join(tb)
        self.exc = exc
        self.tb = '\n"""\n%s"""' % tb
    def __reduce__(self):
        return _rebuild_exc, (self.exc, self.tb)


def _rebuild_exc(exc, tb):
    exc.__cause__ = _RemoteTraceback(tb)
    return exc


class _WorkerItem(object):
    def __init__(self, future, fn, args, kwargs):
        self.future = future
        self.fn = fn
        self.args = args
        self.kwargs = kwargs


class _ResultItem(object):
    def __init__(self, work_id, exception=None, result=None):
        self.work_id = work_id
        self.exception = exception
        self.result = result


class _CallItem(object):
    def __init__(self, work_id, fn, args, kwargs):
        self.work_id = work_id
        self.fn = fn
        self.args = args
        self.kwargs =kwargs


def _get_chunks(*iterables, chunksize):
    """分块迭代一个可调用对象"""
    it = zip(*iterables)
    while True:
        chunk = tuple(itertools.slice(it, chunksize))
        if not chunk:
            return
        yield chunk


def _process_chunk(fn, chunk):
    """将可迭代对象的一部分传给map.

    这个函数在一个独立的进程中运行。
    """
    return [fn(args) for args in chunk]


def _process_worker(call_queue, result_queue):
    """eval"call_queue"中的一个call，然后把结果放到"result_queue".

    这个worker在一个独立的进程中运行。

    参数:
        call_queue: 一个`multiprocessing.Queue`实例，放置`_CallItem`对象。
        result_queue: 一个`multiprocessing.Queue`实例，防止`_ResultItem`对象.
        shutdonw: 一个`multiprocessing.Event`实例，可以释放信号给worker，让它在
                  队列"call_queue"空的时候退出。
    """
    while True:
        call_item = call_queue.get(block=True)
        if call_item is None:
            # 唤醒queue管理线程
            result_queue.put(os.getpid())
            return
        try:
            r = call_item.fn(*call_item.args, **call_item.kwargs)
        except BaseException as e:
            exc = _ExceptionWithTraceback(e, e.__traceback__)
            result_queue.put(_ResultItem(call_item.work_id, exception=exc))
        else:
            result_queue.put(_ResultItem(call_item.work_id,
                                         result=r))


def _add_call_item_to_queue(pending_work_items,
                            work_ids,
                            call_queue):
    """将`pending_work_items`中的`_WorkItems`填充`call_queue`.

    这个函数永远不会堵塞。

    参数：
        pending_work_items: 一个字典，映射work_ids到_WorkItems.例如:
            {5: <_WorkItem...>, 6:<_WorkItem...>, ...}
        work_ids: 一个放置work_id的`queue.Queue`实例
        call_queue: 一个`multiprocessing.Queue`，将会把`_WorkItems`
            填充到`_CallItems`
    """
    while True:
        if call_queue.full():
            return
        try:
            work_id = work_ids.get(block=False)
        except queue.Empty:
            return
        else:
            work_item = pending_work_items[work_id]

            if work_item.future.set_running_or_notify_cancel():
                call_queue.put(_CallItem(work_id,
                                         work_item.fn,
                                         work_item.args,
                                         work_item.kwargs),
                               block=True)
            else:
                del pending_work_items[work_id]
                continue


def _queue_management_worker(executor_reference,
                             processes,
                             pending_work_items,
                             work_ids_queue,
                             call_queue,
                             result_queue):
    """管理这个进程和worker进程的通信。

    这个函数运行在local线程。

    参数:
        executor_reference: `ProcessPoolExecutor`的一个`weakref.ref`对象
        processes: 一个`multiprocessing.Process`实例的list，用作workers。
        pending_worker_items: 一个字典，映射work_id到`_WorkerItem`，例如
            {5: <_WorkItem...>, 6: <_WorkItem...>}
        work_ids_queue: 一个包含work_id的`queue.Queue`
        call_queue: 一个`multiprocessing.Queue`队列，将`_WorkItem`转为
            `_CallItem`并填充队列.
        result_queue: 一个`multiprocessing.Queue`队列，里面的item是由
            process worker生成的`_ResultItem`
    """
    executor = None

    def shutting_down():
        return _shutdown or executor is None or executor._shutdown_thread

    def shutdown_worker():
        # 这是上界值
        nb_children_alive = sum(p.is_alive() for p in processes.values())
        for i in range(0, nb_children_alive):
            call_queue.put_nowait(None)
        # 尽快释放queue的资源
        call_queue.close()
        # 这里要注意：如果没有在创建的进程中调用`.join()`，
        # 那么在一些版本的Mac OS中可能会造成死锁
        for p in processes.values():
            p.join()

    reader = result_queue._reader

    while True:
        _add_call_item_to_queue(pending_work_items,
                                work_ids_queue,
                                call_queue)

        sentinels = [p.sentinel for p in processes.values()]
        assert sentinels
        ready = wait([reader] + sentinels)
        if reader in ready:
            result_item = reader.recv()
        else:
            # 标记进程池broken
            executor = executor_reference()
            if executor is not None:
                executor._broken = True
                executor._shutdown_thread = True
                executor = None
            # 所有运行中的future都会被标记为失败
            for work_id, work_item in pending_work_items.items():
                work_item.future.set_exception(
                    BrokenProcessPool(
                        "a process in the process pool was "
                        "terminated abruptly while the future was "
                        "running or pending."
                    )
                )
                # 删除对象的引用。请看issue16284
                del work_item
            pending_work_items.clear()
            # 强制终结剩下的worker
            for p in processes.values():
                p.terminate()
            shutdown_worker()
            return
        if isinstance(result_item, int):
            # 使用一个worker的pid来清理并shutdown
            assert shutting_down()
            p = processes.pop(result_item)
            p.join()
            if not processes:
                shutdown_worker()
                return
        elif result_item is not None:
            work_item = pending_work_items.pop(result_item.work_id, None)
            if work_item is not None:
                if result_item.exception:
                    work_item.future.set_exception(result_item.exception)
                else:
                    work_item.future.set_result(result_item.result)
                # Delete references to object. See issue16284
                del work_item
        # Check whether we should start shutting down.
        executor = executor_reference()
        # No more work items can be added if:
        #   - The interpreter is shutting down OR
        #   - The executor that owns this worker has been collected OR
        #   - The executor that owns this worker has been shutdown.
        if shutting_down():
            try:
                # Since no new work items can be added, it is safe to shutdown
                # this thread if there are no pending work items.
                if not pending_work_items:
                    shutdown_worker()
                    return
            except Full:
                # This is not a problem: we will eventually be woken up (in
                # result_queue.get()) and be able to send a sentinel again.
                pass
        executor = None

_system_limits_checked = False
_system_limited = None
def _check_system_limits():
    global _system_limits_checked, _system_limited
    if _system_limits_checked:
        if _system_limited:
            raise NotImplementedError(_system_limited)
    _system_limits_checked = True
    try:
        nsems_max = os.sysconf("SC_SEM_NSEMS_MAX")
    except (AttributeError, ValueError):
        # sysconf not available or setting not available
        return
    if nsems_max == -1:
        # indetermined limit, assume that limit is determined
        # by available memory only
        return
    if nsems_max >= 256:
        # minimum number of semaphores available
        # according to POSIX
        return
    _system_limited = "system provides too few semaphores (%d available, 256 necessary)" % nsems_max
    raise NotImplementedError(_system_limited)


class BrokenProcessPool(RuntimeError):
    """
    Raised when a process in a ProcessPoolExecutor terminated abruptly
    while a future was in the running state.
    """


class ProcessPoolExecutor(_base.Executor):
    def __init__(self, max_workers=None):
        """Initializes a new ProcessPoolExecutor instance.
        Args:
            max_workers: The maximum number of processes that can be used to
                execute the given calls. If None or not given then as many
                worker processes will be created as the machine has processors.
        """
        _check_system_limits()

        if max_workers is None:
            self._max_workers = os.cpu_count() or 1
        else:
            if max_workers <= 0:
                raise ValueError("max_workers must be greater than 0")

            self._max_workers = max_workers

        # Make the call queue slightly larger than the number of processes to
        # prevent the worker processes from idling. But don't make it too big
        # because futures in the call queue cannot be cancelled.
        self._call_queue = multiprocessing.Queue(self._max_workers +
                                                 EXTRA_QUEUED_CALLS)
        # Killed worker processes can produce spurious "broken pipe"
        # tracebacks in the queue's own worker thread. But we detect killed
        # processes anyway, so silence the tracebacks.
        self._call_queue._ignore_epipe = True
        self._result_queue = SimpleQueue()
        self._work_ids = queue.Queue()
        self._queue_management_thread = None
        # Map of pids to processes
        self._processes = {}

        # Shutdown is a two-step process.
        self._shutdown_thread = False
        self._shutdown_lock = threading.Lock()
        self._broken = False
        self._queue_count = 0
        self._pending_work_items = {}

    def _start_queue_management_thread(self):
        # When the executor gets lost, the weakref callback will wake up
        # the queue management thread.
        def weakref_cb(_, q=self._result_queue):
            q.put(None)
        if self._queue_management_thread is None:
            # Start the processes so that their sentinels are known.
            self._adjust_process_count()
            self._queue_management_thread = threading.Thread(
                    target=_queue_management_worker,
                    args=(weakref.ref(self, weakref_cb),
                          self._processes,
                          self._pending_work_items,
                          self._work_ids,
                          self._call_queue,
                          self._result_queue))
            self._queue_management_thread.daemon = True
            self._queue_management_thread.start()
            _threads_queues[self._queue_management_thread] = self._result_queue

    def _adjust_process_count(self):
        for _ in range(len(self._processes), self._max_workers):
            p = multiprocessing.Process(
                    target=_process_worker,
                    args=(self._call_queue,
                          self._result_queue))
            p.start()
            self._processes[p.pid] = p

    def submit(self, fn, *args, **kwargs):
        with self._shutdown_lock:
            if self._broken:
                raise BrokenProcessPool('A child process terminated '
                    'abruptly, the process pool is not usable anymore')
            if self._shutdown_thread:
                raise RuntimeError('cannot schedule new futures after shutdown')

            f = _base.Future()
            w = _WorkItem(f, fn, args, kwargs)

            self._pending_work_items[self._queue_count] = w
            self._work_ids.put(self._queue_count)
            self._queue_count += 1
            # Wake up queue management thread
            self._result_queue.put(None)

            self._start_queue_management_thread()
            return f
    submit.__doc__ = _base.Executor.submit.__doc__

    def map(self, fn, *iterables, timeout=None, chunksize=1):
        """Returns an iterator equivalent to map(fn, iter).
        Args:
            fn: A callable that will take as many arguments as there are
                passed iterables.
            timeout: The maximum number of seconds to wait. If None, then there
                is no limit on the wait time.
            chunksize: If greater than one, the iterables will be chopped into
                chunks of size chunksize and submitted to the process pool.
                If set to one, the items in the list will be sent one at a time.
        Returns:
            An iterator equivalent to: map(func, *iterables) but the calls may
            be evaluated out-of-order.
        Raises:
            TimeoutError: If the entire result iterator could not be generated
                before the given timeout.
            Exception: If fn(*args) raises for any values.
        """
        if chunksize < 1:
            raise ValueError("chunksize must be >= 1.")

        results = super().map(partial(_process_chunk, fn),
                              _get_chunks(*iterables, chunksize=chunksize),
                              timeout=timeout)
        return itertools.chain.from_iterable(results)

    def shutdown(self, wait=True):
        with self._shutdown_lock:
            self._shutdown_thread = True
        if self._queue_management_thread:
            # Wake up queue management thread
            self._result_queue.put(None)
            if wait:
                self._queue_management_thread.join()
        # To reduce the risk of opening too many files, remove references to
        # objects that use file descriptors.
        self._queue_management_thread = None
        self._call_queue = None
        self._result_queue = None
        self._processes = None
    shutdown.__doc__ = _base.Executor.shutdown.__doc__

atexit.register(_python_exit)


