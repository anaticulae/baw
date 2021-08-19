#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019-2021 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================

import concurrent.futures
import contextlib
import functools
import os
import shutil
import stat
import sys
import time
import webbrowser

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
    """
    try:
        yield
    except exceptions as failure:
        error(failure)
        exit(code)


def log(msg: str = '', end: str = NEWLINE):
    """Write message to logger

    Args:
        msg(str): message to log
        end(str): lineending
    Hint:
        Logging with default arguments will log a newline
    """
    msg = forward_slash(msg)
    print(msg, end=end, file=sys.stdout, flush=True)


def error(msg: str):
    """Print error-message to stderr and add [ERROR]-tag"""
    # use forward slashs
    msg = forward_slash(msg)
    print('[ERROR] %s' % msg, file=sys.stderr, flush=True)


# backward compatibility
logging = log  # pylint:disable=C0103
logging_error = error  # pylint:disable=C0103

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


def get_setup():
    try:
        adress = os.environ['HELPY_URL']
        internal = int(os.environ['HELPY_INT_PORT'])
        external = int(os.environ['HELPY_EXT_PORT'])
        return (adress, internal, external)
    except KeyError as failure:
        logging_error(f'Missing global var {failure}')
        exit(FAILURE)


def package_address():
    try:
        internal = os.environ['HELPY_INT_DIRECT']
        external = os.environ['HELPY_EXT_DIRECT']
        return (internal, external)
    except KeyError as failure:
        logging_error(f'Missing global var {failure}')
        exit(FAILURE)


def tmpdir():
    try:
        tmpdir = os.environ['TMPDIR']
    except KeyError as failure:
        logging_error(f'Missing global var `TMPDIR`')
        exit(FAILURE)
    return tmpdir


@functools.lru_cache(maxsize=16)
def tmp(root: str) -> str:
    """Return path to temporary folder. Create folder if required.

    Args:
        root(str): project root
    Returns:
        path to temporary folder
    """
    assert root
    _, projectname = os.path.split(root)
    path = os.path.join(tmpdir(), 'kiwi', projectname, TMP)
    os.makedirs(path, exist_ok=True)
    return path


def check_root(root: str):
    if not os.path.exists(root):
        raise ValueError('Project root does not exists' % root)


def file_append(path: str, content: str):
    assert os.path.exists(path), str(path)
    with open(path, mode='a', newline=NEWLINE) as fp:
        fp.write(content)


def file_create(path: str, content: str = ''):
    assert not os.path.exists(path), str(path)
    with open(path, mode='w', newline=NEWLINE) as fp:
        fp.write(content)


def file_read(path: str):
    assert os.path.exists(path), str(path)
    with open(path, mode='r', newline=NEWLINE) as fp:
        return fp.read()


def file_remove(path: str):
    assert os.path.exists(path), str(path)
    assert os.path.isfile(path), str(path)
    os.remove(path)


def file_replace(path: str, content: str):
    """Replace file content

    1. If not exists, create file
    2. If exists,     compare content, if changed than replace
                                       if not, do nothing
    Args:
        path(str): path to file
        content(str): content to write
    """
    if not os.path.exists(path):
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
    time_diff = time.time() - before
    logging('Runtime: %.2f secs\n' % time_diff)


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


def remove_tree(path: str):
    assert os.path.exists(path), path

    def remove_readonly(func, path, _):  # pylint:disable=W0613
        """Clear the readonly bit and reattempt the removal."""
        os.chmod(path, stat.S_IWRITE)
        func(path)

    try:
        shutil.rmtree(path, onerror=remove_readonly)
    except PermissionError:
        logging_error('Could not remove %s' % path)
        exit(FAILURE)


def skip(msg: str):
    """Logging skipped event.

    Args:
        msg(str): message to skip
    """
    logging('Skip: %s' % msg)


@contextlib.contextmanager
def empty(*args, **kwargs):  # pylint:disable=W0613
    yield


def openbrowser(url: str):
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
    if testrun:
        executor = concurrent.futures.ThreadPoolExecutor
    return executor
