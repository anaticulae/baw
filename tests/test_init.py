#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019-2023 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================

import os
import sys

import pytest

import tests


@tests.nightly
def test_init_project_in_empty_folder(project_example):
    """Run init in empty folder.

    Intitialize project and check that documentation is generated.
    """
    index = project_example.join('docs/index.rst')
    assert os.path.exists(index)


@pytest.mark.skipif(
    sys.hexversion >= 0x030900F0,
    reason='python 3.10, update Sphinx',
)
@tests.nightly
def test_doc_cmd(project_example, monkeypatch):
    """Run doc cmd to generate documentation."""
    tests.baaw('doc', monkeypatch)
    created = project_example.join('tmpdir/docs/xcd/html/index.html')
    assert os.path.exists(created)


@tests.hasbaw
@tests.hasgit
@tests.longrun
@tests.nonvenv
@pytest.mark.usefixtures('testdir')
def test_escaping_single_collon(monkeypatch):
    """Generate project with ' in name and test install"""
    tests.baaw('init xcd "I\'ts magic"', monkeypatch)
    tests.assert_run('.', 'pip install --editable .')


@pytest.mark.parametrize('cmd', [
    'init myroject "This is a beautyful project"',
    'init myroject "This is a beautyful project" --cmdline',
])
@tests.hasbaw
@tests.hasgit
@tests.longrun
@pytest.mark.usefixtures('testdir')
def test_run_complex_cmd(monkeypatch, cmd):
    """Run help and version and format cmd to reach basic test coverage"""
    tests.baaw(cmd, monkeypatch)
