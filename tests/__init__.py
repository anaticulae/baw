# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019-2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import contextlib
import functools
import os
import subprocess
import sys

import pytest

import baw.git
import baw.run
import baw.runtime
import baw.utils

THIS = os.path.dirname(__file__)
PROJECT = os.path.abspath(os.path.join(THIS, '..'))
DATA = os.path.join(THIS, 'data')

REQUIREMENTS = os.path.join(PROJECT, 'baw/requires/requirements-dev.txt')

LONGRUN = 'LONGRUN' in os.environ
NO_LONGRUN_REASON = 'Takes to mutch time'

FAST = 'FAST' in os.environ
NIGHTLY = 'NIGHTLY' in os.environ
VENV = 'VENV' in os.environ

FAST_TESTS = FAST or (not LONGRUN and not NIGHTLY)

# pylint: disable=invalid-name
longrun = pytest.mark.skipif(FAST_TESTS, reason='test requires long time')
nightly = pytest.mark.skipif(not NIGHTLY, reason='require long, long time')
skip_missing_packages = pytest.mark.skip(reason='package(s) not available')
nonvenv = pytest.mark.skipif(not VENV, reason='erquire venv')
skip_venv = pytest.mark.skipif(VENV, reason='do not run in venv env')


def register_marker(name: str):
    """After upgrading pytest, markers must be registered in pytest
    config. To avoid putting holyvalue markers in every pytest.ini we
    bypass them by directly acessing the pytest API. This may fail in
    the future."""
    pytest.mark._markers.add(name)  # pylint:disable=W0212
    return getattr(pytest.mark, name)


longrun = register_marker('longrun')
nightly = register_marker('nightly')


def hasprog(program: str):
    installed = baw.runtime.hasprog(program)
    result = pytest.mark.skipif(not installed, reason=f'install {program}')
    return result


hasgit = hasprog('git')
hasbaw = hasprog('baw')


def run(command: str, cwd: str = None):
    """Run external process."""
    cwd = cwd if cwd else os.getcwd()
    completed = subprocess.run(  # nosec
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
    msg = f'{completed.stderr}\n{completed.stdout}'
    assert not completed.returncode, msg
    baw.utils.log(command)
    baw.utils.log(completed.stdout)
    if completed.stderr:
        baw.utils.error(completed.stderr)
    yield completed


@contextlib.contextmanager
def assert_run_fail(command: str, cwd: str = None):
    completed = run(command, cwd)
    msg = f'{completed.stderr}\n{completed.stdout}'
    assert completed.returncode, msg
    yield completed


EXAMPLE_PROJECT_NAME = 'xkcd'


@pytest.fixture
def example(testdir, monkeypatch):
    """Creating example project due console"""
    if run('which baw').returncode:
        pytest.skip('install baw')
    if not baw.git.installed():
        pytest.skip('install git')
    baw.git.update_userdata()
    cmd = f'baw --verbose init {EXAMPLE_PROJECT_NAME} "Longtime project"'
    with monkeypatch.context() as context:
        tmpdir = lambda: testdir.tmpdir.join('tmpdir')  # pylint:disable=C3001
        context.setattr(baw.config, 'bawtmp', tmpdir)
        with assert_run(cmd, cwd=testdir.tmpdir):
            assert os.path.exists(os.path.join(testdir.tmpdir, '.git'))
            yield testdir.tmpdir


@pytest.fixture
def simple(example, monkeypatch):  # pylint:disable=W0621
    runner = functools.partial(
        baaw,
        monkeypatch=monkeypatch,
    )
    yield runner, example


def file_count(path: str):
    return len(os.listdir(path))


def baaw(
    command,
    monkeypatch,
    verbose: bool = True,
):
    command = cmd_split(command)
    with monkeypatch.context() as context:
        # Remove all environment vars
        # baw is removed as first arg
        cmd = ['baw']
        if verbose:
            cmd += ['--verbose']
        cmd += command
        context.setattr(sys, 'argv', cmd)
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


def stdout(capsys) -> str:
    out = capsys.readouterr().out
    result = str(out)
    return result
