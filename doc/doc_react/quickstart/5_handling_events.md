# Handling Events

React中的事件处理和DOM中的事件处理类似。不过有一些语法上的区别：

- React事件命名使用驼峰命名法，而不是小写形式
- JSX中你需要将函数当作事件handler传入，而不是字符串

例如，在HTML中：

```javascript
<button onclick='activateLasers'>
    Activate Lasers
</button>
```

React中有些不同：

```javascript
<button onClick={activateLasers}>
    Activate Lasers
</button>
```

另一个不同之处在于你不能在React中通过返回`false`去取消默认行为。你必须显式地调用`preventDefault`.例如，就普通的HTML来说，想要预防link打开新页面这种默认行为：

```javascript
<a href="#" onclick="console.log('The link was clicked.'); return false">
  Click me
</a>
```

在React中，你必须这么写：

```javascript
function ActionLink() {
    function handleClick(e) {
        e.preventDefault();
        console.log('this link was clicked.');
    }

    return (
        <a href="#" onClick={handleClick}>
            Click me
        </a>
    )
}
```

这里，`e`是synthetic event。React根据W3C规范来定义这些synthetic even，所以你不需要考虑跨浏览器之间的兼容性问题。

在使用React的时候，你一般不需要在创建HTML元素之后为它添加监听器`addEventListener`。而是，在元素初始渲染的时候提供一个监听器。

在你使用类定义一个组件时，一个常见的模式是将事件handler名称当作类的方法名。例如，`Toggle`组件渲染一个按钮，可以在“on”和“off”之间切换:

```javascript
class Toggle extends React.Component {
    constructor (props) {
        super(props);
        this.state = {isToggleOn: true};

        // 找个binding是必须的
        this.handleClick = this.handleClick.bind(this);
    }

    handleClick() {
        this.setState(prevState => ({
            isToggleOn: !prevState.isToggleOn
        }));
    }

    render() {
        return (
            <button onClick={this.handleClick}>
              {this.state.isToggleOn ? 'On' : 'Off'}
            </button>
        );
    }
}


ReactDOM.render(
    <Toggle />,
    document.getElementById('root')
);
```

你必须小心JSX回调中this的含义。在Javascript中，类方法默认不会绑定。如果你忘记绑定`this.handleClick`，然后把它传入到JSX中的`onClick`，函数调用的时候`this`会变为`undefined`.

这不是React特有的行为；这是Javascript函数原理的一部分。一般来说，在你引用一个方法但又没有直接调用它的时候(函数后面没有`()`)，比如`onClick={this.handleClick}`，你应该首先绑定这个方法。

如果你很烦调用`bind`，其实还有两种其它方法。如果你使用实验中的`public class fields`语法，你可以使用类字段来正确绑定callback：

```javascript
class LoggingButton extends React.Component {
    // 这个语法确保`this`绑定到了handleClick
    // 不过这是一个“实验中”的语法
    handleClick = () => {
        console.log('this is: ', this)
    }

    render() {
        return (
            <button onClick={this.handleClick}>
                Click me
            </button>
        );
    }
}
```

在创建React App时，这个语法是默认开启的。

如果你不使用类字段语法，你可以在callback中时间箭头函数:

```javascript
class LoggingButton extends React.Component {
    handleClick() {
        console.log('this is: ', this);
    }

    render() {
        reutrn (
            <button onClick={(e) => this.handleClick(e)}>
              Click me
            </button>
        );
    }
}
```

后一种方法存在一些问题可能会导致额外的渲染开销。我们一般推荐在构造器中使用bind或者使用class field语法。

## Passing Arguments to Event Handlers

在一个循环中往往想对事件处理器传入额外的参数。例如，如果`id`是行ID，下面的语法都有效:

```javascript
<button onClick={(e) => this.deleteRow(id, e)}>Delete Row</button>
<button onClick={this.deleteRow.bind(this, id)}>Delete Row</button>
```

上面两行代码是等同的，分别使用箭头函数和`Function.prototype.bind`.

在`bind`例子中，`e`参数会自动传入，所以不需要自己处理。

