# Overview

PIL, Python Image Library，是一个用来图像处理的python库。

这个库(pillow)提供了额外的格式支持，内部对象的表达，以及更强大
的图像处理能力。

核心的image库设计与访问以像素格式存储的数据。它是所有图像处理工具的基础。

## Image Archives

你可以用PIL来创建thumbnails，转换文件格式，打印图片，等等...

## Image Display

当前主要有Tk的`PhotoImage`和`SitmapImage`两个接口，以及Windows DIB接口.

## Image Processing

这个库包含基础的图像处理功能，包括点操作，过滤，以及色彩空间转换。

这个库还支持图片resize，rotation，以及任意形式的变形。

另外还有一个柱形图方法，可以让你将一些统计数据拉入图片。
