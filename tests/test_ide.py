# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020-2023 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import pytest

import baw.cmd.ide
import baw.utils
import tests


@pytest.fixture
def workspace(testdir, monkeypatch):
    name = 'short'
    tests.baaw(f'init {name} "I\'ts magic"', monkeypatch)
    space = str(testdir)
    return space


def test_ide_open(workspace, monkeypatch):  # pylint:disable=W0621
    with monkeypatch.context() as patched:
        # do not open ide
        patched.setattr(baw.cmd.ide, 'start', lambda root: baw.SUCCESS)
        baw.cmd.ide.ide_open(workspace)


CONFIG = 'pyproject.toml'


def test_ide_invalid_pyproject(workspace, monkeypatch, capsys):  # pylint:disable=W0621
    # make config invalid
    previous = baw.utils.file_read(CONFIG)
    assert previous
    before = 'dependencies = ['
    assert before in previous
    after = previous.replace(before, before[0:-4])
    baw.file_replace(CONFIG, after)
    # run baw
    with monkeypatch.context() as patched:
        # do not open ide
        patched.setattr(baw.cmd.ide, 'start', lambda root: baw.SUCCESS)
        with pytest.raises(SystemExit):
            baw.cmd.ide.ide_open(workspace)
    error = tests.stderr(capsys)
    assert 'invalid config pyproject.toml' in error
