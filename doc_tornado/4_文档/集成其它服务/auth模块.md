## tornado.auth -- OpenID和Oauth的第三方登录

这个模块包含不同的第三方验证模式的实现。

这个模块中的所有类都是类mixin，用来和`tornado.web.RequestHandler`一起多重继承。它们有两种用途：

- 在一个登录handler中，使用类似`authenticate_redirect(), authorize_redirect()` 或者 `get_authenticated_user()`这些方法来建立用户的标识，并且将验证token存入到你的数据库或者cookies。

- 在非登录handler中，使用类似`facebook_request()`或者`twitter_request()`这些方法，用验证的token来请求服务。

因为所有服务的验证方式不同，它们接受的参数也不同。

下面是一个Google Oauth的用法例子：

```python
class GoogleOauth2LoginHandler(tornado.web.RequestHandler,
                               tornado.auth.GoogleOauth2Mixin):
    @tornado.gen.coroutine
    def get(self):
        if self.get_argument("code", False):
            user = yield self.get_authenticated_user(redirect_uri='http://your.site.com/auth/google',
                                                     code=self.get_argument('code'))
        # 保存user信息
        else:
            yield self.authrize_redirect(
                redirect_uri='http://your.site.com/auth/google',
                client_id=self.settings['google_oauth']['key'],
                scope=['profile', 'email'],
                response_type='code',
                extra_params={'approval_prompt': auto}
            )
```

### 常见协议

这个类实现了OpenID和Oauth标准。一般需要继承这个类来对特定的站点使用。自定义的程度根据需求而不同，但多数情况下覆盖类属性(处于历史原因，这些属性的名称以下划线开头)的值就足够了。

- `tornado.auth.OpenIdMixin`

    OpenID的抽象接口。

    类属性：

    - `_OPENID_ENDPOINT`: 身份标示提供者的URI。

    方法：

    - `authenticate_redirect(callback_uri=None, ax_attrs=['name', 'email', 'language', 'username'], callback=None)`

        重定向到这个服务的验证URL。

        在验证完成后，服务会重定向回到给定的URI，并且会携带额外的参数，包括`openid.mode`.

        我们默认请求验证用户给定的属性(name, email, language, username)。如果你不需要所有这些属性，你可以在`ax_attrs`参数中设置。

    - `get_authenticated_user(callback, http_client=None)`

        根据重定向回来的请求，获取验证用户的数据。

        这个方法应该在handler接受从`authentiacte_redirect()`方法的重定向请求之后调用。

        这个方法的结果一般存于数据库，或者存于cookie。

    - `get_auth_http_client()`

        返回一个`AsyncHTTPClient`实例，用于验证用途的请求。

        可以重写，使用一个HTTPClient或者一个CurlAsyncHTTPClient。


- `tornado.auth.OAuthMixin`

    OAuth1.0和OAuth1.0a的抽象实现。

    **类属性**：

    - `_OAUTH_AUTHORIZE_URL`: 服务的OAuth验证URL。
    - `_OAUTH_ACCESS_TOKEN_URL`: 服务的OAuth访问token URL。
    - `_OAUTH_VERSION`: 可以是"1.0"或者"1.0a"。
    - `_OAUTH_NO_CALLBACKS`: 如果服务要求高级的callback注册，需要把这个属性设置为`True`。

    子类必须重写`_oauth_get_user_future`以及`_oauth_consumer_token`方法。

    **方法**:

    - `authorize_redirect(callback_uri=None, extra_params=None, http_client=None, callback=None)`

        将用户重定向到这个服务的OAuth验证URL。

        如果之前你已在第三方服务中注册了一个callback URI，参数`callback_uri`可以省略。一些服务(包括FriendFeed)，你必须在服务中注册callback URI，而不能用这个方法指定一个callback。

        这个方法设置一个叫做`_oauth_request_token`的cookie在随后的`get_authenticated_user`的使用(处于安全的原因)。

        注意这个方法是异步的，不过它调用了`RequestHandler.finish`，所以你没必要传入一个callback或者处理它返回的Future。但是，如果这个方法在一个通过`@gen.coroutine`封装的函数中被调用，你必须使用`yield`让response不要过早的结束。

    - `get_authenticated_user(callback, http_client=None)`

        获取OAuth验证用户和访问Token。

        这个方法应该在你的OAuth callback URL的handler中被调用，用以完成注册处理。我们将验证用户字典和这个callback一起运行。这个字典包含一个`access_key`，它可以用来对这个服务作出带授权的请求。根据服务的设定，这个字典还会包含一些其它字段，如`name`。

    - `_oauth_consumer_token()`

        子类必须重写这个方法，来返回它的`OAuth`consumer keys。

        返回的值必须是一个字典，包含两个键：`key`和`secret`。

    - `_oauth_get_user_future(access_token, callback)`

        子类必须重写这个方法，来获取用户的基础信息。

        应该返回一个Future，它的结果是一个字典，包含了用户的基本信息，可以使用`access_token`来对服务请求用户信息。

        access token应该追加到返回的字典中，让`get_authenticated_user`方法可以使用。

   - `get_auth_http_client()`

        返回一个`AsyncHTTPClient`实例，用于验证用途的请求。

        可以重写，使用一个HTTPClient或者一个CurlAsyncHTTPClient。


