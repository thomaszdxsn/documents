## Motivation

这个模块的主要作用是，实现了RFC3548定义的编码和解码函数，
定义了Base16, Base32, 和Base64算法，以及Ascii85和Base85的事实标准实现。

RFC3548定义的编码适合用来转码二进制数据，可以将它们安全地通过email发送，
也可以用作URLs的部分，或者包含在HTTP POST请求数据中。

这个模块提供了两套接口。

现在的这套接口可以用来处理类bytes对象 <-> ascii bytes 的转码/编码。

旧的一套接口并不支持解码字符串，但是它支持对文件对象进行编码/解码。

## Reference

-- | --
[RFC1521](https://tools.ietf.org/html/rfc1521.html) | MIME的第一部分: 描述网络消息体格式的一套机制
[RFC2045](https://tools.ietf.org/html/rfc2045.html) | MIME的第一部分：网络消息的格式
[RFC3548](https://tools.ietf.org/html/rfc3548.html) | Base16, Base32和Base64这些数据编码的定义
[RFC1924](https://tools.ietf.org/html/rfc1924.html) | IPv6的简洁表达形式

