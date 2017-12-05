#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""dict_of_sets_with_default.py

一个高级association proxy的例子是使用嵌套的association proxies来生成一个多维的Python集合对象，
这个对象以字符串（键），一组整数（值）集合的字典形式出现，隐藏了底层的映射类。

这个例子是一个3表模型，其中的父表以字符串为键，集合作为值的字典形式出现。association proxy扩展用来隐藏持久化的细节。可以通过访问字典中一个不存在的键来生成新的集合，这个特性和Python官方库的"collections.defaultdict"一样。
"""

import operator

from sqlalchemy import String, Integer, Column, create_engine, ForeignKey
from sqlalchemy.orm import relationship, Session
from sqlalchemy.orm.collections import MappedCollection
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.associationproxy import association_proxy


class BaseClass(object):
    id = Column(Integer, primary_key=True)


Base = declarative_base(cls=BaseClass)


class GenDefaultCollection(MappedCollection):
    def __missing__(self, key):
        self[key] = b = B(key)
        return b


class A(Base):
    __tablename__ = 'a'
    associations = relationship(
        "B",
        collection_class=lambda: GenDefaultCollection(operator.attrgetter('key'))
    )

    collections = association_proxy("associations", "values")
    # 建立‘associations’到对'b'关联代理中‘values’的关联


class B(Base):
    __tablename__ = 'b'
    a_id = Column(Integer, ForeignKey('a.id'), nullable=False)
    elements = relationship('C', collection_class=set)
    key = Column(String)

    values = association_proxy("elements", "value")

    # 建立"associations"到对'c'关联代理中"value"的关联

    def __init__(self, key, values=None):
        self.key = key
        if values:
            self.values = values


class C(Base):
    __tablename__ = 'c'
    b_id = Column(Integer, ForeignKey('b.id'), nullable=False)
    value = Column(Integer)

    def __init__(self, value):
        self.value = value


if __name__ == '__main__':
    engine = create_engine('sqlite://', echo=True)
    Base.metadata.create_all(engine)
    session = Session(engine)

    # 只显式引用了'A', 其它的表都通过集合使用
    session.add_all([
        A(collections={
            "1": set([1, 2, 3])
        })
    ])
    session.commit()

    a1 = session.query(A).first()
    print(a1.collections['1'])
    a1.collections['1'].add(4)
    session.commit()

    a1.collections['2'].update([7, 8, 9])
    session.commit()
    print(a1.collections['2'])