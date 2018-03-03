# Arrow Function

**箭头函数表达式**相比`function expression`更加简洁，并没有属于它自己的`this`, `arguments`, `super`或者`new.target`.

## Syntax

### Basic Syntax

```javascript
(param1, param2, ..., paramN) => { statements }
(param1, param2, ..., paramN) => expression
// 等同于 => { return expression; }

// 如果只有一个参数，也可以不用括号
(singleParam) => { statements }
singleParam => { statements }

// 无参数箭头函数，必须加上一对括号
() => { statements }
```

### Advanced Syntax

```javascript
// 如果函数体返回一个对象字面量，需要外面加上一对括号
params => ({foo: bar})

// 支持Rest参数和默认参数
(param1, param2, ...rest) => { statements }
(param1 = defaultValue1, param2, ..., paramN = defaultValueN) => { statements } 

// 支持参数unpack
var f = ([a, b] = [1, 2], [x: c] = {x: a + b}) => a + b + c; f(); // 6
```

## Description

### Shorter functions

```javascript
var materials = [
  'Hydrogen',
  'Helium',
  'Lithium',
  'Beryllium'
];

materials.map(function(material) {
    return material.length;
}); // [[8, 6, 7, 9]

materials.map((material) => {
    return material.length;
}); // [8, 6, 7, 9]

materials.map(({length}) => length); // [8, 6, 7, 9]
```

### No seperate `this`

```javascript
function Person() {
    // Person()构造器定义了`this`作为实例本身
    this.age = 0;

    setInterval(function growUp() {
        // 在non-strict模式中，growUp()函数定义`this`作为全局对象，
        // 这和构造器中的意义不一样
        this.age++;
    }, 1000)
}

var p = new Person();
```

在ECMA3/5中，`this`值可以提前赋值给一个变量：

```javascript
function Person() {
    var that = this;
    that.age = 0;

    setInterval(function growUp() {
        that.get++;
    }, 1000);
}
```

箭头函数没有它自己的this；所以可以在闭包中使用`this`:

```javascript
function Person() {
    this.age = 0;

    setInteval(() => {
        this.age++;
    }, 1000);
}

var p = new Person;
```

#### Relation with strict mode

```javascript
var f = () => { 'use strict'; return this; };
f() === window; // or the global object
```

#### Invoked through call or apply

由于箭头函数没有它自己的this，方法`call()`和`apply()`只可以传入参数，第一个参数`thisArg`会被忽略。

```javascript
var adder = {
    base: 1,

    add: function(a) {
        var f = v => v + this.base;
        return f(a);
    },

    addThruCall: function(a) {
        var f = v => v + this.base;
        var b = {
            base: 2
        };

        return f.call(b, a);
    }
};

console.log(adder.add(1)); // 2
console.log(adder.addThruCall(1)); // 2
```

### No binding of `arguments`

箭头函数没有它自己的`arguments`对象：

```javascript
var arguments = [1, 2, 3];
var arr = () => arguments[0];

arr(); // 1

function foo(n) {
    var f = () => arguments[0] + n;
    return f();
}

foo(1); // 2
```

大多数时候应该使用rest参数来替代arguments对象：

```javascript
function foo(n) {
    var f = (...args) => args[0] + n;
    return f(10);
}

foo(1); // 11
```

### Arrow functions used as methods

```javascript
'use strict';

var obj = {
    i: 10,
    b: () => console.log(this.i, this),
    c: function() {
        console.log(this.i, this);
    }
}

obj.b(); // undefined, Window(or Global)
obj.c(); // 10, Object {...}
```

箭头函数没有它自己的this。另外一个例子是`Object.defineProperty()`:

```javascript
'use strict';

var obj = {
    a: 10
};

Object.defineProperty(obj, 'b', {
    get: () => {
        console.log(this.a, typeof this.a, this); undefined 'undefined' Window(or Global)
        return this.a + 10; 
    }
})
```

### Use of the `new` operator

因为箭头函数不能用于构造器，所以如果将它用于new则会抛出错误:

```javascript
var Foo = () => {};
var foo = new Foo(); // TypeError
```

### Use of `prototype` property

箭头函数没有自己的`prototype` property:

```javascript
var Foo = () => {};
console.log(Foo.property); // undefined
```

### Use of the `yield` keyword

箭头函数的函数体内不能使用`yield`关键字。

## Function body

箭头函数可以有“简洁的函数体”或者“块级函数体".

```javascript
var func = x => x * x;
// 简洁函数体，隐式使用return

var func = (x, y) => { return x + y; };
// 在块级函数体内，需要显式用return
```

## Returning object literals

注意在简洁函数体内要返回对象字面量，如果用这样的语法：`params => {object: literal}`不会有效：

```javascript
var func = () => { foo: 1};
// 调用func会返回undefined

var func = () => { foo: function() {}};
// 语法错误：函数语句需要名称
```

这是因为`{}`中的代码会看作是语句来执行。

**记住**，要使用括号：

```javascript
var func = () => ({foo: 1})
```

## Line breaks

箭头函数不可以在参数和箭头之间换行：

```javascript
var func = () 
            => 1;
// SyntaxError: expected expression, got '=>'
```

## Parsing order

虽然箭头函数的函数不是一个操作符，箭头函数在操作符优先级中仍然有一个特殊规则：

```javascript
let callback;

callback = callback || function() {}; // ok

callback = callback || () => {};
// SyntaxError: invalid arrow-function arguments

callback = callback || (() => {}); // ok
```

## More examples

```javascript
// 一个空箭头函数，返回undefined
let empty = () => {};

(() => 'foobar')();
// 返回'foobar'
// 这是立即执行函数表达式(IIFE)

var simple = a => a > 15 ? 15 : a;
simple(16); // 15
simple(10); // 10

let max = (a, b) => a > b ? a : b;

# 适合用于数组的map，filter
var arr = [5, 6, 13, 0, 1, 18, 23];

var sum = arr.reduce((a, b) => a + b);
// 66

var even = arr.filter(v => v % 2 == 0);
// [6, 0, 18]

var double = arr.map(v => v * 2);
// [10, 12, 26, 0, 2, 36, 46]

// 更简洁的promise链
promise.then(a => {
    // ...
}).then(b => {
    // ...
});

// 无参数的箭头函数
setTimeout(() => {
    console.log('I happen sonner');
    setTimeout(() => {
        console.log('I happen later');
    }, 1);
}, 1);
```