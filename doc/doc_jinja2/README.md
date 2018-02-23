# Welcome to Jinja2

官网: [http://jinja.pocoo.org/docs/2.10/](http://jinja.pocoo.org/docs/2.10/)

Jinja2是一个现代的，对于设计师友好的Python模版语言，模仿自Django模版。它快，用途宽泛，以及可以选择使用沙盒模版执行环境来确保安全。

示例：

```python
<title>{% block title %}{% endblock %}</title>
<ul>
{% for user in users %}
    <li><a href='{{ user.url }}'>{{ user.username }}</a></li>
{% endfor %}
</ul>
```

特性:

- 沙盒化执行
- 强大的HTML自动转义系统，可以防范XSS攻击
- 模版继承
- 通过优化的PythonJIT代码来编译
- 可选择模版预编译
- 很容易debug。在trackback中会列出问题代码的准确行号
- 可配置化的语法





