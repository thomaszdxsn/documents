# Hybird Property

```python
class hybird_property:

    is_attribute = True

    def __init__(self, fget, fset=None, fdel=None,
                 expr=None, custom_comparator=None, update_expr=None):
        self.fget = fget
        self.fset = fset
        self.fdel = fdel
        self.expr = expr
        self.custom_comparator = custom_comparator
        self.update_expr = update_expr
        util.update_wrapper(self, fget)

    def __get__(self, instance, owner):
        if instance is None:
            return self._expr_comparator(owner)
        else:
            self.fget(instance)

    def __set__(self, instance, value):
        if self.fset is None:
            raise AttributeError('')
        self.fset(instance, value)
```
