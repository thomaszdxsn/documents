使用`association object`模式的例子，使用一个中间类来代表多对多关系中的中间部分.

- `basic_association.py`

    阐释一个`Order`和`Item`对象集合之间的多对多关系，通过一个"association object"`OrderItem`来关联购买价格.

- `proxied_association.py`

    和`basic_association.py`同样的例子，但是使用了`sqlalchemy.ext.associationproxy`.

- `dict_of_sets_with_default.py`

    一个高级的association proxy例子，它阐释了association proxy嵌套，生成多层Python集合的场景，在这个例子中，字典以字符串作为键，以一个整数集合作为值，将底层的映射类隐藏.