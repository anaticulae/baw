# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019-2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import contextlib
import os
import random
import subprocess
import sys

import pytest

import baw.run
import baw.utils

MAX_NUMBER = 20
MAX_TEST_RANDOM = 10**MAX_NUMBER

THIS = os.path.dirname(__file__)
PROJECT = os.path.abspath(os.path.join(THIS, '..'))
DATA = os.path.join(THIS, 'data')

REQUIREMENTS = os.path.join(PROJECT, 'baw/requires/requirements-dev.txt')

LONGRUN = 'LONGRUN' in os.environ.keys()
NO_LONGRUN_REASON = 'Takes to mutch time'

FAST = 'FAST' in os.environ.keys()
NIGHTLY = 'NIGHTLY' in os.environ.keys()
VIRTUAL = 'VIRTUAL' in os.environ.keys()

NO_BAW = FAST
NO_BAW_RESON = 'Installing baw takes long time'

FAST_TESTS = FAST or (not LONGRUN and not NIGHTLY)

# pylint: disable=invalid-name
cmds = pytest.mark.skipif(NO_BAW, reason='decrease response time')
longrun = pytest.mark.skipif(FAST_TESTS, reason='test requires long time')
nightly = pytest.mark.skipif(not NIGHTLY, reason='require long, long time')
skip_missing_packages = pytest.mark.skip(reason='package(s) not available')
nonvirtual = pytest.mark.skipif(not VIRTUAL, reason='No venv env')
skip_virtual = pytest.mark.skipif(VIRTUAL, reason='do not run in venv env')

HASBAW = subprocess.run(
    'baw --help',
    check=False,
    shell=True,
    capture_output=True,
).returncode
hasbaw = pytest.mark.skipif(not HASBAW, reason='install baw')
HASGIT = subprocess.run(
    'git help',
    check=False,
    shell=True,
    capture_output=True,
).returncode
hasgit = pytest.mark.skipif(not HASGIT, reason='install git')


def tempname():
    """Get random file-name with 20-ziffre, random name

    Returns:
        filename(str): random file name
    """
    return str(random.randrange(MAX_TEST_RANDOM)).zfill(MAX_NUMBER)


def tempfile():
    """Get temporary file-path located in `TEMP_FOLDER`.

    Returns:
        filepath(str): to tempfile in TEMP_FOLDER
    """
    temp = os.path.join(PROJECT, baw.utils.TMP)
    os.makedirs(temp, exist_ok=True)

    name = 'temp%s' % tempname()
    path = os.path.join(temp, name)
    if os.path.exists(path):
        return tempfile()
    return path


def run(command: str, cwd: str = None):
    """Run external process."""
    cwd = cwd if cwd else os.getcwd()
    completed = subprocess.run(
        command,
        cwd=cwd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
        check=False,
    )
    return completed


@contextlib.contextmanager
def assert_run(command: str, cwd: str = None):
    completed = run(command, cwd)

    msg = '%s\n%s' % (completed.stderr, completed.stdout)
    assert not completed.returncode, msg
    yield completed


@contextlib.contextmanager
def assert_run_fail(command: str, cwd: str = None):
    completed = run(command, cwd)
    msg = '%s\n%s' % (completed.stderr, completed.stdout)
    assert completed.returncode, msg
    yield completed


EXAMPLE_PROJECT_NAME = 'xkcd'


@pytest.fixture
def example(testdir, monkeypatch):
    """Creating example project due console"""
    if run('baw --help').returncode:
        pytest.skip('install baw')
    if run('git help').returncode:
        pytest.skip('install git')
    assert not NO_BAW, 'test require baw-package, but this is not wanted'
    cmd = f'baw init {EXAMPLE_PROJECT_NAME} "Longtime project"'
    with monkeypatch.context() as context:
        tmpdir = lambda: testdir.tmpdir.join('tmpdir')
        context.setattr(baw.config, 'bawtmp', tmpdir)
        with assert_run(cmd, cwd=testdir.tmpdir):
            assert os.path.exists(os.path.join(testdir.tmpdir, '.git'))
            yield testdir.tmpdir


def file_count(path: str):
    return len(os.listdir(path))


def run_command(command, monkeypatch):
    command = cmd_split(command)
    with monkeypatch.context() as context:
        # Remove all environment vars
        # baw is removed as first arg
        context.setattr(sys, 'argv', ['baw'] + command)
        with pytest.raises(SystemExit) as result:
            baw.run.main()
        result = str(result)
        assert 'SystemExit(0)' in result, result


def cmd_split(cmd: str) -> list:
    """\
    >>> cmd_split('baw init project "long description" --withcmd')
    ['baw', 'init', 'project', '"long description"', '--withcmd']
    >>> cmd_split('baw init project "long description"')
    ['baw', 'init', 'project', '"long description"']
    >>> cmd_split('"baw" init project "long description"')
    ['"baw"', 'init', 'project', '"long description"']
    >>> cmd_split('plan new')
    ['plan', 'new']
    """
    # TODO: REPLACE WITH STDLIB?
    # import shlex
    # return list(shlex.shlex(cmd))
    if isinstance(cmd, (list, tuple)):
        return cmd
    cmd = cmd.split('"')
    if len(cmd) == 1:
        return cmd[0].split()
    result = []
    for item in cmd:
        if not item:
            continue
        withquotation = item[0].strip() and item[-1].strip()
        if withquotation:
            result.append(f'"{item}"')
        else:
            result.extend(item.split())
    return result
