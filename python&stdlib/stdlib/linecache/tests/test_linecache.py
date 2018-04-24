import tempfile
import linecache

import pytest

lorem = '''Lorem ipsum dolor sit amet, consectetuer
adipiscing elit.  Vivamus eget elit. In posuere mi non
risus. Mauris id quam posuere lectus sollicitudin
varius. Praesent at mi. Nunc eu velit. Sed augue massa,
fermentum id, nonummy a, nonummy sit amet, ligula. Curabitur
eros pede, egestas at, ultricies ac, apellentesque eu,
tellus.

Sed sed odio sed mi luctus mollis. Integer et nulla ac augue
convallis accumsan. Ut felis. Donec lectus sapien, elementum
nec, condimentum ac, interdum non, tellus. Aenean viverra,
mauris vehicula semper porttitor, ipsum odio consectetuer
lorem, ac imperdiet eros odio a sapien. Nulla mauris tellus,
aliquam non, egestas a, nonummy et, erat. Vivamus sagittis
porttitor eros.'''

@pytest.fixture
def temp_data_file():
    with tempfile.NamedTemporaryFile('w+t') as temp:
        temp.write(lorem)
        temp.flush()
        yield temp


def test_licache_getline(temp_data_file):
    src_line = lorem.split('\n')[4]
    cache_line = linecache.getline(temp_data_file.name, 5).strip()
    assert src_line == cache_line


def test_linecache_get_blank_line(temp_data_file):
    cache_line = linecache.getline(temp_data_file.name, 8)
    assert cache_line == '\n'


def test_linecache_get_overline(temp_data_file):
    cache_line = linecache.getline(temp_data_file.name, 500)
    assert cache_line == ''


def test_linecache_get_not_exists_file():
    cache_line = linecache.getline('notexits.txt', 1)
    assert cache_line == '' 
