# Add React to a New Application

这章节主要介绍使用React来构件一个单页应用，包括很多开发流程工具如代码检查，测试，产品优化等等。

如果你不需要建立单页应用，你可以选择[add React to your existing build pipeline](https://reactjs.org/docs/add-react-to-an-existing-app.html)或者[use it from CDN](https://reactjs.org/docs/cdn-links.html).

## Create React App

[Create React App](http://github.com/facebookincubator/create-react-app)是用来开启创建一个React单页应用的最好工具。它会为你建立起开发环境，让你可以使用最新的Javascript特性，提供给开发者一个极佳的开发体验，并且会在代码上线时为你优化代码。

你需要在本机安装`Node6.0`以上。

```javascript
npm install -g create-react-app
create-react-app my app

cd my-app
npm start
```

创建React App并不会处理后端和数据库；它只是创建了一个前端建设管道，你可以使用任何其它的后端。它在底层使用了Babel和Webpack，但是就像0配置一样可以直接使用。

在你准备好部署到线上的时候，运行`npm run build`将会为你创建一个`build`文件夹。你可以在[create-react-app的文档](https://github.com/facebook/create-react-app/blob/master/packages/react-scripts/template/README.md#table-of-contents)中学到更多有关环境搭建的事情。

## Other Starter Kits

## Advanced