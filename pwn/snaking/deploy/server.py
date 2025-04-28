#!/usr/bin/python3

import sys
import signal
import tempfile
import os

def timeout(signum, stack):
    print('Timeout!')
    sys.exit(1)

signal.signal(signal.SIGALRM, timeout)
signal.alarm(60)

sys.stdout.write('File size: ')
sys.stdout.flush()

size = int(sys.stdin.readline().strip())
if size > 1024 * 1024:
    sys.stdout.write('Too large!')
    sys.stdout.flush()
    sys.exit(1)

sys.stdout.write('Data: ')
sys.stdout.flush()

SANDBOX = '''
from bitset import bitset, install_seccomp

del __builtins__.id
install_seccomp()

'''
script = SANDBOX + sys.stdin.read(size)
filename = tempfile.mktemp()

with open(filename, 'w') as f:
    f.write(script)

os.system(f'python3 {filename}')
os.unlink(filename)
