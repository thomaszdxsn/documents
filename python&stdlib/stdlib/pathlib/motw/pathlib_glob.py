import pathlib

p = pathlib.Path('.')

for f in p.glob('*.py'):
    print(f)
