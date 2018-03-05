# Forms

React中HTML表单元素和其它DOM元素有些不同，因为表单元素原生保持内部状态。例如，下面这个普通的HTML表单接受一个name:

```javascript
<form>
    <label>
      Name:
      <input type='text' name='name' />
    </label>
    <input type="submit" value="Submit" />
</form>
```

这个表单可以用。但是大多数情况下，需要用一个JS函数来处理表单的提交，检查用户输入的数据。React处理这些情况的技术叫做"被控制组件(controlled components)".

## Controlled Components

在HTML中，表单元素如`<input>`, `<textarea>`和`<select>`都会维持它自己的状态，并且在用户输入的时候会更新。在React中， 可变的状态一般由组件的state属性维持，并且只可以使用`setState()`进行更新。

我们可以组合这两种方式，让React的state变为"single source of truth".然后React组件渲染一个表单并控制用户输入后发生什么事情。

例如，如果我们想让上面例子在表单提交的时候将name打印出来，我们可以把form写成被控制组件:

```javascript
class NameForm extends React.Component {
    constructor(props) {
        super(props);
        this.state = {value: ''};

        this.handleChange = this.handleChange.bind(this);
        this.handleSubmit = this.handleSubmit.bind(this);
    }

    handleChange() {
        this.setState({value: event.target.value})
    }

    handleSubmit() {
        alert('A name was submitted: ' + this.state.value);
        event.preventDefault();
    }

    render() {
        return (
            <form onSubmit={this.handleSubmit}>
                <label>
                    Name:
                    <input type='text' value={this.state.value}
                           onChange={this.handleChange}>
                </label>
                <input type='submit' value='Submit' />
            </form>
        );
    }
}
```

由于为我们的表单元素设置了`value`属性，显示的value总是是`this.state.value`，making the React state the source of truth。因为`handleChange`在每次按下键盘的时候都会触发，所以显示的值也会根据用户的输入而更新。

对于一个被控制组件，每个状态变化都会有一个关联的handler函数。这可以让你直接修改和验证用户的输入。例如，如果我们想让name以全大写格式写，我们可以这样写`handleChange`:

```javascript
handleChange(event) {
    this.setState({value: event.target.value.toUpperCase()});
}
```

## The textarea Tag

在HTML中，`<textarea>`元素把文本定义为它的子节点：

```javascript
<textarea>
  Hello there, this is some text in a text area
</textarea>
```

在React中，`<textarea>`使用`<value>`属性来存储文本：

```javascript
class EssayForm extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            value: 'Please write an essay about your favorite DOM element.'
        };

        this.handleChange = this.handleChange.bind(this);
        this.handleSubmit = this.handleSubmit.bind(this);
    }

    handleChange(event) {
        this.setState({value: event.target.value});
    }

    handleSubmit(event) {
        alert('An essay was submitted: ' + this.state.value);
        event.preventDefault();
    }

    render() {
        return (
            <form onSubmit={this.handleSubmit}>
                <label>
                    Essay:
                    <textarea value={this.state.value} onChange={this.handleChange} />
                </label>
                <input type='submit' value='Submit'>
            </form>
        );
    }
}
```

## The select Tag

在HTML中，`<select>`创建一个下拉列表。例如，下面这个HTML创建一个关于花的下拉列表：

```javascript
<select>
    <option value='grapefruit'>Grapefruit</option>
    <option value='lime'>Lime</option>
    <option selected value='coconut'>Coconut</option>
    <option value='mango'>Mango</option>
</select>
```

注意Coconut选项是默认选中的，因为`selected`属性。React不实用`selected`属性，而是对根节点指定`value`属性：

```javascript
class FlavorForm extends React.Component {
    constructor(props) {
        super(props);
        this.state = {value: 'coconut'};

        this.handleChange = this.handleChange.bind(this);
        this.handleSubmit = this.handleSubmit.bind(this);
    }

    handleChange(event) {
        this.setState({value: event.target.value});
    }

    handleSubmit(event) {
        alert('Your favorite flavor is: ' + this.state.value);
        event.preventDefault();
    }

    render() {
        return (
            <form onSubmit={this.handleSubmit}>
                <label>
                    Pick your favorite La Croix flavor:
                    <select value={this.state.value} onChange={this.handleChange}>
                        <option value="grapefruit">Grapefruit</option>
                        <option value="lime">Lime</option>
                        <option value="coconut">Coconut</option>
                        <option value="mango">Mango</option>
                    </select>
                </label>
                <input type='submit' value='Submit'>   
            </form>
        );
    }
}
```

> 注意，你可以为`value`熟悉传入一个数组，允许你在`select`标签中选多个选项:
>
> `<select multiple={true} value={['B', 'C']}>`

## The file input Tag

在HTML中，`<input type='file'>`允许用户从自己的设备选择一个或多个文件上传到服务器：

```javascript
<input type='file' />
```

因为它的value是只读的，它在React中是uncontrolled component.

## Handing Multiple Inputs

当你需要处理多个被控制的`input`元素，你可以为每个元素加入一个`name`属性，让handler可以根据`event.target.name`来选择：

```javascript
class Reservation extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            isGoing: true,
            numberOfGuests: 2
        };

        this.handleInputChange = this.handleInputChange.bind(this);
    }

    handleInputChange(event) {
        const target = event.target;
        const value = target.type === 'checkbox' ? target.checked : target.value;
        const name = target.name;

        this.setState({
            [name]: value
        });
    }

    render() {
        return (
            <form>
                <label>
                    Is Going
                    <input
                        name='isGoing'
                        type='checkbox'
                        checked={this.state.isGoing}
                        onChange={this.handleInputChange} />
                </label>
                <br />
                <label>
                    Number of guests:
                    <input
                      name='numberOfGuests'
                      type='number'
                      value={this.state.numberOfGuests}
                      onChange={this.handleInputChange}
                    />
                </label>
            </form>
        );
    }
}
```

注意，我们使用ES6的*计算属性名*语法：

```javascript
this.setState({
    [name]: value
});
```

等同于ES5的代码：

```javascript
var partialState = {};
partialState[name] = value;
this.setState(partialState);
```


## Controlled Input Null Value

如果你设置一个`value`的时候value仍然可以编辑，你可能会意外的将`value`设置为`undefined`或者`null`.

```javascript
ReactDOM.render(<input value="hi" />, mountNode);

setTimeout(function() {
    ReactDOM.render(<input value={null} />, mountNode)
}, 1000);
```

## Alternatives to Controlled Components

...