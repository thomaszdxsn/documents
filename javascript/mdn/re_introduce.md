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

有一个特殊值`NaN`，它代表一个非数值值：

```javascript
parserInt('hello', 10);     // NaN
```

你可以使用内置函数`isNaN()`来测试一个值是否为`NaN`:

```javascript
isNaN(NaN);     // true
```

另外还有两个特殊值`Infinity`和`-Infinity`:

```javasscript
1 / 0;      // Infinity
-1 / 0;     // -Infinity
```

你可以使用内置函数`isFinite()`来测试`Infinity`, `-Infinity`和`NaN`:

```javascript
isFinite(1 / 0);        // false
isFinite(-Infinity);    // false
isFinite(NaN);          // false
```

> `parseInt()`，`parseFloat()`函数在解析字符串的时候会在碰到不合法字符的时候停下，然后把之前的数字字符串解析返回。而一元操作符`+`碰到这种情况会直接返回NaN。

## Strings

Javascript中的String是Unicode字符序列。更精确来说，它是UTF-16code unit序列；每个code unit代表16位数字。每个Unicode字符代表1或2个code unit。

如果你想表现单个字符，你可以只使用单个字符的字符串。

想要获取一个字符串的长度(以code unit为基准)，可以访问它的`length`属性：

```javascript
"Hello".length;     // 5
```

另外字符串也是对象。它有一些方法可以帮助你方便的处理字符串：

```javascript
'hello'.chartAt(0);     // "h"
"hello, world".replace('hello', 'goodbye');     // "goodbye, world"
"hello".toUpperCase();      // "HELLO"
```

## Other Types

Javascript区分`null`(这个值代表None值，`null`是关键字)和`undefined`(代表没有定义的值)。undefined实际上是一个常量。

Javascript有一个布尔类型，分别是`true`和`false`.任何值都可以转换为布尔值：

1. `false`, `0`，空字符串(`""`), `NaN`, `null`以及`undefined`都代表是`false`.
2. 其它的值都代表是`true`.

你可以使用`Boolean()`函数(构造器?)来进行转换：

```javascript
Boolean('');  // false
Boolean(234); // true
```

Javasript的很多语句都会作布尔值的隐式转换，比如`if`语句。出于这个原因，一般所谓的“true值”和"false值"是值可以转换为tru或者false的值。

布尔值支持的操作符包括： `&&`, `||`, `!`.

## Variables

Javascript支持以下三个关键字来声明变量：`let`, `const`或者`var`.

`let`允许声明块级别变量。声明的变量只可以在闭包块中访问：

```javascript
let a;
let name = 'Simon';
```

```javascript
myLetVariable; // undefined

for (let myLetVariable = 0; myLetVariable < 5; myLetVariable++) {
  myLetVariable; // 0
}

myLetVariable; // undefined
```

`const`运行你声明常量。声明的常量只能在声明所在的代码块中访问：

```javascript
const PI = 3.14;    
Pi = 1; // 将会抛出错误
```

`var`是最常见的声明变量关键字。它没有之前两个关键字的种种限制。var声明的变量会进行变量提升(runtime时首先收集var语句然后赋值)

```javascript
var a; 
var name = 'Simon';
```

```javascript
// myVarVariable *is* visible out here 

for (var myVarVariable = 0; myVarVariable < 5; myVarVariable++) { 
  // myVarVariable is visible to the whole function 
} 

// myVarVariable *is* visible out here
```

Javascript和其它语言的一个重要不同之处就是，JS中的代码块并不包含自身的域；只有函数包含域。所以如果使用var来申明变量，它可以在整个域中获取。不过，从ECMA2015开始，推荐使用`let`和`const`语句来声明块级变量。

## Operators

Javascript数值操作符包括`+`, `-`, `*`, `/`和`%`。赋值操作符是`=`。另外还有递增/递减操作符，分别是`+=`, `-=`。也可以使用`++`和`--`来代替递增/递减操作符(操作数为1)。

`+`操作符同样可以用于字符串串联：

```javascript
'hello' + ' world';     // "hello world"
```

如果把数值(或其他值)和字符串相加，在相加的时候其它值首先会转换为字符串：

```javascript
"3" + 4 + 5;        // "345"
3 + 4 + "5";        // 75
```

将一个值和空字符相加，可以用来将它转换为字符串。

Javascript中的比较操作符包括：`<`, `>`, `<=`, `>=`.它们都可以用于字符串和数值。

