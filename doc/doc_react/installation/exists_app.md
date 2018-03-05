# Add React to an Existing Application

*使用React，不需要你重新编写整个app*

我们推荐将React作为你应用的一小部分加入，比如独立的控件。

一个现代的pipeline一般由下面这些组成：

- 一个`包管理器(package manager)`，比如Yarn或者npm。它让你可以利用到广泛的第三方库。
- 一个`bundler`，比如`webpack`或者`Browserify`.它可以让你编写模块化的代码，在编译的时候将它们打包进一个模块中。
- 一个`编译器(Babel)`。它可以让你使用最新的ES特性，但是同样适用于旧版本的浏览器。

## Installing React

我们推荐使用`Yarn`或者`npm`来管理前端依赖。如果你还不了解包管理器，推荐阅读[Yarn documentation](https://yarnpkg.com/en/docs/getting-started).

通过Yarn来安装React：

```javascript
yarn init
yarn add react react-dom
```

通过npm来安装react:

```javascript
npm init
npm install --save react react-dom
```

## Enabling ES6 and JSX

我们推荐使用React的时候一并使用Babel，它可以让你的ES6代码和JSX运行。

这篇[Babel安装教程](https://babeljs.io/docs/setup/)会告诉你怎么搭建Babel.确认你安装了`babel-preset-react`和`babel-preset-env`，并且在`.bablerc`配置文件中激活了它们。

## Hello World with ES6 and JSX

我们推荐使用bundler，比如`Webpack`或者`Browserify`，它们让你可以编写模块化的代码。

最迷你的一个React示例看起来像下面这样:

```javascript
import React from 'react';
import ReactDOM from 'react-dom';

ReactDOM.render(
    <h1>Hello, World!</h1>,
    document.getElemenyById('root');
);
```

## Development and Production Version

默认情况下，React包含很多有为开发者提供帮助的warnings。这些警告在开发的时候很有用。

不过，它们会让React的开发版本变得庞大，速度也相对更慢，所以不应该在产品版本中开启它。

- [Creating a Production Build with Create React App](https://reactjs.org/docs/optimizing-performance.html#create-react-app)

- [Creating a Production Build with Single-File Builds
](https://reactjs.org/docs/optimizing-performance.html#single-file-builds)

- [Creating a Production Build with Brunch](https://reactjs.org/docs/optimizing-performance.html#brunch)

- [Creating a Production Build with Browserify](Creating a Production Build with Browserify)

- [Creating a Production Build with Rollup](https://reactjs.org/docs/optimizing-performance.html#rollup)

- [Creating a Production Build with webpack](Creating a Production Build with webpack)





