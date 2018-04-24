import pathlib

p = pathlib.Path('./source/pathlib/pathlib_name.py')
print('path    : {}'.format(p))
print('name    : {}'.format(p.name))
print('suffix  : {}'.format(p.suffix))
print('stem    : {}'.format(p.stem))
