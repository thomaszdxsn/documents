# CDN Links

可以通过CDN来构件React应用：


```html
<script crossorigin src="https://unpkg.com/react@16/umd/react.development.js"></script>
<script crossorigin src="https://unpkg.com/react-dom@16/umd/react-dom.development.js"></script>
```

## Why the crossorigin Attribute?

如果你通过CDN来使用React，我们推荐加入crossorigin属性:

`<script crossorigin src="..."></script>`

我们同样推荐你使用的CDN是否设置了`Access-Control-Allow-Origin: *`HTTP头部。

