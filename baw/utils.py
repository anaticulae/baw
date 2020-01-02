#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019-2020 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================

import sys
from contextlib import contextmanager
from os import chmod
from os import environ
from os import makedirs
from os import remove
from os.path import abspath
from os.path import dirname
from os.path import exists
from os.path import isfile
from os.path import join
from shutil import rmtree
from stat import S_IWRITE
from time import time

ROOT = abspath(join(dirname(__file__), '..'))  #  Path to installed baw-tool

BAW_EXT = '.baw'
TMP = '.tmp'

REQUIREMENTS_TXT = 'requirements.txt'

SUCCESS = 0
FAILURE = 1

INPUT_ERROR = 2

NEWLINE = '\n'
UTF8 = 'utf8'


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
        logging_error(error)
        exit(code)


def logging(msg: str = '', end: str = NEWLINE):
    """Write message to logger

    Args:
        msg(str): message to log
        end(str): lineending
    Hint:
        Logging with default arguments will log a newline
    """
    msg = forward_slash(msg)
    print(msg, end=end, file=sys.stdout, flush=True)


def logging_error(msg: str):
    """Print error-message to stderr and add [ERROR]-tag"""
    # use forward slashs
    msg = forward_slash(msg)
    print('[ERROR] %s' % msg, file=sys.stderr, flush=True)


PLAINOUTPUT = 'PLAINOUTPUT'
SAVEGUARD = 'IAMTHESAVEGUARDXYXYXYXYXYXYXYXYXYXYXY'
SECOND_GUARD = 'OHMANIHAVETGOLEARNMOREPYTHONTHATS'


def forward_slash(content: str, save_newline=True):
    # TODO: HACK
    if PLAINOUTPUT in environ:
        return content
    content = str(content)
    if save_newline:
        # Save newline
        content = content.replace('\n', SECOND_GUARD)
        content = content.replace(r'\n', SAVEGUARD)
    # Forward slash
    content = content.replace(r'\\', '/').replace('\\', '/')
    if save_newline:
        # Restore newline
        content = content.replace(SECOND_GUARD, '\n')
        content = content.replace(SAVEGUARD, r'\n')
    return content


def get_setup():
    try:
        adress = environ['HELPY_URL']
        internal = int(environ['HELPY_INT_PORT'])
        external = int(environ['HELPY_EXT_PORT'])
        return (adress, internal, external)
    except KeyError as error:
        logging_error('Missing global var %s' % error)
        exit(FAILURE)


def package_address():
    try:
        internal = environ['HELPY_INT_DIRECT']
        external = environ['HELPY_EXT_DIRECT']
        return (internal, external)
    except KeyError as error:
        logging_error('Missing global var %s' % error)
        exit(FAILURE)


def tmp(root):
    """Return path to temporary folder. If not exists, create folder

    Args:
        root(str): project root
    Returns:
        path to temporary folder
    """
    assert root
    path = join(root, TMP)
    makedirs(path, exist_ok=True)
    return path


def check_root(root: str):
    if not exists(root):
        raise ValueError('Project root does not exists' % root)


def file_append(path: str, content: str):
    assert exists(path), str(path)
    with open(path, mode='a', newline=NEWLINE) as fp:
        fp.write(content)


def file_create(path: str, content: str = ''):
    assert not exists(path), str(path)
    with open(path, mode='w', newline=NEWLINE) as fp:
        fp.write(content)


def file_read(path: str):
    assert exists(path), str(path)
    with open(path, mode='r', newline=NEWLINE) as fp:
        return fp.read()


def file_remove(path: str):
    assert exists(path), str(path)
    assert isfile(path), str(path)
    remove(path)


def file_replace(path: str, content: str):
    """Replace file content

    1. If not exists, create file
    2. If exists,     compare content, if changed than replace
                                       if not, do nothing
    Args:
        path(str): path to file
        content(str): content to write
    """
    if not exists(path):
        file_create(path, content)
        return
    current_content = file_read(path)
    if current_content == content:
        return

    with open(path, mode='w', newline=NEWLINE) as fp:
        fp.write(content)


def print_runtime(before: int):
    """Determine runtime due the diff of current time and provided time
    `before`. Log this timediff.

    Args:
        before(int): time recorded some time before - use time.time()
    """
    time_diff = time() - before
    logging('Runtime: %.2f secs\n' % time_diff)


@contextmanager
def profile():
    """Print runtime to logger to monitore performance"""
    start = time()
    try:
        yield
    except Exception:
        print_runtime(start)
        raise
    else:
        print_runtime(start)


def remove_tree(path: str):
    assert exists(path)
    try:

        def remove_readonly(func, path, _):
            "Clear the readonly bit and reattempt the removal"
            chmod(path, S_IWRITE)
            func(path)

        rmtree(path, onerror=remove_readonly)
    except PermissionError:
        logging_error('Could not remove %s' % path)
        exit(FAILURE)


def skip(msg: str):
    """Logging skipped event

    Args:
        msg(str): message to skip"""
    logging('Skip: %s' % msg)
