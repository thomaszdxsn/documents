# Components and Props

**Components可以让你把UI拆分为独立的，可重用的部分，让你可以单独的思考各个部分的代码**.

概念上来说，组件(components)很像Javascript的函数。它可以接受任意数量的输入(叫做`props`)然后返回一个React element。

## Functional and Class Components

定义Component最简单的方式是写一个Javascript函数：

```javascript
function Welcome(props) {
    return <h1>Hello, {props.name}</h1>;
}
```

这个函数是一个合法的React component，因为它只接受一个“props”作为参数并且返回一个React element。我们把这种component叫做"functional component"。

也可以使用ES6的class来定义一个component：

```javascript
class Welcome extends React.Component {
    render() {
        return <h1>Hello, {this.props.name}</h1>;
    }
}
```

上面两个component，从React角度上来看是等同的。

## Rendering a Component

在之前，我们只遇到代表DOM标签的React elements，比如

```javascript
const element = <div />;
```

不过，elements也可以代表用户定义的components：

```javascript
const element = <Welcome name='Sara' />;
```

在element代表用户定义的components的时候，它的JSX属性会以一个对象的形式传入这个component。我们把这个对象叫做`props`.

例如，下面这段代码会在页面中渲染"Hello Sara":

```javascript
function Welcome(props) {
    return <h1>Hello, {props.name}</h1>
}

const element = <Welcome name='Sara' />;
ReactDOM.render(
    element,
    document.getElementById('root')
);
```

让我们总结一下发生了什么：

1. 我们调用`ReactDOM.render()`并传入`<Welcome name='Sara' />`.
2. React以`{name: 'Sara'}`调用Welcome组件.
3. 我们的Welcome组件返回`<h1>Hello, Sara</h1>`作为结果.
4. React DOM快速更新DOM来匹配`<h1>Hello, Sara</h1>`.

> 注意
>
> Component名称应该遵循首字母大写的形式。
>
> React会把小写形式的component看作是DOM标签，比如`<div />`代表HTML div标签，不过`<Welcome />`会代表一个组件，并要求可见域中要可以获取`Welcome`。

## Composing Components

Components可以让其它components作为它的输出。这可以让我们进行复杂的抽象。

例如，我们可以创建一个`App`组件，让它渲染`Welcome`多次:

```javascript
function Welcome(props) {
    return <h1>Heloo, (props.name)</h1>;
}


function App() {
    return (
        <div>
            <Welcome name='Sara' />
            <Welcome name='Cahal' />
            <Welcome name='Edite' />
        </div>
    );
}


ReactDOM.render(
    <App />,
    document.getElementById('root')
);
```

## Extracting Components

不要害怕把一个组件切分成更小的组件。

例如，考虑下面这个Comment组件：

```javascript
function Comment(props) {
    return (
        <div className='Comment'>
          <div className='UserInfo'>
            <img className='Avatar'
              src={props.author.avatar.Url}
              alt={props.author.name}
            />
            <div className='UserInfo-name'>
                {props.author.name}
            </div>
          </div>
          <div className='Comment-text'>
            {props.text}
          </div>
          <div className='Comment-date'>
            {formartDate(props.date)}
          </div>
        </div>
    );
}
```

它的`props`中包括`author`, `text`和`date`，描述了一个社交网站的一条评论。

这个组件看起来很复杂因为嵌套太多。让我们从它当中提取出其它的组件。

首先，我们提取出`Avatar`:

```javascript
function Avatar(props) {
    return (
        <img className='Avatar'
          src={props.user.avatarUrl}
          alt={props.user.name}
        />
    );
}
```

`Avatar`不需要知道是否要在`Comment`里面被渲染。这是为什么我们把属性叫做`user`而不是`author`，前者更加通用。

我们推荐prop的命名采用component自身的视角，而不是采用实际使用上下文的语境。

然后，我们把`Comment`稍微简化了一些：

```javascript
function Comment(props) {
    return (
        <div className='Comment'>
          <div className='UserInfo'>
            <Avatar user={props.author} />
            <div  className='UserInfo-name'>
              {props.author.name}
            </div>
          </div>
          <div className='Comment-text'>
            {props.text}
          </div>
          <div className='Comment-date'>
            {formatDate(props.date)}
          </div>
        </div>  
    );
}
```

然后，我们提取出`UserInfo`组件：

```javascript
function UserInfo(props) {
    return (
        <div className='UserInfo'>
          <Avatar user={props.user}>
          <div className='UserInfo-name'>
            {props.user.name}
          </div>
        </div>
    );
}
```

让我们进一步简化`Comment`:

```javascript
function Comment(props) {
    return (
        <div className='Comment'>
            <UserInfo user={props.author} />
            <div className='Comment-text'>
              {props.text}
            </div>
            <div className='Comment-date'>
              {formatDate(props.date)}
            </div>
        </div>
    );
} 
```

## Props are Read-Only

无论你是通过函数还是类来声明一个component，都必须不更改它的props。考虑一下下面的`sum`函数:

```javascript
function sum(a, b) {
    return a + b;
}
```

这种函数叫做“纯函数”，因为它没有修改输入的参数，同样的输入总是会返回同样的结果。

相反，下面这个函数就“不够纯”，因为它修改了输入的参数:

```javascript
function withdraw(account, amount) {
    account.total -= amount;
}
```

React是相当弹性的，不过它有一条严格的规则:

**所有的React component必须相对于它的props为一个纯函数形式。**

当然，应用UI是动态的，并且总是发生改动。在下一章节，我们会介绍一个新概念:"状态"("state").状态允许React component修改它们的输出而不违反上面的规则。

