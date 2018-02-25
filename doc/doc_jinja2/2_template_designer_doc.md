# Template Designer Documentation

这篇文档主要描述模版引擎的语法和语义，可以作为创建Jinja2模版的有效参考。因为这个模版引擎非常的弹性，你的应用的配置可以和这里的代码有些区别。

## Synopsis

Jinja模版其实就是一个简单的文本文件。Jinja可以生成任何以文本为基础的文件格式(比如`HTML`, `XML`, `CSV`, `LaTex`...)。Jinja模版不限定于扩展名：比如`.html`或者`.xml`，任何其它的扩展名也是可以的。

一个模版可以包含`变量`和`表达式`，它们会在模版渲染的时候被替换掉；另外还有`tags`，它可以控制模版的逻辑。模版的语法受到Django和Python启发。

下面是一个迷你模版，它使用默认Jinja2配置阐释了一些基础用法:

```python
<!DOCTYPE html>
<html lang='en'>
<head>
    <title>My Webpage</title>
</head>
<body>
    <ul id='navigation'>
    {% for item in navigation %}
        <li><a href="{{ item.href }}">{{ item.caption }}</a></li>
    {% endfor %}
    </ul>

    <h1>My Webpage</h1>
    {{ a_variable }}
    
    {# a comment #}
</body>
</html>
```

上面的例子使用默认的配置。应用开发者可以修改语法，比如把`{% foo %}`改为`<% foo %>`，或者类似的修改。

有很多种区分符。Jinja2默认的区分符包括:

- `{% ... %}`表示语句(statements)
- `{{ ... }}`表示表达式(expressions)
- `{# ... #}`表示注释，不会输出到最终渲染的模版中
- `# ... ##`行语句(line statements)

## Variable

模版变量通过传入到模版的context字典定义。

你可以认为传入到模版中的变量仍然是一个Python变量(对象)。仍然可以访问变量的属性或者元素。

你可以使用点号`(.)`或者Python的下标语法来访问一个变量的属性。

下面的两句代码效果一样:

```python
{{ foo.bar }}
{{ foo['bar'] }}
```

你一定要明白最外面的两个大括号不是变量的一部分，而是用来打印这个语句的。如果你在一个tag中访问变量，那么就不需要将它们再放到两个大括号中。

如果一个变量或者属性不存在，你会获得一个undefined的值。模版怎么对待这个值取决于你的模版配置：默认会打印空字符串，如果你相对这个值进行其它操作则会报错。

### Implementation

出于方便的原因，Jinja2中的`foo.bar`并不遵照Python的语法规则：

- 首先它会检查foo是否有bar属性(`getattr(foo, 'bar')`)
- 如果没有，检查foo是否有"bar"这个item(`foo.__getitem__('bar')`)
- 如果没有，返回一个undefined值。

对于一个序列来说，`foo['bar']`会这样处理：

- 首先检查foo是否有"bar"这个item(`foo.__getitem__('bar')`)
- 如果没有，检查foo是否有bar这个属性(`getattr(foo, 'bar')`)
- 如果没有，返回一个undefined值。

如果一个对象有相同名称的item和属性，你需要谨记两种用法其中的差别。另外，`attr()`filter只会查询属性。

## Filters

变量可以通过`fitlers`来修饰。filters通过管道符号(`|`)和变量分隔，可以选择将变量放在一个括号里。多个filter可以链接起来。一个filter的输出将会作为输入传入给下一个filter。

例如，`{{ name|striptags|title }}`将会移除变量的HTML标签，然后将输出以标题格式化，代码为`(title(striptargs(name))`.

如果filter可以接受参数，那么可以在filter后面加入括号以及参数，就像函数调用一样。例如：`{{ listx|join(', ') }}`将会把一个list以逗号作为分隔符join起来:`str.join(',', listx)`.

## Tests

除了filters，还有所谓的`tests`。tests可以测试一个变量对比一个普通的表达式。想要测试一个变量或者表达式，你需要加入`is`关键字。例如，想要查询一个变量是否定义，你可以写`name is defined`，它会根据`name`是否定义在当前模版的context中来返回True或者False。

tests也可以接受参数。如果你的test只有一个参数，你可以不实用括号。例如，下面两行代码效果上是一样的：

```python
{% if loop.index is divisibleby 3 %}
{% if loop.index is divisibleby(3) %}
```

## Comments

将要把模版中的某些行注释掉，可以使用默认为`{# ... #}`的注释语法。

```python
{# note: ommented-out template because we no longer use this 
    {% for user in users %}
        ...
    {% endfor %}
#}
```

## Whitespace Control

在默认的配置中：

- 如果存在单独存在的换行符，将会把它移除。
- 其它的空白字符(空格，制表符，换行符等...)都会保持原样。

