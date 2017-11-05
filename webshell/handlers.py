#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from tornado import gen, web

from .service import WebShellService
from .forms import WebShellCreateForm
from ..base.handlers import BaseHandler


class WebShellListHandler(BaseHandler):
    @gen.coroutine
    @web.authenticated
    def get(self):
        db_info = yield self.async_db(WebShellService.get_object_list)
        self.data['field_list'] = ['id', 'url', '状态', '字符集', '密码类型', '密码', '国家', '地区']
        self.data.update(db_info)
        self.write(self.data)

    @gen.coroutine
    @web.authenticated
    def post(self):
        pass