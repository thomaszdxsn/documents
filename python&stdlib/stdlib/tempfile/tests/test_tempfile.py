import pathlib
import tempfile

import pytest


def test_TemporaryFile():
    with tempfile.TemporaryFile('w+t') as temp:
        temp.write('hello world')
        temp.seek(0)
        assert temp.read() == 'hello world'


def test_TemporaryFile_close_but_ValueError():
    with tempfile.TemporaryFile('w+t') as temp:
        temp.write('hello world')

    with pytest.raises(ValueError):
        temp.read()


def test_NamedTemporaryFile():
    with tempfile.NamedTemporaryFile() as temp:
        assert temp.name is not None

        f = pathlib.Path(temp.name)

    assert not f.exists()


def test_SpooledTemporaryFile():
    from io import StringIO, TextIOWrapper
    with tempfile.SpooledTemporaryFile(max_size=100,
                                       mode='w+t',
                                       encoding='utf-8') as temp:
        for i in range(3):
            temp.write('This line is 33.00000 over characcter.\n')
            if i < 2:
                assert temp._rolled is False
                assert isinstance(temp._file, StringIO)
            else:
                assert temp._rolled is True
                assert isinstance(temp._file, TextIOWrapper)


def test_TemporaryDirectory():
    with tempfile.TemporaryDirectory() as directory_name:
        assert isinstance(directory_name, str)
        the_dir = pathlib.Path(directory_name)
        a_file = the_dir / 'a.txt'
        a_file.touch()
        assert a_file.exists()
    assert not a_file.exists()



