"""Illustrates the "materialized paths" pattern.

Materialized paths is a way to represent a tree structure in SQL with fast
descendant and ancestor queries at the expense of moving nodes (which require
O(n) UPDATEs in the worst case, where n is the number of nodes in the tree). It
is a good balance in terms of performance and simplicity between the nested
sets model and the adjacency list model.
(Meterialized paths是在SQL中表达树结构的一种方式。可以在扩展或移除node的时候提供快速的祖先／后代查询(它最坏需要 O(n)　次的UPDATE，n是树中node的数量). 它的性能和简单性处于`nested set`模式和`adjacency list`模式之间)

It works by storing all nodes in a table with a path column, containing a
string of delimited IDs. Think file system paths:
(它将所有的节点存储在一个包含`path`列的表中，这个path列包含一个字符串，指代组合起来的ID.可以将它想象成文件系统)

    1
    1.2
    1.3
    1.3.4
    1.3.5
    1.3.6
    1.7
    1.7.8
    1.7.9
    1.7.9.10
    1.7.11

Descendant queries are simple left-anchored LIKE queries, and ancestors are
already stored in the path itself. Updates require going through all
descendants and changing the prefix.
(后代查询只是简单的左锚LIKE查询，而祖先已经存储在path中.更新操作需要遍历所有后代并修改它们的前缀)
"""

from sqlalchemy import create_engine, Column, Integer, String, func, select
from sqlalchemy.orm import remote, foreign, relationship, Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.expression import cast
from sqlalchemy.dialects.postgresql import ARRAY

Base = declarative_base()


class Node(Base):
    __tablename__ = 'node'

    id = Column(Integer, primary_key=True, autoincrement=False)
    path = Column(String(500), nullable=False, index=True)

    # 想要找到这个node的后代，我们需要搜索以当前node的path为path前缀的node
    descendants = relationship(
        'Node',
        viewonly=True,
        order_by=path,
        primaryjoin=remote(foreign(path)).like(path.concat(".%"))
    )

    # 想要找到这个node的祖先有点复杂。
    # 我们需要创建一个伪secondary表，因为这个行为有些像many-to-many
    secondary = select([
        id.label('id'),
        func.unnest(cast(func.string_to_array(
            func.regexp_replace(path, r"\.?\d+$", ""), "."),
            ARRAY(Integer))).label('ancestor_id')
    ]).alias()
    
    ancestor = relationship(
        "Node", viewonly=True, secondary=secondary,
        primaryjoin=id==secondary.c.id,
        secondaryjoin=secondary.c.ancestor_id == id,
        order_by=path
    )

    @property
    def depth(self):
        return len(self.path.split(".")) - 1

    def __repr__(self):
        return "Node(id={})".format(self.id)

    def __str__(self):
        root_depth = self.depth
        s = [str(self.id)]
        s.extend(((n.depth - root_depth) * "  " + str(n.id))
                  for n in self.descendants)
        return "\n".join(s)

    def move_to(self, new_parent):
        new_path = new_parent + "." + str(self.id)
        for n in self.descendants:
            n.path = new_path + n.path[len(self.path):]
        self.path = new_path


if __name__ == '__main__':
    engine = create_engine("postgresql://scott:tiger@localhost/test", echo=True)
    Base.metadata.create_all(engine)

    session = Session(engine)

    print("-" * 80)
    print("create a tree")
    session.add_all([
        Node(id=1, path="1"),
        Node(id=2, path="1.2"),
        Node(id=3, path="1.3"),
        Node(id=4, path="1.3.4"),
        Node(id=5, path="1.3.5"),
        Node(id=6, path="1.3.6"),
        Node(id=7, path="1.7"),
        Node(id=8, path="1.7.8"),
        Node(id=9, path="1.7.9"),
        Node(id=10, path="1.7.9.10"),
        Node(id=11, path="1.7.11"),
    ])
    session.flush()
    print(session.query(Node).get(1))

    print("-" * 80)
    print("move 7 under 3")
    session.query(Node).get(7).move_to(session.query(Node).get(3))
    session.flush()
    print(str(session.query(Node).get(1)))

    print("-" * 80)
    print("move 3 under 2")
    session.query(Node).get(3).move_to(session.query(Node).get(2))
    session.flush()
    print(str(session.query(Node).get(1)))

    print("-" * 80)
    print("find the anscestor of 10")
    print([n.id for n in session.query(Node).get(10).ancestor])

    session.close()
    Base.metadata.drop_all(engine)
