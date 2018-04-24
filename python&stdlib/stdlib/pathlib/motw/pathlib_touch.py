import pathlib
import time


p = pathlib.Path('touched')
if p.exists():
    print('already exists')
else:
    print('creating now')

p.touch()
start = p.stat()

time.sleep(1)

p.touch()
end = p.stat()

print("Start:", time.ctime(start.st_mtime))
print("End:", time.ctime(end.st_mtime))
