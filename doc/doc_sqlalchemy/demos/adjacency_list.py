#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from sqlalchemy import Column, ForeignKey, Integer, String, create_engine
from sqlalchemy.orm import Session, relationship, backref, joinedload_all
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.collections import attribute_mapped_collection

Base = declarative_base()


class TreeNode(Base):
    __tablename__ = 'tree'
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey(id))
    name = Column(String(50), nullable=False)

    children = relationship(
        "TreeNode",
        # 级联删除
        cascade='all, delete-orphan',

        # 临接表多对一的"一"的一方需要使用remote作为join条件
        backref=backref('parent', remote_side=id),

        # children将会在"name"属性上面作为一个字典显示
        collection_class=attribute_mapped_collection("name")
    )

    def __init__(self, name, parent=None):
        self.name = name
        self.parent = parent

    def __repr__(self):
        return "TreeNode(name={}, id={}, parent_id={})".format(self.name, self.id, self.parent_id)

    def dump(self, _indent=0):
        return " " * _indent + repr(self) + \
               "\n" + \
               "".join([
                   c.dump(_indent=_indent + 4)
                   for c in self.children.values()
               ])


if __name__ == "__main__":
    engine = create_engine("sqlite://", echo=True)


    def msg(msg, *args):
        msg = msg % args
        print("\n\n\n" + '-' * len(msg.split('\n')[0]))
        print(msg)
        print("-" * len(msg.split('\n')[0]))

    msg('创建Tree表:')

    Base.metadata.create_all(engine)

    session = Session(engine)

    node = TreeNode('rootnode')
    TreeNode('node1', parent=node)
    TreeNode('node3', parent=node)

    node2 = TreeNode('node2')
    TreeNode('subnode1', parent=node2)
    TreeNode('subnode2', parent=node2)

    msg("创建新的树结构:\n%s", node.dump())

    msg("flush + commit:")

    session.add(node)
    session.commit()

    msg("保存之后的树结构:%s", node.dump())

    TreeNode("node4", parent=node)
    TreeNode("subnode3", parent=node.children['node4'])
    TreeNode("subnode4", parent=node.children['node4'])
    TreeNode("subsubnode1", parent=node.children['node4'].children['subnode3'])

    # 从父节点中移除子节点，将会通过级联规则"delete-orphan"
    del node.children['node1']

    msg('移除节点后，刷新＋提交:')
    session.commit()

    msg('保存之后的树结构:%s', node.dump())

    msg("完全清空session, 在根节点上选择树, "
        "使用贪婪join读取来join４级深度")
    session.expunge_all()

    node = session.query(TreeNode). \
        options(joinedload_all("children", "children",
                               "children", "children")). \
        filter(TreeNode.name == 'rootnode'). \
        first()

    msg("完整的树:\n%s", node.dump())

    msg("对root结点标记删除，刷新 + 删除")

    session.delete(node)
    session.commit()