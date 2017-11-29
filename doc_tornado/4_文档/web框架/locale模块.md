## tornado.locale -- 国际化支持

生成国际化字符串的翻译方法。

想要读取一个本地字符串，并且生成一个翻译的字符串，可以这样作：

```python
user_locale = tornado.locale.get("es_LA")
print(user_locale.translate("Sign out"))
```

`tornado.locale.get()`返回最近匹配的locale，并不一定返回你指定的locale。你可以为`translate()`方法增加额外的参数来支持复数化形式的翻译：

```python
people = [...]
message = user_locale.translate(
    "%(list)s is online", "%(list)s are online", len(people)
)
print(message % {"list": user_locale.list(people)})
```

如果`len(people) == 1`会选择第一个串作为结果，否则会选择第二个。

应用应该调用`load_translations`(使用简单的CSV格式)或者`load_gettext_translations`(使用`gettext`和相关工具支持的`.mo`格式)中的一个。如果以上的方法都没用被使用，`Locale.translate`方法只会返回原始的字符串。

- `tornado.locale.get(*locale_codes)`

    根据给定的locale码并返回最近的匹配。

    我们会根据顺序迭代所有的locale码。如果碰到一个匹配的代码，我们会返回这个locale。否则我们会进入下一个循环。

    默认情况下，如果没有匹配代码的情况下，我们返回`en_US`。你可以通过`set_default_locel()`来更改默认的locale。

- `tornado.set_default_locale(code)`

    设置默认的locale。

    默认locale是假定这个语言适用于系统中的所有字符串。

- `tornado.locale.load_translations(directory, encoding=None)`

    从一个目录的CSV文件中读取翻译文本。

    翻译文本支持Python命名占位符的字符串。

    这个目录应该包含类似`LOCALE.csv`形式的翻译文本文件，比如`es_GT.csv`。CSV文件应该具有2-3个列：字符串，译文，复数形式译文(可选)。

    这个文件使用`csv`模块的默认"excel"方言来读取。在这个格式下，逗号后面不应该存在空格。

    如果没有给定`encoding`参数，编码将会自动检测获取(在utf8-utf16之间).

    一个`es_LA.csv`的例子：

    ```python
    "I love you", "Te amo"
    "%(name)s liked this", A %(name)s les gustó esto","plural"
    "%(name)s liked this","A %(name)s le gustó esto","singular"
    ```

- `tornado.locale.load_gettext_translations(directory, domain)`

    从`gettext`的locale树中读取译文。

    locale树类似于文件系统的`/usr/share/locale`，比如:

    `{directory}/{lang}/LC_MESSAGES/{domain}.mo`

    你的app翻译需要三个必须的步骤：

    1. 生成POT翻译文件：

        `xgettext --language=Python --keyword=_:1,2 -d mydomain file1.py file2.html etc`

    2. 合并当前的POT文件：

        `msmerge old.po mydomain.po > new.po`

    3. 编译：

        `msgfmt mydomain.po -o {directory}/pt_BR/LC_MESSAGES/mydomain.mo`

- `tornado.locale.get_supported_locales()`

    返回一个所有支持locale代码的列表。

- `tornado.locale.Locale(code, translations)`

    一个代表locale的对象。

    在调用`load_translations`或者`load_gettext_translations`中的一个后，调用`get`或者`get_closet`来获取一个`Locale`对象。

    - 类方法`get_closet(*locale_codes)`

        返回给定locale代码最近的匹配。

    - 类方法`get(code)`

        返回给定locale代码的Locale。

        如果这个locale代码不支持，会抛出一个异常。

    - `translate(message, plural_message=None, count=None)`

        返回给定message在当前locale下面的译文。

        如果第二个参数`plural_message`给定，你同样必须给定`count`。

    - `format_date(date, gmt_offset=0, relative=True, shorter=False, full_format=False)`

        格式化给定的日期。

        默认会返回相对时间(比如,“2 minutes ago”)。但是你可以使用`relative=False`来返回绝对时间。

    - `format_day(date, gmt_offset=0, dow=True)`

        将给定的day以星期的形式格式化。

    - `list(parts)`

        返回一个逗号分割的列表。

    - `friendly_number(value)`

        通过给定的整数返回一个逗号分割的数字。

- `tornado.locale.CSVLocale(code, translations)`

    使用tornado的CSV翻译格式实现locale。

- `tornado.locale.GettextLocale(code, translations)`

    使用`gettext`模块实现locale。

    - `pgettext(context, message, plural_message=None, count=None)`

        允许为翻译设置上下文，接受复数形式。

        使用例子：

        ```python
        pgettext("law", "high")
        pgettext("good", "right")
        ```

        复数消息例子：

        ```python
        pgettext("organization", "club", "clubs", len(clubs))
        pgettext("stick", "club", "clubs", len(clubs))
        ```

        想要生成上下文形式的POT文件，需要在第1个步骤时增加选项option:

        `xgettext [basic options] --keyword=pgettext:1c,2 --keyword=pgettext:1c,2,3`

    