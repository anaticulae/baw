#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019-2023 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================

import os

import pytest
import utilo

import baw.runtime
import tests


@tests.nightly
def test_init_project_in_empty_folder(project_example):
    """Run init in empty folder.

    Intitialize project and check that documentation is generated.
    """
    index = project_example.join('docs/index.rst')
    assert os.path.exists(index)


@tests.hasbaw
@tests.hasgit
@tests.longrun
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


@tests.hasbaw
@tests.hasgit
@tests.longrun
@pytest.mark.usefixtures('testdir')
def test_upgrade_version_number(simple, monkeypatch):
    root = simple[1]

    upgrade = """\
        git config advice.setUpstreamFailure false
        touch ABC
        git add .
        git commit -a -m "feat(hello): this is comm"
    """.splitlines()

    for cmd in upgrade:
        baw.runtime.run_target(root, cmd)

    content = utilo.file_read(os.path.join(root, 'pyproject.toml'))
    assert 'version = "0.0.0"' in content, content

    tests.baaw(
        'release minor --no_test --no_sync --no_linter --no_push',
        monkeypatch,
    )

    content = utilo.file_read(os.path.join(root, 'pyproject.toml'))
    assert 'version = "0.1.0"' in content, content
