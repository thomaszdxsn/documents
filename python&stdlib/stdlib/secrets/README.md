## Motivation

这个模块的起因是，OpenBSD的开发者Theo de Raadt，联系了Guido，他担心Python
的标准库容易让开发者在很疏忽的情况下创造一些安全问题，于是有了这个标准库。

虽然`random`模块的官方文档已经说明，它的默认`Random`实现是有安全漏洞的。但是
Raadt仍然觉得警告容易被开发者忽略。

## Reference

[PEP506](https://www.python.org/dev/peps/pep-0506/) | 这个模块的PEP

[Raddt联系Guido的邮件](https://mail.python.org/pipermail/python-ideas/2015-September/035820.html) | 描述了他担心的问题



