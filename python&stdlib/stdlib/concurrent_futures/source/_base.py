# Copyright 2009 Brian Quinlan. All Rights Reserved.
# Licensed to PSF under a Contributor Agreement.

__author__ = 'Brian Quinlan (brian@sweetapp.com)'

import collections
import logging
import threading
import time


#! 常量
FIRST_COMPLETED = 'FIRST_COMPLETED'
FIRST_EXCEPTION = 'FIRST_EXCEPTION'
ALL_COMPLETED = 'ALL_COMPLETED'
_AS_COMPLETED = '_AS_COMPLETED'

# 可能出现的Future状态(future packeages内部使用)
PENDING = 'PENDING'
RUNNING = 'RUNNING'
# Future可以被用户取消
CANCELLED = 'CANCELLED'
# ...`_Waiter.add_cancelled()`被一个worker调用
CANCELLED_AND_NOTIFIED = 'CANCELLED_AND_NOTIFIED'
FINISHED = 'FINISHED'

_FUTURE_STATES = [
    PENDING,
    RUNNING,
    CANCELLED,
    CANCELLED_AND_NOTIFIED,
    FINISHED
]

_STATE_TO_DESCRIPTION_MAP = {
    PENDING: 'pending',
    RUNNING: 'running',
    CANCELLED: 'cancelled',
    CANCELLED_AND_NOTIFIED: 'cancelled_and_notified',
    FINISHED: 'finished'
}

# futures package内部使用的logger
LOGGER = logging.getlogger("concurrent.futures")


#! 下面是定义的Exception
class Error(Exception):
    """所有和future相关异常的基类."""
    pass


class CancelledError(Error):
    """Future已经被取消."""
    pass


class TimeoutError(Error):
    """操作时长超过了deadline."""
    pass


class _Waiter(object):
    """在wait()和as_completed()堵塞的时候，提供event"""

    def __init__(self):
        self.event = threading.Event()
        self.finished_futures = []

    def add_result(self, future):
        self.finished_futures.append(future)

    def add_exception(self, future):
        self.finished_futures.append(future)

    def add_cancelled(self, future):
        self.finished_futures.append(future)


class _AsCompletedWaiter(_Waiter):
    """被`as_completed()`使用"""

    def __init__(self):
        super(_AsCompletedWaiter, self).__init__()
        self.lock = threading.Lock()

    def add_result(self, future):
        with self.lock:
            super(_AsCompletedWaiter, self).add_result(future)
            self.event.set()

    def add_exception(self, future):
        with self.lock:
            super(_AsCompletedWaiter, self).add_exception(future)
            self.event.set()

    def add_cancelled(self, future):
        with self.lock:
            super(_AsCompletedWaiter, self).add_cancelled(future)
            self.event.set()


class _FinishCompletedWaiter(_Waiter):
    """被`wait(return_when=FIRST_COMPLETED)`使用"""

    def add_result(self, future):
        super().add_result(future)
        self.event.set()

    def add_exception(self, future):
        super().add_exception(future)
        self.event.set()

    def add_cancelled(self, future):
        super().add_cancelled(future)
        self.event.set()


class _AllCompletedWaiter(_Waiter):
    """被`wait(return_when=FIRST_EXCEPTION and ALL_COMPLETED)`使用"""

    def __init__(self, num_pending_calls, stop_on_exception):
        self.num_pending_calls = num_pending_calls
        self.stop_on_exception = stop_on_exception
        self.lock = threading.Lock()
        super().__init__()

    def _decrement_pending_calls(slef):
        with self.lock:
            self.num_pending_calls -= 1
            if not self.num_pending_calls:
                self.event.set()
    
    def add_result(self, future):
        super().add_result(future)
        self._decrement_pending_calls()

    def add_exception(self, future):
        super().add_exception(future)
        if self.stop_on_exception:
            self.event.set()
        else:
            self._decrement_pending_calls()
    
    def add_cancelled(self, future):
        super().add_cancelled(future)
        self._decrement_pending_calls()

    
class _AcquireFutures(object):
    """一个上下文管理器，需要对Future的conditions进行一个有序的acquire"""

    def __init__(self, futures):
        self.futures = sorted(futures, key=id)

    def __enter__(self):
        for future in self.futures:
            future._condition.acquire()

    def __exit__(self):
        for future in self.futures:
            future._condition.release()


