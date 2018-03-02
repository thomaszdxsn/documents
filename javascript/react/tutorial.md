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


### Lifting State Up

pass 