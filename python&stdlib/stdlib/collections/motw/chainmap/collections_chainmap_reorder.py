import collections

a = {'a': 'A', 'c': 'C'}
b = {'b': 'B', 'c': 'D'}

m = collections.ChainMap(a, b)

print(m.maps)
print('c = {}\n'.format(m['c']))

m.maps = list(reversed(m.maps))

print(m.maps)
print('c = {}'.format(m['c']))


