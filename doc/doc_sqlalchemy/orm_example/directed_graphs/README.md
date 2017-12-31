directed graph(有向图)结构持久化的例子。这个图存储edge的集合，每个edge都有一个"lower"和"upper"节点：

```python
n2 = Node(2)
n5 = Node(5)
n2.add_neighbor(n5)
print(n2.higher_neighbors())
```