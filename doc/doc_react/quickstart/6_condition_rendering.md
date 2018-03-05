# Condition Redering

*在React中，你可以根据需求封装创建很多不同的Components。然后你可以根据应用的状态选择渲染它们中的一部分*.

React中的条件渲染和Javascript中的条件语句类似。

考虑下面两个组件：

```javascript
function UserGreeting(props) {
    return <h1>Welcome back!</h1>;
}


function GuestGretting(props) {
    return <h1>Please sign up.</h1>;
}
```

我们创建一个`Greeting`语句，根据用户是否登陆来选择显示上面的其中一个：

```javascript
function Greeting(props) {
    const isLoggedIn = props.isLoggedIn;
    if (isLoggedIn) {
        return <UserGreeting />;
    }
    return <GuestGretting />;
}

ReactDOM.render(
    <Greeting isLoggedIn={false} />,
    document.getElementById('root')
);
```

## Element Variables

你可以使用变量来存储elements。这可以帮助你根据条件渲染一部分组件。

考虑下面来个组件，分别代表登入和登出:

```javascript
function LoginButton(props) {
    return (
        <button onClick={props.onClick}>
            Login
        </button>
    );
}


function LogoutButton(props) {
    return (
        <button onClick={props.onClick}>
            Logout
        </button>
    );
}
```

在下面的例子中，我们创建一个有状态的组件，叫做`LoginControl`.

它会根据当前的状态来渲染`<LoginButton />`或者`<LogoutButton />`：

```javascript
class LoginControl extends React.Component {
    constructor(props) {
        super(props);
        this.handleLoginClick = this.handleLoginClick.bind(this);
        this.handleLogoutClick = this.handleLogoutClick.bind(this);
        this.state = {isLoggedIn: false};
    }

    handleLoginClick() {
        this.setState({isLoggedIn: true});
    }

    handleLogoutClick() {
        this.setState({isLoggedIn: false});
    }

    render() {
        const isLoggedIn = this.state.isLoggedIn;
        
        let button = null;
        if (isLoggedIn) {
            button = <LogoutButton onClick={this.handleLogoutClick} />;
        } else {
            button = <LoginButton onClick={this.handleLoginClick} />;
        }

        return (
            <div>
                <Greeting isLoggedIn={isLoggedIn} />
                {button}
            </div>
        );
    }
}

ReactDOM.render(
    <LoginControl />,
    document.getElementById('root');
);
```

有时你可能想要使用更加简短的语法。在JSX中有集中内嵌条件语句。

## Inline If with Logical && Operator

你可以在JSX中通过大括号嵌入任意表达式。包括Javascript逻辑&&操作符。可以用来判断是否包含一个元素：

```javascript
function Mailbox(props) {
    const unreadMessages = props.unreadMessages;
    return (
        <div>
            <h1>Hello!</h1>
            {unreadMessages.length > 0 &&
                <h2>
                    You have {unreadMessage.length} unread messages.
                </h2>
            }
        </div>
    );
}

const messages = ['React', 'Re: React', 'Re:Re: React'];
ReactDOM.render(
    <Mailbox unreadMessages={messages} />,
    document.getElementById('root')
);
```

这个语法有效是因为，`true&&expression`总是会eval这个expression，而`false&expression`则不会eval expression。

因此，如果条件是true，`&&`之后的元素将会输出。否者，元素会被忽略。

## Inline If-Else with Conditional Operator

另一个内嵌条件语句是：`condition ? true : false`.

在下面的例子中，我们使用条件语句来渲染一小块文本：

```javascript
render() {
    const isLoggedIn = this.state.isLoggedIn;
    return (
        <div>
            The user is <b>{isLoggedIn ? 'currently' : 'not'}</b> Logged in.
        </div>
    );
}
```

也可以用在更大的表达式上面：

```javascript
render() {
    const isLoggedIn = this.state.isLoggedIn;
    return (
        <div>
            {isLoggedIn ? (
                <LogoutButton onClick={this.handleLogoutClick} />
            ) : (
                <LoginButton onClick={this.handleLoginClick} />
            )}
        </div>
    );
}
```

## Preveting Component from Rendering

在一些罕见的情况下，你希望一个组件隐藏自身，甚至在另一个组件渲染它的时候也这样。可以返回`null`来达到这个效果。

在下面的例子中，`<WarningBanner />`根据`warn`值来决定是否渲染：

```javascript
function WarningBanner(props) {
    if (!props.warn) {
        return null;
    }

    return (
        <div className='warning'>
          Warning!
        </div>
    );
}


class Page extends React.Component {
    constructor(props) {
        super(props);
        this.state = {showWarning: true};
        this.handleToggleClick = this.handleToggleClick.bind(this);
    }

    handleToggleClick() {
        this.setState(prevState => ({
            showWaring: !prevState.showWarning
        }));
    }

    render() {
        return (
            <div>
                <WarningBanner warn={this.showWarning} />
                <button onClick={this.handleToggleClick}>
                  {this.state.showWarning ? 'Hide' : 'Show'}
                </button>
            </div>
        );
    }
}


ReactDOM.render(
    <Page />,
    document.getElementById('root')
);
```

