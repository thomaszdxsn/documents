# Composition vs Inheritance

React有一个强大的混合模型(composition model),我们推荐使用混合而不是继承来重用组件之间的代码。

在这章节中，我们会思考一些React新手往往想用继承解决的问题，并且展示如何使用混合来解决。

## Containment

一些组件不知道直接有哪些子组件。通常见于类`Sidebar`或者`Dialog`组件。

我们推荐使用这些组件使用一个特殊的`children`prop来直接传入子元素:

```javascript
function FancyBorder(props) {
    return (
        <div className={'FancyBorder FancyBorder-' + props.color}>
            {props.children}
        </div>
    );
}
```

可以让另一个组件在JSX中传入任意的子元素:

```javascript
function WelcomeDialog() {
    return (
        <FancyBorder color='blue'>
            <h1 className='Dialog-title'>
                Welcome
            </h1>
            <p className='Dialog-message'>
                Thank you for visiting our spacecraft!
            </p>
        </FancyBorder>
    );
}
```

任何嵌入`<FancyBorder>`的JSX标签都会传入`FancyBorder`组件，作为属性`children`。由于`FancyBorder`在一个`<div>`中渲染了`{props.children}`，传入的元素会出现在最终的输出中。

另外一种情况不太常见，有时你需要在一个组件中有多个“洞(hole)”。在这种情况下你可以用自己的命名而不是`children`:

```javascript
function SplitPane(props) {
    return (
        <div className='SplitPane'>
            <div className='SplitPane-left'>
                {props.left}
            </div>
            <div className='SplitPane-right'>
                {props.right}
            </div>
        </div>
    );
}


function App() {
    return (
        <SplitPane
            left={<Contacts />}
            right={<Chat />}
        />
    );
}
```

React的元素如`<Contacts />`和`<Chat />`都是对象，所以你可以将它作为prop传入给另外一个组件。

## Specializaiton

有时我们会把一种组件看作另一种的“特殊情况”。例如，我们会认为`WelcomeDialog`是`Dialog`的一种特殊情况。

在React中，同样可以使用混合模型来实现：

```javascript
function Dialog(props) {
    return (
        <FancyBorder color="blue">
            <h1 className="Dialog-title">
                {props.title}
            </h1>
            <p className="Dialog-message">
                {props.message}
            </p>
        </FancyBorder>
    );
}


function WelcomeDialog() {
    return (
        <Dialog
            title="Welcome"
            message="Thank you for visiting our spacecraft!"
        />
    );
}
```

可以定义一个类来使用混合:

```javascript
function Dialog(props) {
    return (
        <FancyBorder color='blue'>
            <h1 className='Dialog-title'>
                {props.title}
            </h1>
            <p className='Dialog-message'>
                {props.message}
            </p>
            {props.children}
        </FancyBorder>
    );
}


class SignUpDialog extends React.Component {
    constructor(props) {
        super(props);
        this.handleChange = this.handleChange.bind(this);
        this.handleSighUp = this.hadnleSighUp.bind(this);
        this.state = {login: ''};
    }

    render() {
        return (
            <Dialog title='Mars Exploration Program'
                    message='How should we refer to you?'>
                <input value={this.state.login}
                       onchange={this.handleChange} />
                <button onClick={this.handleSighUp}>
                  Sign Me Up!
                </button>
            </Dialog>  
        );
    }

    handleChange(e) {
        this.setState({login: e.target.value});
    }

    handleSignUp() {
        alert(`Welcome aborted, $(this.state.login)!`);
    }
}
```

## So What Abount Inheritance?

在Facebook中，我们使用React构建上千个组件，但我们仍然没有碰到一个情况是必须用继承来实现的。

props和composition可以给你充足的弹性。记住组件可以接受任意数量的props，包含原语值，React元素或者函数。

如果你想重用组件之间的非UI功能，我们推荐把它提取出来放在一个单独的Javascript模块。组件可以引入它并使用，不需要继承。

