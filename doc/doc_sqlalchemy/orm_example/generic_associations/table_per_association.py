"""table_per_association.py

讲解mixin如何通过已生成的关联表来为每个夫类创建一个通用的关联。这个关联对象本身只存在于一个表中，被所有的父表所分享。

这个配置的优势在于所有的Adreess行都在一个表中，所以"Address"的定义可以在一个地方来维护。
关联表包含Address的外键，所有Address没有依赖于系统。
"""

from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Table
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.orm import Session, relationship


@as_declarative()
class Base(object):
    """一个基类，自动提供表名，帮助你定义主键列
    """
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()
    id = Column(Integer, primary_key=True)


class Address(Base):
    """Address类

    在一个表中表达所有的address记录
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
    """HasAddresses是一个mixin，为每个父类提供一个address_association表
    """

    @declared_attr
    def addresses(cls):
        address_association = Table(
            "%s_addresses" % cls.__tablename__,
            cls.metadata,
            Column("address_id", ForeignKey("address.id"),
                               primary_key=True),
            Column("%s_id" % cls.__tablename__,
                            ForeignKey("%s.id" % cls.__tablename__),
                            primary_key=True)
        )
        return relationship(Address, secondary=address_association)


class Customer(HasAddresses, Base):
    name = Column(String)


class Supplier(HasAddresses, Base):
    company_name = Column(String)


engine = create_engine('sqlite://', echo=True)
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