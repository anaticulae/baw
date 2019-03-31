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
from os import makedirs
from os import remove
from os.path import exists
from os.path import isfile
from os.path import join
from subprocess import PIPE
from sys import stderr
from sys import stdout

BAW_EXT = '.baw'
GIT_EXT = '.git'
GIT_REPO_EXCLUDE = '.git/info/exclude'
TMP = '.tmp'

SUCCESS = 0

NEWLINE = '\n'


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


def logging(msg: str = '', end=NEWLINE):
    print(msg, end=end)


def logging_error(msg: str):
    """Print error-message to stderr and add [ERROR]-tag"""
    print('\n[ERROR] %s\n' % msg, file=stderr)


def flush():
    """Flush stdout"""
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


def tmp(root):
    """Return path to temporary folder. If not exists, create folder

    Args:
        root(str): project root
    Returns:
        path to temporary folder
    """
    assert root
    tmp = join(root, TMP)
    makedirs(tmp, exist_ok=True)
    return tmp


def check_root(root: str):
    if not exists(root):
        raise ValueError('Project root does not exists' % root)


def file_append(path: str, content: str):
    assert exists(path)
    with open(path, mode='a', newline=NEWLINE) as fp:
        fp.write(content)


def file_create(path: str, content: str = ''):
    assert not exists(path)
    with open(path, mode='w', newline=NEWLINE) as fp:
        fp.write(content)


def file_read(path: str):
    assert exists(path), path
    with open(path, mode='r', newline=NEWLINE) as fp:
        return fp.read()


def file_remove(path: str):
    assert exists(path), path
    assert isfile(path), path
    remove(path)


def file_replace(path: str, content: str):
    """Replace file content"""
    if not exists(path):
        file_create(path, content)
        return
    current_content = file_read(path)
    if current_content == content:
        return

    with open(path, mode='w', newline=NEWLINE) as fp:
        fp.write(content)
