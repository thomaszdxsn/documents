#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""basic_association.py
使用"Order"和"Item"来解释多对多关系，通过一个关联对象OrderItem并且加入一个`price`属性来关联多对多关系.

这个关联对象模型是多对多的一种形态，它为关联关系添加了额外的数据．

这个例子从一个"Order"开始，它有一个集合引用"items",对每个item有一个特定的价格
"""
from datetime import datetime

from sqlalchemy import (create_engine, Column, Integer, String, DateTime,
                        Float, ForeignKey, and_)
from sqlalchemy.orm import relationship, Session
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Order(Base):
    __tablename__ = 'order'

    order_id = Column(Integer, primary_key=True)
    customer_name = Column(String(30), nullable=False)
    order_date = Column(DateTime, default=datetime.now)
    order_items = relationship("OrderItem", cascade="all, delete-orphan",
                              backref='order')

    def __init__(self, customer_name):
        self.customer_name = customer_name


class Item(Base):
    __tablename__ = 'item'
    item_id = Column(Integer, primary_key=True)
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
    price = Column(Float)

    def __init__(self, item, price=None):
        self.item = item
        self.price = price or item.price

    item = relationship(Item, lazy='joined')


if __name__ == '__main__':
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)

    session = Session(engine)

    # 创建目录
    tshirt, mug, hat, crowbar = {
        Item('SA T-Shirt', 10.99),
        Item('SA Mug', 6.50),
        Item('SA Hat', 8.99),
        Item('MySQL Crowbar', 16.99)
    }
    session.add_all([tshirt, mug, hat, crowbar])
    session.commit()

    # 创建一个order
    order = Order('john smith')

    # 为order创建3个orderitem并且保存
    order.order_items.append(OrderItem(mug))
    order.order_items.append(OrderItem(crowbar, 10.99))
    order.order_items.append(OrderItem(hat))
    session.add(order)
    session.commit()

    # 查询订单，打印items
    order = session.query(Order).filter_by(customer_name='john smith').one()
    print([(order_item.item.description, order_item.price)
           for order_item in order.order_items])

    # 打印买了低于售价的"MySQL.crowbar"的订单
    q = session.query(Order).join('order_items', 'item')
    q = q.filter(and_(Item.description == 'MySQL Crowbar',
                      Item.price > OrderItem.price)).all()
    print([order.customer_name for order in q])

    Base.metadata.drop_all(engine)