如果一个应用配置了Jinja2的`trim_blocks`选项，那么在一个模版block后的第一个换行符将会被自动移除(像PHP一样).`lstrip_blocks`选项可以移除模版block开头之前的换行符(不过如果block之前的首字符如果不是换行符则无效)。

在同时激活`trim_blocks`和`lstrip_blocks`之后，你可以把block tag放到新行中，在渲染时这些多余的字符都会被移除，防止内容之间出现不正常空白。例如，如果没有`trim_blocks`和`lstrip_blocks`选项，下面这个模版：

```python
<div>
    {% if True %}
        yay
    {% endif %} 
</div>
```

在渲染的时候将会在div在存在换行符：

```html
<div>

        yay

</div>
```

不过在激活`trim_blocks`和`lstrip_blocks`之后，模版block占用的行都会被移除，其它的空白字符会保留：

```html
<div>
        yay
</div>
```

你可以通过将一个加号(`+`)放在block tag的开头来手动禁用`lstrip_blocks`:

```python
<div>
        {%+ if something %}yay{% endif %}
</div>
```

你也可以手动移除模版中的空格。如果你将一个减号加入到模版tag block，注释，变量的开头/结尾部分，这个block的前/后的空格都会被移除。

```python
{% for item in seq -%}
    {{ item }}
{%- endfor %}
```

这样所有的元素之间都不会存在空格。如果seq是一个从1到9的list，那么输出就是`123456789`.

如果开启了`line statements`，一行开头的空格会被自动移除。

默认情况下，Jinja2会移除结尾的换行符。如果想要保留，请开启`keep_trailing_newline`选项。

### Note

你不能在tag和减号(`-`)之间加入空格.

正确语法：

`{%- if foo -%}...{% endif %}`

错误语法：

`{% - if foo - %}...{% endif %}`

## Escaping

比如有时你想要直接把`{{`作为原生字符串输入，应该如何作呢？

可以使用变量表达式：

`{{ '{{' }} `

也可以使用`{% raw %}`标签，下面的例子会把item放在两个大括号中。

```python
{% raw %}
    <ul>
    {% for item in seq %}
        <li>{{ item }}</li>
    {% endfor %}
    </ul>
{% endraw %}
```

## Line Statements

如果应用开启了line statements，那么你可以将一行都标记为statement。比如，如果将line statement前缀设置为`#`，下面两个例子的效果就是一样的：

```python
<ul>
# for item in seq
    <li>{{ item }}</li>
# endfor
</ul>

<ul>
{% for item in seq %}
    <li>{{ item }}</li>
{% endfor %}
</ul>
```

line statements的前缀是可以配置的。另外为了可读性，一个语句(如if, for...)，可以以一个冒号来结尾:

```python
# for item in seq:
    ...
# endfor
```

### Note

如果使用括号，line statements是可以跨越多行的：

```python
<ul>
# for href, caption in [('index.html', 'Index'),
                        ('about.html', 'About')]:
    <li><a href="{{ href }}">{{ caption }}</a></li>
# endfor
</ul>
```

从Jinja2.2开始，line statement也可以加入注释了。例如，如果line comment的前缀配置为`##`，在`##`后面的字符都会被看作是注释：

```python
# for item in seq:
    <li>{{ item }}</li>     ## this comment is ignored
# endfor
```

## Template Inheritance

Jinja最强大的特性之一就是模版继承。模版继承允许你构件“基础骨架”型的模版，包含你网站使用的一些通用元素，然后定义了一些`blocks`允许子模版覆盖它们。

我们可以通过一个例子来快速掌握模版继承。

### Base Template

这个模版，我们叫做`base.html`，定义了一个简单的HTML骨架文档。它的子模版可以填充空白的blocks：

```html
<!DOCTYPE html>
<html lang='en'>
<head>
    {% block head %}
    <link rel='stylesheet' href='style.css'>
    <title>{% block titel %}{% endblock} - My Webpage</title>
    {% endblock %}
</head>
<body>
    <div id="content">{% block content %}{% endblock %}</div>
    <div id="footer">
        {% block footer %}
        &copy; Copyright 2008 by <a href='http://domain.invalid/'>you</a>.
        {% endblock %}
    </div>
</body>
</html>
```

在这个例子中，使用`{% block %}`标签定义了4个允许子模版填充的blocks。所有的blocks标签都是告诉模版引擎，这个占位符允许子模版来覆盖。

### Child Template

一个子模版可能看起来像这样：

```html
{% extends "base.html" %}
{% block title %}Index{% endblock %}
{% block head %}
    {{ super() }}
    <style type="text/css">
        .important {color: #336699}
    </style>
{% endblock %}
{% block content %}
    <h1>Index</h1>
    <p class="important">
        Welcome to my awesome homepage.
    </p>
{% endblock %}
```

