# Copyright 2009 Brian Quinlan. All Rights Reserved.
# Licensed to PSF under a Contributor Agreement.

"""Implements ThreadPoolExecutor."""

__author__ = 'Brian Quinlan (brian@sweetapp.com)'

import atexit
from concurrent.futures import _base
import queue
import threading
import weakref
import os


# Worker以Deamon线程的方式创建。允许解释器在退出的时候
# 把ThreadPoolExecutor的闲置线程关闭。不过，让worker线程
# 和解释器一起死亡有两个不好的属性：
#   - 在解释器关闭的时候worker仍然可能在运行，
#     意味着它们可能以不可预见的方式失败.
#   - 在eval一个worker item的时候这个worker可能被杀死，
#     如果worker有副作用的话这可能会造成糟糕的结果。比如：写入一个文件
#
# 为了解决这个问题，加入了一个`exit handler`，它会告诉worker在它们的
# worker队列清空时，且线程结束的时候退出。

_threads_queues = weakref.WeakKeyDictionary()
_shutdown = False


def _python_exit():
    global _shutdown
    _shutdown = True
    items = list(_threads_queues.items())
    for t, q in items:  #! q代表queue
        q.put(None)
    for t, q in items:  #! t代表thread
        t.join()


atexit.register(_python_exit)


class _WorkItem(object):

    def __init__(self, future, fn, args, kwargs):
        self.future = future
        self.fn = fn
        self.args = args
        self.kwargs = kwargs

    def run(self):
        if not self.future.set_running_or_notify_cancel():
            return

        try:
            result = self.fn(*self.args, **self.kwargs)
        except BaseException as e:
            self.future.set_exception(e)
        else:
            self.future.set_result(result)
        

def _worker(executor_reference, worker_queue):
    try:
        while True:
            work_item = work_queue.get(block=True)
            if work_item is not None:
                work_item.run()
                del work_item
                continue
            executor = executor_reference()
            # 在下面情况下退出:
            #   - 解释器关闭 OR
            #   - worker所属的executor被垃圾回收 OR
            #   - worker所属的executor已经关闭
            if _shutdown or executor is None or executor._shutdown:
                # 注意其它worker
                work_queue.put(None)
                return
            del executor
    except BaseException:
        _base.LOGGER.critical('Exception in worker', exc_info=True)

    
class ThreadPoolExecutor(_base.Executor):

    def __init__(self, max_workers=None):
        """初始化一个新的ThreadPoolExecutor实例

        参数：
            max_workers: 开启的最大线程数量.
        """
        if max_workers is None:
            # 使用这个数量的worker，因为线程通常是进行I/O任务,
            # 而不是进行CPU密集型计算工作
            max_workers = (os.cpu_count() or 1) * 5
        if max_workers <= 0:
            raise ValueError("max_workers must be greater than 0")
        
        self._max_workers = max_workers
        self._worker.queue = queue.Queue()
        self._threads = set()
        self._shutdown = False
        self._shutdown_lock = threading.Lock()

    def submit(self, fn, *args, **kwargs):
        with self._shutdown_lock:
            if self._shutdown:
                raise RuntimError('cannot schedule new futures after shutdown!')

            f = _base.Future()
            w = _WorkItem(f, fn, args, kwargs)

            self._worker_queue.put(w)
            self._adjust_thread_count()
            return f
    submit.__doc__ = _base.Exception.submit.__doc__

    def _adjust_thread_count(self):
        # 在executor丢失以后，weakref的callback
        # 会唤醒worker线程
        def weakref_cb(_, q=self._work_queue):
            q.put(None)
        # TODO(bquinlan): 如果闲置的线程比work queue
        # 里面的itme还多，应该避免创建新的线程
        if len(self._threads) < self._max_workers:
            t = threading.Thread(target=_worker,
                                 args=(weakref.ref(self, weakref_cb),
                                      self._work_queue))
            t.daemon = True
            t.start()
            self._threads.add(t)
            _threads_queues[t] = self._worker_queue

    def shutdown(self, wait=True):
        with self._shutdown_lock:
            self._shutdown = True
            self.work_queue.put(None)
        if wait:
            for t in self._threads:
                t.join()
    shutdown.__doc__ = _base.Executor.__doc__