"""generic_fk.py

Illustrates a so-called "generic foreign key", in a similar fashion
to that of popular frameworks such as Django, ROR, etc.  This
approach bypasses standard referential integrity
practices, in that the "foreign key" column is not actually
constrained to refer to any particular table; instead,
in-application logic is used to determine which table is referenced.
讲解所谓的”通用外键“，这种方式在Django，RoR中经常使用。这种方式没有遵循SQL标准规范，这里的外键并没有指向任意特定的表；而是在应用层逻辑中决定这个外键应该引用哪个表。

This approach is not in line with SQLAlchemy's usual style, as foregoing
foreign key integrity means that the tables can easily contain invalid
references and also have no ability to use in-database cascade functionality.
这种方式不是SQLAlchemy的风格，放弃外键约束意味着表容易包含不正确的引用，并且不能再使用数据库级联功能了。

However, due to the popularity of these systems, as well as that it uses
the fewest number of tables (which doesn't really offer any "advantage",
though seems to be comforting to many) this recipe remains in
high demand, so in the interests of having an easy StackOverflow answer
queued up, here it is.   The author recommends "table_per_related"
or "table_per_association" instead of this approach.
不过，由于这个系统的受欢迎程度，并且它所使用的表是最少的，所以还是推荐在这里.不过更加推荐使用”table_per_related"和"table_per_association"来替代它.

.. versionadded:: 0.8.3

"""
from sqlalchemy import create_engine, Column, String, Integer, and_
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.orm import Session, relationship, foreign, remote, backref
from sqlalchemy import event


@as_declarative()
class Base(object):
    @declared_attr
    def __tablename__(cls):
        return cls.__tablename__.lower()
    id = Column(Integer, primary_key=True)


class Address(Base):
    street = Column(String)
    city = Column(String)
    zip = Column(String)

    # 这个属性是关于父对象的类型的
    discriminator = Column(String)

    # 引用父对象的主键
    parent_id = Column(Integer)
    
    @property
    def parent(self):
        return getattr(self, "parent_%s" %self.discriminator)

    def __repr__(self):
        return "%s(street=%r, city=%r, zip=%r)" %(
            self.__class__.__name__,
            self.street,
            self.city,
            self.zip
        )


class HasAddresses(object):

    @event.listens_for(HasAddresses, "mapper_configured", propagate=True)
    def set_listener(mapper, class_):
        name = class_.__name__
        discriminator = name.lower()
        class_.addresses = relationship(
            Address,
            primaryjoin=and_(
                class_.id == foreign(remote(Address.parent_id)),
                Address.discriminator == discriminator
            ),
            backref=backref(
                "parent_%s" % discriminator,
                primaryjoin=remote(class_.id) == foreign(Address.parent_id)
            )
        )

        @event.listens_for(class_.addresses, "append")
        def append_address(target, value, initiator):
            value.discriminator = discriminator


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
        print(address.parent)