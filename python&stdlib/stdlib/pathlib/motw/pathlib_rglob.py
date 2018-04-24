"""
rglob == recursive glob
"""

import pathlib


p = pathlib.Path('..')


for f in p.rglob('pathlib_*.py'):
    print(f)
