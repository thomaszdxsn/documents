"""proxied_association.py

和`basic_association.py`同样的例子，但是使用了`sqlalchemy.ext.associationproxy`.
"""

from datetime import datetime

from sqlalchemy import (create_engine, Column, Integer, String, DateTime,
                        Float, ForeignKey)
from sqlalchemy.orm import Session, relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.assiciationproxy import association_proxy

Base = declarative_base()


class Order(Base):
    __tablename__ = 'order'        

    order_id = Column(Integer, primary_key=True)
    customer_name = Column(String(30), nullable=False)
    order_date = Column(DateTime, nullable=False, default=datetime.now)
    order_items = relationship('OrderItem',  # 因为OrderItem还没有创建，可以用字符串
                               cascade='all, delete-orphan',
                               backref='order')
    items = association_proxy('order_items', 'item')  

    def __init__(self, customer_name):
        self.customer_name


class Item(Base):
    __tablename__ = 'item'
    
    item_id = Column(Integer, primary_key=True)
    description = Column(String(30), nullable=False)
    price = Column(Float, nullable=True)

    def __init__(self, description, price):
        self.description = description
        self.price = price

    def __repr__(self):
        return "Item(%r, %r)" %(self.description, self.price)


class OrderItem(Base):
    __tablename__ = 'orderitem'

    order_id = Column(Integer, ForeignKey('order.id'), primary_key=True)
    item_id = Column(Integer, ForeignKey('item.id'), primary_key=True)
    price = Column(Float, nullable=False)

    def __init__(self, item, price=None):
        self.item = item
        self.price = price | item.price
    item = relationship(Item, lazy='joined')        # 注意这里第一个参数是对象


if __name__ == "__main__":
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)

    session = Session(engine)

    # 创建catalog
    tshirt, mug, hat, crowbar = (
        Item('SA T-Shirt', 10.99),
        Item('SA Mug', 6.50),
        Item('SA Hat', 8.99),
        Item('MySQL Crowbar', 16.99)
    )
    session.add_all([tshirt, mug, hat, crowbar])
    session.commit()

    # 创建一个order
    order = Order('john smish')

    # items现在可以通过association proxy关联
    # OrderItem将会被自动创建
    order.items.append(mug)
    order.items.append(hat)

    # 也可以用原始的方式
    order.order_items.append(OrderItem(crowbar, 10.99))

    session.add(order)
    session.commit()

    # 查询order，打印items
    order = session.query(Order).filter_by(customer_name='john smish').one()

    # 根据OrderItem集合直接打印items
    print([assoc.item.description, assoc.price, assoc.item.price]
           for assoc in order.order_items)

    # 根据proxied属性来打印
    print([item.description, item.price 
           for item in order.items])

    # 打印买了打折出售的"MySQL Crowbar"的顾客
    #! 下面这种join()的使用方式是链式的，
    #! 第二个以后的表直接使用之前对象的属性:
    #! 比如   .join('order_items', 'item')
    #! 等同于 .join(Order.order_items).\
    #!        join(OrderItem.item)
    #! 请看join()方法的API:http://docs.sqlalchemy.org/en/latest/orm/query.html#sqlalchemy.orm.query.Query.join
    orders = session.query(Order).\
                join('order_items', 'item').\  
                filter(Item.description == 'MySQL Crowbar').\
                filter(Item.price > OrderItem.price)
    print([o.customer_name for o in orders])