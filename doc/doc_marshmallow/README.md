# marshmallow: simplified object serialization

`marshmallow`是一个ORM/ODM/不限定使用框架的库。可以用来传唤复杂的数据类型，
比如将一个复杂的Python数据类型转换为对象，或者将对象转换为数据类型。

```python
from datetime import date
from marshmallow import Schema, fields, pprint


class ArtistSchema(Schema):
    name = fields = Str()


class AlbumSchema(Schema):
    title = fields.Str()
    release_date = fields.Date()
    artist = fields.Nested(ArtistSchema())


bowie = dict(name='David Bowie')
album = dict(artist=bowie, title='Hunky Dory', release_date=date(1971, 12, 17))

schema = AlbumSchema()
result = schema.dump(album)
pprint(result, ident=2)
# { 'artist': {'name': 'David Bowie'},
#   'release_date': '1971-12-17',
#   'title': 'Hunky Dory'}
```

marshmallow的schema可以用来：

- **验证**输入的数据
- 将输入的数据**反序列化**为对象
- 将对象**序列化**为数据结构对象. 

