from contextlib import contextmanager
from os import environ
from os import makedirs
from os.path import abspath
from os.path import dirname
from os.path import exists
from os.path import join
from random import randrange
from subprocess import run as _run

import pytest

MAX_NUMBER = 20
MAX_TEST_RANDOM = 10**MAX_NUMBER

THIS = dirname(__file__)
PROJECT = abspath(join(THIS, '..'))
DATA = join(THIS, 'data')
REQUIREMENTS = join(PROJECT, 'requirements-dev.txt')

FAST = 'LONGRUN' not in environ.keys()
FAST_REASON = 'Takes to mutch time'

skip_missing_packages = pytest.mark.skip(
    reason="Required package(s) not available")
skip_longrunning = pytest.mark.skipif(FAST, reason="Test require long time")


def tempname():
    """Get random file-name with 20-ziffre, random name

    Returns:
        filename(str): random file name
    """
    return str(randrange(MAX_TEST_RANDOM)).zfill(MAX_NUMBER)


def tempfile():
    """Get temporary file-path located in `TEMP_FOLDER`.

    Returns:
        filepath(str): to tempfile in TEMP_FOLDER
    """
    # TODO: Investigate for better approch due pytest
    TEMP = join(PROJECT, 'temp')
    makedirs(TEMP, exist_ok=True)

    name = 'temp%s' % tempname()
    path = join(TEMP, name)
    if exists(path):
        return tempfile()
    return path


def run(command: str, cwd: str):
    """Run external process"""
    completed = _run(
        command,
        cwd=cwd,
        shell=True,
        universal_newlines=True,
    )
    return completed


def file_append(path: str, content: str):
    assert exists(path)

    with open(path, mode='a') as fp:
        fp.write(content)


@contextmanager
def assert_run(command: str, cwd: str):
    completed = run(command, cwd)
    msg = '%s\n%s' % (completed.stderr, completed.stdout)
    assert completed.returncode == 0, msg
    yield completed


@contextmanager
def assert_run_fail(command: str, cwd: str):
    completed = run(command, cwd)
    msg = '%s\n%s' % (completed.stderr, completed.stdout)
    assert completed.returncode, msg
    yield completed


@pytest.fixture
def example(tmpdir):
    """Creating example project due console"""
    project_name = 'xkcd'
    cmd = 'baw --init %s "Longtime project"' % project_name
    with assert_run(cmd, cwd=tmpdir) as completed:
        assert exists(join(tmpdir, '.git'))

    return tmpdir
