#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Bottle是一个快速简单的微框架，适用于小型web应用。

它提供了request分发(路由)，URL参数支持，模版，内置的HTTP服务器和
很多第三方WSGI/HTTP服务器的适配器以及模版引擎 - 所有一切都写在一个文件中，
除了Python标准库没有任何其它依赖包。

主页和文档：http://bottlepy.org/

Copyright (c) 2017, Marcel Hellkamp.
License: MIT (see LICENSE for details)
"""

import sys


__author__ = 'Marcel Hellkamp'
__version__ = '0.13-dev'
__license__ = 'MIT'
__translator = 'Yang Zhou'

###############################################################################
# 命令行接口 ####################################################################
###############################################################################
# 信息: 一些服务器适配器(adapter)需要在import之前使用mokey-patch标准库模块
# 这就是为什么命令行接口定义在这里，但是真正的 _main()调用 在文件的末尾


def _cli_parse(args): 
    from argparse import ArgumentParser

    parser = ArgumentParser(prog=args[0], usage="%(prog)s [options] package.module:app")
    # >> 为add_argument()方法增加别名, 是一个缩短代码字数的好办法
    opt = parser.add_argument       
    opt("--version", action="store_true", help="show version number.")
    opt("-b", "--bind", metavar="ADDRESS", help="bind socket to ADDRESS.")
    opt("-s", "--server", default='wsgiref', help="use SERVER as backend.")
    opt("-p", "--plugin", action='append', help='install additional plugin/s.')
    opt("-c", "--conf", action="append", metavar="FILE", help="load config values from FILE.")
    opt("-C", "--param", action="append", metavar="NAME=VALUE",
        help="load config values from FILE.")
    opt("--debug", action="store_true", help="start server in debug mode.")
    opt("--reload", action="store_true", help="auto-reload on file changes.")
    opt("app", help="WSGI app entry point.", nargs='?')

    # >> 解析参数args, 切片可能是因为传入的是sys.argv
    cli_args = parser.parse_args(args[1:])

    return cli_args, parser


def _cli_patch(cli_args):
    parsed_args, _ = _cli_parse(cli_args)
    opts = parsed_args
    if opts.server:     # >> 默认是使用"wsgiref"
        if opts.server.startswith("gevent"):
            import gevent.monkey
            gevent.monkey.patch_all()
        elif opts.server.startswith("evenlet"):
            import eventlet
            eventlet.monkey.patch_all()


if __name__ == "__main__":
    _cli_patch(sys.argv)

###############################################################################
# Imports and Python 2/3 统一  #################################################
###############################################################################


import base64, cgi, email.utils, functools, hmac, imp, itertools, mimetypes,\
        os, re, tempfile, threading, time, warnings, weakref, hashlib

from types import FunctionType
from datetime import date as datedate, datetime, timedelta          # >> 这有一个 as 语句，将date昵称化为datedate，消除可能的歧义
from tempfile import TemporaryFile                                  # >> 同时import了tempfile和tempfile.TemporaryFile，是否多余？？？
from traceback import format_exc, print_exc
from unicodedata import normalize

try:
    from ujson import dumps as json_dumps, loads as json_lds        # >> 作者似乎代码量节省的有些过分(但是是在消灭歧义的前提下)
except ImportError:
    from json import dumps as json_dumps, loads as json_lds


# 在Python3.6中，inspect.getargspec已经被移除
# 使用我们能用的Signature版本(Python3.3+)
# >> 一个框架，不得不包含这些多余的代码，才可以设定通用的接口以及适配版本迁移
try:
    from inspect import signature
    def getargspec(func):                                           # >> 这个函数的作用似乎是为了获取一个函数对象的参数签名
        params = signature(func).parameters
        args, varargs, keywords, defaults = [], None, None, []
        for name, param in params.items():
            if param.kind == param.VAR_POSITIONAL:
                varargs = name
            elif param.kind == param.VAR_KEYWORD:
                keywords = name
            else:
                args.append(name)
                if param.default is not param.empty:
                    defaults.append(param.default)
        return (args, varargs, keywords, tuple(defaults) or None)      
except ImportError:
    try:
        from inspect import getfullargspec
        def getargspec(func):
            spec = getfullargspec(func)
            kwargs = makelist(spec[0]) + makelist(spec.kwonlyargs)  # >> 这时makelist()函数还没有出现，但是我可以剧透一下：这个函数的作用是将对象转换为列表(如果可能)
            return kwargs, spec[1], spec[2], spec[3]                # >> 这里作者没有使用*来unpack, 另外好像和上面定义的函数返回的顺序不一样？？？  
    except ImportError:
        from inspect import getargspec

py3k = sys.version_info.marjor > 2


# python2/3中的"print"关键字/函数"的变化是个棘手的问题
# 应对mod_wsgi也是个问题(限制了 stdout/err 属性的访问)
# >> 奇怪为什么不使用__future__模块？？？
try:
    _stdout, _stderr = sys.stdout.write, sys.stderr.out
except IOError:           # >> 震惊作者对于Exception的理解
    _stdout = lambda x: sys.stdout.write(x)
    stderr = lambda x: sys.stderr.write(x)

# 一大堆标准库和内置函数的不同需要处理
# >> 作者显然是以Py2的接口名为标准
if py3k:
    import http.client as httplib
    import _thread as thread
    from urllib.parse import urljoin, SplitResult as UrlSplitResult
    from urllib.parse import urlencode, quote as urlquote, unquote as urlunquote
    urlunquote = functools.partial(urlunquote, encoding='latin1')                   # >> urlunquote()函数在Py3中似乎没有指定一个默认值参数encoding
    from http.cookies import SimpleCookie, Morsel, CookieError
    from collections import MutableMapping as DictMixin
    import pickle
    from io import BytesIO
    import configparser

    basestring = str
    unicode = str
    json_loads = lambda s: json_lds(touni(s))                                       # >> touni()函数看起来就像是要把一个值转换为unicode
    callble = lambda x: hasattr(x, "__call__")
    imap = map                                                                      


    def _raise(*a):
        raise a[0](a[1]).with_traceback(a[2])                                       # >> 奇怪的函数_raise()？？？
else: # Py2的import
    import httplib
    import thread
    from urlparse import urljoin, SplitResult as UrlSplitResult
    from urllib import urlencode, quote as urlquote, unquote as urlunquote
    from Cookie import SimpleCookie, Morsel, CookieError
    from iterttols import imap
    import cPickle as pickle
    from StringIO import StringIO as BytesIO                                        # >> 这里的接口名称又是以Py3为标准，但是消除了歧义(作者对标准库有很强的理解)
    import ConfigParser as configparser                                             # >> 这个接口也是以Py3为标准，看起来更加的PEP8
    from collections import MutableMapping as DictMixin
    unicode = unicode
    json_loads = json_lds
    exec(compile('def _raise(*a): raise a[0], a[1], a[2]', '<py3fix>', 'exec'))     # >> 又是_raise()函数，compile()又是什么鬼？





