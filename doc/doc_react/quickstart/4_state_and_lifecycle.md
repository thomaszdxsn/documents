# State and Lifecycle

迄今为止，我们只学会一种方式来更新UI。

我们调用`ReactDOM.render()`来修改渲染的输出：

```javascript
function ticker() {
    const element = (
        <div>
            <h1>Hello, world!</h1>
            <h2>It is {new Date().toLocalTimeString()}.</h2>
        </div>
    );
    ReactDOM.render(
        element,
        document.getElementById('root')
    );
}

setInteval(tick, 1000);
```

在这个章节，我们会让`Clock`组件封装，可重用。它会建立起自己的timer，并且每秒更新。

我们先看看怎么封装这个clock：

```javascript
function Clock(props) {
    return (
        <div>
            <h1>Hello, world!</h1>
            <h2>It is {props.date.toLocaleString()}.</h2>
        </div>
    );
}


function tick() {
    ReactDOM.render(
        <Clock date={new Date()} />,
        document.getElementById('root')
    );
}

setInteval(tick, 1000)
```

不过还有关键的地方没有实现，`Clock`应该建立起自己的timer，应该在Clock内部实现每秒更新。

理论上我们直接渲染`Clock`这个component就好了。

```javascript
ReactDOM.render(
    <Clock />,
    document.getElementById('root')
);
```

为了实现它，我们必须为Clock组件加入状态。

State和props类似，不过它是私密属性并且完全由组件本身控制。

## Converting a Function to a Class

你可以通过下面5个步骤，把`Clock`由一个函数组件转换为一个类组件：

1. 创建一个ES6 class，取相同的名称，继承自`React.Component`.
2. 加入一个空方法，叫做`render()`.
3. 将原来函数组件中的内容复制黏贴到`render()`中.
4. 将`render()`中的`props`替换为`this.props`.
5. 删除原来的函数组件声明.

```javascript
class Clock extends React.Component {
    render() {
        return (
            <div>
                <h1>Hello, world!</h1>
                <h2>It is {this.props.date.toLocalTimeString()}.</h2>
            </div>
        );
    }
}
```

## Adding Local State to a Class

我们将通过3个步骤把`date`从props移动到state里面；

1. 将`render()`方法中的`this.props.date`替换为`this.state.date`:

```javascript
class Clock extends React.Component {
    render() {
        return (
            <div>
                <h1>Hello, world!</h1>
                <h2>It is {this.state.date.toLocalTimeString()}.</h2>
            </div>
        );
    }
}
```

2. 加入一个`constructor`，初始化`this.state`:

```javascript
class Clock extends React.Component {
    constructor (props) {
        super(props);
        this.state = {date: new Date()};
    }

    render () {
        ...
    }
}
```

注意，我们为构造器传入了`props`:

```javascript
constructor(props) {
    super(props);
    this.state = {date: new Date()};
}
```

3. 将`<Clock />`元素中的`date`移除:

```javascript
ReactDOM.render(
    <Clock />,
    document.getElementById('root')
);
```

最后的代码像这样：

```javascript
class Clock extends React.Component {
  constructor(props) {
    super(props);
    this.state = {date: new Date()};
  }

  render() {
    return (
      <div>
        <h1>Hello, world!</h1>
        <h2>It is {this.state.date.toLocaleTimeString()}.</h2>
      </div>
    );
  }
}

ReactDOM.render(
  <Clock />,
  document.getElementById('root')
);
```

## Adding Lifecycle Methods to a Class

在一个多组件的应用中，很重要的一点就是在组件被销毁的时候可以释放它所用的资源。

我们想要在Clock被渲染到DOM的第一时间，设置一个timer。在React中把这种行为叫做"mounting".

我们想要在把这个DOM移除的第一时间，清除这个timer。React中把这个行为叫做“unmounting".

我们可以在一个component中声明一些特殊的方法，在mount和unmount的时候运行一些代码：

```javascript
class Clock extends React.Component {
    constructor(props) {
        super(props);
        this.state = (date: new Date());
    }

    componentDidMount() {

    }

    componentWillUnmount() {

    }

    render() {
        return (
            <div>
                <h1>Hello, world!</h1>
                <h2>It is {this.state.date.toLocaleTimeString()}.</h2>
            </div>
        );
    }
}
```

这些方法叫做"生命周期钩子(lifecycle hook)".

`componentDidMount()`钩子会在组件输出被渲染到DOM的时候调用。可以在这里设置一个timer：

```javascript
componentDidMount() {
    this.timerID = setInterval(
        () => this.tick(),
        1000,
    );
}
```

注意我们把timer ID保存到`this`里。

除了`this.props`由React建立，`this.state`有特殊含义意外。this其它的命名空间可以随意使用。

如果数据不会在render()使用，那么它不应该被放在state中。

我们在`componentWillUnmount()`钩子中销毁这个timer：

```javascript
componentWillUnmount() {
    clearInterVal(this.timerID);
}
```

最后，我们实现一个方法叫做`tick`，`Clock`组件每秒钟都会调用它。

