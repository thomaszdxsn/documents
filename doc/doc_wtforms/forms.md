# Forms

Form是WTForms的最高级的API。

它包含字段定义，字段验证，接受输入，收集错误等等功能。

## The Form Class

- class`wtforms.form.Form`

    声明Form基类。

    - `__init__(formdata=None, obj=None, prefix='', data=None, **kwargs)`

        这个构造器通常在你的web应用的view/controller中使用。

        在一个Form构建完成以后，它的字段值由formdata, obj, 和kwargs构成.

        **注意**, obj和kwargs形式的数据传入方式都假定你已经作了类型转换。

        参数:

        - formdata: 传入用户输入的数据，通常是`request.POST`.
        formdata应该是某种请求数据的封装，一个表单input应该可以
        有多个值，值应该是unicode字符串，比如Werkzeug/Django/WebOb的Multidict

        - obj: 如果formdata为空，将会用这个对象作为传入的表单数据.

        - prefix: 如果提供了这个参数，所有的字段值都会加上这个前缀。

        - data: 接受字典型的数据。只有在formdata和obj都不存在的时候才
        可以传入。

        - meta: 如果提供了这个参数(这个参数应该是一个字典)，它将会
        覆盖表单的meta实例。

        - **kwargs: 如果formdata和obj都是空，这些关键字参数将会作为
        表单数据。

        属性：

        - data

            一个字典，包含每个字段的值。

            注意，在你每次访问的时候，它的值都会生产一次。

            所以你需要小心使用它，如果你重复地访问，很可能会造成性能
            问题。

            一般来说，你应该只使用它来迭代表单的数据。

            如果你只是想访问某个特定字段的数据，可以使用`form.<field>.data`，
            而不是这个代理属性(proxy property)。

        - errors

            一个字典，包含每个字段的错误，以list的形式保存。

            如果form还没有被验证，这个字典应该是空的，也就是没有错误。

            请注意，这是一个惰性属性，只有在你首次访问它的时候才会被创建。

            如果你在访问它之后调用`validate()`，缓存的结果将会失效，并且
            在下次访问的时候重新生成。

        - meta

            这是一个对象，它包含多种多样的配置选项，可以用来自定义表单的行为。

        方法：

        - `validate()`

            验证表单，调用每个字段的validate，以及额外的
            `Form.validate_<field_name>`验证器。

        - `populate_obj(obj)`

            通过obj的属性来构建表单字段的值。

            **注意**：这是一个毁坏性的操作；任何字段和对象属性只要相同，就会被
            覆盖。请小心使用。

            一个典型的例子，是修改edit profile view:

            ```python
            def edit_profile(request):
                user = User.objects.get(pk=requests.session['userId'])
                form = EditProfileForm(request.POST, obj=user)

                if request.POST and form.validate:
                    form.populdate_obj(user)
                    user.save()
                    return redirect('/home')
                return render_to_response('edit_profile.html', form=form)
            ```

            在上面的例子中，因为表单没有和user对象直接绑定，所以你不需要
            担心会有脏数据。

        - `__iter__()`

            通过定义的数据迭代表单的字段。

            ```python
            {% for field in form %}
                <tr>
                    <th>{{ field.label }}</th>
                    <td>{{ field }}</td>
                </tr>
            {% endfor %}
            ```

        - `__contains__(name)`

            如果一个字段名称是表单定义的字段名称，返回True.

        - `_get_translations()`

            已经弃用了。使用`Meta.get_translations`来替代。

            必须返回一个提供`gettext()`和`ngettext()`方法的对象。


## Defining Forms

想要定义一个表单，你需要继承`Form`，并且在Form子类中
通过属性声明的方式定义字段。

```python
class MyForm(Form):
    first_name = StringField('First Name', validators=[validators.input_required()])
    last_name = StringField('Last Name', validators=[validators.optional()])
```

字段名称可以是任何合法的Python标识符，但是有下面的限制：

- 字段名是大小写敏感的
- 字段名不可以以下划线开头
- 字段名不可以以"validate"开头

### Form Inheritance

Form可以按照需求来继承另一个form。

新的form可以包含所有父类form的字段，以及子类中定义的新的字段。

```python
class PastebinEdit(Form):
    language = SelectField("Programming Language", choices=PASTEBIN_LANGUAGES)
    code = TextAreaField()


class PastebinEntry(PastebinEdit):
    name = StringField('User Name')
```

### In-line Validators

想要加入一次性的自定义的验证方式，不要写validator，
直接定义一个`validate__fieldname`形式的方法就好了.

```python
class SignupForm(Form):
    age = IntegerField('Age')

    def validate_age(form, field):
        if field.data < 13:
            raise ValidationError("We're sorry, your must be 13 or older to register")
```

## Using Forms

Form通常在MVC的controller中被构建，一般使用请求输入来构建，
甚至可以是一个ORM对象。

```python
def edit_article(request):
    article = Article.get(...)
    form = MyForm(request.POST, article)
```

典型的CRUD view一般都有让用户编辑更新的状况。

构造后的表单可以验证输入的数据，在验证不合法的时候将会生成错误。

```python
if request.POST and form.validate():
    form.populdate_obj(article)
    article.save()
    return redirect('/articles')
```

如果验证失败，可以仍然将这个Form对象传入到模版中，用来现实错误信息。

`return render('edit.html', form=form, article=article)`

## Low-Level API

对于一些特殊的应用，想要更加自定义WTForms，可能需要使用`BaseForm`.

`BaseForm`是`Form`的父类，Form的大都数逻辑都是来自于BaseForm.

它们之间主要的不同就是字段一般是定义于BaseForm的子类。如果你想要用BaseForm
定义字段，你必须以字典的形式传入它的构造器。

另外，BaseForm并不会保持字段的定义顺序，以及inline验证器。

因为这些原因，绝大多数情况下我们都推荐使用`Form`而不是`BaseForm`.

BaseForm提供了一个字段的容器，在实例化的时候将它们绑定在一起，并放在一个内部
的字典中。通过字典键值对形式的访问就可以访问/修改它内部的字段了。

- class`wtforms.form.BaseForm`

    因为BaseForm对字段名称没有限制，所以它可以是任何合法的Python字符串。

    但是我们推荐和Form保持一致。

    参数:

    - fields: 一个字典或者2字段数组的列表，代表表单的字段
    - prefix: 如果提供了，它会用作为字段值的前缀
    - meta: 一个meta实例，用来构造和自定义WTForms的行为

    属性:

    - data: 同Form.data
    - errors: 同Form.errors
    
    方法：

    - `process(formdata=None, obj=None, data=None, **kwargs)`

        接受form, obj, data以及关键字参数的输入，通过定义的字段来处理它们。

        因为BaseForm的初始化的时候不会接受数据，所以你必须通过这个方法
        来处理数据。

    - `validate(extra_validators=None)`

        调用每个form字段的验证器。

    - `__iter__()`

    - `__contains(name)`

    - `__getitem__(name, value)`

    - `__setitem__(name, value)`

    - `__delitem__(name)`


