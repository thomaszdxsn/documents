# Introducing JSX

请看下面这个变量声明：

```javascript
const element = <h1>Hello, world!</h1>;
```

这个标签语法既不是字符串也不是HTML。

它叫做JSX，是Javascript的语法扩展。我们推荐使用它来描述UI的样子。JSX可能看起来像一个标签语言，但是你能在其中使用Javascript全部的功能。

JSX生成Javascript“element”。

## Why JSX?

React承认渲染逻辑和UI逻辑紧耦合的事实，包括：事件是如何处理的，状态是怎么改变的，以及数据在显示之前是怎么准备的。

预期把标签和逻辑任意的放在不同文件中，React将关注点切入到使用“component”来进行解耦。我们之后会介绍到component，不如如果你不喜欢在JS中放入标签，[这个视频](https://www.youtube.com/watch?v=x7cQ3mrcKaY)会试图说服你这么做。

React并不要求一定要使用JSX，但是大多数人最终都会喜欢这么作。JSX也会让React展示更多有用的错误/警告信息。

## Embedding Expressions in JSX

你可以通过大括号，把任意的Javascript expression放到JSX中。

例如，`2+2`, `user.firstName`，`formatName(user)`都是合法的表达式：

```javascript
function formatName(user) {
    return user.firstName + " " + user.lastName;
}


const user = {
    firstName: 'Harper',
    lastName: 'Perez'
};

const element = (
    <h1>
      Hello, {formatName(user)}!
    </h1>
);

ReactDOM.render(
    element,
    document.getElementById('root')
);
```

## JSX is an Expression Too

在编译之后，JSX表达式会变成常规的Javascript函数，也是一个Javascript对象。

这意味着你可以将JSX放在`if`和`for`循环中，将它赋值给一个变量，将它当作参数传递，函数也可以直接返回它：

```javascript
function getGreeting(user) {
    if (user) {
        return <h1>Hello, {formatName(user)}!</h1>;
    }
    return <h1>Hello, Stranger.</h1>;
}
```

## Specifying Attributes with JSX

你可以使用引号来把一个字符串字面量指定为属性：

```javascript
const element = <div tableIndex="0"></div>
```

也可以使用大括号，让一个表达式作为属性：

```javascript
const element = <img src={user.avatarUrl}></img>;
```

在嵌入表达式作为属性时，不要加入引号。

> 因为JSX更接近与Javascript而不是HTML，React DOM使用**驼峰命名法**作为属性的命名习惯。而不是使用原始的HTML名称。
>
> 比如`class`变为`className`，而`tableindex`变为`tableIndex`.

## Specifying Children with JSX

如果一个标签没有闭合标签，你可以像HTML一样直接使用`/>`：

```javascript
const element = <img src={user.avatarUrl} />;
```

JSX标签可能拥有子标签：

```javascript
const element = (
    <div>
        <h1>Hello!</h1>
        <h2>Good to see you here.</h2>
    </div>
);
```

## JSX Prevents Injection Attacks

可以放心的把用户输入的数据放在JSX中：

```javascript
const title = response.potentialMailiciousInput;
// 不过可以放在JSX中
const element = <h1>{title}</h1>;
```

默认情况下，JSX会在渲染之前把值给转义。在渲染之前任何东西都会被转换为字符串。因此可以预防XSS攻击。

## JSX Represents Objects

Babel使用`React.createElement()`来渲染JSX。

下面两个例子是等同的：

```javascript
const element = (
    <h1 className='greeting'>
        Hello, World!
    </h1>
);
```


```javascript
const element = React.createElement(
    'h1',
    {className: 'greeting'},
    'Hello World'
);
```

`React.createElement()`会执行一些检查，帮助你检查代码中潜在的bug，它本质上会创建一个类似如下的对象：

```javascript
const element = {
    type: 'h1',
    props: {
        className: 'greeting',
        children: 'Hello, world'
    }
};
```

这些对象叫做"React elements"。你可以将它们认为是最终在屏幕中显示的东西。React读取这些变量，用它们来构建DOM，并保持更新。

> 我们推荐你为编辑器加入"Babel语言定义"(http://babeljs.io/docs/editors)插件，它会把ES6和JSX的代码进行高亮处理。