###############################################################################
#                                Kiwi Project                                 #
#                                    2019                                     #
#                          Helmut Konrad Fahrendholz                          #
#                             kiwi@derspanier.de                              #
###############################################################################

from configparser import ConfigParser
from contextlib import contextmanager
from functools import partial
from os import environ
from os.path import join
from subprocess import PIPE
from sys import stderr
from sys import stdout

BAW_EXT = '.baw'
GIT_EXT = '.git'


@contextmanager
def handle_error(*exceptions, code=1):
    """Catch given `exceptions` and print there message to `stderr`. Exit
    system with given `code`.

    Args:
        exeception(iterable): of exception, which are handle by this context
        code(int): returned error-code
    Raises:
        SystemExitExecetion if given `exceptions` is raised while executing
        contextmanager.
    """
    try:
        yield
    except exceptions as error:
        print('[ERROR] %s' % error, file=stderr)
        exit(code)


print = partial(print, file=stdout, flush=True)


def logging(msg: str = ''):
    print(msg)


def logging_error(msg: str):
    """Print error-message to stderr and add [ERROR]-tag"""
    print('\n[ERROR] %s\n' % msg, file=stderr)


def flush():
    print('', end='', flush=True)


def get_setup():
    try:
        internal = int(environ['HELPY_INT_PORT'])
        external = int(environ['HELPY_EXT_PORT'])
        adress = environ['HELPY_URL']
        return (adress, internal, external)
    except KeyError as error:
        print_error('Missing global var %s' % error)
        exit(1)
