# Lifting State Up

有时会有几个组件反射相同的数据。我们推荐把共享的状态上升到它们最近的共同祖先。

在本章中，我们会创建一个温度计算器，根据给定的温度计算水是否沸腾。

我们先从一个组件`BoilingVerdict`开启.它接受`celsius`温度作为一个prop，并且会打印它是否能够让水沸腾：

```javascript
function BoilingVerdict(props) {
    if (props.celsius >= 100)
        return <p>The water would boil.</p>;
    return <p>The water would not boil.</p>;
}
```

接下来，我们创建一个组件`Calculator`。它会渲染一个`<input>`让你输入温度，将输入的值保存在`this.state.temperature`.

另外，它会根据当前输入的值渲染`BoilingVerdict`:

```javascript
class Calculator extends React.Component {
    constructor(props) {
        super(props);
        this.handleChange = this.handleChange.bind(this);
        this.state = {temperature: ''};
    }

    handleChange(e) {
        this.setState({temperature: e.target.value});
    }

    render() {
        const temperature = this.state.temperature;
        return (
            <fieldset>
                <legend>Enter temperature in Celsius: </legend>
                <input 
                    value={temperature}
                    onChange={this.handleChange} />
                
                <BoilingVerdict
                    celsius={parseFloat(temperature)} />
            </fieldset>
        );
    }
}
```

## Adding a Second Input

新的需求来了，除了Celsius输入，我们又需要提供一个Fahrenheit输入，将它们保持同步。

我们可以从`Calculator`中提取出`TemperatureInput`组件。

```javascript
const scaleNames = {
    c: 'Celsius',
    f: 'Fahrenheit'
};


class TemperatureInput extends React.Component {
    constructor(props) {
        super(props);
        this.handleChange = this.handleChange.bind(this);
        this.state = {temperature: ''};
    }

    handleChange(e) {
        this.setState({temperature: e.target.value});
    }

    render() {
        const temperature = this.state.temperature;
        const scale = this.props.scale;
        return (
            <fieldset>
                <lengend>Enter temperature in {scaleNames[scale]}:</lengend>
                <input value={temperature}
                       onChange={this.handleChange} />
            </fieldset>
        );
    }
}
```

我们修改`Calculator`，让它渲染两个独立的温度input：

```javascript
class Calculator extends React.Component {
    render() {
        return (
            <div>
                <TemperatureInput scale='c' />
                <TemperatureInput scale='f' />
            </div>
        );
    }
}
```

## Writing Conversion Functions

首先，我们要编写两个函数来进行Celsius和Fahrenheit之间的转换:

```javascript
function toCelsius(fahrenheit) {
    return (fahrenheit - 32) * 5 / 9;
}


function toFahrenheit(celsius) {
    return (celsius * 9 / 5) + 32;
}
```

这两个函数用来转换数字。我们还要编写一个函数接受一个字符串参数`temperature`以及一个转换函数参数，返回一个字符串。

如果temperatur非法，则返回一个空字符串：

```javascript
function tryConvert(temperature, convert) {
    const input = parseFloat(temperature);
    if (Number.isNaN(input)) {
        return '';
    }
    const output = convert(input);
    const rounded = Math.round(output * 1000) / 1000;
    return rounded.toString();
}
```

## Lifting State Up

目前，所有的`TemperatureInput`组件都在它们自己的局部state独立保持它的值：

```javascript
class TemperatureInput extends React.Component {
    constructor(props) {
        super(props);
        this.handleChange = this.handleChange.bind(this);
        this.state = {temperature: ''};
    }

    handleChange(e) {
        this.setState({temperature: e.target.value});
    }

    render() {
        const temperature = this.state.temperature;
        // ...
    }
}
```

不过，我们需要这个两个状态相互同步。在更新Celsius input的时候，Fahrenheit input应该反射转换后的温度。反之亦然。

在React中，分享状态可以通过将状态移给组件的一个最近的共同祖先来实现。这叫做“lifting state up”。我们将会把`TemperatureInput`中的state移到`Calculator`中。

让我们一步一步来。

