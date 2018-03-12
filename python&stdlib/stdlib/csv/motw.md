# csv -- Comma-separated Value Files

**用途: 读/写CSV文件**

`csv`模块可以用来将数据从数据库输出到以逗号分割的文本文件，通常把这种文件叫做CSV格式。

## Reading

### csv_reader.py

使用`reader()`来创建一个对象，用来读取一个CSV文件。reader可以用来按照顺序迭代文件中的每一行。

```python
import csv
import sys


with open(sys.argv[1], 'rt') as f:
    reader = csv.reader(f)
    for row in reader:
        print(row)
```

`reader()`的第一个参数是一个文本行资源，在这个例子中它是一个对象，但是也可以接受任何可迭代对象(例如`StringIO`, `list`等实例)。
其它的参数可以用来控制如何解析输入的数据。

假定有一个`testdata.csv`文件:

```csv
"Title 1","Title 2","Title 3","Title 4"
1,"a",08/18/07,"å"
2,"b",08/19/07,"∫"
3,"c",08/20/07,"ç"
```

在读取它的时候，会解析它的每一行并将它转换为一个字符串list.

```shell
$ python3 csv_reader.py testdata.py

['Title 1', 'Title 2', 'Title 3', 'Title 4']
['1', 'a', '08/18/07', 'å']
['2', 'b', '08/19/07', '∫']
['3', 'c', '08/20/07', 'ç']
```

解析器将会把字符串中出现换行符的情况仍然当作一行：

```csv
"Title 1","Title 2","Title 3"
1,"first line
second line",08/18/07
```

```shell
$ python3 csv_reader.py testlinebreak.csv

['Title 1', 'Title 2', 'Title 3']
['1', 'first line\nsecond line', '08/18/07']
```

## Writing

### csv_writer.py

写入CSV文件也很简单。使用`writer()`来创建一个对象用于写入，然后迭代要写入的行，
使用`writerow()`来写入。

```python
# csv_writer.py

import csv
import sys

unicode_chars = 'å∫ç'

with open(sys.argv[1], 'wt') as f:
    writer = csv.writer(f)
    writer.writerow(('Title 1', 'Title 2, 'Title 3', 'Title 4'))
    for i in range(3):
        row = (
            i + 1,
            chr(ord('a') + i),
            '08/{:02d}/07'.format(i + 1),
            unicode_chars[i],
        )
        writer.writerow(row)
        
print(open(sys.argv[1], 'rt').read())
```

写入情况看起来和上面的输出不太应用，因为一些值缺乏引号。

```shell
$ python3 csv_writer.py testout.csv

Title 1,Title 2,Title 3,Title 4
1,a,08/01/07,å
2,b,08/02/07,∫
3,c,08/03/07,ç
```

## Quoting

### csv_writer_quoted.py

writer的quote行为和reader不一样，所以上面例子中的第二，三列都没有加上引号。
为了加上引号，你需要使用quoting参数.

```python
writer = csv.writer(f, quoting=csv.QUOTE_NONNUMERIC)
```

在这个例子中，`QUOTE_NONNUMMERIC`会为所有非数值的值加上引号:

```shell
$ python3 csv writer_quoted.py testout_quoted.csv

"Title 1","Title 2","Title 3","Title 4"
1,"a","08/01/07","å"
2,"b","08/02/07","∫"
3,"c","08/03/07","ç"
```

有四个不同的quoting选项:

- QUOTE_ALL

    将所有的值都加上引号，不管它们的类型。

- QOUTE_MINIMAL

    只对特殊字符加上引号。这是默认选项。

- QUOTE_NONNUMERIC

    引用所有非int或float的字段。如果用于reader，输入字段不包含引号的情况都会被转换为float。

- QUOTE_NONE

    任何值都不要加上引号。

## Dialects

CSV文件并没有标准定义，所以parser需要更加弹性化。弹性化意味着可以有很多参数用来
控制`csv`对数据的解析和写入。`csv`模块并不是把这些参数分别传入`reader`或者`writer`，
而是把它们分组放入了一个`dialect`对象。

Dialect类可以通过名称来著出，所以`csv`模块的调用者不需要提前知道参数设置。
完整的dialect注册list可以通过`list_dialects()`取回。

### csv_list_dialects.py

```python
import csv 

print(csv.list_dialects())
```

标准库包括三个dialects：excel, excel-tabs,以及unix。

