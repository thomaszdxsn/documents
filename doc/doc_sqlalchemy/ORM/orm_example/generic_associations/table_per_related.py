"""table_per_related.py

Illustrates a generic association which persists association
objects within individual tables, each one generated to persist
those objects on behalf of a particular parent class.

This configuration has the advantage that each type of parent
maintains its "Address" rows separately, so that collection
size for one type of parent will have no impact on other types
of parent.   Navigation between parent and "Address" is simple,
direct, and bidirectional.
这个配置的优势是，每种类型的父类都分别维持了自己的"address"行，所以一个父类型的集合大小不会影响另一个父类型。在父类和Address之间的导航是简单、直接和双向的。

This recipe is the most efficient (speed wise and storage wise)
and simple of all of them.
这个示例是最高效的(无论速度还是存储)，并且也是最简单的。

The creation of many related tables may seem at first like an issue
but there really isn't any - the management and targeting of these tables
is completely automated.
创建多个关联表乍看起来是一个问题，但是其实不算 - 对这些表的管理和导航都是自动完成的。
"""

from sqlalchemy import create_engine, Column, String, Integer, ForeignKey
from sqlalchemy.orm import Session, relationship
from sqlalchemy.ext.declarative import declared_attr, as_declarative


@as_declarative()
class Base(object):
    """基类。提供自动化表名定义和帮助你生成主键列"""

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    id = Column(Integer, primary_key=True)


class Address(object):
    """定义每个"address"表中都会出现的列
    
    这是一个声明式minin，所以除了column以外的mapper属性都应该使用`@declared_attr`来装饰
    """
    street = Column(String)
    city = Column(String)
    zip = Column(String)

    def __repr__(self):
        return "%s(street=%r, city=%r, zip=%r)" %(
            self.__class__.__name__,
            self.street,
            self.city,
            self.zip
        )


class HasAddresses(object):
    """HasAddresses是一个mixin。
    将会为每个父对象创建一个新的Address类.
    """

    @declared_attr
    def addresses(cls):
        # 创建新的一个类，它们和父类都是多对一关系
        cls.Address = type(
            "%sAddresses" % cls.__name__,
            (Address, Base,),       # 元类中指定的基类
            dict(
                __tablename__ = "%s.address" %cls.__tablename__,
                parent_id = Column(Integer, 
                                ForeignKey("%s.id" %cls.__tablename__)),
                parent=relationship(cls)
            )
        )
        return relationship(cls.Address)


class Customer(HasAddresses, Base):
    name = Column(String)


class Supplier(HasAddresses, Base):
    company_name = Column(String)


engine = create_engine("sqlite://", echo=True)
Base.metadata.create_all(engine)

session = Session(engine)

session.add_all([
    Customer(
        name='customer 1',
        addresses=[
            Address(
                street='123 anywhere street',
                city='New York',
                zip='10110'
            ),
            Address(
                street='40 main street',
                city='San Francisco',
                zip='95732'
            )
        ]
    ),
    Supplier(
        company_name='Ace Hammers',
        addresses=[
            Address(
                street='2569 west elm',
                city='Detroit',
                zip='56785'
            )
        ]
    )
])

session.commit()

for customer in session.query(Customer):
    for address in customer.addresses:
        print(address)
        print(address.parent)