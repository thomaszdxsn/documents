# Tutorial: Intro To React

## Before We Start

### What We're Building

今天，我们要构建一个交互式的tic-tac-toe游戏。

如果你想的话，可以先[点击](https://codepen.io/gaearon/pen/gWWZgR?editors=0010)看看最后应用的样子。如果代码还看不懂，没关系，因为它的语法对你来说还很陌生。我们会通过这个教程一步一步帮助你学会如何创建这个游戏。

在玩游戏的时候。你可以点击按钮来回溯。

一旦你熟悉了这个游戏，可以关闭页面了，我们在下个章节先从一个简单的模版开始。

### Prerequisites

我们假定你已经熟悉HTML和Javascript，不过如果你不熟悉的话也可以继续。

如果你需要复习Javascrit，我们推荐阅读[这篇文章](https://developer.mozilla.org/en-US/docs/Web/JavaScript/A_re-introduction_to_JavaScript)。另外我们会用到ES6的一些特性。在这篇教程中，我们使用[箭头函数](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Functions/Arrow_functions)，[类](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Classes), [let](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/let)和[const](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/const)语句。你可以使用[Babel REPL](https://babeljs.io/repl/#?presets=react&code_lz=MYewdgzgLgBApgGzgWzmWBeGAeAFgRgD4AJRBEAGhgHcQAnBAEwEJsB6AwgbgChRJY_KAEMAlmDh0YWRiGABXVOgB0AczhQAokiVQAQgE8AkowAUAcjogQUcwEpeAJTjDgUACIB5ALLK6aRklTRBQ0KCohMQk6Bx4gA)来检查ES6代码的编译。

### How to Follow Along

有两种方式可以完成这篇教程：你可以在浏览器中完成代码编写，或者可以在你自己的机器建立开发环境。

#### If You Prefer to Write Code in the Browser

这是最简单的方式。

首先，在一个新的标签页中打开[started code](https://codepen.io/gaearon/pen/oWWQNa?editors=0010)。它应该会显示一个空的tic-tac-toe field。

下一章建立本地环境的内容可以跳过了。

#### If You Prefer to Write Code in Your Editor

另外，你可以在你自己的机器上面建立一个项目。

注意：**完成这篇教程并不一定需要自己搭建环境**。

你需要进行如下步骤：

1. 确认你安装了最新的`Node.js`.
2. 创建一个新的react项目

    ```shell
    npm install -g create-react-app
    create-react-app my-app
    ```

3. 删除新项目中`/src`目录下的所有内容(不是删除目录)

    ```shell
    cd my-app
    rm -f src/*
    ```

4. 为`src/`文件夹加入一个文件，叫做`index.css`，复制[这里](https://codepen.io/gaearon/pen/oWWQNa?editors=0100)的内容

5. 为`src/`文件夹加入一个文件，叫做`index.js`，复制[这里](https://codepen.io/gaearon/pen/oWWQNa?editors=0010)的内容

6. 将下面三行代码加入到`src/index.js`的顶部:

    ```javascript
    import React from 'react';
    import ReactDom from 'react-dom';
    import './index.css';
    ```

现在你在项目中运行`npm start`，然后在浏览器中打开`http://localhost:3000`，你可以看到一个空的tic-tac-toe field.

### Help, I'm Stuck!

如果你遇到了问题，可以到[社区](https://reactjs.org/community/support.html)寻求帮助。

## Overview

### What is React?

React是声明式，高效的和富有弹性的Javascript库，用来创建客户端界面。

React拥有各式各样的组件，不过我们先从`React.Component`的子类开始:

```javascript
class ShoppingList extends React.Component {
    render() {
        return (
            <div className='shopping-list'>
                <h1>Shopping List for (this.props.name)</h1>
                <ul>
                    <li>Instagram</li>
                    <li>WhatsApp</li>
                    <li>Oculus</li>
                </ul>
            </div>
        );
    }
}

// 使用方法: <ShoppingList name="Mark" />
```

我们可以看到类XML标签。你的组件告诉React你想要渲染哪些东西 -- 然后React会在你的数据变动的时候更新渲染的内容。

在这里，`ShoppingList`是一个**React component class**，或者叫做**React component type**.components可以接受参数，叫做`props`，并且可以通过`render`方法来返回想要渲染的view。

`render`方法返回**你想要渲染的东西的描述**，然后React接受这个描述并把她渲染在屏幕中。实际上，`render`会返回一个`React element`，它是你想要渲染的东西的一个轻量级描述。多数React开发者使用一种特殊语法(即JSX)来编写这些结构。`<div />`语法会通过`React.createElement('div')`来变形。上面的例子等同于：

```javascript
return React.createElement('div', {className: 'shopping-list'},
    React.createElement('h1', /* ... h1 children ... */),
    React.createElement('ul', /* ... ul children ... */)
);
```

[完整版本](https://babeljs.io/repl/#?presets=react&code_lz=DwEwlgbgBAxgNgQwM5IHIILYFMC8AiJACwHsAHUsAOwHMBaOMJAFzwD4AoKKYQgRlYDKJclWpQAMoyZQAZsQBOUAN6l5ZJADpKmLAF9gAej4cuwAK5wTXbg1YBJSswTV5mQ7c7XgtgOqEETEgAguTuYFamtgDyMBZmSGFWhhYchuAQrADc7EA)

如果你好奇，可以在[API参考](https://reactjs.org/docs/react-api.html#createelement)中看到`createElement()`的描述，但是我们不会在这篇教程直接使用它。我们将会继续使用JSX。

你可以在JSX中放入任何JavaScript表达式。每个React element都是一个Javascript对象，你可以将它存储在一个变量或者传入到你的程序中。

`ShoppingList`组件只渲染内置的DOM组件，你也可以使用自定义的React Component(通过`<ShoppingList />`)。每个组件都是被封装的，所以可以独立操作它，让你可以通过简单的组件构建复杂的UI。

### Getting Started

从这个例子开始：[Starter Code](https://codepen.io/gaearon/pen/oWWQNa?editors=0010).

我们有三个组件：

- Square
- Board
- Game

Square组件渲染一个简单的`<button>`，Board渲染9个squares，Game组件渲染一个board以及一些占位符，我们之后会填充它。暂时组件之间没有交互。

### Passing Data Through Props

让我们尝试从Borad组件传一些数据到Square组件。

在Board的`renderSquare`方法中，修改代码将`value` prop传入到Square:

```javascript
class Board extends React.Component {
    renderSquare(i) {
        return <Square value={i} />
    }
}
```

然后修改Square的`render`方法来渲染传入的value：

```javascript
class Square extends React.Component {
    render() {
        return (
            <button className="square">
                {this.props.value}
            </button>
        )
    }
}
```

### An Interactive Component

让我们让Sqaure组件在点击的时候显示“X”。是这修改button标签:

```javascript
class Square extends React.Component {
    render() {
        return {
            <button className='square' onClick=({} => alert('click'))>
                {this.props.value}
            </button>
        }
    }
}
```

如果你现在点击一个square，你可以看到浏览器发出一个alert。

React组件可以通过在构造器中设置`this.state`来拥有自己的状态，它可以认为是组件的私密属性。让我们把square当前的值存储在状态中，在square被点击的时候修改它。

首先，为Square类增加一个构造器用来初始化状态：

```javascript
class Square extends React.Component {
    constructor (props) {
        super(props);
        this.state = {
            value: null,
        };
    }
    
    render () {
        <button className='sqaure' onClick={() => alert('click')}>
            {this.props.value}
        </button>
    }
}
```

在Javascript class中，在定义子类的构造器时，你需要显式调用`super()`;

现在修改Square的`render`方法，让它显示当前的状态，在点击的时候切换状态：

- 将`<button>`标签中的`this.props.value`替换为`this.state.value`.
- 将事件handler`() => alert()`替换为`() => this.setState({value: 'X'})`

```javascript
class Square extends React.Component {
    constructor (pros) {
        super(props);
        this.state = {
            value: null,
        };
    }

    render() {
        return {
            <button className"square" onClick={() => this.setState({value: 'X'})}>
                {this.state.value}
            </button>
        };
    }
}
```

在调用`this.setState`的时候，会对组件进行更新，让React可以合并传入的状态并重新渲染。在一个组件重新渲染的时候，`this.state.value`将会变为`X`，所以你可以看到`X`.

### Developer Tools

...


## Lifting State Up

现在我们创建了tic-tactic-tac-toe游戏的基础部分。但是，状态还封装在每个Square组件中。想要创建一个成熟的游戏，我们需要检查如果一个玩家赢的时候，将X和O替换。为了检查一个用户胜利，我们需要原地检查9个square的值而不是分开检查每个Square组件。

你可能会认为Board应该可以用来询问每个Square状态的东西。虽然技术上React可以这么做，不过不鼓励这么做，因为这样会让代码很难懂，很难重构。

最佳解决方案是把状态存储在Board中而不是分别存储在每个Square中 -- Board组件会告诉每个Square应该显示什么。

**在你想要聚集多个子组件的数据，或者想要让两个组件互相通讯，状态的变动可以存储在父组件中。父组件可以通过props把状态传回给子组件，所以子组件总是和父组件保持同步**

在重构React组件的时候很常见的情况就是推送状态的改动，让我们借这个机会来一窥究竟。为Board加入一个构造器，设置一个初始的state，一个包含9个null的数组，对应9个squares：

```javascript
class Board extends React.Component {
    constructor (props) {
        super(props);
        this.state = {
            squares: Array(9).fill(null),
        };
    }

    renderSquare(i) {
        return <Square value={i} />
    }

    render() {
        const status = 'Next player: X';

        return (
        <div>
            <div className="status">{status}</div>
            <div className="board-row">
            {this.renderSquare(0)}
            {this.renderSquare(1)}
            {this.renderSquare(2)}
            </div>
            <div className="board-row">
            {this.renderSquare(3)}
            {this.renderSquare(4)}
            {this.renderSquare(5)}
            </div>
            <div className="board-row">
            {this.renderSquare(6)}
            {this.renderSquare(7)}
            {this.renderSquare(8)}
            </div>
        </div>
        );
    }
}
```

我们会在之后填充，让board看起来像这样:

```javascript
[
    'O', null, 'X',
    'X', 'X', 'O',
    'O', null, null
]
```

Board的`renderSquare`方法现在看起来像这样:

```javascript
renderSquare(i) {
    return <Square value={i} />;
}
```

让我们修改它，把一个`value`prop传入到Square:

```javascript
renderSquare(i) {
    return <Square value={this.state.squares[i]} />;
}
```

现在我们想要修改sqaure点击后发生的事情。Board组件现在存储填充的square，意味着我们需要某种方式让Square的状态更新通知到Board。由于组件的状态是隐私的，我们不能直接更新状态给Board。

最常见的一种模式就是从Board传入一个函数给Square，在点击的时候触发这个函数。让我们再次修改Board的`renderSquare`:

```javascript
renderSquare(i) {
    return (
        <Sqaure
         value={this.state.squares[i]}
         onClick={() => this.handleClick(i)} 
        />
    );
}
```

出于利于阅读的因素，我们将返回的元素拆分成多行，并且加入括号让Javascript不会为return语句自动加入分号。

现在我们从Board传入两个参数到Square：`value`和`onClick`。后者是一个Square可以调用的函数。让我们对Square作下列的一些改动：

- 在Square的`render`方法中，替换`this.state.value`为`this.props.value`.
- 在Square的`render`方法中，替换`this.setState()`为`this.props.onClick()`.
- 删除Square的constructor，因为它不在有属于自己的状态了.

在这些改动之后，Square看起来像这样:

```javascript
class Square extends React.Component {
    render() {
        return (
            <button className='square' onClick={() => this.props.onClick()}>
                {this.props.value}
            </button>
        );
    }
}
```

现在square点击的时候，会调用Board传入的onClick函数：

1. 内置DOM`button`组件的`onClick`属性告诉React建立一个点击事件监听
2. 在这个button被点击的时候，React将会调用Sqaure`render()`方法定义的`onClick`事件handler。
3. 这个事件handler会调用`this.props.onClick()`属性，Square的属性由Board指定
4. Board将`onClick={() => this.handleClick(i)}`传入给Square，所以在调用的时候会在Board上面运行`this.handleClick(i)`
5. 我们暂时还没有定义`handleClick()`方法，所以程序还不能正常运行。

注意DOM`<button>`元素的`onClick`属性对于React有特殊意义，我们也可以叫做其它名称。但是React app的惯例是使用`on*`来命名属性，使用`handle*`来命名handler方法。

试着点击square，你会碰到网页报错。因为我们还没有定义`handleClick`:

```javascript
class Board extends React.Component {
    constructor (props) {
        super(props);
        this.state = {
            squares: Array(9).fill(null),
        };
    }

    handleClick(i) {
        return (
            <Square
              value={this.state.squares[i]}
              onClick={() => this.handleClick(i)}
            />
        );
    }

    render() {
        const status = 'Next player: X';

        return (
        <div>
            <div className="status">{status}</div>
            <div className="board-row">
            {this.renderSquare(0)}
            {this.renderSquare(1)}
            {this.renderSquare(2)}
            </div>
            <div className="board-row">
            {this.renderSquare(3)}
            {this.renderSquare(4)}
            {this.renderSquare(5)}
            </div>
            <div className="board-row">
            {this.renderSquare(6)}
            {this.renderSquare(7)}
            {this.renderSquare(8)}
            </div>
        </div>
        );
    }
}
```

我们调用`.slice()`方法来获得`squares`数组的一份拷贝，而不是修改现有的数组。

现在你可以正常点击square了，不过状态现在是存储在Board，而不是分别存储在每个Square中，这样我们的游戏才能继续创建下去。注意无论何时Board的状态发生了变化，Square组件都会自动重新渲染。

Square不再需要保持它自己的状态；它会从它的父组件Board中接受值，并且会在被点击时通知Board。我们把这种组件叫做被控制组件(`controlled components`).

### Why Immutability Is Important

在前面的示例代码中，我们建议使用`.slice()`来拷贝一份squares数组，而不是直接修改现存的数组。让我们来解释一下为什么要这么做。

一般有两种方式来修改数据。第一种方法是通过直接修改一个变量的值来改变数据。第二种方法是将数据拷贝，修改，然后重新赋值。

#### Data change with mutation

```javascript
var player = {score: 1, name: 'Jeff'};
player.scode = 2;
// {score: 2, name: 'Jeff'}
```

#### Data change without mutation

```javascript
var player = {score: 1, name: 'Jeff'}

var newPlayer = Object.assign({}, player, {score: 2})
// player没有改变，而newPlayer是{score: 2, name: 'Jeff'}

// 或者你可以使用对象spread语法
var newPlayer = {...player, score: 2}
```

后面一种方法的结果是一样的，不过不会直接修改数据。我们会从后者获得更高的性能优势。

#### Easier Undo/Redo and Time Travel

不可变类型让复杂的特性更容易实现。例如，在这个教程的后面部分我们将要实现在游戏步骤的回溯。避免直接对数据的改动，可以让我们持有一份旧数据的引用，在需要的时候可以切换回去。

#### Tracking Changes

确定一个可变对象是否改变了是很复杂的，因为可以直接对对象进行改动。这就需要你将当前的对象和之前的对象进行对比，遍历整个对象tree，比较每个变量和值。这个过程会变得及其复杂。

而确定一个不可变对象是否改变则简单得多。如果一个对象的引用和之前不同，那么这个对象就改动了。

#### Determining When to Re-render in React

React中使用不可变类型的最大优势在于可以让你创建纯组件(pure components)。因为不可变数据在改动的时候可以更容易发现，它同样可以帮助React提高自动重新渲染的性能。

### Functional Components

我们移除了Square中的constructor，事实上，React对于这种只实现了`render`方法的组件，可以使用一种更加简单的语法，叫做`functional components`。不需要继承`React.Component`了，只需要编写一个函数，接受props并返回想要渲染的东西就好了。

让我们把Square类替换成函数:

```javascript
function Square(props) {
    return (
        <button className='square' onClick={props.onClick}>
            {props.value}
        </button>
    )
}
```

你需要把所有的`this.props`改为`props`.你的App中的很多组件都可以重写成functional components：这种组件需要写的代码更少，React可以更容易地优化它们。

在我们重写代码的时候，把`onClick={() => props.onClick()}`改写为`onClick={props.onClick}`.注意不能传入`onClick={props.onClick()}`，这会让函数立即被调用。

### Taking Turns

我们的游戏现在只能X一个人玩，让我们帮他加入一个玩伴。

让我们把`X`设定为先手。修改Board组件的初始状态：

```javascript
class Board extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            squares: Array(9).fill(null),
            xIsNext: true,
        };
    }

    ...
}
```

每次点击的时候我们都应该切换xIsNext的状态：

```javascript
handleClick(i) {
    const squares = this.state.squares.slice();
    squares[i] = this.state.xIsNext ? 'X' : 'O';
    this.setState({
        sqaures: sqaures,
        xIsNext: !this.state.xIsNext,
    });
} 
```

现在X和O发生了轮换，可以修改Board`render`方法中的status文本，来显示下一步使用哪个标记：

```javascript
render() {
    const.status = 'Next player: ' + (this.state.xIsNext ? 'X': 'O');

    return (...)
}
```

### Declaring a Winner

让我们来确定哪个玩家胜利。在文件末尾加入一个helper函数：

```javascript
function calculateWinner(squares) {
    const lines = [
        [0, 1, 2],
        [3, 4, 5],
        [6, 7, 8],
        [0, 3, 6],
        [1, 4, 7],
        [2, 5, 8],
        [0, 4, 8],
        [2, 4, 6]
    ];
    for (let i = 0; i< lines.length; i++) {
        const [a, b, c] = lines[i];
        if (squares[a] && squares[a] === squares[b] && squares[a] === squares[c]) {
            return squares[a];
        }
    }
    return null;
}
```

你可以在Board的`render`函数中调用它来检查是否出现了胜利者，如果出现赢家则在status文本中显示“Winner: [X/O]”.

```javascript
render() {
    const winnder = calculateWinnder(this.state.squares);
    let status;
    if (winnder) {
        status = 'Winnder: ' + winnder;
    } else {
        status = 'Next Player: ' + (this.state.xIsNext ? 'X': 'O')
    }

    return ...
}
```

你可以修改一下`handleClick`方法，让它在分出胜利者的情况下再被点击无效果：

```javascript
handleClick(i) {
    const squares = this.state.squares.slice();
    if (calculateWinner(squares) || squares[i]) {
        return;
    }
    squares[i] = this.state.xIsNext ? 'X': 'O';
    this.setState({
        squares: squares,
        xIsNext: !this.state.xIsNext
    });
}
```

恭喜，你的tic-tac-toe游戏完成了！

## Storing a History

让这个游戏可以检查board以前的状态。我们已经在每次移动的时候创建了一个新的`squares`数组，意味着我们可以同时存储之前board的状态。

最后存储的数据结构大致如下：

```javascript
history = [
  {
    squares: [
      null, null, null,
      null, null, null,
      null, null, null,
    ]
  },
  {
    squares: [
      null, null, null,
      null, 'X', null,
      null, null, null,
    ]
  },
  // ...
]
```

我们想要Game组件作为最上层的组件，让它负责显示移动的步骤。就像我们把Square的状态移到Board中一样，让我们再次把Board状态移到Game中 -- 所以我们可以在顶层获得所有信息。

首先我们为Game的构造器增加一些初始状态：

```javascript
class Game extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            history: [{
                squares: Array(9).fill(null)
            }],
            xIsNext: true;
        };
    }

    render() {
        return (
            <div className="game">
              <div className="game-board">
                <Board />
              </div>
              <div className="game-info">
                <div>{/* status */</div>
                <ol>{/* TODO */}</ol>
              </div>
            </div>
        );
    }
}
```

然后修改Board，让它可以通过props获得`squares`，并且获得Game指定的onClick，就像我们之前对Square进行的变形一样。你可以将每个square的位置穿给click handler，所以我们仍然知道哪个square被点击了。你需要依次作下面这些事情：

- 删除Board中的`constructor`
- 将Board的`renderSquare`方法中的`this.state.squares[i]`替换为`this.props.squares[i]`
- 将Board的`renderSquare`方法中的`this.handlerClick(i)`替换为`this.props.onClick(i)`


Game的`render()`方法应该可以显示最近历史：

```javascript
render() {
    const history = this.state.history;
    const current = history[history.length - 1]; // last
    const winner = calculateWinner(current.squares);

    let status;
    if (winner) {
        status = 'Winner: ' + winner;
    } else {
        status = 'Next player: ' + (this.state.xIsNext ? 'X' : 'O')
    }

    return render(
        <div className="game">
          <div className="game-board">
            <Board
              squares={current.squares}
              onClick={(i) => this.handleClick(i)}
            />
          </div>

          <div className='game-info'>
            <div>{status}</div>
            <ol>{/* TODO */}</ol>
          </div>
        </div>
    );
}
```

因为现在由Game来负责渲染status，我们可以删除Board的`render`方法中的`<div className="status">{status}</div>`代码：

```javascript
  render() {
    return (
      <div>
        <div className="board-row">
          {this.renderSquare(0)}
          {this.renderSquare(1)}
          {this.renderSquare(2)}
        </div>
        <div className="board-row">
          {this.renderSquare(3)}
          {this.renderSquare(4)}
          {this.renderSquare(5)}
        </div>
        <div className="board-row">
          {this.renderSquare(6)}
          {this.renderSquare(7)}
          {this.renderSquare(8)}
        </div>
      </div>
    );
  }
```

接下来，我们需要把Board中的`handleClick`方法移到Game中。你也将它直接剪切到Game中。

不过我们需要稍微修改一下它，因为Game的state结构稍有不同。Game的`handleClick`可以将一个新的entry推送到栈中。

```javascript
handleClick(i) {
    const history = this.state.history;
    const current = history[history.length - 1];
    const squares = current.squares.slice();
    if (calculateWinner(squares) || squares[i]) {
        return
    }
    squares[i] = this.state.xIsNext ? 'X' : 'O';
    this.setState({
        history: history.concat([{
            squares: squares,
        }]),
        xIsNet: !this.state.xIsNext,
    })
}
```

### Showing the Moves

让我们显示游戏的动作。我们之前学到了React元素是JS的第一类对象，我们可以将它存储或者传递。想要在React渲染多个items，我们可以传入一个React元素的数组。让我们来修改Game的`render`方法：

```javascript
render() {
    const history = this.state.history;
    const current = history[history.length - 1];
    const winner = calculateWinner(current.squares);
    
    const moves = history.map((step, move) => {
        const desc = move ?  // move代表索引，如果为0代表没有history
        'Go to move #' + move :
        'Go to game start';
      return (
          <li>
            <button onClick={() => this.jumpTo(move)}>{desc}</button>
          </li>
      );
    });

    let status;
    if (winner) {
        status = 'Winner: ' + winner;
    } else {
        status = 'Next player: ' + (this.state.xIsNext ? 'X': 'O');
    }

    return (
        <div className='game'>
          <div className='game-board'>
            <Board
              squares={current.squares}
              onClick={(i) => this.handleClick(i)}
            />
          </div>
        <div className='game-info'>
          <div>{status}</div>
          <ol>{moves}</ol>
        </div>
    );
}
```

对于history中的每一个步骤，我们都会创建一个`<li>`标签，以及一个`<button>`包含一个click handler。

### Keys

在你渲染一个item list的时候，React总是会为每个item存储一些信息。如果你渲染一个拥有state的组件，那么这个state需要被存储 - 不管你如何实现你的组件，React会存储一份引用.

当你更新list的时候，React需要确定哪些东西改动了。你不能对list增/删/更新...

想象你要把下面这个list:

```javascript
<li>Alexa: 7 tasks left</li>
<li>Ben: 5 tasks left</li>
```

转变为：

```javascript
<li>Ben: 9 tasks left</li>
<li>Claudia: 8 tasks left</li>
<li>Alex: 5 tasks left</li>
```

人的肉眼来看，像是Alex和Ben换了位置，并且加入了Claudia -- 不过React只是一个电脑程序，并不知道你想要干什么。作为结果，React会要求你为list中每个元素指定一个key property，这个key必须相对它的兄弟元素是唯一的。在这个例子中，`alexa`，`ben`，`claudia`可以作为key；如果元素和数据库对象相符，那么使用数据库ID是一个好主意：

```javascript
<li key={user.id}>{user.name}: {user.taskCount} tasks left</li>
```

`key`是一个特殊的property，因该留给React(另外还有`ref`，一个高级特性)。在一个元素创建后，React拉取了`key`property并将它存储在返回的元素上。虽然它看起来像props的一部分，但是不能用`this.props.key`来访问。React使用这个key来决定哪个元素已经更新；一个组件没有办法知道它自己的key。

在一个list被重新渲染后，React接受每个元素的新版本，然后查找之前list是否存在这个key。在一个key加入到集合后，会创建一个组件；在一个key被移除后，将会销毁这个组件。Keys可以让React知道每个组件的标示，所以可以在重新渲染时可以维护状态。如果你修改一个组件的key，这个组件会被销毁并重新创建一个新的组件。

**无论何时你要创建一个动态list，都强烈推荐你赋值一个合适的key**。如果你手头没有合适的key，你可能需要考虑重构一下数据结构(意思就是数据结构不太合理)。

如果你不指定任何key，React会警告你，然后使用数组的索引作为key。

组件的key并不要求全局唯一，只要相对于它的兄弟组件是唯一的就可以了。

### Implementing Time Travel

对于我们的move list，我们已经对每个步骤都有一个唯一ID：即move发生的顺序。在Game的`render`方法中，加入`<li key='{move}'>`可以消除警告：

```javascript
const moves = history.map((step, move) => {
    const desc = move ? 
        'Go to move #' + move : 
        'Go to game start';
    return (
        <li key={move}>
          <button onClick={() => this.jumpTo(move)}>{desc}</button>
        </li>
    )
})
```

现在点击move按钮仍然会报错，因为`jumpTo`还没有被定义。让我们为Game的state加入一个新的key，代表我们当前处于哪个step。


首先，将`stempNumber: 0`加入到Game的`constructor`:

```javascript
class Game extends React.component {
    constructor (props) {
        super(props);
        this.state = {
            history: [{
                squares: Array(9).fill(null);
            }],
            stempNumber: 0,
            xIsNext: true
        };
    }
}
```

然后，我们为Game加入`jumpTo`方法来更新状态。我们同样想要更新`xIsNext`.如果索引移动到了一个偶数，我们会把`xIsNext`设为true。

为Game class加入一个方法，`jumpTo`:

```javascript
handleClick(i) {
    // 这个方法没有变化
}

jumpTo(step) {
    this.setState({
        stepNumber: step,
        xIsNext: (step % 2) === 0
    });
}

render() {
    // 这个方法也没有变化
}
```

在创建一个新的move的时候，更新`stepNumber`: 

```javascript
handleClick(i) {
    const history = this.state.history.slice(0, this.state.stepNumber + 1); // 截取history
    const current = history[history.length - 1];
    const squares = current.squares.slice();
    if (calculateWinner(squares) || square[i]) {
        return;
    }

    squares[i] = this.state.xIsNext ? 'X' : 'O';
    this.setState({
        history: history.concat([{
            squares: squares
        }]),
        stepNumber: history.length,
        xIsNext: !this.state.xIsNext
    }); 
}
```

### Wrapping Up

你成功创建了一个tic-tac-toe游戏:

- 让你可以玩tic-tac-toe
- 可以指出哪个玩家是胜利者
- 可以存储储游戏移动的历史记录
- 允许玩家跳到某一个步骤

如果你想要继续练习，可以考虑实现以下的功能：

1. 在move history list中显示每次移动的位置
2. 为move list中当前的步骤加粗
3. 重写Board，用两个循环来创建squares，而不是硬编码
4. 加入一个toggle按钮，允许你将moving list进行重新排序(升/降序)
5. 在某人赢的时候，高亮获胜的三个棋子