它会使用`this.setState()`来规划组件本地状态(state)的更新:

```javascript
class Clock extends React.Component {
    constructor(props) {
        super(props);
        this.state = {date: new Date()};
    }

    componentDidMount() {
        this.timerID = setInterval(
            () => this.tick(),
            1000
        );
    }

    componentWillUnmount() {
        clearInterval(this.timerID);
    }

    tick() {
        this.setState({
            date: new Date()
        });
    }

    render() {
        return (
            <div>
                <h1>Hello, world!</h1>
                <h2>It is {this.state.date.toLocaleTimeString()}.</h2>
            </div>
        );
    }
}


ReactDOM.render(
    <Clock />,
    document.getElementById('root')
);
```

现在clock每秒都会tick了。

让我们总结一下这些方法的调用顺序:

1. 当`<Clock />`传入`ReactDOM.render()`时，React会调用`Clock`组件的构造器。由于Clock需要显示当前的时间，它会初始化一个`this.state`对象，包含当前的时间。我们之后会更新这个state。

2. React然后调用`Clock`组件的`render()`方法。这是让React知道该把什么显示在屏幕上。React然后更新DOM来匹配`Clock`渲染的输出。

3. 在`Clock`的输出插入到DOM之后，React调用`componentDidMount()`生命周期钩子。在这里，`Clock`组件要求浏览器设置了一个timer，每秒钟调用一次组件的`tick()`方法。

4. 每秒钟浏览器都会调用`tick()`方法。在这个方法里，Click组件通过`setState()`方法来更新UI。多亏了`setState()`方法，React才知道状态改动了，然后它会再次调用render让最新的输出显示出来。这时候，render方法里面的`this.state.date`和之前不一样，因为它反应的是当前时间。所以它会被更新到DOM中。

5. 如果`Clock`组件从DOM中移除，React会调用`componentWillUnmount()`生命周期钩子来移除timer，释放它所占用的资源。

## Using State Correctly

关于`setState()`你需要知道三件事:

### Do Not Modify State Directly

例如，下面这条语句不会重新渲染一个组件：

```javascript
// 错误
this.state.comment = 'Hello';
```

应该使用`setState()`方法：

```javascript
// 正确
this.setState({comment: 'Hello'});
```

唯一你可以赋值`this.state`的地方就是构造器。

### State Updates May be Asynchronous

React可能出于性能原因将多个`setState()`调用合并到一起。

因为`this.props`和`this.state`可能会异步更新，你不应该依赖它们来计算下一个状态。

例如，下面的更新counter代码是错误的：

```javascript
// 错误
this.setState({
    counter: this.state.counter + this.props.increment;
})
```

想要修复这个问题，你需要使用`setState()`的第二种形式(函数重载)，传入一个函数对象而不是传入一个对象。这个函数应该把之前的状态接受作为第一个参数, props作为第二个参数：

```javascript
// 正确
this.setState((prevState, props) => ({
    counter: prevState.counter + props.increment
}));
```

### State Updates are Merged

在你调用`setState()`以后，React将你提供的对象合并到当前的state。

例如，你的state可能包含以下独立变量:

```javascript
constructor(props) {
    super(props);
    this.state = {
        post: [],
        comments: []
    };
}
```

你可以通过单独的`setState()`来分别更新它们:

```javascript
componentDidMount() {
    fetchPosts().then(response => {
        this.setState({
            posts: response.posts
        });
    });

    fetchComments().then(response => {
        this.setState({
            comments:response.comments
        });
    });
}
```

合并是“shallow”形式，所以`this.setState({comments})`不会管`this.state.posts`，而是完全替换`this.state.comments`.

## The Data Flows Down

不管是父组件还是子组件都不知道对方是否有状态，也不要关心对方是函数组件还是类组件。

这是为什么state总是叫做local属性或者封装属性。

一个组件可以选择为子组件传入props：

```javascript
<h2>It is {this.state.date.toLocaleTimeString()}.</h2>
// 子组件
<FormattedDate date={this.state.date} />
// FormattedDate组件会把date作为它的props，不会把它转换为自己的state
function FormattedDate(props) {
  return <h2>It is {props.date.toLocaleTimeString()}.</h2>;
}
```

这种形式通常叫做"自上而下(top-down)"或者"单向(unidirectional)"数据流。很多state总是属于一些特定的组件，很多数据或者衍生的UI只能在这个组件层级之下才能收到影响。

如果你把一个组件树想象为一个props瀑布，每个组件的state就像额外加入的水资源，不过同样只会往下流。

为了展示所有的组件都是隔离的，我们创建了一个`App`组件，它渲染三个`<Clock>`:

```javascript
function App() {
    return (
        <div>
            <Clock />
            <Clock />
            <Clock />
        </div>
    );
}

ReactDOM.render(
    <App />,
    document.getElementById('root')
);
```

每个Clock都会建立它自己的timer，并且独立更新。

在React app里面，一个组件是否有状态决定于组件的实现细节，并且不是一尘不变的。你由在一个有状态的组件中使用无状态的组件，反之亦然。

