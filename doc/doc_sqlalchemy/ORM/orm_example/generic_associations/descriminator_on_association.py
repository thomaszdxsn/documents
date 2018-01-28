"""discriminator_on_related.py

Illustrates a mixin which provides a generic association
using a single target table and a single association table,
referred to by all parent tables.  The association table
contains a "discriminator" column which determines what type of
parent object associates to each particular row in the association
table.

SQLAlchemy's single-table-inheritance feature is used
to target different association types.
这里用到了SQLAlchemy的单表继承特性.

This configuration attempts to simulate a so-called "generic foreign key"
as closely as possible without actually foregoing the use of real
foreign keys.   Unlike table-per-related and table-per-association,
it uses a fixed number of tables to serve any number of potential parent
objects, but is also slightly more complex.
这个配置试图尽可能模仿所谓的“通用外键"，但是并没有使用真正的外键。它不像之前两个例子需要多个Table来对应多个关系(只需一个即可)，但是配置方面可能稍显复杂。

"""
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declared_attr, as_declarative
from sqlalchemy.orm import Session, relationship, backref
from sqlalchemy.ext.associationproxy import association_proxy


@as_declarative
class Base(object):
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    id = Column(Integer, primary_key=True)


class AddressAssociation(Base):
    """为特定父类关联一个Address对象的集合"""
    __tablename__ = 'address_association'

    discriminator = Column(String)

    __mapper_args__ = {
        "polymorhpic_on": discriminator
    }


class Address(Base):
    association_id = Column(Integer, 
                        ForeignKey('address_association.id'))
    street = Column(String)
    city = Column(String)
    zip = Column(String)
    association = relationship('AddressAssociation',
                               bacref='addresses')
    parent = association_proxy('association', 'parent')

    def __repr__(self):
        return "%s(street=%r, city=%r, zip=%r)" %(
            self.__class__.__name__,
            self.street,
            self.city,
            self.zip
        )


class HasAddresses(object):
    @declared_attr
    def address_association_id(cls):
        return Column(Integer, ForeignKey('address_association.id'))

    @declared_attr
    def address_association(cls):
        name = cls.__name__
        discriminator = name.lower()

        assoc_cls = type(
            "%sAddressAssociation" %name,
            (AddressAssociation,),
            dict(
                __tablename__=name,
                __mapper_args__={
                    'polymorhpic_identity': discriminator
                }
            )
        )

        cls.addresses = association_proxy(
            "address_association", "addresses",
            creator=lambda addresses: assoc_cls(addresses=addresses)
        )
        
        return relationship(assoc_cls,
                    backref=backref('parent', uselist=False))


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
    for Address in customer.addresses:
        print(address)
        print(address.parent)