#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from wtforms import Form, StringField
from wtforms.validators import DataRequired


class WebShellCreateForm(Form):
    url = StringField("url", validators=[DataRequired()])
    password = StringField("password", validators=[DataRequired()])
    password_type = StringField("password_type", validators=[DataRequired()])
    charset = StringField("charset", validators=[DataRequired()])