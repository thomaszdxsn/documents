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

    


