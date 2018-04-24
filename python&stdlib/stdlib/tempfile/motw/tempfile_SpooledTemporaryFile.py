"""
幽灵文件：

  在达到阈值之前，文件内容都存在内存中，使用io.BytesIO或者io.StringIO.

  达到阈值之后才会写入到磁盘中
"""

import tempfile


with tempfile.SpooledTemporaryFile(max_size=100,
                                   mode='w+t',
                                   encoding='utf-8') as temp:
    print('temp: {!r}'.format(temp))

    for i in range(3):
        temp.write('This line is repeated over and over.\n')
        print(temp._rolled, temp._file)
