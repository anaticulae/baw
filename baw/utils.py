#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019-2023 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================

import binascii
import concurrent.futures
import contextlib
import functools
import os
import random
import sys
import time
import webbrowser

import baw

BAW_EXT = '.baw'
TMP = '.tmp'

REQUIREMENTS_TXT = 'requirements.txt'
REQUIREMENTS_DEV = 'requirements.dev'
REQUIREMENTS_EXTRA = 'requirements.ext'

SUCCESS = 0
FAILURE = 1

INPUT_ERROR = 2

NEWLINE = '\n'
UTF8 = 'utf8'


@contextlib.contextmanager
def handle_error(*exceptions: list, code: int = 1):
    """Catch given `exceptions` and print there message to `stderr`. Exit
    system with given `code`.

    Args:
        exceptions(iterable): of exception, which are handle by this context
        code(int): returned error-code
    Raises:
        SystemExit: if given `exceptions` is raised while executing context
    Yields:
        Context: to run operation

    >>> with handle_error(ValueError, code=10):
    ...     raise ValueError('HeKo')
    Traceback (most recent call last):
    ...
        sys.exit(code)
    SystemExit: 10
    """
    try:
        yield
    except exceptions as failure:
        error(failure)
        sys.exit(code)


def log(msg: str = '', end: str = NEWLINE):
    """Write message to logger

    Args:
        msg(str): message to log
        end(str): lineending
    Hint:
        Logging with default arguments will log a newline
    """
    msg = forward_slash(msg)
    msg = fix_encoding(msg)
    print(msg, end=end, file=sys.stdout, flush=True)


def completed(completed, force: bool = False):  # pylint:disable=W0621
    if not completed.returncode and not force:
        return
    if completed.stdout and completed.stdout.strip():
        # stdout can be None
        log(completed.stdout)
    if completed.stderr and completed.stderr.strip():
        # stderr can be None
        log(completed.stderr)


def verbose(msg: str = '', end: str = NEWLINE, verbose: bool = False):  # pylint:disable=W0621
    if not verbose:
        return
    log(msg=msg, end=end)


def error(msg: str, end: str = NEWLINE):
    """Print error-message to stderr and add [ERROR]-tag"""
    # use forward slashs
    msg = forward_slash(msg)
    msg = fix_encoding(msg)
    print(f'[ERROR] {msg}', end=end, file=sys.stderr, flush=True)


def fix_encoding(msg: str) -> str:
    """Remove invalid character to display on console

    Args:
        msg(str): message with invalid character
    Returns:
        message `without` invalid character
    """
    # ensure to have str
    msg = str(msg)
    # convert for windows console
    encoding = 'cp1252' if 'win' in sys.platform else 'utf-8'
    # remove non valid char to avoid errors on win-console
    msg = msg.encode(encoding, errors='xmlcharrefreplace').decode(encoding)
    return msg


PLAINOUTPUT = 'PLAINOUTPUT'
SAVEGUARD = 'IAMTHESAVEGUARDXYXYXYXYXYXYXYXYXYXYXY'
SECOND_GUARD = 'OHMANIHAVETGOLEARNMOREPYTHONTHATS'


def forward_slash(content: str, save_newline=True):
    # TODO: HACK
    if PLAINOUTPUT in os.environ:
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


@functools.lru_cache(maxsize=16)
def tmp(root: str) -> str:
    """Return path to temporary folder. Create folder if required.

    Args:
        root(str): project root
    Returns:
        path to temporary folder

    >>> tmp(baw.ROOT)
    '...'
    """
    assert root
    # queuemo-1.17.2-py3.8.egg
    projectname = os.path.split(root)[1].split('-')[0]
    import baw.config  # pylint:disable=W0621
    path = os.path.join(baw.config.bawtmp(), 'tmp', projectname)
    os.makedirs(path, exist_ok=True)
    return path


def tmpfile() -> str:
    """\
    >>> tmpfile()
    '...'
    """
    name = str(int(random.random() * 10000000000)).zfill(10)  # nosec
    tmps = tmp(baw.ROOT)
    result = os.path.join(tmps, name)
    if os.path.exists(result):
        # try again
        return tmpfile()
    return result


@contextlib.contextmanager
def tmpdir(delete: bool = False) -> str:  # pylint:disable=W0613
    path = tmpfile()
    os.makedirs(path)
    yield path


def check_root(root: str):
    if not os.path.exists(root):
        raise ValueError(f'Project root: {root} does not exists')


def file_append(path: str, content: str):
    assert os.path.exists(path), str(path)
    with open(path, mode='a', newline=NEWLINE, encoding=UTF8) as fp:
        fp.write(content)


def file_create(path: str, content: str = ''):
    assert not os.path.exists(path), str(path)
    content = normalize_final(content)
    with open(path, mode='w', newline=NEWLINE, encoding=UTF8) as fp:
        fp.write(content)


