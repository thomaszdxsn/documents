import linecache

no_such_file = linecache.getline(
    'this_file_does_not_exists.txt', 1)
print('NO FILE: {!r}'.format(no_such_file))
