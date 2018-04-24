import pathlib


usr_local = pathlib.Path('/usr/local')
share = usr_local / '..' / 'share'
print(share, share.resolve())
