import collections

a = {'a': 'A', 'c': 'C'}
b = {'b': 'B', 'c': 'C'}

m = collections.ChainMap(a, b)
print('Before: {}'.format(m['c']))
a['c'] = 'E'
print('After : {}'.format(m['c']))
print(m.maps)
