# tutorial

## Using the Image class

PIL中最重要的一个类是`Image`类，它定义在`Image`模块中.

你可以有几种方式来实例化这个类：可以载入一个图片文件，处理其它的图片，或者
从scratch开始创建一个图片。

想要把一个文件的图片读入，可以使用`Image`模块的`open()`函数:

```python
>>> from PIL import Image
>>> im = Image.open('hpper.ppm')
```

如果成功，这个函数将会返回一个Image对象。

你现在可以使用实例的属性来检查文件的内容了.

```python
>>> print(im.format, im.size, im.mode)
PPM (512, 512) RGB
```

`format`属性标示图片的资源。

如果图片不是读取自一个文件，`format`属性的值会是None。

`size`属性是一个2-tuple，代表宽x高(像素)。

`mode`属性定义图片的bands的名称，以及像素类型和深度。

一般"L"代表灰度图片，"RGB"代表彩色图片，"CMYK"代表pre-press图片.

如果图片不能打开，将会跑出IOError。

一旦你有了一个Image类的实例，你可以用这个实例的一些方法来处理图片。

例如，你可以通过下面这条代码来显示图片：

`>>> im.show()`

## Reading and writing images

PIL支持很多种图片文件格式。

想要在硬盘中读取文件，可以使用`Image.open()`。你不需要知道文件实际的格式是什么，
这个库会自己推算出文件格式.

想要保存这个文件，可以使用`Image.save()`。

在保存文件的时候，文件名很重要。除非你指定了格式，这个库都会根据文件格式指定
后缀名。

### Convert files to JPEG

```python
import os
import sys
from PIL import Image

for infile in sys.argv[1:]:
    f, e = os.path.splitext(infile)
    outfile = f + '.jpg'
    if infile != outfile:
        try:
            Image.open(infile).save(outfile)
        except IOError:
            print('cannot convert', infile)
```

`save()`方法的第二个参数可以用来指定文件格式。如果你使用了一个非标准的
文件扩展名，你必须这样做：

### Create JPEG thumbnails

```python
import os
import sys
from PIL import Image


size = (128, 128)


for infile in sys.argv[1:]:
    outfile = os.path.splittext(infile)[0] + '.thumbnail'
    if infile != outfile:
        try:
            im = Image.open(infile)
            im.thumbnail(size)
            im.save(outfile, 'JEPG')
        except IOError:
            print("connot create thumbnail for", infile)
```

请记住，这个库不会试图解码或者读取raster数据，除非真的需要那么做。

在你打开一个文件的时候，这个文件的头部将会被读取，用来确定这个文件的格式，
或者诸如mode，size等属性。

这意味打开文件是一个相对快速的操作，它和文件的大小或者压缩类型无关。

### Identify Image Files

```python
import sys
from PIL import Image


for infile in sys.argv[1:]:
    try:
        with Image.open(infile) as im:
            print(infile, im.format, "%dx%d" % im.size, im.mode)
    except IOError:
        pass
```

## Cutting, pasting, and merging images

`Image`类包含一些方法，可以让你操控图片的一些区域。

想要从图片中截取一小部分，可以用`crop()`方法。

### Copying a subrectangle from an image

```python
box = (100, 100, 400, 400)
region = im.crop(box)
```

region定义为4-tuple，它们代表坐标(左，上，右，下)。

PIL使用坐标系统，比如(0, 0)来代表左上角。

注意，坐标是相对于像素的为止，所以上面的例子其实是(300x300)像素。

### Processing a subrectangle, and pasting it back

```python
region = region.transpose(Image.ROTATE_180)
im.paste(region, box)
```

### Rolling an image

```python
def roll(image, delta):
    xsize, ysize = image.size

    delta = delta % xsize
    if delta == 0: return image

    part1 = image.crop((0, 0, delta, ysize))
    part2 = image.crop((delta, 0, xsize, ysize))
    part1.load()
    part2.load()
    image.paste(part2, (0, 0, xsize - delta, ysize))
    image.paste(part1, (xsize - delta, 0, xsize, ysize))

    return image
```

