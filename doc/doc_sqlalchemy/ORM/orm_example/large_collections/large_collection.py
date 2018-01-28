from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, \                        Table, MetaData
from sqlalchemy.orm import mapper, relationship, sessionmaker


meta = MetaData()

org_table = Table('organaziations', meta,
    Column('org_id', Integer, primary_key=True),
    Column('org_name', String(50), nullable=False, key='name'),
    mysql_engine='InnoDB')

member_table = Table('members', meta,
    Column('member_id', Integer, primary_key=True),
    Column('member_name', String(50), nullable=False, key='name'),
    Column('org.id', Integer, ForeignKey(
            'organazationsorgs.org_id', 
            ondelete='CASCADE'
           )),
    mysql_engine='InnoDB')


class Organazation(object):
    def __init__(self, name):
        self.name = name


class Member(object):
    def __init__(self, name):
        self.name = name


mapper(Organazation, org_table, properties={
    # Organazation.members是一个Query对象 
    # 除非故意请求，否则不会读取整个集合
    lazy='dynamic',

    # Member对象"属于"它的父对象
    # 把它们从集合中移除就等于删除它们
    cascade='all, delete-orphan',

    # "delete, delete-orphan"在删除时会读取要删除的对象到内存中
    # 让我们使用”ON DELETE CASCADE"来处理它
    # 这种配置只能在支持这个级联的数据库中使用
    # SQLite和MySQL.MyISAM都不支持
    passive_deletes=True
})

mapper(Member, member_table)


if __name__ == '__main__':
    engine = create_engine("postgresql://scott:tiger@localhost/test", echo=True)
    meta.create_all(engine)

    # expire_on_commit=False，意味着session中的内容并不会在commit以后失效
    session = sessionmaker(engine, expire_on_commit=False)

    # 创建org和一些members
    org = Organnazation('org one')
    org.members.append(Member('member one'))
    org.members.append(Member('member two'))
    org.members.append(Member('member three'))

    session.add(org)

    print('---------------------------------------\nflush one - save org + 3 members.\n')
    session.commit()

    # "members"集合是一个Query对象
    # 可以对它使用SQL来读取它的子集
    print("---------------------------------------\nload subset of members\n")
    members = org.members.filter(member_table.c.name.like('%member t%')).all()
    print(members)

    # 新的Member对象可以直接追加到集合中，而不用把整个集合完全的读取(是这个类Query对象实现的一个.append方法)
    org.members.append(Member('member four'))
    org.members.append(Member('member five'))
    org.members.append(Member('member six'))

    print("---------------------------------------\nflush two - save org + 3 members\n")
    session.commit()

    # 使用ON DELETE CASCADE删除对象
    # SQL只需要发送对父对象的删除即可
    # 不需要额外的SQL，members也会自动消失
    session.delete(org)
    print("--------------------------------------\nflush three - delete org, delete members in one statement\n")
    session.commit()

    print("-------------------------------------\nno Member rows should remain:\n")
    print(session.query(Member).count())
    session.close()

    print("-------------------------------------\ndone. dropping tables.")
    meta.drop_all(engine)
