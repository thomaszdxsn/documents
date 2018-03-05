# Lists and Keys

给定如下的代码，我们使用`map()`函数接受一个number数组，然后将每个number翻倍。我们把`map()`返回的新的数组赋值给变量`doubled`然后打印它:

```javascript
const numbers = [1, 2, 3, 4, 5];
const doubled = numbers.map((number) => number * 2);
console.log(doubled);
```

这段代码将会在控制台打印`[2, 4, 6, 8, 10]`.

在React中，将数组变形为element list几乎是一样的。

## Rendering Multiple Components

你可以构件一个元素集合，然后使用大括号来将它们包含在JSX中。

下面代码中，我们使用JS的`map()`函数来迭代`numbers`数组。每个item我们都返回一个`<li>`元素。最终，我们把这个元素数组赋值给`listItems`:

```javascript
const numbers = [1, 2, 3, 4, 5];
const listItems = numbers.map((number) => 
    <li>{number}</li>
);
```

我们把整个`listItems`数组放到一个`<ul>`元素中，将它渲染在DOM中：

```javascript
ReactDOM.render(
    <ul>{listItems}</ul>,
    document.getElementById('root')
);
```

## Basic List Component

通常你想要在一个组件中渲染一个list。

我们可以重构上面的例子，让它变为一个组件并接受一个数组作为参数，返回`<ul>`元素.

```javascript
function NumberList(props) {
    const numbers = props.numbers;
    const listItems = numbers.map((number) => 
        <li>{number}</li>
    );
    return (
        <ul>{listItems}</ul>
    );
}


const numbers = [1, 2, 3, 4, 5];
ReactDOM.render(
    <NumberList numbers={numbers} />,
    document.getElementById('root')
);
```

在你运行这段代码的时候，应该会看到警告，要求你为list中每个item提供一个key。`key`是一个特殊的字符串属性，在创建元素list的时候每个元素都应该包含一个key。我们将在下章讨论为什么key很重要。

让我们为每个item加入一个key：

```javascript
function NumberList(props) {
    const numbers = props.numbers;
    const listItems = numbers.map((number) => 
        <li key={number.toString()}>
            {number}
        </li>
    );

    return (
        <ul>{listItems}</ul>
    );
}

const numbers = [1, 2, 3, 4, 5];
ReactDOM.render(
  <NumberList numbers={numbers} />,
  document.getElementById('root')
);
```

## Keys

Keys可以帮助React识别哪个item发生了变动，以及item的加入和移除情况。给定元素的key应该是一个稳定的标示：

```javascript
const numbers = [1, 2, 3, 4, 5];
const listItems = numbers.map((number) => 
    <li key={number.toString()}>
        {number}
    </li>
);
```

挑选key最好的方式是选择一个相对于兄弟元素唯一的字符串标示。通常使用你数据的ID作为key：

```javascript
const todoItems = todos.map((todo) => 
    <li key={todo.id}>
        {todo.text}
    </li>
);
```

当你要渲染的item没有稳定ID时，最后的一种方式是使用item的索引作为key:

```javascript
const todoItems = todos.map((todo, index) => 
    <li key={index}>
        {todo.text}
    </li>
);
```

如果item的顺序会更改，我们不推荐使用索引作为key。

## Extracting Components with Keys

Key只有在涉及数组的情况下有意义。

例如，如果你提取出一个`ListItem`组件，你应该在`<ListItem />`的数组中保持key，而不是由`ListItem`的每一个`<li>`来保持key.

### Example: Incorrect Key Usage

```javascript
function ListItem(props) {
    const value = props.value;
    return (
        // 错误，不需要在这里指定key
        <li key={value.toString()}>
            {value}
        </li>
    );
}


function NumberList(props) {
    const numbers = props.numbers;
    const listItems = numbers.map((number) => 
    // 错误！Key应该在这里指定
    <ListItem value={number} />
    );

    return (
        <ul>
            {listItems}
        </ul>
    );
}


const numbers = [1, 2, 3, 4, 5];
ReactDOM.render(
    <NumberList numbers={numbers} />,
    document.getElementById('root')
);
```

### Example: Correct Key Usage

```javascript
function ListItem(props) {
    // 正确！这里不需要指定key
    return <li>{props.value}</li>
} 


function NumberList(props) {
    const numbers = props.numbers;
    const listItems = numbers.map((number) =>
    
    // 正确!Key应该指定在Array里面
    <ListItem key={number.toString()}
              value={number} />
    );

    return (
        <ul>
            {listItems}
        </ul>
    );
}


const numbers = [1, 2, 3, 4, 5];
ReactDOM.render(
  <NumberList numbers={numbers} />,
  document.getElementById('root')
);
```

## Keys Must Only Be Unique Among Siblings

数组使用key必须和兄弟节点保持唯一.不过不需要是全局唯一。在两个数组间可以存在相同的key：

```javascript
function Blog(props) {
    const sidebar = (
        <ul>
            {props.posts.map((post) => 
                <li key={post.id}>
                    {post.title}
                </li>
            )}
        </ul>
    );
    const content = props.posts.map((post) =>
        <div key={post.id}>
            <h3>{post.title}</h3>
            <p>{post.content}</p>
        </div>
    );
    return (
        <div>
            {sidebar}
            <hr />
            {content}
        </div>
    );
}


const posts = [
  {id: 1, title: 'Hello World', content: 'Welcome to learning React!'},
  {id: 2, title: 'Installation', content: 'You can install React from npm.'}
];
ReactDOM.render(
  <Blog posts={posts} />,
  document.getElementById('root')
);
```

Key是作为React提示而存在的，但是不需要将它传给你的组件。如果你的组件中需要同样的值，使用另一个名称传给props:

```javascript
const content = posts.map((post) => 
    <Post
        key={post.id}
        id={post.id}
        title={post.title}
    />
);
```

上面的例子中，`Post`组件可以读取`props.id`，但是读不到`props.key`.

## Embedding map() in JSX

在上面的例子中我们声明了一个独立的`listItems`变量并让它包含在JSX中：

```javascript
function NumberList(props) {
    const numbers = props.numbers;
    const listItems = numbers.map((number) =>
        <ListItem key={number.toString()}
                  value={number} />
    );
    return (
        <ul>
            {listItems}
        </ul>
    );
}
```

JSX允许在大括号中嵌入任何的表达式，所以我们可以插入`map()`的结果:

```javascript
function NumberList(props) {
    const numbers = props.numbers;
    return (
        <ul>
            {numbers.map((number) =>
                <ListItem key={number.toString()}
                          value={number} />
            )}
        </ul>
    );
}
```

记住，如果`map()`嵌套太深，最好还是单独分离出一个组件。