这里的关键是`{% extends %}`标签。它告诉模版引擎这个模版“扩展”自其它的模版。在模版系统eval这个模版的时候，会首先定位它的父模版。extends标签应该是模版的第一个标签。在它之前的东西都会正常渲染，可能会造成一些混淆。

模版的文件名依据模版的loader。例如，`FileSystemLoader`允许你通过一个给定的文件名称来访问其它的模版。你可以通过斜杠来访问其它目录的模版：

`{% extends 'layout/default.html' %}`

但是这个行为取决于应用如何配置Jinja2。注意因为子模版没有覆盖`footer`block，仍然会使用父模版中的内容。

你不能在一个模版中定义多个相同名称的`{% block %}`标签。因为一个block标签在所有的目录中都会运作。也就是说，一个block标签并不只是提供一个用来填充的占位符 - 它同样可以在父模版中定义未填充时的默认内容。如果在一个模版中有两个相同名称的block标签，父模版就不知道使用哪一个了。

如果你要将一个block渲染多次，你可以使用特殊变量`self`:

```html
<title>{% block title %}{% endblock %}</title>
<h1>{{ self.title() }}</h1>
{% block body %}{% endblock %}
```

### Super Blocks

可以在覆盖的时候渲染父模版blocks中定义的内容。

```html
{% block sidebar %}
    <h3>Table Of Contents</h3>
    ...
    {{ super() }}
{% endblock %}
```

### Named Block End-Tags

Jinja2允许你为了可读性将block的名称放在block的结尾标签中：

```html
{% block sidebar %}
    {% block inner_sidebar %}
        ...
    {% endblock inner_sidebar %}
{% endblock sidebar %}
```

### Block Nesting and Scope

Block可以通过嵌套来适应复杂的布局。不过，每个默认的block都不能访问外部域的参数:

```html
{% for item in seq %}
    <li>{% block loop_item %}{{ item }}{% endblock %}</li>
{% endfor %}
```

这个例子会输出空的`<li>`元素，因为`item`不可以在block中访问。这是因为block是可以被子类继承重写的，但是变量可能并不存在。

从Jinja2.2开始，你可以显式地指定可以在block中访问变量。通过在block声明中加入`scoped`:

```html
{% for item in seq %}
    <li>{% block loop_item scoped %}{{ item }}{% endblock %}</li>
{% endfor %}
```

### Template Objects

如果一个模版对象传入到模版context中，你可以直接extends它：

`{% extends layout_template %}`

## HTML Escaping

在通过模版生成HTML的时候，变量中包含的字符是有安全风险的。有两种方式来对付：

1. 手动转义每个变量
2. 默认自动转义一切内容

这两种方式Jinja2都支持。根据应用的配置来决定使用哪一种。默认的配置是不会自动转义；这是因为很多因素：

- 转义一切会造成巨大的性能开销
- 变量的安全信息是很脆弱的. It could happen that by coercing safe and unsafe values, the return value is double-escaped HTML.

### Working with Manual Escaping

如果使用手段转义，你要负责需要转义的变量。什么东西要转义呢？如果你有一个变量包含以下字符(`>`, `<`, `&`, `"`)，你应该将它们转义，除非它们是完全可信赖的内容。可以通过filter`e`来转义：

`{{ user.username | e }}`

### Working with Automatic Escaping

在开启自动转义的时候，除了被显式标记为安全的值，其它的所有值都会默认被转义。变量可和表达式可以使用下列方式标记为安全：

1. context字典加入`MarkupSafe.Markup`
2. 在模版中使用filter:`|safe`

这个方式的一个问题就是Python并没有tainted value的概念；所以一个值是不是安全的很容易搞混。

如果一个值没有标记为安全，将会对它自动进行转义；可能就是一个包含双引号的内容，想要避免很简单，使用Jinja2为你提供的工具而不要使用Python内部的，如`str.format`或者`%`格式化方式。

Jinja2的函数(macros, super, self.BLOCKNAME)总是会返回标记为safe的内容。

模版中的字符字面量也会被自动转义，因为它们不是包含`__html__`属性的`MarkupSafe.Markup`字符串。

## List of Control Structures

控制结构即指程序中的控制流 - 条件(比如if/elif/else)，for循环，以及类似macros和blocks的东西。默认的语法设置中，控制结构出现在`{% ... %}`block内部。

### For

迭代一个序列的每一项。例如，想要显示一个list变量`users`中的每一个user：

```html
<h1>Members:</h1>
<ul>
{% for user in users %}
    <li>{{ user.username | e }}</li>
{% endfor %}
</ul>
```

