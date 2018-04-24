import pathlib


def test_pathlib_convenience():
    home = pathlib.Path.home()
    assert str(home) == '/Users/zhouyang'
    cwd = pathlib.Path.cwd()
    assert '/Users/zhouyang' in str(cwd)


def test_pathlib_iterdir():
    p = pathlib.Path('.')
    for f in p.iterdir():
        f = str(f)
        if f.endswith('.py'):
            assert f.startswith('test')


def test_pathlib_glob():
    p = pathlib.Path('.')

    for f in p.glob('*.py'):
        assert str(f).startswith('test')


def test_pathlib_rglob():
    p = pathlib.Path('..')
    for f in p.glob('*.py'):
        assert ('tests' in str(f)) or ('motw' in str(f))
