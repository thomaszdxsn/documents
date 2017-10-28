## tornado.template -- 生成弹性的输出内容

一个简单的模版系统，把模版编译为Python代码。

基础用法:

```python
t = template.Template("<html>{{ myvalue }}</html>")
print(t.generate(myvalue='XXX'))
```

`Loader`是一个类，它从根目录读取模版并且缓存编译后的模版：

```python
loader = template.Loader("/home/btaylor")
print(loader.load("test.html").generate(myvalue='XXX'))
```

我们编译所有的模版为原生Python字符串，语句。模版的语法：

```python
### base.html
<html>
    <head>
        <title>{% block title %}Default Title{% end %}</title>
    </head>
    <body>
        <ul>
            {% for student in students %}
                {% block student %}
                    <li> {{ escape(student.name) }}</li>
                {% end %}
            {% end %}
        </ul>
    </body>
</html>


### bold.html
{% extends "base.html" %}

{% block title %}A bolder title{% end %}

{% block student %}
    <li><span class="bold">{{ escape(student.name) }}</span></li>
{% end %}
```

不想大多数其它模版系统一样，我们并不会为模版中的语句表达式作任何限制。`if`和`for`块都能
直接翻译为Python代码，所以你可以作出复杂的表达式如：

```python
{% for student in [p for p in people if p.student and p.age > 23] %}
    <li>{{ escape(student.name) }}</li>
{% end %}
```

直接翻译为Python代码意思就是你可以在表达式中轻松使用函数，就像上面例子中的`escape()`函数。
你可以将函数像其它变量一样传入到模版中(在一个`RequestHandler`中，
重写`RequestHandler.get_template_namespace`)：

```python
def add(x, y):
    return x+y
template.execute(add=add)

### 模版中
{{ add(1, 2) }}
```

默认情况下，我们为所有模版提供的函数包括:`escape()`, `url_escape()`, `json_encode()`
以及`squeeze()`。

一般的应用并不会创建Template或者Loader实例，而是在`RequestHandler`中使用`self.render()`
和`self.render_string()`方法，它们会根据setting`template_path`来自动读取模版。

以`_tt_`为前缀的变量名是模版系统的保留变量，在应用中应该不适用这种命名。


### 语法参考

模版表达式以两个大括号包裹：`{{ ... }}`。内容可以是任何Python表达式，会根据当前的autoescape
配置来决定是否转义。模版的其它内容都是直接使用`{% ... %}`。

想要注释一部分内容，让它在输出时被忽略，可以通过使用：`{# ... #}`实现。

如果你在`{{`,`{%`, `{#`中使用`{{!`,`{%!`，`{#!`，这些标签都会被转义。

- `{% apply *function* %}...{% end %}`

    在`apply`和`end`之间的所有模版变量都会被应用这个函数：

    `{% apply linkify %}{{ name }} said: {{ message }}{% end %}`

- `{% autoescape *function* %}`

    为当前文件设置自动转义模式。这个配置不会影响其它文件，其实它们通过`{% include %}`
    引用进来。注意自动转义模式可以全局配置，在Application setting或者Loader里面都可以：

    ```python
    {% autoescape xhtml_escape %}
    {% autoescape None %}
    ```

- `{% block *name* %}...{% end %}`

    声明一个命名的，可替换的块。这个块可以用于使用`{% extends %}`的子模版中。在父模版中
    block可以被子模版相同命名block中的内容替换:

    ```python
    <!-- base.html -->
    <title>{% block title %}Default title{% end %}</title>

    <!-- mypage.html -->
    {% extends "base.html" %}
    {% block title %}My page title{% end %}
    ```

- `{% comment ...%}`

    一个注释，在模版输出中将被移除。注意这里没有`{% end %}`标签；

    注释在comment和闭合`%}`之间。

- `{% extends *filename* %}`

    继承自其它模版。使用`extends`的模版应该包含一个或多个`block`标签，用来替换父模版中
    内容。任何在自模版中为包含在`block`标签中的内容都会被忽略。