```javascript
123 == '123';   // true
1 = true;       // true
```

为了避免隐式类型转换，可以使用三个等号的操作符：

```javascript
123 === '123';      // false
1 === true;         // false
```

当然，`!=`也有它对应的版本`!==`.

## Control structures

Javascript的控制结构和C语言很相似。条件语句支持`if`，`else`:

```javascript
var name = 'kittens';
if (name == 'puppies') {
    name += ' woof';
} else if (name == 'kittens') {
    name += ' meow';
} else {
    name += '!'
}
name == 'kittens meow';     // true
```

Javascript有`while`和`do while`循环语句：

```javascript
while (true) {
    // 一个死循环!
}

var input;

do {
    input = get_input()
} while (inputIsNotValid(input));
```

Javascript的`for`循环类似于C和Java：

```javascript
for (var i = 0; i < 5; i++) {
    // 会迭代5次
}
```

`for`语句还有两个兄弟: `for..of`

```javascript
for (let value of array) {
    // 迭代array中的每一个值
}
```

以及`for ... in`

```javascript
for (let property in object) {
    // 处理object中的每一个property
}
```

`&&`和`||`操作符可以用来作为短路逻辑，意味着是否执行第二个操作数取决于第一个操作数的结果。可以用来检查一个值是否为null.

```javascript
var name = o && o.getName();
```

或者可以用来缓存一个值：

```javascript
var name = cachedName || (cachedName = getName());
```

Javascript有三元操作符，可以用来作简单的条件判断：

```javascript
var allowed = (age > 18) ? 'yes' : 'no';
```

`switch`语句可以用于多分支条件语句：

```javascript
switch (action) {
    case 'draw':
        drawIt();
        break;
    case 'eat':
        eatIt();
        break;
    default:
        doNothing();
}
```

如果你不使用`break`，控制流会接着往下走。

## Objects

Javascript中的对象实际是一个键值对的集合。它类似于：

- Python中的字典
- Ruby和Perl中的hash
- C和C++中的Hash表
- Java中的Hashmap
- PHP中的associative array

由于Javascript中一切解释对象。所以Javascript程序原生就需要和hash表查询打交道，所以它才能这么快。

对象中的“name”部分是一个字符串，“value”部分可以是Javascript的任何值类型 - 甚至可以是其它对象。

有两个方式可以创建一个对象：

```javascript
var obj = new Object(); // 构造器语法
var obj = {};  // 字面量语法
```

对象字面量语法可以用来初始化：

```javascript
var obj = {
    name: 'Carrot',
    for: 'Max', // for是保留字，使用"_for"来替代它
    details: {
        color: 'orange',
        size: 12
    }
}
```

可以链式访问嵌套结构：

```javascript
obj.details.color;      // orange
obj['details']['size']; // 12
```

下面的例子创建了一个对象原型`Person`，以及一个原型的实例`You`:

```javascript
function Person(name, age) {
    this.name = name;
    this.age = age;
}

// 定义一个对象
var you = new Person('You', 24)
```

在创建完成之后，对象的property可以通过两种方式来访问：

```javascript
// 点式记号法
obj.name = 'Simom';
var name = obj.name;

// 方括号记号法
obj['name'] = 'Simon';
var name = obj['name'];
var user = prompt('what is your key?')
obj[user] = prompt('what is its value?')
```

有时一个property和JS保留字冲突，你必须使用第二种方式来访问：

```javscript
obj.for = 'Simon';  // for是保留字，所以不能这么访问属性
obj['for'] = 'Simon';
```

## Array

Javascript中的Array是一种特殊类型的对象。它和普通对象拥有很多一样的特性，不过它的`length`属性反应最后一个元素的索引+1。

创建array的方法：

```javascript
var a = new Array();
a[0] = 'dog';
a[1] = 'cat';
a[2] = 'hen';
a.length; // 3

// 字面量创建方式
var a ['dog', 'cat', 'hen']
a.length;   // 3
```

`array.length`反应它所包含的最后一个元素的索引+1：

```javascript
var a = ['dog', 'cat', 'hen']
a[100] = 'fox'
a.length;       // 101
```

如果你访问一个不存在的索引，会返回一个undefined.

```javascript
typeof a[90]; // undefined;
```

可以使用`for`和`for .. of`来迭代数组：

```javascript
for (var i = 0; i < a.length; i++) {
    // 每次迭代可以访问a[i]
}

for (const currentValue of a){
    // currentValue是a中按顺序的量
}
```

