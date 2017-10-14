#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""proxied_association.py

和basic_association同样的例子，
增加了'sqlalchemy.ext.associationproxy'
对显式指定一个“OrderItem“引用
"""

from datetime import datetime

from sqlalchemy import (create_engine, Column, Integer, String, DateTime,
                        Float, ForeignKey)
from sqlalchemy.orm import relationship, Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.associationproxy import association_proxy

Base = declarative_base()


class Order(Base):
    __tablename__ = 'order'

    order_id = Column(Integer, primary_key=True)
    customer_name = Column(String(30), nullable=False)
    order_date = Column(DateTime, nullable=False, default=datetime.now)
    order_items = relationship('OrderItem',
                               cascade='all,delete',
                               backref='order')
    items = association_proxy("order_items", "item")

    def __init__(self, customer_name):
        self.customer_name = customer_name


class Item(Base):
    __tablename__ = 'item'
    item_id = Column(Integer, priamry_key=True)
    description = Column(String(30), nullable=False)
    price = Column(Float, nullable=False)

    def __init__(self, description, price):
        self.description = description
        self.price = price

    def __repr__(self):
        return "Item({}, {})".format(self.description, self.price)


class OrderItem(Base):
    __tablename__ = 'orderitem'
    order_id = Column(Integer, ForeignKey('order.order_id'), primary_key=True)
    item_id = Column(Integer, ForeignKey('item.item_id'), primary_key=True)
    price = Column(Float, nullable=False)

    def __init__(self, item, price=None):
        self.item = item
        self.price = price or item.price

    item = relationship(Item, lazy='joined')


if __name__ == '__main__':
    engine = create_engine('sqlite://')
    Base.metadata.create_all(engine)

    session = Session(engine)

    # 创建Item
    tshirt, mug, hat, crowbar = (
        Item('SA T-Shirt', 10.99),
        Item('SA Mug', 6.50),
        Item('SA Hat', 8.99),
        Item('MySQL Crowbar', 16.99)
    )
    session.add_all([tshirt, mug, hat, crowbar])
    session.commit()

    # 创建一个Order
    order = Order('john smith')

    # 通过association proxy来增加item
    # 将会自动创建OrderItem
    order.items.append(mug)
    order.items.append(hat)

    # 显式增加一个OrderItem
    order.order_items.append(OrderItem(crowbar, 10.99))

    session.add(order)
    session.commit()

    # 查询order, 打印items
    order = (session.query(Order).filter_by(customer_name='john smith')
             .one())

    # 通过OrderItem集合直接打印items
    print([(assoc.item.description, assoc.price, assoc.item.price)
           for assoc in order.order_items])

    # 通过"proxies" items集合直接打印items
    print([(item.description, item.price)
           for item in order.items])

    # 打印买了"MySQL Crowbar"的消费者
    orders = session.query(Order). \
        join('order_itmes', 'item'). \
        filter(Item.description == 'MySQL Crowbar'). \
        filter(Item.price > OrderItem.price)
    print([o.customer_name for o in orders])