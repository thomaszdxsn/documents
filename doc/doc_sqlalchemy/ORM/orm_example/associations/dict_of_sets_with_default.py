"""dict_of_sets_with_default.py

一个高级的association proxy例子，它阐释了association proxy嵌套，生成多层Python集合的场景，在这个例子中，字典以字符串作为键，以一个整数集合作为值，将底层的映射类隐藏.


这里有３个表，代表一个父表拥有一个字典集合，字典中的每个值存储了一个整数集合。
association proxy隐藏了持久化细节。
在访问一个不存在键的时候，同样会生成一个新的整数集合，和"collection.defaultdict"一样
"""

import operator

from sqlalchemy import create_engine, Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship, Session
from sqlalchemy.orm.collections import MappedCollection
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.associationproxy import association_proxy


class Base(object):
    id = Column(Integer, primary_key=True)

Base = declarative_base(cls=Base)


class GenDefaultCollection(MappedCollection):
    def __missing__(self, key):
        self[key] = b = B(key)
        return b


class A(Base):
    __tablename__ = 'a'

    associations = relationship(
        "B",
        collection_class=lambda: GenDefaultCollection(operator.attrgetter("key"))
    )

    collections = association_proxy("associations", "values")


class B(Base):
    __tablename__ = 'b'

    a_id = Column(Integer, ForeignKey("a.id"))
    elements = relationship('C', collection_class=set)
    key = Column(String)

    values = association_proxy("elements", "value")

    def __init__(self, key, values=None):
        self.key = key
        if values:
            self.values = values


class C(Base):
    __tablename__ = 'c'

    b_id = Column(Integer, ForeignKey("b.id"))
    value = Column(Integer)

    def __init__(self, value):
        self.value = value


if __name__ == "__main__":
    engine = create_engine("sqlite://", echo=True)
    Base.metadata.create_all(engine)
    session = Session(engine)

    # 下面代码只提到了"A"

    session.add(
        A(collections={
            "1": set([1, 2, 3])
        })
    )
    session.commit()


    a1 = session.query(A).first()
    print(a1.collections['1'])
    a1.collections['1'].add(4)
    session.commit()

    a1.collections['2'].update([7, 8, 9])
    session.commit()

    print(a1.collections['2'])


