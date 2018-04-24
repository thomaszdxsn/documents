import pathlib


p = pathlib.Path('example_dir')

print('Creating {}'.format(p))
p.mkdir()
