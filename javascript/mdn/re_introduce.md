# A re-introduction to JavaScript (JS tutorial)

为什么本文标题叫做re-introduce(重新介绍)？因为Javascript曾经是世界上最臭名昭著的难以理解。也有很多人把它叫做玩具语言，但是不要被它表面的简单所欺骗，Javascript现在可以编写了很多高性能应用。这篇文章就是帮助你们深入了解JS中的高级技巧的。

首先有必要从Javascript的历史谈起。Javascript是Brendan Eich于1995年以Netscape工程师的身份发明的。为了蹭Sun公司的Java语言的热度，它被改名叫做Javascript(之前叫做LiveScript)，但是它和Java其实并没有什么关系。

不像其它语言一样，Javascript没有“输入”和“输出”的概念。它设计之初就是作为host环境运行的脚本。最常见的host环境就是浏览器，不过Javascript也可以用于很多其它场景，包括Adobe Acrobat, Adobe Photoshop, SVG images...

## Overview

Javascript是一个multi-paradigm，动态语言，拥有类型，操作符，标准的built-in对象，以及方法。它的语法基于Java的C。Javascript支持对象原型形式的面向对象编程。Javascript也支持函数式编程 - 函数也是对象。

让我们先看一下Javascript有哪些类型Types:

- Number
- String
- Boolean
- Object
    - Function
    - Array
    - Date
    - Regexp
- Symbol
- null
- undefined

另外还有一些内置的`Error`类型。不过我们暂时只讨论列出在这里的类型。

## Numbers

Javascript中的numbers是"双进度64位IEEE754值(double-precision 64-bit format IEEE 754 values)"。因为这种形式的numbers，会造成一些有趣的结果。在Javascript没有C的那种integer。

请看：

`0.1 + 0.2 == 0.30000000000000004;`

整数值被当作32位int。

支持标准的算数操作符，包括加，减，模等等。另外有一个内置的对象Math，它提供了一些常见的数学函数和常量：

```javascript
Math.sin(3.5);
var circumference = 2 * Math.PI * r;
```

你可以使用内置的`parseInt()`函数把一个字符串转换成一个整数。它的第二个可选参数代表进制：

```javascript
parseInt('123', 10);        // 123
parseInt('010', 10);        // 10
```

类似的，还有一个浮点数转换函数`parseFloat()`。不过它总是会转换为十进制浮点数。

你也可以使用一元操作符`+`来将值转换为数值：

```javascript
+ '42';     // 42
+ '010';    // 10
+ '0x10';   // 16
```





