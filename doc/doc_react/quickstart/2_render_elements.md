# Rendering Elements

**element是React app中最小的构件块**

Element定义你在屏幕中见到的东西：

```javascript
const element = <h1>Hello, world</h1>;
```

不像浏览器的DOM元素，React元素是普通对象，可以以极地开销来创建。React DOM会注意React元素的更新情况，并让DOM保持同步更新。

> 注意"elements"和"components"不同，"elements"是"components"最终创建的东西，在下章我们会介绍Components。

## Rendering an Element into the DOM

让我们假设你的HTML文件有一个`<div>`:

```javascript
<div id="root"></div>
```

我们把它叫做DOM根节点，因为在里面的一切都会由React DOM进行管理。

使用React创建的应用一般只有一个根结点。如果你把React继承到已有的APP中，你也可以有很多隔离的根节点。

想要把一个React element渲染为一个DOM节点，可以将它们传入`reactDOM.render()`:

```javascript
const element = <h1>Hello, world</h1>;
ReactDOM.render(element, document.getElementById('root'));
```

## Updating the Rendered Element

React elements是不可变的(immutable)。一旦你创建了一个element，你就不能再修改它的属性或者子元素了。一个elment就像电影中的一帧(frame)一样：它代表一个确切时间点内的UI。

就我们所知而言，更新UI的唯一办法就是创建一个新的element，并将它传给`ReactDOM.render()`.

```javascript
function tick() {
    const element = (
        <div>
            <h1>Hello, world!</h1>
            <h2>It is {new Date().toLocalTimeString()}.</h2>
        </div>
    );
    ReactDOM.render(element, document.getElementById('root'));
}

setInterval(tick, 1000);
```

上面的例子，每秒钟都会重新调用`ReactDOM.render()`

## React Only Updates What's Necessary

React DOM会比较elment和之前的element，只会对应该更新的地方进行更新。

即使我们上个例子在代码中是重新渲染了整个UI，但是只有改动的文本会被更新。