- `{% for *var* in *expr* %}...{% end %}`
    
    和Python的`for`语句一样。在循环中可以使用`{% break %}`和`{% continue %`}。

- `{% from *x* import *y* %}`

    和Python的`import`语句一样。

- `{% if *condition* }...{% elif *condition %}..{% else %}...{% end %}`

    条件语句，输出符合条件判断那部分内容(`elif`和`else`是可选的)

- `{% include *filename* %}`

    可以包含其它的模版文件。包含的文件可以看到所有的局部变量(`{% autoescape %}`是个例外)。另外，使用`{% module Template(filename, **kwargs)}`可以用来包含一个带有隔离命名空间的模版。

- `{% module *expre* %}`

    渲染一个`UIModule`。UIModule的输出不会被转义：

    `{% module Template("foo.html", arg=42) %}`

- `{% raw *expr* %}`

    输出给定表达式的原生结果。

- `{% set *x* = *y* %}`

    设置一个局部变量。

- `{% try %}...{% except %}...{% else %}...{% finally %}...{% end %}`

    和Python的try语句一样。

- `{% while *condition* %}...{% end %}`

    和Python的while语句一样。在循环中可以使用`(% break %)`和`{% continue %}`。

- `{% whitespace *mode* %}`

    为本文件的剩余部分设置whitespace模式(或者直到下次直接使用`{% whitespace %}`)

### 类参考

- `tornado.template.Template(template_string, name='<string>', loader=None, compress_whitespace=None, autoescape="xhtml_escape", whitespace=None)`

    一个编译的模版。

    我们把给定的template_string编译为Python代码。你可以通过`generate()`为模版传入变量。

    构建一个Template。

    参数：

    - `template_string`(字符串)： 模版文件的内容
    - `name`(字符串)：读取模版的名称(用于错误消息)
    - `loader`(tornado.template.BaseLoader)：这个`BaseLoader`对这个模版负责，用来解析`{% include %}`和`{% extend %}`。
    - `compress_whitespace`(布尔)：从Tornado4.3开始被弃用。
    - `autoescape`(字符串)：模版命名空间的一个函数名称，或者使用`None`来默认禁用这个模版的转义。
    - `whitespace`(字符串)：一个用来制定对待whitespace的方式的字符串。

    方法：

    - `generate(**kwargs)`

        通过给定的参数来生成模版。

- `tornado.template.BaseLoader(autoescape='xhtml_excape', namespace=NOne, whitespace=None)`

    模版读取器的基类。

    在使用如`{% extends %}`和`{% include %}`来构造模版时，必须使用一个模版读取器。这个读取器会缓存所有已经被读取的模版。

    构造一个模版读取器。

    参数：

    - `autoescape`(字符串)：值是模版命名空间中的一个函数的名称，比如`xhtml_escape`，或者传入None来默认禁用自动转义模式。

    - `namespace`(字典)：一个加入到模版默认命名空间的字典，或者None。

    - `whitespace`(字符串)：一个指定模版对待whitespace默认行为的字符串。

    方法：

    - `reset()`

        重置编译模版的缓存。

    - `resolve_path(name, parent_path=None)`

        将一个相对路径转换为绝对路径(内部使用的方法)。

    - `load(name, parent_path=None)`

        读取一个模版。

- `tornado.template.Loader(root_director, **kwargs)`

    一个模版读取器，它从单个根目录读取。

- `tornado.template.DictLoader(dict, **kwargs)`

    一个模版读取器，它从单个根目录读取。

- 异常`tornado.template.ParseError(message, filename=None, lineno=0)`

    抛出一个模版语法错误。

- 函数`tornado.template.filter_whitespace(mode, text)`

    根据`mode`来转换`text`中的空白字符。

    可选的model为：

    - `all`: 返回所有未经修改的空白字符。
    - `single`: 将连续的空白字符转换为单个空白字符，保存空白行
    - `one`: 将连续的空白字符转换为单个空白字符，移除空白行。