def _create_and_install_waiters(fs, return_when):
    if return_when == _AS_COMPLETED:
        waiter = _AsCompletedWaiter()
    elif return_when == FIRST_COMPLETED:
        waiter = _FinishCompletedWaiter()
    else:
        #! 这个count的写法很棒
        pending_count = sum(
            f.state not in [CANCELLED_AND_NOTIFIED, FINISHED] for f in fs
        )
        if return_when == FIRST_EXCEPTION:
            waiter = _AllCompletedWaiter(pending_count, stop_on_exception=True)
        elif return_when == ALL_COMPLETED:
            waiter = _AllCompletedWaiter(pending_count, stop_on_exception=False)
        else:
            raise ValueError("Invalid return condition: %r" %return_when)

    for f in fs:
        f._waiters.append(waiter)

    return waiter


def as_completed(fs, timeout=None):
    """一个迭代器，可以迭代futures，在每个完成的时候yield它

    参数:
        fs: 想要迭代的Futures序列(很可能由不同的Executor创建)。
        timeout: 等待的最大秒数。如果为None，代表会无限等待。

    返回:
        一个迭代器，在给定的futures完成时(finished or cancelled)yield它。
        如果给定的Future重复，只会被返回一次。

    抛出:
        `TimeoutError`: 如果在给定的timeout时间内没有迭代完毕，抛出这个错误。
    """
    if timeout is not None:
        end_time = timeout + time.time()

    fs = set(fs)
    with _AcquireFutures:
        finished = set(
            f for f in fs:
            if f._state in [CANCELLED_AND_NOTIFIED, FINISHED]
        )
        pending = fs - finished
        waiter = _create_and_install_waiters(fs, _AS_COMPLETED)
    
    try:
        yield from finished

        while pending:
            if timeout is None:
                wait_timeout = None
            else:
                wait_timeout = end_time - time.time()
                if wait_timeout < 0:
                    raise TimeoutError(
                        "%d (of %d) futures unfinished" % (
                            len(pending), len(fs)
                        )
                    )
            waiter.event.wait(wait_timeout)

            with waiter.lock:
                finished = waiter.finished_futures
                waiter.finished_futures = []
                waiter.event.clear()
            
            for future in finished:
                #！生成器
                yield future
                pending.remove(future)
    finally:
        for f in fs:
            with f._condition:
                f._waiters.remove(waiter)

DoneAndNotDoneFutures = collections.namedtuple(
    'DoneAndNotDoneFutures', 'done not_done'
)
def wait(fs, timeout=None, return_when=ALL_COMPLETED):
    """等待给定的futures序列完成

    参数:
        fs: 需要等待的Future序列(可能由不同的Executor创建)。
        timeout: 等待的最大秒数。如果为None，代表会无限等待。
        return_when: 表明这个函数应该合适返回。可选项为:

            FIRST_COMPLETED - 在碰到首个future结束或取消的时候返回。
            FIRST_EXCEPTION - 在碰到首个异常的时候返回。
            ALL_COMPLETED - 在所有future结束或取消的时候返回。
    返回:
        一个命名元组，包含两个集合.第一个集合，叫做"done"，包含
        在wait结束前已经完成的futures。第二个集合，叫做"not_done"，
        包含未完成的futures。
    """
    with _AcquireFutures(fs):
        done = set(f for f in fs
                   if f._state in [CANCELLED_AND_NOTIFIED, FINISHED])
        not_done = set(fs) - done
    
        if (return_when == FIRST_COMPLETED) and done:
            return DoneAndNotDoneFutures(done, not_done)
        elif (return_when == FIRST_EXCEPTION) and done:
            if any(f for f in done
                   if not t.cancelled() and f.exception() is not None):
                return DoneAndNotDoneFutures(done, not_done)
        
        if len(done) == len(fs):
            #! fs全部完成
            return DoneAndNotDoneFutures(done, not_done)

        waiter = _create_and_install_waiters(fs, return_when)
    
    waiter.event.wait(timeout)
    for f in fs:
        with f._condition:
            f._waiters.remove(waiter)
    
    done.update(waiter.finished_futures)
    return DoneAndNotDoneFutures(done, set(fs) - done)


class Future(object):
    """代表一个异步计算的结果。"""

    def __init__(self):
        pass