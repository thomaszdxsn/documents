讲解了各种各样的**通用关联**方式。

所有的例子都使用了声明式扩展以及声明式mixin。都使用了相同的两个类，`Customer`和`Supplier`，都继承了一个`HasAddress`mixin，这个mixin确保父类提供了一个`addresses`关系集合，集合中包含`Address`对象。

文件列表:

- `table_per_association.py`

    讲解mixin如何通过已生成的关联表来为每个夫类创建一个通用的关联表(即secondary)。这个关联对象本身只存在于一个表中，被所有的父表所分享。

- `table_per_related.py`

    讲解一个通用的关联，它将关联对象分别持久化到各自的表。

- `descriminator_on_association.py`

    讲解一个mixin使用单个表和单个关联表提供一个通用的关联。关联表包含一个"discriminator"列来决定关联到这条记录的父类。

- `generic_fk.py`

    讲解所谓的”通用外键“，这种方式在Django，RoR中经常使用。这种方式没有遵循SQL标准规范，这里的外键并没有指向任意特定的表；而是在应用层逻辑中决定这个外键应该引用哪个表。