也可以使用`for ... in`，不过如果你为Array.prototype加入了一些额外的prorperty，也会将它迭代出来。

ECMA2015加入了另外一种迭代方式叫做`forEach()`:

```javascript
['dog', 'cat', 'hen'].forEach(function(currenctValue, index, array) {
    // Do something with currentValue or array[index]
})
```

如果你想为Array追加item，使用`.push()`方法.

```javscript
a.puth(item)
```

Array另外还有一些方法：

方法名 | 描述
-- | --
a.toString() | 返回数组的字符串表现形式(调用每个元素的`.toString()`方法)
a.toLocalString() | 返回数组的字符串表现形式(调用每个元素的`.toLocalString()`方法)
a.concat(item1[, item2[, ...]]) | 将这些item加入，返回一个新的数组
a.pop() | 移除并返回最后一个item
a.push(item, ... itemN) | 将item追加到当前数组的结尾
a.reverse() | 逆转array的顺序
a.shift() | 移除并返回第一个item
a.slice(start[, end]) | 返回一个子数组
a.sort([cmpfn]) | 将数组排序，可选择传入一个排序函数
a.splice(start, delcount[, item1[, ...itemN]]) | 让你可以将数组的一端元素删除(可选择替换)
a.unshift(item1[,...itemN]) | 将item prepend到数组的首端


## Functions

和对象一样，函数也是Javascript的核心元素。见面是一个最简单的函数：

```javascript
function add(x, y) {
    var total = x + y;
    return total;
}
```

你可以调用一个函数但是不传入它所需的参数。这会返回给你一个undefined而不是报错:

```javascript
add(); // NaN
```

函数可以接受多于它所其它的参数：

```javascript
add(2, 3, 4);       // 5
```

另外在函数体内有一个特殊的变量叫做`arguments`，它代表函数接受的所有参数：

```javascript
function add() {
    var sum = 0;
    for (var i = 0, j = arguments.length; i< j; i++) {
        sum += arguments[i];
    }
    return sum
}

add(2, 3, 4, 5); // 14
```

另外ECMA2015引入了一个rest参数语法`...variable`这个variable能代表剩余传入的参数：

```javascript
function avg(...args) {
    var sum = 0;
    for (let value of args) {
        sum += value;
    }
    return sum / args.length;
}

avg(2, 3, 4, 5); // 3.5
```

如果你想要以一个数组来调用上面这个函数，当然可以选择重写让它接受一个数组参数，但是有更方便的方法：

```javascript
avg.apply(null, [2, 3, 4, 5]); // 3.5
```

Javascript允许你创建匿名函数：

```javascript
var avg = function() {
    var sum = 0;
    for (var i = 0, j = arguments.length; i < j; i++) {
        sum += arguments[i];
    }
    return sum / arguments.length;
};
```

另外可以使用立即执行函数来模拟C中的代码块：

```javascript
var a = 1;
var b = 2;

(function() {
    var b = 3;
    a += b;
})();

a; // 4
b; // 2
```

Javascirpt允许你递归调用函数：

```javascript
function countCharts(elm) {
    if (elm.nodeType == 3) {
        return elm.nodeValue.length;
    }
    var count = 0;
    for (var i = 0, child; child = elem.childNodes[i]; i++) {
        count += countCharts(child);
    }
    return count;
}
```

那么怎么递归调用匿名函数呢？Javascript运行你使用一种IIFEs(立即调用函数表达式)：

```javascript
var charsInBody = (function counter(elm) {
    if (elm.nodeType == 3) {
        return elm.nodeValue.length;
    }
    var count = 0;
    for (var i = 0, child; child = elm.childNodes[i]; i++) {
    count += counter(child);
    }
    return count()
})(document.body);
```

## Custom objects

```javascript
function makePerson (first, last) {
    return {
        first: first,
        last: last
    }
}

function personFullName(person) {
    return person.first + ' ' + person.last;
}

function personFullNameReversed(person) {
    return person.last + ', ' + person.first;
}

s = makePerson('Simon', 'Willson');
personFullName(s);          // "Simon Willison"
personFullNameReversed(s);  // "Willison, Simon"
```

可以使用上面的方法来处理数据，不过是在太丑陋了。因为函数就是对象，所以你可以这么作：

