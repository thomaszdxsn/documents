#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from tornado.log import gen_log


class BaseService(object):
    model = None
    unique = None
    unique_desc = None

    @classmethod
    def verify_unique(cls, unique_value, db_session):
        if cls.unique:
            exists = (db_session.query(cls.model)
                                .filter(getattr(cls.model, cls.unique) == unique_value)
                                .one_or_none())
            if exists is not None:
                return False
        return True

    @classmethod
    def get_object_list(cls, order=None, db_session=None):
        object_list = db_session.query(cls.model)
        return {"object_list": object_list}

    @classmethod
    def get_object_by_id(cls, id_, db_session=None):
        obj = db_session.query(cls.model).get(id_)
        if obj is None:
            return {"error": 1, "message": "对象不存在"}
        return {"error": 0, "obj": obj}

    @classmethod
    def delete(cls, id_, db_session=None):
        obj = db_session.query(cls.model).get(id_)
        if obj is None:
            return {"error": 1, "message": "对象不存在"}
        db_session.delete(obj)
        try:
            db_session.flush()
        except Exception as e:
            db_session.rollback()
            gen_log.error("对象删除失败: {}".format(str(e)), exc_info=True)
            return {"error": 2, "message": "数据库错误"}
        else:
            return {"error": 0, "message": "对象删除成功!"}

    @classmethod
    def add(cls, db_session=None, **kwargs):
        # 验证对象是否违反唯一性
        unique_value = kwargs.get(cls.unique)
        if cls.verify_unique(unique_value, db_session) is False:
            return {
                "error": 1,
                "message": {cls.unique: "{}已经存在, 请重新输入".format(cls.unique_desc)}
            }
        # 创建对象
        obj = cls.model(**kwargs)
        db_session.add(obj)
        try:
            db_session.flush()
        except Exception as e:
            db_session.rollback()
            gen_log.error("对象新增失败: {}".format(str(e)), exc_info=True)
            return {"error": 2, "message": "数据库错误"}
        else:
            return {"error": 0, "message": "对象新增成功!"}

    @classmethod
    def update(cls, id_, db_session=None, **kwargs):
        # 验证对象是否存在
        obj = db_session.query(cls.model).get(id_)
        if obj is None:
            return {"error": 1, "message": "对象不存在"}
        # 验证对象是否违反唯一性
        unique_value = kwargs.get(cls.unique)
        if getattr(obj, cls.unique) != unique_value:
            if cls.verify_unique(unique_value, db_session) is False:
                return {
                    "error": 2,
                    "message": {cls.unique: "{}已经存在, 请重新输入".format(cls.unique_desc)}
                }
        # 更新对象
        for key, value in kwargs:
            setattr(obj, key, value)
        db_session.add(obj)
        try:
            db_session.flush()
        except Exception as e:
            db_session.rollback()
            gen_log.error("对象更新失败: {}".format(str(e)), exc_info=True)
            return {"error": 3, "message": "数据库错误"}
        else:
            return {"error": 0, "message": "对象更新成功!"}


