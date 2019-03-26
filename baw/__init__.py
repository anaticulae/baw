from functools import partial
from os.path import abspath
from os.path import dirname
from os.path import join

__version__ = '0.1.1'

THIS = dirname(__file__)
ROOT = abspath(join(THIS, '..'))
