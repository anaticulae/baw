#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019-2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================

import os

import pytest

import tests


@tests.skip_cmd
@tests.skip_longrun
def test_init_project_in_empty_folder(project_example):
    """Run init in empty folder.

    Intitialize project and check that documentation is generated.
    """
    index = project_example.join('docs/index.rst')
    assert os.path.exists(index)


@tests.skip_cmd
@tests.skip_longrun
def test_doc_command(project_example, monkeypatch):
    """Run --doc command to generate documentation."""
    tests.run_command('--doc', monkeypatch)
    created = project_example.join('tmpdir/docs/xcd/html/index.html')
    assert os.path.exists(created)


@tests.skip_cmd
@tests.skip_longrun
@tests.skip_nonvirtual
@pytest.mark.usefixtures('testdir')
def test_escaping_single_collon(monkeypatch):
    """Generate project with ' in name and test install"""
    tests.run_command('init xcd "I\'ts magic"', monkeypatch)
    tests.assert_run('.', 'pip install --editable .')


@pytest.mark.parametrize('command', [
    'init myroject "This is a beautyful project"',
    'init myroject "This is a beautyful project" --cmdline',
])
@tests.skip_longrun
@pytest.mark.usefixtures('testdir')
def test_run_complex_command(monkeypatch, command):
    """Run help and version and format command to reach basic test coverage"""
    tests.run_command(command, monkeypatch)