因为变量会保持它们自己的对象属性，也可以迭代类字典这种容器：

```html
<dl>
{% for key, value in my_dict.iteritems() %
    <dt>{{ key | e }}</dt>
    <dd>{{ value | e }}</dd>
{% endfor %}
</dl>
```

注意，Python的字典不是有序的。

在for循环代码块中，你可以访问一些特殊的变量：

变量名 | 描述
-- | --
loop.index | 当前迭代的次数(索引自1开始)
loop.index0 | 当前迭代的次数(索引自0开始)
loop.revindex | 剩余的迭代次数(索引自1开始)
loop.revindex0 | 剩余的迭代次数(索引自0开始)
loop.first | 如果是首次迭代，返回True
loop.last | 如果是最后一次迭代，返回True
loop.length | 序列的长度
loop.cycle | 一个helper函数，可以循环迭代一个序列
loop.depth | Indicates how deep in a recursive loop the rendering currently is. Starts at level 1
loop.depth0 | Indicates how deep in a recursive loop the rendering currently is. Starts at level 0
loop.previtem | 之前一次迭代的item，如果是首次迭代则返回undefined
loop.nextitem | 之后一次迭代的item，如果是最后一次迭代则返回undefined
loop.changed(*val) | 如果之前以另一个值调用过(或者没有调用过)，则返回True

在一个for循环中，可以使用`loop.recyle`来生成循环迭代的对象:

```html
{% for row in rows %}
    <li class="{{ loop.cycle('odd', 'even') }}">{{ row }}</li>
{% endfor %}
```

和Python语法不一样，没有办法对一个循环进行`break`或者`continue`。不过，你可以在迭代的时候过滤这个序列让你可以跳过一些item：

```html
{% for user in users if not user.hiddent %}
    <li>{{ user.username | e }}</li>
{% endfor %}
```

并且特殊变量`loop`会正确的计数；没有迭代的user不会计入考量。

如果序列为空或者筛选移除了所有的item，所以没有办法迭代，你可以使用`else`来渲染一个默认的代码块：

```html
<ul>
{% for user in users %}
    <li>{{ user.username | e }}</li>
{% else %}
    <li><em>no users found</em></li>
{% endfor %}
</ul>
```

注意，Python中`for`语句的`else`字句只有在循环没有被break的时候才会执行。而Jinja的循环永远不会被break，这个`else`字句和Python语法并不相同(它只有在没有发生枚举的情况下会被执行)。

也可以生成递归循环。如果你需要处理递归数据如sitemap或者RDFa你需要使用递归循环。想要使用递归循环，你需要在loop定义中加入`recursive`修饰符.然后通过特殊变量loop来迭代你想要递归的变量：

```html
<ul class="sitemap">
{%- for item in sitemap recursive %}
    <li><a href="{{ item.href|e }}">{{ item.title }}</a>
    {%- if item.children -%}
        <ul class='submenu'>{{ loop(item.children) }}</ul>
    {%- endif %}</li>
{%- enfor %}
</ul>
```

`loop`变量总是会引用最近的一个循环。如果我们有多层的循环，我们可以在我们想要递归的循环中将变量loop重新绑定:`{% set outer_loop = loop %}`。然后我们可以调用`{{ outer_loop(...) }}`.

请注意，在loop中的变量赋值会在下一次迭代的时候清除。

如果你想要检查某些值是否在上次/下次迭代的时候修改，你可以使用`previtem`或者`nextitem`:

```html
{% for value in values %}
    {% if loop.previtem is defined and value > loop.previtem %}
        The value just created!
    {% endif %}
    {{ value }}
    {% if loop.nextitem is defined and loop.nextitem > value %}
        The value will increase even more!
    {% endif %}
{% endfor %}
```

如果你只是想看一个值是否更改，可以直接使用`.changed()`:

```html
{% for entry in entries %}
    {% if loop.changed(entry.category) %}
        <h2>{{ entry.category }}</h2>  # cool, 可以实现博客的archive
    {% endif %}
    <p>{{ entry.message }}</p>
{% endfor %}
```

### If

Jinja2中的`if`语句和Python的if语句一样。最简单的情况是，你可以用来测试一个变量是否定义，非空或者非False：

```html
{% if users %}
<ul>
{% for user in users %}
    <li>{{ user.username | e}}</li>
{% endfor %}
</ul>
{% endif %}
```

至于多分枝条件，你可以使用Python中的`elif`和`else`:

```html
{% if kenney.sick %}
    Kenney is sick.
{% elif kenny.dead %}
    You killed Kenny! You bastard!!!
{% else %}
    Kenney looks okay -- so far
{% endif %}
```