```shell
$ python3 csv_list_dialects.py

['excel', 'excel-tab', 'unix']
```

### Creating a Dialect

如果有数据使用`|`作为分隔符，比如

```csv
"Title 1"|"Title 2"|"Title 3"
1|"first line
second line"|08/18/07
```

#### csv_dialect.py

你可以注册一个新的dialect:

```python
# csv_dialect.py

import csv

csv.register_dialect('pipes', delimiter='|')

with open('testdata.pipes', 'r') as f:
    reader = csv.reader(f, dialect='pipes')
    for row in reader:
        print(row)
```

使用"pipes"dialect，可以用它来读取以|分隔字段的文件:

```shell
$ python3 csv_dialect.py

['Title 1', 'Title 2', 'Title 3']
['1', 'first line\nsecond line', '08/18/07']
```

### Dialect Parameters

dialect可以指定解析/写入一个数据文件的所有token。下面的表格列出了文件格式的方方面面：

属性 | 默认值 | 意义
-- | -- | --
delimiter | , | 字段分隔符(单字符)
doublequote | True | 一个flag，控制是否使用双引号来quote
escapechar | None | 用来转义序列的字符
lineterminator | \r\n | writer用来换行的字符
quotechar | " | 用来包裹特殊值的字符(单字符)
quoting | QUOTE_MINIMAL | 控制quoting行为
skipinitialspace | False | 是否忽略字段分隔符之后的空白

#### csv_dialect_variations.py

```python
import csv
import sys

csv.register_dialect(
    'escaped',
    escapechar='\\',
    duoblequote=False,
    quoting=csv.QUOTE_NONE,
)
csv.register_dialect(
    'singlequote',
    quotechar="'",
    quoting=csv.QUOTE_ALL,
)

quoting_modes = {
    getattr(csv, n): n
    for n in dir(csv)
    if n.startswith('QUOTE_')
}

TEMPLATE = '''
Dialect: "{name}"

  delimiter   = {dl!r:<6}    skipinitialspace = {si!r}
  doublequote = {dq!r:<6}    quoting          = {qu}
  quotechar   = {qc!r:<6}    lineterminator   = {lt!r}
  escapechar  = {ec!r:<6}
'''

for name in sorted(csv.list_dialects()):
    dialect = csv.get_dialect(name)
    
    print(TEMPLATE.format(
        name=name,
        dl=dialect.delimiter,
        si=dialect.skipinitialspace,
        dq=dialect.doublequote,
        qu=quoting_modes[dialect.quoting],
        qc=dialect.quotechar,
        lt=dialect.lineterminator,
        ec=dialect.escapechar,
    ))

    writer = csv.writer(sys.stdout, dialect=dialect)
    writer.writerow(
        ('col1', 1, '10/01/2010',
         'Special chars: " \' {} to parse'.format(
            dialect.delimiter))
    )
    print()
```

这个程序可以展示不同的dialect格式化的不同：

```shell
$ python3 csv_dialect_variations.py

Dialect: "escaped"

  delimiter   = ','       skipinitialspace = 0
  doublequote = 0         quoting          = QUOTE_NONE
  quotechar   = '"'       lineterminator   = '\r\n'
  escapechar  = '\\'

col1,1,10/01/2010,Special chars: \" ' \, to parse

Dialect: "excel"

  delimiter   = ','       skipinitialspace = 0
  doublequote = 1         quoting          = QUOTE_MINIMAL
  quotechar   = '"'       lineterminator   = '\r\n'
  escapechar  = None

col1,1,10/01/2010,"Special chars: "" ' , to parse"

Dialect: "excel-tab"

  delimiter   = '\t'      skipinitialspace = 0
  doublequote = 1         quoting          = QUOTE_MINIMAL
  quotechar   = '"'       lineterminator   = '\r\n'
  escapechar  = None

col1    1       10/01/2010      "Special chars: "" '     to parse"

Dialect: "singlequote"

  delimiter   = ','       skipinitialspace = 0
  doublequote = 1         quoting          = QUOTE_ALL
  quotechar   = "'"       lineterminator   = '\r\n'
  escapechar  = None

'col1','1','10/01/2010','Special chars: " '' , to parse'

Dialect: "unix"

  delimiter   = ','       skipinitialspace = 0
  doublequote = 1         quoting          = QUOTE_ALL
  quotechar   = '"'       lineterminator   = '\n'
  escapechar  = None

"col1","1","10/01/2010","Special chars: "" ' , to parse"
```

