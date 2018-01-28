大集合的示例。

讲解了在关联对象集合过于庞大时使用`relationship`的一些选项，包括:

- 使用“dynamic"关系，可以在访问时切片只访问集合的部分内容
- 通过`passive_deletes=True`以及**ON DELETE CASCADE**可以大幅提高关联对象删除的效率