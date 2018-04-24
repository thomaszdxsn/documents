"""
这个脚本介绍如何签名Pickle化的数据
"""

import hashlib
import hmac
import io
import pickle
import pprint


def make_digest(message):
    hash = hmac.new(
        b'secret-shared-key-goes-here',
        message,
        hashlib.sha1
    )
    return hash.hexdigest().encode('utf-8')


class SimpleObject:

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name


out_s = io.BytesIO()


o = SimpleObject('digest matches')
pickled_data = pickle.dumps(o)
digest = make_digest(pickled_data)
header = b'%s %d\n' % (digest, len(pickled_data))
print("WRITING: {}".format(header))
out_s.write(header)
out_s.write(pickled_data)


o = SimpleObject('digest does not match')
pickled_data = pickle.dumps(0)
digest = make_digest(b'not the pickled data at all')
header = b'%s %d\n' %(digest, len(pickled_data))
print('\nWRITING: [}'.format(header))
out_s.write(header)
out_s.write(pickled_data)

out_s.flush()

in_s = io.BytesIO(out_s.getvalue())

while True:
    first_line = in_s.readline()
    if not first_line:
        break
    incoming_digest, incoming_length = first_line.split(b' ')
    incoming_length = int(incoming_length.decode('utf-8'))
    print('\nREAD:', incoming_digest, incoming_length)