### Macros

Macro可以类比普通编程语言的函数。可以让你实践DRY原则。

下面是一个简单的macro例子，用来渲染一个form元素:

```html
{% macro input(name, value='', type='text', size=20) -%}
    <input type="{{ type }}" name="{{ name }}" 
           value="{{ value|e }}" size="{{ size }}">
{% endmacro %}
```

这个macro可以像函数一样调用：

```html
<p>{{ input('username') }}</p>
<p>{{ input('password', type='password') }}</p>
```

在macro中，你可以访问三种特殊变量：

- `varargs`

    如果传入的位置参数多于这个macro接收的参数，它们将会存储到`varargs`这个list中。

- `kwargs`

    像`varargs`，不过存储的是额外的关键字参数。

- `caller`

    如果这个macro通过`call`标签来调用，caller将会作为一个callable macrol来存储在这个变量中。

Macro对象也暴露了一些内部属性：

- `name`

    这个macro的名称。`{{ input.name }}`将会打印input.

- `arguments`

    这个macro接受的参数，元组。

- `default`

    默认值的元组。

- `catch_kwargs`

    如果macro接受了额外的关键字参数则返回True(也就是说可以访问特殊变量`kwargs`)

- `catch_varargs`

    如果macro接受了额外的位置参数则返回True(也就是说可以访问特殊变量`varargs`)

- `caller`

    如果macro可以访问特殊变量`caller`，则返回True。

### Call

有些情况需要把一个macro传给另一个macro。出于这个目的，你可以使用特殊的`call`标签。下面是一个macro利用call的例子：

```html
{% macro render_dialog(title, class='dialog') -%}
    <div class="{{ class }}">
        <h2>{{ title }}</h2>
        <div class="contents">
            {{ caller() }}
        </div>
    </div>
{% endmacro %}


{% call render_dialog('Hello World') %}
    This is a simple dialog rendered by using a macro and
    a call block.
{% endcall %}
```

你可以将`call`标签看作是一个匿名macro。

下面是一个为call传入参数的例子:

```html
{% macro dump_users(users) -%}
    <ul>
    {%- for user in users %}
        <li><p>{{ user.username|e }}</p>{{ caller(user) }}</li>
    {%- endfor %}
    </ul>
{% endmacro %}

{% call(user) dump_users(list_of_user) %}
    <dl>
        <dl>Realname</dl>
        <dd>{{ user.realname|e }}</dd>
        <dl>Description</dl>
        <dd>{{ user.description }}</dd>
    </dl>
{% endcall %}
```

### Filters

Filter标签允许你将一个常规的Jinja filter应用于一块模版数据：

```html
{% filter upper %}
    This text becomes uppercase
{% endfilter %}
```

### Assignments

在一个代码块中，你可以将一个值赋值给一个变量。在模版顶层赋值后这个变量可以被其它模版引入。

赋值使用`set`标签，可以赋值多个变量：

```html
{% set navigation = [('index.html', 'Index'), ('about.html', 'About')] %}
{% set ket, value = call_something() %}
```

#### Scope Behavior

请记住变量不能在一个block中赋值。不过也有例外，因为有些语句不会添加作用域。比如下面的模版结果可能不如你所想象：

```html
{% set iterated = false %}
{% for item in seq %}
    {{ item }}
    {% set iterated = true %}
{% endfor %}
{% if not iterated %} did not iterate {% endif %}
```

Jinja不能这么写，你应该使用for的else字句:

```html
{% for item in seq %}
    {{ item }}
{% else %}
    did not iterate
{% endfor %}
```

从2.10版本开始，一些复杂的例子可以使用namespace对象来传播(可以穿越作用域):

```html
{% set ns = namespace(found=false) %}
{% for item in items %}
    {% if item.check_soemthing() %}
        {% set ns.found = true %}
    {% endif %}
    * {{ item.title }}
{% endfor %}
Found item having something: {{ ns.found }}
```

注意`set`标签中的`obj.attr`语法只可以对namespace对象使用；如果对其它对象使用这个语法则会抛出错误。

### Block Assignments

从Jinja2.8开始，可以使用block级set标签来代替一部分数据。这种方法有时可以代替macro。在这种情况下，你不需要使用等号(`=`)和值，只需要写一个变量名就好了。

例子：

```html
{% set navigation %}
    <li><a href='/'>Index</a></li>
    <li><a href='/downloads'>Downloads</a></li>
{% endset %}
```

现在变量`navigation`可以代表一块HTML代码。

从Jinja2.10开始，block级set标签可以接受filter：

```html
{% set reply | wordwrap %}
    You wrote:
    {{ message }}
{% endset %}
```

### Extends

