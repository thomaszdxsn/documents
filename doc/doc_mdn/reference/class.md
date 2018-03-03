# Classes

## Defining classes

Classes是一种“特殊函数”，就像`function expressions`和`function declarations`意义，class语法同样有`class expressions`和`class declarations`.

### Class declarations

可以使用`class declarations`来定义类。使用关键字`class`:

```javascript
class Rectangle {
    constructor (height, width) {
        this.height = height;
        this.width = width;
    }
}
```

#### Hoisting

`function declarations`和`class declarations`的一个重要的不同之处就在于function declrations是会提升(hoisted)的而class declarations并不会。你需要首先声明类让后再去使用它，否则会抛出`ReferenceError`:

```javascript
var p = new Rectangle(); // ReferenceError

class Rectangle {}
```

### Class expressions

`class expression`是另一种定义类的方式。class expression可以命名也可以不命名：

```javascript
// unmaed
var Rectangle = class {
    constructor (height, width) {
        this.height = height;
        this.width = width;
    }
};

// named
var Rectangle = class Rectangle {
    constuctor (height, width) {
        this.height = height;
        this.width = width;
    }
}
```

## Class body and method definitions

class的body是大括号`{}`中的部分.这是你定义类成员的地方，如方法或者构造器。

### Strict mode

`class declarations`和`class expressions`的body是在**strict mode**中执行的。

### Constructor

`constuctor`方法是一个特殊的方法，用于一个class的初始化。如果一个class中有多个constructor方法则会抛出`SyntaxError`错误。

在constructor中可以使用`super`关键字来调用父类的constructor.

### Prototype methods

```javascript
class Rectangle {
    constructor (height, width) {
        this.height = height;
        this.width = width;
    }

    // Getter 使用`get`关键字
    get area() {
        return this.calcArea();
    }

    // Method
    calcArea() {
        return this.height * this.width;
    }
}

const square = new Rectangle(10, 10);

console.log(square.area); // 100
```

### Static methods

`static`关键字可以为class定义静态方法。静态方法不需要实例化即可调用，实例反而不能调用这个方法。静态方法通常用来为应用创建一些工具函数。

```javascript
class Point {
    constructor (x, y) {
        this.x = x;
        this.y = y;
    }

    static distance(a, b) {
        const dx = a.x - b.x;
        const dy = a.y - b.y;

        return Math.hypot(dx, dy);
    }
}

const p1 = new Point(5, 5);
const p2 = new Point(10, 10);

console.log(Point.distance(p1, p2)); // 7.0710678118654755
```

### Boxing with prototype and static methods

在一个静态/原型方法不使用this对象来调用，this的值会变为undefined。不会发生自动装箱(autoboxing):

```javascript
class Animal {
    speak() {
        return this;
    }

    static eat() {
        return this;
    }
}

let obj = new Animal();
obj.speak(); // Animal {}
let speak = obj.speak;
speak(); // undefined

Animal.eat(); // class Animal
let eat = Animal.eat;
eat(); // undefined;
```

如果我们使用基于传统函数形式的类，可以自动装箱(autoboxing):

```javascript
function Animal() { }

Animal.prototype.speak = function() {
    return this;
}

Animal.eat = function() {
    return this;
}

let obj = new Animal();
let speak = obj.speak;
speak();  // global object

let eat = Animal.eat;
eat();  // global object
```

## Sub classing with `extends`

`extends`关键字可以用在class declarations或者class expressions，可以用来创建一个类的子类：

```javascript
class Animal {
    constructor (name) {
        this.name = name;
    }

    speak() {
        console.log(this.name + ' make a noise.');
    }
}


class Dog extends Animal {
    speak() {
        console.log(this.name + 'barks.');
    }
}


var d = new Dog('Mitzie');
d.speak(); // Mitzie barks.
```

或者在传统的函数型类中：

```javascript
function Animal (name) {
    this.name = name;
}

Animal.prototype.speak = function() {
    console.log(this.name + ' make a noise.');
}

class Dog extends Animal {
    speak() {
        console.log(this.name = " barks.");
    }
}

var d = new Dog('Mitzie');
d.speak(); // Mitzie barks.
```

注意类不能继承一般对象。如果你一定要继承，可以使用`Object.setPrototypeOf()`:

```javascript
var Animal = {
    speak() {
        console.log(this.name + ' make a noise.')
    }
};


class Dog {
    consturctor (name) {
        this.name = name;
    }
}


Object.setPrototypeOf(Dog.prototype, Animal);

var d = new Dog('Mitzie');
d.speak(); // Mitzie makes a noise.
```

## Species

如果你想要继承`Array`.可以使用species模式来覆盖默认的构造器。

例如，当使用方法如`map()`并返回默认的构造器，你想要这个方法返回一个父`Array`对象，而不是`MyArray`对象。可以使用symbol`Symbol.species`:

```javascript
class MyArray extends Array {
    // 重写species
    static get [Symbol.species]() { return Array; }
}

var a = new MyArray(1, 2, 3);
var mapped = a.map(x => x * x);

console.log(mapped instanceof MyArray); // false
console.log(mapped instanceof Array); // true
```

## Super class calls with `super`

`super`关键字用来调用父类相符的方法：

```javascript
class Cat {
    constructor (name) {
        this.name = name;
    }

    speak () {
        console.log(this.name + ' make a noise.');
    }
}


class Lion extends Cat {
    speak() {
        super.speak();
        console.log(this.name + ' roars.');
    }
}


var l = new Lion('Fuzzy');
l.speak();
// Fuzzy makes a noise.
// Fuzzy roars.
```

## Mix-ins

抽象子类或者mix-ins是类的模版。ECMA的类只能有一个父类，所以不能多重继承。

所以必须这样实现mix-ins:

```javascript
// 匿名函数的class declarations
var calculatorMixin = Base => class exetends Base {
    calc() {}
};

var randomizerMixin = Base => class extends Base {
    randomize() {}
};

// 可以这样使用
class Foo {}
class Bar extends calculatorMixin(ramdomizerMixin(Foo)) {}
```


