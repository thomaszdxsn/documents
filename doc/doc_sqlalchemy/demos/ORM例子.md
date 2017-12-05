[TOC]

SQLAlchemy发行包包含各种例子代码，阐释了各种查询模式，有些是常见的有些不是。所有的可运行文件都在发行包的`/examples`目录，描述和源代码也都存在于这里。

另外的一些SQLAlchemy例子，有些是用户贡献的，可以在官网的wiki上面观看：[http://www.sqlalchemy.org/trac/wiki/UsageRecipes](http://www.sqlalchemy.org/trac/wiki/UsageRecipes).

## 映射诀窍

### 邻接表(adjacency list)

“字典嵌字典”的结构，可以使用邻接表模式来实现：

```python
node = TreeNode('rootnode')
node.append('node1')
node.append('node3')
session.add(node)
session.commit()

dump_tree(node)
```

### 关联(associations)

一个阐释"关联对象"模式的用法，这是一个代表多对多关系中间表的一个类．

### 有向图(directed graphs)

pass