```javascript
function makePerson(first, last) {
    return {
        first: first,
        last: last,
        fullName: function() {
            return this.first + ' ' + this.last;
        },
        fullNameReversed: function() {
            return this.last + ", " + this.first;
        }
    };
}

s = makePerson('Simon', 'Willison');
s.fullName(); // "Simon Willison"
s.fullNameReversed(); // "Willison, Simon"
```

你可以看到代码中有`this`关键字。在一个函数中，`this`就代表当前的对象。

不过`this`是很容易写出bug的：

```javascript
s = makePerson('Simon', 'Willson');
var fullName = s.fullName;
fullName(); 
```

当我们直接调用`fullName()`而不是`s.fullName()`的时候，`this`会指向全局对象。

我们可以利用`this`来改进我们的makePerson函数:

```javascript
function Person(first, last) {
    this.first = first;
    this.last = last;
    this.fullName = function() {
        return this.first + " " + this.last;
    };
    this.fullNameReversed = function() {
        return this.last + ', ' + this.first;
    };
}
var s = new Person('Simon', 'Willison');
```

现在我们引入了一个新的关键字`new`。new和this戚戚相关。它会创建一个全新的对象，然后调用函数定义，然后把this替换到这个全新对象上面。

我们可以先创建方法函数，然后把它指派给一个构造器：

```javascript
function Person(first, last) {
    this.first = first;
    this.last = last;
}
Person.prototype.fullName = function() {
    return this.first + ' ' + this.last;
}
Person.prototype.fullNameReversed = function() {
    return this.last + ", " + this.first;
}
```

`Person.prototype`是Person所有实例共享的一个对象。它支持链式查询(也叫做原型链)：如果你访问的一个Person的property但是它还没有设定，Javascript将会检查`Person.prototype`看是否有可以提到的property。

这是个极强大的功能。Javascript让你可以在任何时候修改prototype，实现所谓的monkey-patch:

```javascript
s = new Person('Simon', 'Willison');
s.firstNameCaps(); // TypeError

Person.prototype.firstNameCaps = function() {
    return this.first.toUpperCase();
}
s.firstNameCaps(); // "SIMON"
```

包括内置对象的prototype也可以被修改：

```javascript
var s = 'Simon';
s.reversed(); // TypeError

String.prototype.reversed = function() {
    var r = '';
    for (var i = this.length - 1; i >= 0; i--) {
        r+=this[i];
    }
    return r;
};

r.reversed();
```


一个原型是原型链的一部分。这个链条的根节点是`Object.prototype`，它的方法包括`toString()` -- 可以用它来调试`Person`对象：

```javascript
var s = new Person('Simon', 'Willson');
s.toString(); // [object Object]

Person.prototype.toString = function() {
    return "<Person: " + this.FullName() + ">";
}

s.toString(); // "<Person: Simon Willson>"
```

记得之前使用`avg.apply()`方法吗，为什么第一个参数传入null？因为传入`apply()`的第一个参数会被看作当作`this`的对象。例如我们可以重新创建一个new:

```javascript
function trivialNew(constructor, ...args) {
    var o = {};
    constructor.apply(o, args);
    return o;
}
```

这不是完整的`new`复制版，因为它没有设置原型链。只是用来做个示例。

调用：

```javascript
var bill = trivialNew(Person, 'William', 'Orange')
```

大概和下面语句一样:

```javascript
var bill = new Person('Willam', 'Orange')
```

`apply()`还有一个姊妹函数叫做`call`，它和`apply()`大致相同，不过它是针对对象本身来调用函数的：

```javascript
function lastNameCaps() {
    return this.last.toUpperCase();
}
var s = new Person('Simon', 'Willson');

lastNameCaps.call(s);
// 和下面两条语句相等
s.lastNameCaps = LastNameCaps;
s.lastNameCaps(); // WILLSON
```

### Inner functions

Javascript中的函数可以在另一个函数体内声明。嵌套函数的一个重要细节就是可以访问父函数体内的变量：

```javascript
function parentFunc() {
    var a = 1;

    function nestedFunc() {
        var b = 4;
        return a + b;
    }
    return nestedFunc();
}
```

## Closures

闭包是JS最强大功能之一 - 但是也往往是最容易出错的部分：

```javascript
function makeAdder(a) {
    return function(b) {
        return a + b;
    };
}
var x = makeAddr(5);
var y = makeAddr(20);
x(6);   // 11
y(7);   // 27
```

`makeAdder()`函数字如其名：每次以一个函数调用它的时候会创建一个新的“adder”函数。

