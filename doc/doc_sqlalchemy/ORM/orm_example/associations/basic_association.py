"""basic_association.py

阐释一个`Order`和`Item`对象集合之间的多对多关系，通过一个"association object"`OrderItem`来关联购买价格.

"association object"是多对多关系的一种形式，关联了parent/child关联的额外数据

下面的例子阐释了一个"order", 拥有一个集合属性"items"，每个item关联了一个特定的购买价格
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
    order_date = Column(DateTime, nullable=False, default=datetime.now())
    order_items = relationship('OrderItem', 
                               cascade="all, delete-orphan",
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
        return "Item(%r, %r)" %(
            self.description, self.price
        )

    
class OrderItem(Base):
    __tablename__ = 'orderitem'
    
    order_id = Column(Integer, ForeignKey('order.order_id'), primary_key=True)
    item_id = Column(Integer, ForeignKey('item.item_id'), primary_key=True)
    price = Column(Float, nullable=False)

    def __init__(self, item, price=None):
        self.item = item
        self.price = price          # 这个价格是这个订单特定的价格
    item = relationship(Itme, lazy='joined')


if __name__ == '__main__':
    engine = create_engine('sqlite://')
    Base.metadata.create_all(engine)

    session = Session(engine)

    # 创建catalog
    tshirt, mug, hat, crowbar = (
        Item('SA T-Shirt', 10.99),
        Item('SA Mug', 6.50),
        Item("SA Hat", 8.99),
        Item("MySQL Crowbar", 16.99)
    )

    session.add_all([tshirt, mug, hat, crowbar])
    session.commit()

    # 创建一个order
    oder = Order('john smish')

    # 创建三个OrderItem和order关联，并保存
    order.order_items.append(OrderItem(mug))
    order.order_items.append(OrderItem(crowbar, 10.99))
    order.order_items.append(OrderItem(hat))
    session.add(order)
    session.commit()

    # 查询order, 打印items
    order = session.query(Order).filter_by(customer_name='john smish').one()
    print([order_item.item.description, order_item.price
          for order_item in order.order_items])

    # 打印买了打折出售的"MySQL Crowbar"的顾客
    q = session.query(Order).join('order_items', 'item')
    q = q.filter(and_(Item.description == 'MySQL Crowbar',
                      Item.price > OrderItem.price))

    print([order.customer_name for order in q])