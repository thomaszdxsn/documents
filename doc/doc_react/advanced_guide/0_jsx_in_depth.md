# JSX In Depth

**基本上，JSX只是`React.createElement(...)`函数的语法糖。**

```javascript
<MyButton color='blue' shadowSize={2}>
    Click me
</MyButton>
```

上面的JSX将会被编译为:

```javascript
React.createElement(
    MyButton,
    {color: 'blue', shadowSize: 2},
    'Click Me'
)
```

如果一个元素没有子元素，可以直接使用闭合标签:

```javascript
<div className='sidebar' />
```

将会被编译为:

```javascript
React.createElement(
    'div',
    {className: 'sidebar'},
    null
)
```

## Specifying The React Element Type

pass