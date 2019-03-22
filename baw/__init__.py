from functools import partial
from os.path import abspath
from os.path import dirname
from os.path import join
from sys import stderr
from sys import stdout

__version__ = '0.0.2'

THIS = dirname(__file__)
ROOT = abspath(join(THIS, '..'))