### Splitting and mergin bands

```
r, g, b = im.split()
im = Image.merge('RGB', (b, g, r))
```

## Geometrical transforms

`PIL.Image.Image`类包含`resize()`和`rotate()`方法，前面一个方法可以给图片一个
新的尺寸，后者可以变换图片的角度。

### Simple geometry transforms

```python
out = im.resize((128, 128))
out = im.rotate(45)
```

### Transposing an image

```
out = im.transpose(Image.FLIP_LEFT_RIGHT)
out = im.transpose(Image.FLIP_TOP_BOTTOM)
out = im.transpose(Image.ROTATE_90)
out = im.transpose(Image.ROTATE_180)
out = im.transpose(Image.ROTATE_270)
```

## Color transforms

PIL通过`convert()`方法，可以转换image的像素表达形式。

### Converting between modes

```python
from PIL import Image
im = Image.open("hopper.ppm").convert("L")
```

上面这个方法可以把图片转换为灰度图片。

## Image enhancement

ImageFilter模块包含了很多预先定义的filter，可以用于`.filter()`方法。

### Filters

#### Applying filters

```python
from PIL import ImageFilter
out = im.filter(ImageFilter.DETAIL)
```

### Point Operations

`.point()`方法可以用来翻译一个图片的像素值。

多数情况下，这个方法期待接受一个函数，这个函数接受一个参数（像素）。

#### Appliying point transforms

```python
out = im.point(lambda i: i = 1.2)
```

#### Processing individual bands

```python
# 将图片分割成单独的bands
source = im.split()

R, G, B = 0, 1, 2

# 选择少于100的区域
mask = source[R].point(lambda i: i < 100 and 255)   # pixle & 255

# 处理 green band
out = source[G].point(lambda i: i * 0.7)

# 黏贴处理过的band，但是mask只有在red < 100的时候才会不为0
source[G].paste(out, None, mask)

# 创建一个新的 multiband 图片
im = Image.merge(im.mode, source)
```

### Enhancement

对于更加高级的图像处理，你可以使用`ImageEnhance`模块.

#### Enhancing images

```python
from PIL import ImageEnhance

enh = ImageEnhance.Contrast(im)
enh.enhance(1.3).show('30% more contrast')
```

## Image Sequence

PIL包含一些对image序列的基础支持。

支持的序列格式包括FLI/FLC, GIF，以及一些高级模式。

当你打开一个序列化文件的时候，PIL会自动读取它序列中的第一帧。

你可以使用`.seek()`，移动到你想要去的那一帧。

### Reading sequence

```python
from PIL import Image

im = Image.open('animation.gif')
im.seek(1)

try:
    while 1:
        im.seek(im.tell() + 1)
except EOFError:
    pass
```

注意，大多数版本的PIL只允许你打开下一帧，如果想要之前的帧，你需要重新打开图片。

### Using the ImageSequence Iterator class

```python
from PIL import ImageSequence
for frame import ImageSequence.Iterator(im):
    # ...
```

## Postscript printing

### Drawing Postscript

```python
from PIL import Image
from PIL import PSDraw

im = Image.open('hopper.ppm')
title = 'hopper'
box = (1 * 72, 2 * 72, 7 * 72, 10 * 72)

ps = PSDraw.PSDraw()
ps.begin_document(title)

ps.image(box, im, 75)
ps.rectangle(box)

ps.setfont('HelveticaNarrow.Bold', 36)
ps.text((3 * 72, 4 * 72), title)

ps.end_document()
```

## More on reading images

### Reading from an open file

```python
from PIL import Image
with open('hopper.ppm', 'rb') as fp:
    im = Image.open(fp)
```

### Reading from a string

```python
import StringIO

im = Image.open(StringIO.StringIO(buffer))
```

### Reading from a tar archive

```python
from PIL import Image, TarIO

fp = TarIO.TarIO('Tests/images/hopper.tar', 'hopper.jpg')
im = Image.open(fp)
```

## Controlling the decoder

...
