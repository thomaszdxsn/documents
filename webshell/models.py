#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from sqlalchemy import Column, String, Boolean, Datetime
from ..base.models import Base


class WebShell(Base):
    __tablename__ = 'webshell'
    url = Column(String(256), index=True, unique=True)
    password = Column(String(64))
    password_type = Column(String(64))
    country = Column(String(32))
    district = Column(String(32))
    charset = Column(String(32))
    status = Column(Boolean, default=True)
    last_login = Column(Datetime)