`extends`标签可以让一个模版扩展另一个模版(也可以理解为继承)。你可以在一个文件中拥有多个`extends`标签，但是只会执行它们中的一个。

### Blocks

Block用于模版继承，可以将它看作是占位符。

### Include

*include*语句可以用来把一个模版包含在内并且会将这个文件使用当前的命名空间渲染并返回渲染后的内容：

```html
{% include 'header.html' %}
    Body
{% include 'footer.html' %}
```

包含的模版默认会访问当前激活的context中的变量。

从Jinja2.2以后，你可以为include标记`ignore missing`；它代表如果包含模版如果缺少了必须的变量，Jinja将会忽略那条语句。在将`ignore missing`组合`with`或者`without context`时，它必须放置前面。下面是一个合法的语句：

```html
{% include 'sidebar.html' ignore missing %}
{% include 'sidebar.html' ignore missing with context %}
{% include 'sidebar.html' ignore missing without context %}
```

另外你可以提供一组模版，在将它们包含进来之前检查是否存在。在发现首个存在的模版之后就会把它之后包含进来，剩下的都会被忽略。如果给定了`ignore missing`，如果模版不存在则什么都不渲染，否则会抛出异常。

例子：

```html
{% include ['page_detailed.html', 'page.html'] %}
{% include ['special_sidebar.html', 'sidebar.html'] ignore missing %}
```

### Import

Jinja2支持把常用的代码放到Macro中。macros可以放在不同的模版中，然后引入到一起。这很类似于Python中的import机制。但是你有必要知道import的macro是会缓存的，import的模版不会访问当前模版的变量，而默认使用全局的变量。

有两种方式可以引入模版。你可以引入一个完整到模版到一个变量，或者通过macro。

假设我们有一个helper模块可以用来渲染form(命名为`forms.html`):

```html
{% macro input(name, value='', type='text') -%}
    <inpu type='{{ type }}' value='{{ value|e }}'
          name='{{ name }}'>
{% endmacro %}

{%- macro textarea(name, value='', rows=10, cols=40) -%}
    <textarea name='{{ name }}' rows='{{ rows }}'
              cols='{{ cols }}'>{{ value|e }}</textarea>
{%- endmacro %}
```

想访问一个模版的变量/macro最简单的方式是把这个模版模块以一个变量来引入。然后你就可以访问它的属性了：

```html
{% import 'forms.html' as forms %}
<dl>
    <dt>Username</dt>
    <dd>{{ forms.input('username') }}</dd>
    <dt>Password</dt>
    <dd>{{ form.input('password', type='password') }}</dd>
</dl>
<p>{{ form.textare('comment') }}</p>
```

另外你可以引入特定的变量并且为它取别名：

```html
{% from 'form.html' import input as input_field, textarea %}
<dl>
    <dt>Username</dt>
    <dd>{{ input_field('username') }}</dd>
    <dt>Password</dt>
    <dd>{{ input_field('password', type='password') }}</dd>
</dl>
<p>{{ textarea('comment') }}</p>
```

Macro和变量如果以下划线开头，则视为私有，不能没引入。

## Import Context Behavior

默认情况下，包含的(included)模版会传入到当前的context中而引用的(imported)模版则不会。这是因为引入的模版是会缓存的；因为import会很频繁。

这个行为是可以修改的：可以加入`with context`或者`wintout context`来修改它们默认行为。如果传入到当前的contxt则会关闭缓存。

下面是两个例子:

```html
{% from 'forms.html' import input with context %}
{% include 'header.html' without context %}
```

## Expressions

Jinja2允许基本的表达式。他们可以常规Python表达式类似；不过可能和你所期望的并不一致：

### Literal

最简单的形式是字面量。字面量代表Python的字符串或者数字等对象。存在以下的字面量：

- "Hello World"

    任何在一对单/双引号之间的都是字符串。

- 42 / 42.23

    整数和浮点数通过直接写入即可创建。

- ['list', 'of', 'objects']

    在两个括号之间的就是list。

- (‘tuple’, ‘of’, ‘values’)

    元组和Python中的元组也一样。

- {‘dict’: ‘of’, ‘key’: ‘and’, ‘value’: ‘pairs’}

    字典也一样。

- true / false

    true总是true，false就是false。

> Note
>
>> 特殊常量true, false和none都是小写形式。

### Math

Jinja2允许你对值进行计算。支持以下的运算符：

- `+`

- `-`

- `/`

- `//`

- `%`

- `*`

- `**`

### Comparisons

- `==`

- `!=`

- `>`

- `>=`

- `<`

- `<=`

### Logic

- `and`

- `or`

- `not`

- `(expr)`

### Other Operators

- `in`

- `is`: 作用于test

- `|`: 作用于filter