def file_read(path: str):
    assert os.path.exists(path), str(path)
    with open(path, mode='r', newline=NEWLINE, encoding=UTF8) as fp:
        return normalize_final(fp.read())


def file_read_binary(path: str):
    assert os.path.exists(path), str(path)
    with open(path, mode='rb') as fp:
        return fp.read()


def file_remove(path: str):
    assert os.path.exists(path), str(path)
    assert os.path.isfile(path), str(path)
    os.remove(path)


def normalize_final(content: str):
    content = content.rstrip()
    content = f'{content}\n'
    return content


def file_replace(path: str, content: str):
    """Replace file content

    1. If not exists, create file
    2. If exists,     compare content, if changed than replace
                                       if not, do nothing
    Args:
        path(str): path to file
        content(str): content to write
    """
    content = normalize_final(content)
    if not os.path.exists(path):
        file_create(path, content)
        return
    current_content = file_read(path)
    if current_content == content:
        return

    with open(path, mode='w', newline=NEWLINE, encoding=UTF8) as fp:
        fp.write(content)


def print_runtime(before: int):
    """Determine runtime due the diff of current time and provided time
    `before`. Log this timediff.

    Args:
        before(int): time recorded some time before - use time.time()
    """
    time_diff = time.time() - before
    log('Runtime: %.2f secs\n' % time_diff)  # pylint:disable=C0209


@contextlib.contextmanager
def profile():
    """Print runtime to logger to monitore performance"""
    start = time.time()
    try:
        yield
    except Exception:
        print_runtime(start)
        raise
    else:
        print_runtime(start)


def skip(msg: str):
    """Logging skipped event.

    Args:
        msg(str): message to skip
    """
    log(f'skip: {msg}')


@contextlib.contextmanager
def empty(*args, **kwargs):  # pylint:disable=W0613
    yield


def openbrowser(url: str):
    """\
    >>> openbrowser(__file__) is None
    True
    """
    if 'PYTEST_CURRENT_TEST' in os.environ:
        # running with pytest do not open webbrowser
        return
    webbrowser.open_new(url)


def fork(
    *runnables,
    worker: int = 6,
    process: bool = False,
    returncode: bool = False,
) -> int:
    """Run methods in parallel.

    Args:
        runnables(callable): callables to run
        worker(int): number of worker
        process(bool): if True use Process- instead of ThreadPool
        returncode(bool): always return `returncode` instead of computed
                          result
    Returns:
        returncode if error occurs or returncode=True
        result of computation if no error occurs or returncode is not used

    >>> fork(['Not A Method', 'Also not a method'], returncode=True) == baw.FAILURE
    True
    """
    failure = 0
    executor = concurrent.futures.ThreadPoolExecutor
    if process:
        executor = select_executor()
    result = [None] * len(runnables)
    with executor(max_workers=worker) as pool:
        futures = {pool.submit(item): item for item in runnables}
        for future in concurrent.futures.as_completed(futures):
            index = runnables.index(futures[future])
            try:
                result[index] = future.result()
            except Exception as failed:  # pylint:disable=broad-except
                error(f'future number: {index}; {future} failed.')
                error(failed)
                failure += 1
    if failure or returncode:
        return failure
    return result


def select_executor():
    # TODO: how to use multiprocessing with pytest, see pytest: 38.3.1
    testrun = os.environ.get('PYTEST_PLUGINS', False)
    executor = concurrent.futures.ProcessPoolExecutor
    if testrun:  # pragma:nocover
        executor = concurrent.futures.ThreadPoolExecutor
    return executor


def binhash(data: bytes) -> int:
    """\
    >>> binhash(b'hello')
    907060870
    """
    if isinstance(data, str):
        data: bytes = data.encode('utf8')
    result = binascii.crc32(data)
    return result


def fixup_windows(path):
    """On windows argsparse expand /var/outdir/test.xml to C:/usr/git/var/..

    This fixup fixes this.

    >>> fixup_windows('--junit_xml=C:/usr/git/var/outdir/test.xml')
    '--junit_xml=/var/outdir/test.xml'
    """
    # TODO: IMPORVE LATER
    path = path.replace('C:/usr/git/var', '/var')
    return path


def testing() -> bool:
    """\
    >>> testing()
    True
    """
    if os.environ.get('PYTEST_CURRENT_TEST', None):
        return True
    return False


def exitx(msg='', returncode=FAILURE):
    """End progam. Log optional exit message as failure or success.

    >>> exitx('Fehler?')
    Traceback (most recent call last):
    ...sys.exit(returncode)
    SystemExit: 1
    >>> exitx('Alles gut.', returncode=0)
    Traceback (most recent call last):
    ...
    SystemExit: 0
    """
    if msg:
        if returncode:
            baw.error(msg)
        else:
            baw.log(msg)
    sys.exit(returncode)
