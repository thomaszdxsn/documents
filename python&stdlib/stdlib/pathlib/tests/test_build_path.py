import pathlib


def test_pathlib_operator():
    usr = pathlib.PurePosixPath('/usr')
    assert str(usr) == '/usr'

    usr_local = usr / 'local'
    assert str(usr_local) == '/usr/local'

    usr_share = usr / pathlib.PurePosixPath('share')
    assert str(usr_share)

    root = usr / '..'
    assert str(root) == '/usr/..'

    etc = root / '/etc/'
    assert str(etc) == '/etc'


def test_pathlib_resolve():
    usr = pathlib.Path('/usr')
    root = usr / '..'
    assert str(root.resolve()) == '/'

    usr_local = usr / 'local'
    share = usr_local / '..' / 'share'
    assert str(share.resolve()) == '/usr/share'


def test_pathlib_joinpath():
    root = pathlib.Path('/')
    subdirs = ['usr', 'local']
    usr_local = root.joinpath(*subdirs)
    assert str(usr_local) == '/usr/local'


def test_pathlib_from_existing():
    ind = pathlib.Path('/pathlib/index.rst')
    assert str(ind) == '/pathlib/index.rst'

    py = ind.with_name('pathlib_from_existing.py')
    assert str(py) == '/pathlib/pathlib_from_existing.py'
