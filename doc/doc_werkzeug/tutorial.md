# Werkzeug Tutorial

欢迎来到Werkzeug教程，我们会为教你创建山寨一个TinyURL并把URLs存储在一个Redis实例中。这个应用我们使用Jinja2作为模版，redis作为数据库层，使用Werkzeug作为WSGI层。

你可以使用`pip`来安装依赖库：

`$ pip install Jinja2 redis Werkzeug`

另外你需要确保本机运行了redis server...

## Inroducing Shortly

在这篇教程中，我们会使用Werkzeug创建一个简单的URL简化服务。请注意Werkzeug不是一个框架，它是一个工具可以用它来创建你自己的框架或者应用。它的用户很宽泛，这里例子只是众多使用方式的一种。

## Step0: A Basic WSGI Introduce

Werkzeug是WSGI的工具库。WSGI本身是一个协议，可以让你的web应用更方便的和web服务器沟通。

一个基础的WSGI - “Hello World“应用看起来像下面这样：

```python
def application(environ, start_response):
    start_response('200 OK', [('Content-Type', 'text/plain')])
    return ['Hello World']
```

WSGI应用是一个你可以通过传入一个`environ`和一个`start_response`(callable)调用的东东。environ包含所以到来的信息，`start_response`函数可以用来开启response。使用Werkzeug，你不需要直接处理requests和response对象。

请求的数据通过`environ`变量带来，通过一个environ来访问数据是一个好习惯。WSGI应用提供了一个很nicer的方式来创建response.

下面是是你应该怎么在应用中编写response对象：

```python
from werkzeug.wrappers import Response

def application(environ, start_response):
    response = Response('Hello World!', mimetype='text/plain')
    return response(environ, start_response)
```

下面是一个扩展版本的应用，它会查询URL中的query string：

```python
from werkzeug.wrappers import Request, Response

def application(environ, start_response):
    request = Request(environ)
    text = 'Hello %s!' % request.args.get('name', "World")
    response = Response(text, mimetype='text/plain')
    return response(environ, start_response)
```

这是你需要知道的关于WSGI的所有东西。

## Step1: Creating the Folders

在开始之前，让我们创建这个应用所需的文件夹：

```txt
/shortly
    /static
    /templates
```

shortly文件夹不是一个Python package，只是我们用来存放文件的地方。static文件夹中的内容允许我们的app用户通过HTTP来直接访问，它是存放CSS和JS文件的地方。在templates文件夹中，我们用来存放Jinja2的模版。

## Step2: The Base Structure

现在让我们为应用创建一个模块。我们先在`shortly`文件夹中创建一个`shortly.py`文件，然后我们需要import一些依赖:

```python
import os
import redis
import urlparse

from werkzeug.wrappers import Request, Response
from werkzeug.routing import Map, Rule
from werkzeug.exceptions import HTTPException, NotFound
from werkzeug.wsgi import SharedDataMiddleware
from werkzeug.utils import redirect
from jinja2 import Environment, FileSystemLoader
```

然后我们创建应用的基础结构，并且使用一个函数来为它实例化，另外可以使用WSGI中间件来把static文件夹的内容暴露给WEB：

```python
class Shortly(object):

    def __init__(self, config):
        self.redis = redis.Redis(config['redis_host'], config['redis_port'])
        
    def dispatch_request(self, request):
        return Response('Hello World!')

    def wsgi_app(self, environ, start_response):
        request = Request(environ)
        response = self.dispatch_request(request)
        return response(environ, start_response)

    def __call__(self, environ, start_response):
        return self.wsgi(environ, start_response)


def create_app(redis_host='localhost', redis_port=6379,
               with_static=True):
    app = Shortly({
        'redis_host': redis_host,
        'redis_port': redis_port
    })
    if with_static:
        app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
            '/static': os.path.join(os.path.dirname(__file__), 'static')
        }) 
    return app
```

最后，我们再加上一段代码来启动一个本地开发服务器，以及开启自动代码重载和debugger：

```python
if __name__ == '__main__':
    from werkzeug.serving import run_simple
    app = create_app()
    run_simple('127.0.0.1', 5000, app, use_debugger=True, use_reloader=True)
```

我们可以看到`Shortly`类是一个WSGI应用。`__call__`方法直接委派给了`wsgi_app`。因此我们在`create_app`函数中需要对`wsgi_app`进行再次封装。`wsgi_app`方法之后会创建一个`Request`对象并调用`dispatch_request`来获取一个`Response`对象。你可以看到：“turtles all the way down”.不管是我们创建的Shortly类，还是Werkzeug实现的request对象都实现了WSGI接口。你甚至可以使用`dispath_request`方法返回另一个WSGI应用。

