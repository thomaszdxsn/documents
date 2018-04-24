import collections

import pytest


@pytest.fixture
def data():
    a = {'a': 'A', 'c': 'C'}
    b = {'b': 'B', 'c': 'D'}
    return a, b


def test_chainmap_constructor(data):
    a, b = data
    m = collections.ChainMap(a, b)

    assert m['c'] == 'C'


def test_chainmap_reordering(data):
    a, b = data
    m = collections.ChainMap(a, b)
    m.maps = reversed(m.maps)

    assert m['c'] == 'D'


def test_chainmap_update(data):
    a, b = data
    m = collections.ChainMap(a, b)
    assert m['c'] == 'C'

    a['c'] = 'E'
    assert m['c'] == 'E'

    m['c'] = 'F'
    assert a['c'] == 'F'


def test_chainmap_newchild(data):
    a, b = data
    m = collections.ChainMap(a, b)
    m2 = m.new_child()
    assert len(m.maps) == 2
    assert len(m2.maps) == 3

    m2['c'] = 'E'
    assert m2['c'] == 'E'
    assert m['c'] == 'C'

    c = {'c': 'E'}
    m3 = m.new_child(c)
    assert len(m3) == 3
    assert m3['c'] == 'E'


def test_chainmap_newchild(data):
    a, b = data
    c = {'c': 'E'}
    m = collections.ChainMap(c, a, b)
    assert m['c'] == 'E'
    assert m.parents['c'] == 'C'
    assert m.parents.parents['c'] == 'D'
