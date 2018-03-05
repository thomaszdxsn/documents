# Thinking in React

**React在我们看来，是使用Javascript构建大型快速Web app的最佳方式。它帮助我们构建了Facebook和Instagram**

React最重要的一部分就是它会教你怎么创建app。在这篇文档，我们通过使用React创建一个可搜索的产品数据表来教你是怎么一个思考过程。

## Start With A Mock

想象我们已经有一个JSON API和一些模拟数据。

我们的JSON API返回的数据类似下面这样:

```javascript
[
  {category: "Sporting Goods", price: "$49.99", stocked: true, name: "Football"},
  {category: "Sporting Goods", price: "$9.99", stocked: true, name: "Baseball"},
  {category: "Sporting Goods", price: "$29.99", stocked: false, name: "Basketball"},
  {category: "Electronics", price: "$99.99", stocked: true, name: "iPod Touch"},
  {category: "Electronics", price: "$399.99", stocked: false, name: "iPhone 5"},
  {category: "Electronics", price: "$199.99", stocked: true, name: "Nexus 7"}
];
```

## Step1: Break The UI Into A Component Hierarchy

第一件你想做的事情就是画出每个组件的盒子。如果你和一个设计师合作，它们可能已经帮你做好了！

但是你如何知道哪些东西应该划分为组件？一个原则就是`single responsibility principle`，也就是说，一个组件通常只做一件事。如果一个组件变得很大，通常就需要将它拆分成更小的组件。

由于你经常像一个用户展示一个JSON数据模型，你发现如果你的模型正确的创建，你的UI会很好的映射。这是因为UI和数据模型一般有相同的信息结构。

![demo](https://reactjs.org/static/thinking-in-react-components-eb8bda25806a89ebdc838813bdfa3601-82965.png)

你会看到在这个简单app中我们有5个组件：

1. FilterableProductTable(橙色): 包含了整个示例
2. SearchBar(蓝色): 接受所用用户的输入
3. ProductTable(绿色): 根据用户的输入来筛选输出的数据
4. ProductCategoryRow(天蓝色): 每个分类显示一个头部
5. ProductRow(红色)：每个产品显示一行

现在我们已经识别出我们模拟的组件，让我们将它整理到一个结构里面。这很简单：

- FilterableProductTable
    - SearchBar
    - ProductTable
        - ProductCategoryRow
        - ProductRow

## Step2: Build A Static Version in React

现在你已经知道了组件的结构，是时候实现你的app了。最简单的方式是先创建一个非交互式版本的app。最好解耦这些处理，因为创建一个静态版本要求敲更多代码但不需要怎么思考，加入交互需要思考但不需要敲很多代码。

想要创建一个静态版本的app，你想要构件组件，重用其它组件并使用props来传送数据。props是父组件向子组件传输数据的一种方式。如果你熟悉state的概念，不要使用state来创建你的静态版本app。state保留用来之后的交互。因为现在app是静态版本，还不需要使用它。

你可以自上而下或者自下而上的编写代码。也就是说，你可以先写结构的最上层(`FilterableProductTable`)或者先写结构的最下层(`ProductRow`).在简单的例子中，最好使用自顶向下，对于大型应用，应该使用自下而上并且编写单元测试。

在这一步骤结束之后，你有一个可充用的组件库可以渲染你的数据模型。因为还是静态版本，组件现在只有`render()`方法。结构中的顶层组件(`FilterableProductTable`)可以接受你的数据模型作为prop。如果你对底层的数据模型作出改动并且再次调用`ReactDOM.render()`，UI也会更新。React的单向数据流(或者叫做单向绑定)可以让一切保持模块化和快速。

### A Brief Interlude: Props vs State

React中由两种类型的数据“model”：props和state。区分并理解它们是很重要的，如果你还不能区分它们，请看[这篇文章](https://reactjs.org/docs/interactivity-and-dynamic-uis.html)


## Step3:Identity The Minimal(but complete) Representation Of UI State

想要让你的UI变得可交互，你需要为底层数据模型加入改动的触发。React通过`state`来实现。

为了正确的构建你的app，你首先需要思考你app需要的可变state的最小集合。关键在于DRY(Don't Repeat Yourself).例如，如果你创建一个TODO list，只需要保持一份TODO item数组；不需要为count切分出一份单独的state变量。如果你想要渲染TODO的count，只要使用TODO数组的长度就好了。

思考我们示例应用的所有数据。我们有：

- 原始的产品list
- 用户键入的搜索文本
- checkbox中的值
- 筛选后的产品list

让我们一个一个分析，看看哪个是state。对每一片数据都要问三个问题：

1. 是否是父组件通过props传入的？如果是，它可能就不是state。
2. 是否完全不会改变？如果是，它可能就不是state
3. 它是否根据你组件的其它state或者prop计算得来？如果是，它就不是state

*原始的产品list*是通过props传入的，所以它不是state。*搜索文本*和*checkbox*看起是state，因为它们会改动并且不是通过其它值计算得来的。最后，*筛选后的产品list*不是state，因为它是通过原始list和搜索文本以及checkbox计算得来。

最终，我们的state是：

- 用户键入的搜索文本
- checkbox中的值

## Step4: Identity Where Your State Should Live

OK,所以我们确定了app state的最小集合。然后，我们需要识别哪些组件是可变的。

记住：React是单向数据流的。不需要立即搞清楚哪个组件应该有它自己的state。**这是新手最难搞懂的地方**，所以需要通过下列的步骤来算出：

对于你应用的每部分state：

- 识别每个组件基于这个state渲染的东西
- 找出一个通用的owner组件
- Either the common owner or another component higher up in the hierarchy should own the state.
- 如果你不能发现一个组件是否应该有自己的state，创建一个新的组件用来持有state并将它加入到层级中更上一层的通用位置

让我们在自己的应用中实现这个策略：

- `ProductTable`需要根据state来筛选产品list，`SearchBar`需要显示搜索文本和选中的state。

- 最通用的owner组件是`FilterableProductTable`

- 理论上筛选文本和选中的值应该存在于`FilterableProductTable`

酷，我们决定我们的state放在`FilterableProductTable`。首先，为`FilterableProductTable`的构造器加入一个实例属性`this.state={filterText: '', isStockOnly: false}`.然后将`filterText`和`isStockOnly`作为prop传入`ProductTable`和`SearchBar`.最后，使用这些props来筛选`ProductTable`中的行。

## Step5: Add Inverse Data Flow

到目前位置，我们构建了一个app来正确渲染。现在是时候用另一种方式支持数据流：`FilterableProductTable`需要更新它的state。

React让这个数据流显式地创建，让人可以很容易看懂你的程序，不过它相比传统的双向绑定需要键入更多一些代码。