### Automatically Detecting Dialects

解析文件是配置dialect最佳方式是提前知道正确的设置。`Sniffer`类可以用来guess文件
的配置。

#### csv.dialect_sniffer.py

```python
improt csv 
from io import StringIO
import textwrap

csv.register_dialect('escaped',
                     escapechar='\\',
                     doublequote=False,
                     quoting=csv.QUOTE_NONE)
csv.register_dialect('singlequote',
                     quotechar="'",
                     quoting=csv.QUOTE_ALL)

# 问所有的dialects生成样本数据
samples = []
for name in sorted(csv.list_dialects()):
    buffer = StringIO()
    dialect = csv.get_dialect(name)
    writer = csv.writer(buffer, dialect=dialect)
    writer.writerow(
        ('col1', 1, '10/01/2010',
         'Special chars " \' {} to parse'.format(dialect.delimiter)
    )
    samples.append((name, dialect, buffer.getvalue()))

# 使用sniffer来猜测样本数据应该使用的方言
sniffer = csv.Sniffer()
for name, expected, sample in samples:
    print('Dialect: "{}"'.format(name))
    print('In: {}'.format(sample.rstrip()))
    dialect = sniffer.sniff(sample, delimiters=',\t')
    reader = csv.reader(StringIo(sample), dialect=dialect)
    print('Parsed:\n  {}\n'.format(
          '\n  '.join(repr(r) for r in next(reader))))
```

输出如下：

```shell
$ python3 csv_dialect_sniffer.py

Dialect: "escaped"
In: col1,1,10/01/2010,Special chars \" ' \, to parse
Parsed:
  'col1'
  '1'
  '10/01/2010'
  'Special chars \\" \' \\'
  ' to parse'

Dialect: "excel"
In: col1,1,10/01/2010,"Special chars "" ' , to parse"
Parsed:
  'col1'
  '1'
  '10/01/2010'
  'Special chars " \' , to parse'

Dialect: "excel-tab"
In: col1        1       10/01/2010      "Special chars "" '      to parse"
Parsed:
  'col1'
  '1'
  '10/01/2010'
  'Special chars " \' \t to parse'

Dialect: "singlequote"
In: 'col1','1','10/01/2010','Special chars " '' , to parse'
Parsed:
  'col1'
  '1'
  '10/01/2010'
  'Special chars " \' , to parse'

Dialect: "unix"
In: "col1","1","10/01/2010","Special chars "" ' , to parse"
Parsed:
  'col1'
  '1'
  '10/01/2010'
  'Special chars " \' , to parse'
```

## Using Field Names

除了使用序列化的数据，`csv`模块包含一些类可以使用字典作为字段，包括`DictReader`
和`DictWriter`。

### csv_dictreader.py

```python
# csv_dictreader.py

import csv
import sys

with open(sys.argv[1], 'rt') as f:
    reader = csv.DictReader(f)
    for row in reader:
        print(row)
```

输出如下：

```shell
$ python3 csv_dictreader.py testdata.csv

{'Title 2': 'a', 'Title 3': '08/18/07', 'Title 4': 'å', 'Title 1
': '1'}
{'Title 2': 'b', 'Title 3': '08/19/07', 'Title 4': '∫', 'Title 1
': '2'}
{'Title 2': 'c', 'Title 3': '08/20/07', 'Title 4': 'ç', 'Title 1
': '3'}
```

### csv_dictwriter.py

而`DictWriter`必须给定一组字段名，让它知道如何在输出中将列排序.

```python
# csv_dictwriter.py

import csv
import sys

fieldnames = ('Title1', 'Title2', 'Title3', 'Title4')
headers = (
    n: n
    for n in fieldnames
)
unicode_chars = ''å∫ç''

with open(sys.argv[1], 'wt') as f :
    
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writehader()
    
    for i in range(3):
        writer.writerow({
            'Title 1': i + 1,
            'Title 2': chr(ord('a') + i),
            'Title 3': '08/{:02d}/07'.format(i + 1),
            'Title 4': unicode_chars[i],
        })
print(open(sys.argv[1], 'rt').read())
```

字段名并不会自动写入文件，你需要使用`writerhaader()`方法.

```shell
$ python3 csv_dictwriter.py testout.csv

Title 1,Title 2,Title 3,Title 4
1,a,08/01/07,å
2,b,08/02/07,∫
3,c,08/03/07,ç
```
