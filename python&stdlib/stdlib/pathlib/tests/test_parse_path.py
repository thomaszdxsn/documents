import pathlib


def test_pathlib_parts():
    p = pathlib.Path('/usr/local')
    parts = list(p.parts)
    assert parts == ['/', 'usr', 'local']


def test_pathlib_parents():
    p = pathlib.Path('/usr/local/lib')
    parent = p.parent
    assert str(parent) == '/usr/local'

    parents = list(str(path) for path in p.parents)
    assert parents == ['/usr/local', '/usr', '/']


def test_pathlib_name():
    p = pathlib.Path('./source/pathlib/pathlib_name.py')

    assert str(p) == 'source/pathlib/pathlib_name.py'
    assert str(p.name) == 'pathlib_name.py'
    assert str(p.suffix) == '.py'
    assert str(p.stem) == 'pathlib_name'
