# Copyright 2009 Brian Quinlan. All Rights Reserved.
# Licensed to PSF under a Contributor Agreement.

__author__ = 'Brian Quinlan (brian@sweetapp.com'

from concurrent.futures import (FIRST_COMPLETED,
                                FIRST_EXCEPTION,
                                ALL_COMPLETED,
                                CancelledError,
                                TimeoutError,
                                Future,
                                Executor,
                                wait,
                                as_completed)
from concurrent.futures.process import ProcessPoolExecutor
from concurrent.futures.thread import ThreadPoolExecutor                                