`create_app`工厂函数可以用来创建一个我们应用的实例。不只是传入配置参数，另外还可以选择是否用中间件来输出静态文件。这些东东在开发环境会很有用。

## Intermezzo: Running the Application

现在你可以使用python来执行这个文件，你会看到在你的机器中启动了一台服务器：

```python
$ python shortly.py
 * Running on http://127.0.0.1:5000/
 * Restarting with reloader: stat() polling
```

你可以看到开启了reloader。它使用了一些计数来扫描你的文件变动然后就自动重启。

请用浏览器打开这个URL，会看到“Hello World！”

## Step3: The Environment

现在我们有了一个基础应用类，我们可以在构造器中做一些更有用的事情。我们需要连接redis以及渲染模版，所以让我们继续扩展这个类吧：

```python
def __init__(self, config):
    self.redis = redis.Redis(config['redis_host'], config['redis_port'])
    template_path = os.path.join(os.path.dirname(__file__), 'templates')
    self.jinja_env = Environment(loader=FileSystemLoader(template_path),
                                 autoescape=True)


def render_template(self, template_name, **context):
    t = self.jinja_env.get_template(template_name)
    return Response(t.render(context), mimetype='text/html')
```

## Step4: The Routing

下一步是路由。路由是用来处理URL的解析和匹配的。Werkzeug使用了一套弹性的路由系统。我们需要创建一个`Map`实例并为它加入若干`Rule`对象。买个Rule实例都试图将URL和一个“端点(endpoint)"相对应。端点一般是一个字符串，用来代表URL的唯一标示。我们可以使用它来自动逆推URL，不过这不是本篇URL的内容。

请将下面的代码也放到构造器(`__init__()`)中:

```python
self.url_map = Map([
    Rule('/', endpoint='new_url'),
    Rule('/<short_id>', endpoint='follow_short_link'),
    Rule('/<short_id>+', endpoint='short_link_details')
])
```

我们通过三个rule来创建了一个URL map。`/`代表URL根目录，我们将会为它委派一个函数实现一些逻辑来创建新的URL。第二个rule是目标URL的短链接，第三个rule(和第二个一样不过结尾加了一个`+`)代表链接详情.

那么我们怎么把端点和函数对应起来呢？这取决于你。在这篇教程中我们使用`on_` + 端点的方式：

```python
def dispath_request(self, request):
    adapter = self.url_map.bind_to_environ(request.environ)
    try:
        endpoint, values = adapter.match()
        return getattr(self, 'on_' + endpoint)(request, **values)
    except Exception as e:
        return e
```

我们将URL map和当前的environ绑定在一起，它会返回给我们一个`URLAdapter`.这个adapter可以用来匹配请求的URL(也可以逆推URL)。`.match()`方法将会返回一个endpoint和一个代表URL中值的字典。例如，rule - `follow_short_link`有一个变量叫做`short_id`.在我们输入`http://localhost:5000/foo`的时候，会返回下列值：

```python
endpoint = 'follow_short_link'
values = {'short_id': 'foo'}
```

如果什么都没有匹配，会抛出`NotFound`异常，它是`HTTPException`的子类。所有的HTTP异常都会被WSGI应用捕获并生成错误页面。所以我们可以将它们全部捕获并直接返回错误。

如果匹配正常，我们会调用函数(`on_` + endpoint)，把request作为位置参数和URL解析得来的字典值作为关键字参数来调用这个函数。

最后需要返回这个匹配函数返回的Response对象。

## Step5: The First View

让我们开始写第一个view： new url中的一个:

```python
def on_new_url(self, request):
    error = None
    url = ''
    if request.method == 'POST':
        url = request.form['url']
        if not is_valid_url(url):
            error = 'Please enter a valid URL'
        else:
            short_id = self.insert_url(url)
            return redirect('/%s+' % short_id)
    return self.render_template('new_url.html', error=error, url=url)
```

这个view的逻辑应该很容易看懂。我们先检查request方法是否是POST，然后我们验证这个URL并且会数据库加入一个新的记录，然后重定向到detail页面。这以为这我们需要再写一个helper函数和一个方法。下面这个函数用来检查URL是否合法：

```python
def is_valid_url(url):
    parts = urlparse.urlparse(url)
    return parts.scheme in ('http', 'https')
```

相面这个方法用来吧URL插入到数据库:

```python
def insert_url(self, url):
    short_id = self.redis.get('reverse-url:' + url)
    if short_id is not None:
        return short_id
    url_num = self.redis.incr('last-url-id')
    short_id = base36_encode(url_num)
    self.redis.set('url-target:' + short_id, url)
    self.redis.set('reverse_url: ' + url, short_id)
    return short_id
```

`revser-url:` + URL这个Redis键用来存储short id。如果这个URL以及提交过了，那么它就不会是None，我们直接把这个short id返回就行了。否则，我们需要递增`last-url-id`并且将这个递增数使用base36来转换。然后我们将链接和short id都存储在redis中。下面是转换base36的函数:

