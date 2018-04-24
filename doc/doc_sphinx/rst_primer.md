# reStructuredText Primer

reStructuredText是Sphinx默认使用的文本标记型语言。

这篇文章主要介绍rst的基础概念和语法。

[reStructuredText User Documentation](http://docutils.sourceforge.net/rst.html)

## Paragraphs

段落是reST的基础构块。

段落即那些和其它文本用空行间隔的文本。

和Python一样，reST的缩进也很重要。一个段落的所有行都必须在左对齐的时候保持相同
的缩进。

## Inline markup

标准的reST inline markup都很简单：

- 一个星号：`*text*`，代表重点(斜体)
- 两个星号: `**text**`，代表强调(粗体)
- 反引号：`\`\`text\`\``，代表代码样本

如果星号或者反引号是文本的一部分，你不想让它们变为标记，应该使用反斜杠来进行
转义。

这些标记有一些限制：

- 它们可能不可以嵌套
- 标记内的文本前后不能有空格，比如`* text*`是错误的
- 如果标记前后有字符，必须用空格分割。

## List and Quote-like blocks