- `tornado.auth.OAuth2Mixin`

    OAuth2.0的抽象实现。

    **类属性**：

    - `_OAUTH_AUTHORIZE_URL`: 服务的验证URL
    - `_OAUTH_ACCESS_TOKEN_URL`: 服务的access token URL

    **方法**:

    - `authorize_redirect(redirect_uri=None, client_id=None, client_secret=None, extra_params=None, callback=None, scope=None, response_type='code')`

        将用户重定向到这个服务的OAuth验证URL。

        如果之前你已在第三方服务中注册了一个callback URI，参数`callback_uri`可以省略。一些服务(包括FriendFeed)，你必须在服务中注册callback URI，而不能用这个方法指定一个callback。

    - `oauth2_request(url, callback, access_token=None, post_args=None, **args)`

        通过OAuth2访问token的授权来获取一个给定的URL。

        如果这个请求是POST，需要提供`post_args`参数。query string参数应该通过关键字参数传入。

        用法：

        ```python
        class MainHandler(tornado.web.RequestHandler,
                          tornado.auth.FacebookGraphMixin):
            @tornado.web.authenticated
            @tornado.gen.coroutine
            def get(self):
                new_entry = yield self.oauth2_request(
                    "https://graph.facebook.com/me/feed",
                    post_args={"message": "I am posting from my Tornado application!"},
                    access_token=self.current_user['access_token']
                )

                if not new_entry:
                    # 调用失败，可能是授权过期了？
                    yield self.authorize_redirect()
                    return
                self.finish("Posted a message!")
        ```

    - `get_auth_http_client()`

        返回一个`AsyncHTTPClient`实例，用于验证用途的请求。

        可以重写，使用一个HTTPClient或者一个CurlAsyncHTTPClient。


### Google

- `tornado.auth.GoogleOauth2Mixin`

    使用OAuth2的Google验证。

    为了使用这个Mixin，需要在Google中注册你的应用，然后将相关的参数拷贝到你应用的settings中。

    **步骤**：

    1. 去Google的开发者控制台:[http://console.developers.google.com](http://console.developers.google.com)
    2. 选择一个项目，或者创建一个新的项目。
    3. 在左侧的边框中，选择`APIs&Auth`。
    4. 在API列表中，找到Google+ API，并把它设置为ON。
    5. 在左侧的边框中，选择`Credentials`。
    6. 在页面的Oauth部分中，选择`Create New  Client ID`
    7. 将`Redirect URI`指向你的验证handler。
    8. 将`Client secret`和`Client ID`拷贝到项目的application settings中。

    **方法**:

    - `get_authenticated_user(redirect_uri, code, callback)`

        处理Google用户的登录，返回一个access token。

        结果是一个包含`access_token`字段(及其它)的字典。不想这个模块中的其它`get_authenticated_user`方法，这个方法不会返回用户的额外信息。可以用返回的access token来使用`Oauth2Mixin.oauth2_request`，来请求额外的信息。

        使用例子：

        ```python
        class GoogleOauth2LoginHandler(tornado.web.RequestHandler,
                                       tornado.auth.GoogleOauth2Mixin):
            @tornado.gen.coroutine
            def get(self):
                if self.get_argument("code", False):
                    access = yield self.get_authenticated_user(
                        redirect_uri="http://your.site.com/auth/google",
                        code=self.get_argument("code")
                    )
                    # 保存用户的access token
                else:
                    yield self.authorize_redirect(
                        redirect_uri='http://your.site.com/auth/google',
                        client_id=self.settings['google_auth']['key'],
                        scope=['profile', 'email'],
                        response_type='code',
                        extra_params={"approval_prompt": "auto"}
                    )
        ```

### Facebook

- `tornado.auth.FacebookGraphMixin`

    
    





