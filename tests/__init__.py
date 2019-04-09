from contextlib import contextmanager
from os import environ
from os import makedirs
from os.path import abspath
from os.path import dirname
from os.path import exists
from os.path import join
from random import randrange
from subprocess import PIPE
from subprocess import run as _run

import pytest
from baw.utils import get_setup
from baw.utils import TMP

MAX_NUMBER = 20
MAX_TEST_RANDOM = 10**MAX_NUMBER

THIS = dirname(__file__)
PROJECT = abspath(join(THIS, '..'))
DATA = join(THIS, 'data')

PACKAGE_ADDRESS, INTERNAL_PACKAGE_PORT, EXTERNAL_PACKAGE_PORT = get_setup()

REQUIREMENTS = join(PROJECT, 'requirements-dev.txt')

LONGRUN = 'LONGRUN' in environ.keys()
NO_LONGRUN_REASON = 'Takes to mutch time'

FAST = 'FAST' in environ.keys()
NON_VIRTUAL = 'VIRTUAL' not in environ.keys()

NO_BAW = FAST
NO_BAW_RESON = 'Installing baw takes long time'

skip_missing_packages = pytest.mark.skip(
    reason="Required package(s) not available")
skip_longrun = pytest.mark.skipif(
    not LONGRUN or FAST, reason="Test require long time")
skip_cmd = pytest.mark.skipif(NO_BAW, reason="Decrease response time")
skip_nonvirtual = pytest.mark.skipif(
    NON_VIRTUAL, reason="No virtual environment")


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
    TEMP = join(PROJECT, TMP)
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
        stdout=PIPE,
        stderr=PIPE,
        universal_newlines=True,
    )
    return completed


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


EXAMPLE_PROJECT_NAME = 'xkcd'


@pytest.fixture
def example(tmpdir):
    """Creating example project due console"""
    assert not NO_BAW, 'test require baw-package, but this is not wanted'
    cmd = 'baw --init %s "Longtime project"' % EXAMPLE_PROJECT_NAME
    with assert_run(cmd, cwd=tmpdir):
        assert exists(join(tmpdir, '.git'))

    return tmpdir