首先，把`TemperatureInput`组件中的`this.state.temperatue`替换为`this.props.temperatue`。现在，让我们假定`this.props.temperatue`已经存在：

```javascript
render() {
    const temperature = this.props.temperatue;
    // ...
}
```

我们知道props是只读的。在temperature是state的时候，可以使用`setState`来修改它。不过，现在temperature是一个来自于父组件的prop，`TemperatureInput`不能控制它。

在React中，通常可以让一个组件“被控制”来解决这个问题。就像DOM的`<input>`可以接受`value`和`onChange`prop，所以自定义的`TemperatureInput`可以从父组件中接受`onTemperatureChange`和`temperature`这连个props。

现在，当`TemperatureInput`想要更新它的temperature，它会调用`this.props.onTemperatureChange`:

```javascript
handleChange(e) {
    this.props.onTemperatureChange(e.target.value);
}
```

```javascript
class TemperatureInput extends React.Component {
    constructor(props) {
        super(props);
        this.handleChange = this.handleChange.bind(this);
    }

    handleChange(e) {
        this.props.onTemperatureChange(e.target.value);
    }

    render() {
        const temperature = this.props.temperature;
        const scale = this.props.scale;
        return (
            <fieldset>
                <legend>Enter temperature in {scaleNames[scale]}:</legend>
                <input value={temperature}
                       onChange={this.handleChange}>
            </fieldset>
        );
    }
}
```

现在，我们可以转背写Calculator组件了。

我们会存储当前输入的`temperature`和`scale`到本地state中。

例如，如果我们在Celsius输入37，Calculator的状态组件会变为：

```javascript
{
    temperature: '37',
    scale: 'c'
}
```

将Fahrenheit input编辑为212，Calculator的状态会变为:

```javascript
{
    temperature: '212',
    scale: 'f'
}
```

两个input会保持同步，因为它们的值根据相同的state来计算：

```javascript
class Calculator extends React.Component {
    constructor(props) {
        super(props);
        this.handleCelsiusChange = this.handleCelsiusChange.bind(this);
        this.handleFahrenheitChange = this.handleFahrenheitChange.bind(this);
        this.state = {temperature: '', state: 'c'};
    }

    handleCelsiusChange(temperate) {
        this.setState({scale: 'c', temperature});
    }

    handleFahrenheitChange(temperate) {
        this.setState({scale: 'f', temperature});
    }
    
    render() {
        const scale = this.state.scale;
        const temperature = this.state.temperature;
        const celsius = scale === 'f' ? tryConvert(temperature, toCelsius) : temperature;
        const fahrenheit = scale === 'c' ? tryConvert(temperature, toFahrenheit) : temperature;

        return (
            <div>
                <TemperatureInput 
                    scale='c'
                    temperature={celsius}
                    onTemperatureChange={this.handleCelsiusChange}
                />

                <TemperatureInput 
                    scale='f'
                    temperature={fahrenheit}
                    onTemperatureChange={this.handleFahrenheitChange}
                />

                <BoilingVerdict 
                    celsius={parseFloat(celsius)}
                />
            </div>
        );
    }
}
```

现在，无论你输入什么，`Calculator`的`this.state.temperature`和`this.state.scale`都会更新。

让我们总结一下在你编辑一个input之后发生了什么：

- React调用DOM`<input>`指定的`onChange`函数。在我们的例子中，这是`TemperatureInput`组件的`handleChange`方法.

- `TemperatureInput`组件的`handleChange`方法使用新的值来调用`this.props.onTemperatureChange()`。props包含`onTemperatureChange`，是由父组件`Calculator`提供的.

- 在之前一步渲染的时候，`Calculator`会将Celsius`TemperatureInput`的`onTemperatureChange`设置为`handleCelsiusChange`方法，反之设置为`handleFahrenheitChange`.

- 在这些方法中，`Calculator`组件通过调用`this.setState()`来要求React重新渲染。

- React调用`Calculator`组件的`render`方法来渲染UI的显示结果。所有input控件都会基于当前的temperature和scale来重新计算。temperature转换也在这里进行。

- React DOM更新DOM来匹配最新的值。

## Lessons Learned

...