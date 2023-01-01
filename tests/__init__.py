# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019-2023 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import contextlib
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
nonvenv = pytest.mark.skipif(not VENV, reason='require venv')
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
hasdocker = hasprog('docker')


def run(cmd: str, cwd: str = None):
    """Run external process."""
    cwd = cwd if cwd else os.getcwd()
    completed = subprocess.run(  # nosec
        cmd,
        cwd=cwd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
        check=False,
    )
    return completed


@contextlib.contextmanager
def assert_run(cmd: str, cwd: str = None):
    completed = run(cmd, cwd)
    msg = f'{completed.stderr}\n{completed.stdout}'
    assert not completed.returncode, msg
    baw.utils.log(cmd)
    baw.utils.log(completed.stdout)
    if completed.stderr:
        baw.utils.error(completed.stderr)
    yield completed


@contextlib.contextmanager
def assert_run_fail(cmd: str, cwd: str = None):
    completed = run(cmd, cwd)
    msg = f'{completed.stderr}\n{completed.stdout}'
    assert completed.returncode, msg
    yield completed


def file_count(path: str):
    return len(os.listdir(path))


def baaw(
    cmd,
    monkeypatch,
    verbose: bool = True,
    expect=True,
):
    cmd = cmd_split(cmd)
    with monkeypatch.context() as context:
        # Remove all environment vars
        # baw is removed as first arg
        cmdx = ['baw']
        if verbose:
            cmdx += ['--verbose']
        cmdx += cmd
        context.setattr(sys, 'argv', cmdx)
        with pytest.raises(SystemExit) as result:
            baw.run.main()
        result = str(result)
        if expect:
            assert 'SystemExit(0)' in result, result
        else:
            assert 'SystemExit(0)' not in result, result


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
