## Stdlib doc

- 故意不支持对`update()`传入字符串，因为hash是对应bytes的，不是对应字符的.

- 可获取的算法可以通过`hashlib.algorithms_available()`来查看

源码主要是C实现，所以暂时看不懂的。

关键字: blake2

## Reference

- [hash函数](https://en.wikipedia.org/wiki/Hash_function)
- [加密hash函数](https://en.wikipedia.org/wiki/Cryptographic_hash_function#Cryptographic_hash_algorithms)

