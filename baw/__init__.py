from functools import partial
from os import makedirs
from os.path import abspath
from os.path import dirname
from os.path import join
from sys import stderr
from sys import stdout

__version__ = '0.1.1'

THIS = dirname(__file__)
ROOT = abspath(join(THIS, '..'))


def TMP():
    tmp = join(ROOT, 'tmp')
    makedirs(tmp, exist_ok=True)
    return tmp