- `~`: 将所有操作数转换为字符串然后串联它们

- `()`: 调用一个callable.

- `./[]`: 获取对象的属性.

### If Expression

另外可以使用内联if表达式(三元表达式).

`{% extends layout_template if layout_template is defined else 'master.html' %}`

## List of Builtin Filters

- `asb(number)`

    返回一个参数的绝对值。

- `attr(obj, name)`

    获取一个对象的属性。`foo|attr('bar')`类似`foo.bar`，不过后者也有可能会访问索引。

- `batch(value, linecount, fill_with=None)`

    批处理item的filter。它很像`slice`。在提供第二个参数的时候，将会作为默认值填充缺失的索引：

    ```html
    <table>
    {%- for row in items|batch(3, '&nbsp;') %}
        <tr>
        {%- for column in row %}
            <td>{{ column }}</td>
        {%- endfor %}
        </tr>
    {%- endfor %}
    </table>
    ```

- `capitalize(s)`

    将这个值capitalize。首个字符会变为大写，其它字符都小写。

- `center(value, width=80)`

    通过一个给定的宽度来把一个值在一个字段中居中。

- `default(value, defailt_value=u'', boolean=False)`

    如果这个变量值是undefined，将会返回传入的默认值，否则还是返回变量的值。

    `{{ my_variable | default('my_variable is not defined') }}`

    如果你想要根据判断值是否为False来判断值是否定义：

    `{{ ''|default('the string was empty', true) }}`

    **Aliased**: `d`

 - `dictsort(value, case_sensitive=False, by='key', reverse=False)`

    排序一个字典，yield (key, value)对。因为Python字典是无序的，你可能需要这个函数来排序字典：

    ```html
    {% for item in mydict|dictsort %}
        通过key来排序一个字典，不区分大小写
        
    {% for item in mydict|dicsort(reverse=True) %}
        通过key来排序一个字典，不区分大小写，逆序。

    {% for item in mydict|dictsort(true) %}
        通过key来排序一个字典，区分大小写

    {% for item in mydict|dictsort(false, 'value') %}
        通过value来排序一个字典，不区分大小写
    ```

- `excape(s)`

    将字符`&`, `<`, `>`, `'`和`"`转换为HTML安全的字符。如果你不确定数据是否HTML安全，那么就使用它。

    **Aliased**: `e`

- `filesizeformat(value, binary=False)`

    将一个值变成“易读”的文件size格式(比如13kb, 4.1MB, 102Bytes...).

- `first(seq)`

    返回一个序列的第一个item。

- `float(value, default=0.0)`

    将一个值转换为浮点数。如果不能转换，将还返回默认值.

- `forceescape(value)`

    强制HTML转义。

- `format(value, *args, **kwargs)`

    将一个对象应用python字符串格式化：

    ```html
    {{ "%s - %s"|format('Hello?', 'Foo') }}
        -> Hello? - Foo!
    ```

- `groupby(value, attribute)`

    通过一个通用属性来对一个序列的对象进行分组。

    如果你有一个list，list里面是dict或者对象它们代表person和gender，first_name, 和last_name属性，你想要根据gender来分组所有的用户：

    ```html
    <ul>
    {% for group in persons|groupby('gender') %}
        <li>{{ group.grouper }}</li>
        {% for person in group.list %}
            <li>{{ person.first_name }} {{ person.last_name }}</li>
        {% enfor %}
    {% endfor %}
    </ul>
    ```

    也可以使用tuple来把grouper和list给unpack：

    ```html
    <ul>
    {% for grouper, list in persons|groupby('gender')  %}
        ...
    {% endfor %}
    </ul>
    ```

    你可以看到，用来分组的属性被存储到了`.grouper`属性中，`.list`属性包含分组的数据。

- `indent(s, width=4, first=False, blank=False, indentfirst=None)`

    返回一个字符串的拷贝，每一行会缩进4个空格。首行和空白行默认是不会缩进的。

    参数：

    - `width`: 锁进的空格数量
    - `first`: 是否缩进首行
    - `black`: 是否缩进空白行

- `int(value, default=0, base=10)`

    将一个值转换为整数。如果不能转换，将会返回默认值。base参数代表转换整数的进制，默认是10进制。

- `join(value, d=u'', attribute=None)`

    将一个序列中所有字符串串联起来的字符串。默认使用空字符串作为分隔符来链接：

    ```html
    {{ [1, 2, 3]|join('|') }}
        -> 1|2|3

    {{ [1, 2, 3]|join }}
        -> 123
    ```

    也可以将一组对象的属性join起来：

    ```html
    {{ users|join(', ', attribute='username') }}
    ```

- `last(seq)`

    返回一个序列的最后一个item。

