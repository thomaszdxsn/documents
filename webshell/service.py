#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from .models import WebShell
from ..base.service import BaseService


class WebShellService(BaseService):
    model = WebShell
    unique = "url"
    unique_desc = "url"