```python
def base36_encode(number):
    assert number >= 0, 'positive integer required'
    if number == 0:
        return '0'
    base36 = []
    while number != 0:
        number, i = divmod(number, 36)
        base36.append('0123456789abcdefghijklmnopqrstuvwxyz'[i])
    return ''.join(reversed(base36))
```

## Step6: Redirect View

redirect view很简单。它只要查询redis中的url然后重定向过去就好了。另外我们会递增一个counter，这样我们就知道一个链接被点击了多少次：

```python
def on_follow_short_link(self, request, short_id):
    link_target = self.redis.get('url-taget:' + short_id)
    if link_target is None:
        raise NotFound()
    self.redis.incr('click-count:' + short_id)
    return redirect(link_target)
```

在上面代码中，如果没有找到URL我们会抛出`NotFound`异常，这个异常会冒泡给`dispatch_request`函数，它会被转换为默认的404 response.

## Step7: Detail View

这个link detail view和之前例子很类似，我们只是再次渲染了一个模版。除了查询目标URL，我们会询问redis这个链接被点击了多少次，如果这个键不存在，默认点击数为0:

```python
def on_short_link_details(self, request, short_id):
    link_target = self.redis.get('url-target:' + short_id)
    if link_target is None:
        raise NotFound()
    click_count = int(self.redis.get('click-count:' + short_id) or 0)
    return self.render_template('short_link_details.html',
                                link_target=link_target,
                                short_id=short_id,
                                click_count=click_count)
```

因为redis返回的数据总是为字符串，所以我们需要用`int()`把它转换为整数。

## Step8: Templates

这里列出了所有的模版。把它们拖到文件夹即可。Jinja2支持模版继承，所以首先我们创建一个布局模版并放置几个block作为占位符。我们配置了Jinja2的autoescape，所以字符串会自动按HTML规则转义，它可以防止XSS攻击和渲染错误。

- `layout.html`

    ```html
    <!doctype html>
    <title>{%block title}{% endblock %} | shortly</title>
    <link rel='stylesheet' href='/static/style.css' type='text/css'>
    <div class='box'>
        <h1><a href='/'>shortly</a></h1>
        <p class='tagline'>Shortly is a URL shortener written with Werkzeug</p>
        {% block body %}{% endblock %}
    </div>
    ```

- `new_url.html`

    ```html
    {% extends "layout.html" %}
    {% block title %}Create New Short URL{% endblock %}
    {% block body %}
    <h2>Submit URL</h2>
    <form action="" method=post>
        {% if error %}
        <p class=error><strong>Error:</strong> {{ error }}
        {% endif %}
        <p>URL:
        <input type=text name=url value="{{ url }}" class=urlinput>
        <input type=submit value="Shorten">
    </form>
    {% endblock %}
    ```

- `short_link_detail.html`

    ```html
    {% extends "layout.html" %}
    {% block title %}Details about /{{ short_id }}{% endblock %}
    {% block body %}
    <h2><a href="/{{ short_id }}">/{{ short_id }}</a></h2>
    <dl>
        <dt>Full link
        <dd class=link><div>{{ link_target }}</div>
        <dt>Click count:
        <dd>{{ click_count }}
    </dl>
    {% endblock %}
    ```

## Step9: The Style

为了让它不是丑陋的黑白风，我们需要加入一个简单的样式表：

- `static/style.css`

    ```css
    body        { background: #E8EFF0; margin: 0; padding: 0; }
    body, input { font-family: 'Helvetica Neue', Arial,
                sans-serif; font-weight: 300; font-size: 18px; }
    .box        { width: 500px; margin: 60px auto; padding: 20px;
                background: white; box-shadow: 0 1px 4px #BED1D4;
                border-radius: 2px; }
    a           { color: #11557C; }
    h1, h2      { margin: 0; color: #11557C; }
    h1 a        { text-decoration: none; }
    h2          { font-weight: normal; font-size: 24px; }
    .tagline    { color: #888; font-style: italic; margin: 0 0 20px 0; }
    .link div   { overflow: auto; font-size: 0.8em; white-space: pre;
                padding: 4px 10px; margin: 5px 0; background: #E5EAF1; }
    dt          { font-weight: normal; }
    .error      { background: #E8EFF0; padding: 3px 8px; color: #11557C;
                font-size: 0.9em; border-radius: 2px; }
    .urlinput   { width: 300px; }
    ```
    
## Bonus:Refinements

请看Werkzeug仓库中的example目录，那里有个同样的应用并且追加了一些功能(比如自定义404页面).

- [shortly in the example folder](https://github.com/pallets/werkzeug/blob/master/examples/shortly)