- `length(object)`

    返回一个序列对象或者映射对象的长度。

    **Aliases**: `count`

- `list(value)`

    将这个value转换为list。如果传入一个字符串，那么会返回一个字符list。

- `lower(s)`

    将一个值转换为小写。

- `map()`

    将一个filter应用到一个序列的每个对象上面。

    基础用法是映射到一个属性。想象你有一个users list，但是你只对它的username属性感兴趣：

    `Users on this page: {{ users|map(attribute='username')|join(', ') }}`

    传入filter应用以filter字符串名称形式传入：

    `Users on this page: {{ titles|map('lower')|join(', ') }}`

- `max(value, case_sensitive=False, attribute=None)`

    返回这个序列对象中的最大item。

    ```html
    {{ [1, 2, 3] | max }}
        -> 3
    ```

    参数：

    - `case_sensitive`: 在比较的时候是否对大小写敏感
    - `attribute`: 使用这个对象的某个属性来比较

- `min(value, verbose=False)`

    将这个变量进行美观打印。常用于debugging。

- `random(seq)`

    返回一个序列对象中的一个随机item。

- `reject()`

    对一个序列中每个item进行test，将测试成功的对象剔除。

    如果没有指定test，将会使用bool测试。

    使用例子：

    `{{ numbers | reject('odd') }}`

- `rejectattr()`

    对一个序列中每个对象的属性来进行test，将测试成功的对象剔除。

    如果没有指定test，将会使用bool测试。

    ```html
    {{ users|rejectattr('is_active') }}
    {{ users|rejectattr('email', 'none') }}
    ```

- `replace(s, old, new, count=None)`

    返回一个字符串的拷贝，将会把所有出现的字串都替换成新的。如果指定了可选参数`count`，将会把首先出现`count`次的字串替换：

    ```html
    {{ 'Hello World'|replace('Hello', 'GoodBye') }}
        -> Goodbye World

    {{ 'aaaaargh'|replace('a', "d'oh, ", 2) }}
        -> d'oh, d'oh, aaargh
    ```

- `reverse(value)`

    将一个对象reverse。

- `round(value, precision=0, method='common')`

    将一个数字以给定的精度来round。指定的首个参数是`precision`(默认为0)，第二个参数是round方法：

    - `common`：向上或向下round
    - `ceil`: 向上round
    - `floor`: 向下round

    默认会使用`common`方法.

    ```html
    {{ 42.55|round }}
        -> 43.0
    {{ 42.55|round(1, 'floor') }}
        -> 42.5
    ```

    注意这个filter总是会返回给你浮点数。

- `safe(value)`

    标记这个值是safe的，意味着在自动转义的环境下这个变量不会被转义。

- `select()`

    通过对每个对象进行test来筛选一个对象序列，只会选择test成功的对象。

    如果没有指定test，将会默认使用bool test.

    使用例子：

    ```html
    {{ numbers|select('odd') }}
    {{ numbers|select('odd') }}
    {{ numbers|select("divisibleby", 3) }}
    {{ numbers|select("lessthan", 42) }}
    {{ strings|select("equalto", "mystring") }}
    ```

- `selectattr()`

    和上面例子一样，不过针对属性来select。

    使用例子：

    ```html
    {{ users|selectattr("is_active") }}
    {{ users|selectattr("email", "none") }}
    ```

- `slice(value, slices, fill_with=None)`

    对一个序列对象进行切片。

    ```html
    <div class='columnwrapper'>
        {%- for column in items|slice(3) %}
            <ul class="column-{{ loop.index }}">
            {% for item in column %}
                <li>{{ item }}</li>
            {% endfor %}
            </ul>
        {%- endfor %}
    </div>
    ```

    如果你传入第二个参数，它会用来填充最后一次迭代缺失的值。

- `sort(value, reverse=False, case_sensitive=False, attribute=None)`

    对一个iterable进行排序。默认是升序，如果你在第一个参数传入True，那么就会使用降序排序。

    第二个参数可以决定排序时是否区分大小写：

    ```html
    {% for item in iterable|sort %}
        ...
    {% endfor %}
    ```

    也可以根据一个数据来排序：

    ```html
    {% for item in iterable|sort(attribute='date') %}
    {% endfor %}
    ```
    
- `string(object)`

    将一个字符串转换为unicode。

- `striptags(value)`

    移除一个值的SGML/XML标签。

- `sum(iterable, attribute=None, start=0)`

    返回一个序列对象的sum。

    也可以sum一个特定的属性：

    ```html
    Total: {{ items|sum(attribute='price') }}
    ```

- `title(s)`

    返回一个值的title格式。即，首字符大写，其它字符都小写。

- `tojson(value, indent=None)`

    pass