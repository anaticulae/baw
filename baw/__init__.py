from functools import partial
from os.path import abspath
from os.path import dirname
from os.path import join
from sys import stderr
from sys import stdout

__version__ = '0.0.1'

THIS = dirname(__file__)
ROOT = abspath(join(THIS, '..'))

print = partial(print, file=stdout, flush=True)


def logging(msg: str):
    print(msg)


def logging_error(msg: str):
    """Print error-message to stderr and add [ERROR]-tag"""
    print('\n[ERROR] %s\n' % msg, file=stderr)
