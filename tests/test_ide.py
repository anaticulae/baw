# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020-2023 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import os
import pathlib

import pytest
import utilo

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


def test_ide_open_in_subfolder(workspace, monkeypatch):  # pylint:disable=W0621
    with monkeypatch.context():
        no_code(workspace, monkeypatch)
        # do not open ide
        utilo.run(
            cmd='baw ide',
            cwd=utilo.join(workspace, 'tests'),
        )


def no_code(tmpdir, monkeypatch):
    """Do not open vscode via 'baw ide'"""
    fake_bin = pathlib.Path(tmpdir) / "bin"
    fake_bin.mkdir()

    fake_code = fake_bin / "code"

    fake_code.write_text("#!/bin/sh\n"
                         "true \"$@\"\n")

    fake_code.chmod(0o755)

    monkeypatch.setenv("PATH", f"{fake_bin}:{os.environ['PATH']}")


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
    assert 'fter a key in a key/value pair (at line 18, column 13)' in error
