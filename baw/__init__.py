from os.path import abspath
from os.path import dirname
from os.path import join
from sys import stderr

__version__ = '0.0.1'

THIS = dirname(__file__)
ROOT = abspath(join(THIS, '..'))


def print_error(msg: str):
    """Print error-message to stderr and add [ERROR]-tag"""
    print('\n[ERROR] %s\n' % msg, file=stderr)
