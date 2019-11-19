# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import os
from contextlib import contextmanager
from random import randrange
from subprocess import PIPE
from subprocess import run as _run

from pytest import fixture
from pytest import mark

from baw.utils import TMP
from baw.utils import get_setup

MAX_NUMBER = 20
MAX_TEST_RANDOM = 10**MAX_NUMBER

THIS = os.path.dirname(__file__)
PROJECT = os.path.abspath(os.path.join(THIS, '..'))
DATA = os.path.join(THIS, 'data')

PACKAGE_ADDRESS, INTERNAL_PACKAGE_PORT, EXTERNAL_PACKAGE_PORT = get_setup()

REQUIREMENTS = os.path.join(PROJECT, 'requirements-dev.txt')

LONGRUN = 'LONGRUN' in os.environ.keys()
NO_LONGRUN_REASON = 'Takes to mutch time'

FAST = 'FAST' in os.environ.keys()
VIRTUAL = 'VIRTUAL' in os.environ.keys()

NO_BAW = FAST
NO_BAW_RESON = 'Installing baw takes long time'

FAST_TESTS = not LONGRUN or FAST

skip_cmd = mark.skipif(NO_BAW, reason="Decrease response time")  # pylint: disable=invalid-name
skip_longrun = mark.skipif(FAST_TESTS, reason="Test requires long time")  # pylint: disable=invalid-name
skip_missing_packages = mark.skip(reason="Required package(s) not available")  # pylint: disable=invalid-name
skip_nonvirtual = mark.skipif(not VIRTUAL, reason="No virtual environment")  # pylint: disable=invalid-name
skip_virtual = mark.skipif(  # pylint: disable=invalid-name
    VIRTUAL,
    reason="do not run in virtual environment",
)


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
    temp = os.path.join(PROJECT, TMP)
    os.makedirs(temp, exist_ok=True)

    name = 'temp%s' % tempname()
    path = os.path.join(temp, name)
    if os.path.exists(path):
        return tempfile()
    return path


def run(command: str, cwd: str = None):
    """Run external process"""
    cwd = cwd if cwd else os.getcwd()
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
def assert_run(command: str, cwd: str = None):
    completed = run(command, cwd)

    msg = '%s\n%s' % (completed.stderr, completed.stdout)
    assert completed.returncode == 0, msg
    yield completed


@contextmanager
def assert_run_fail(command: str, cwd: str = None):
    completed = run(command, cwd)
    msg = '%s\n%s' % (completed.stderr, completed.stdout)
    assert completed.returncode, msg
    yield completed


EXAMPLE_PROJECT_NAME = 'xkcd'


@fixture
def example(tmpdir):
    """Creating example project due console"""
    assert not NO_BAW, 'test require baw-package, but this is not wanted'
    cmd = 'baw --init %s "Longtime project"' % EXAMPLE_PROJECT_NAME
    with assert_run(cmd, cwd=tmpdir):
        assert os.path.exists(os.path.join(tmpdir, '.git'))

    return tmpdir


def file_count(path: str):
    return len(os.listdir(path))
