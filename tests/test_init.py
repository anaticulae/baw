#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019 by Helmut Konrad Fahrendholz. All rights reserved.
# Tis file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================

import sys
from os.path import exists

from pytest import fixture
from pytest import mark
from pytest import raises

from baw import main
from tests import assert_run
from tests import skip_cmd
from tests import skip_longrun
from tests import skip_nonvirtual


@fixture
def project_example(testdir, monkeypatch):
    run_command(['--init', 'xcd', '"I Like This Project"'], monkeypatch)
    run_command(['--virtual'], monkeypatch)
    return testdir


@skip_cmd
def test_init_project_in_empty_folder(project_example):  #pylint: disable=W0613,W0621
    """Run --init in empty folder

    Intitialize project and check if documentation is generated."""
    assert exists('docs/pages/bugs.rst')
    assert exists('docs/pages/changelog.rst')
    assert exists('docs/pages/readme.rst')
    assert exists('docs/pages/todo.rst')


@skip_cmd
@skip_longrun
def test_doc_command(project_example, monkeypatch):  #pylint: disable=W0613,W0621
    """Run --doc command to generate documentation."""
    run_command(['--doc'], monkeypatch)
    assert exists('docs/html')


@skip_cmd
@skip_longrun
@skip_nonvirtual
def test_escaping_single_collon(testdir, monkeypatch):  #pylint: disable=W0613
    """Generate project with ' in name and test install"""
    run_command(['--init', 'xcd', '"I\'ts magic"'], monkeypatch)
    assert_run('.', 'pip install --editable .')


@mark.parametrize('command', [
    ['--init', 'myroject', '"This is a beautyful project'],
    ['--init', 'myroject', '"This is a beautyful project"', '--with_cmd'],
])
def test_run_complex_command(testdir, monkeypatch, command):  # pylint: disable=W0613
    """Run help and version and format command to reach basic test coverage"""
    run_command(command, monkeypatch)


def run_command(command, monkeypatch):
    with monkeypatch.context() as context:
        # Remove all environment vars
        # baw is removed as first arg
        context.setattr(sys, 'argv', ['baw'] + command)
        with raises(SystemExit) as result:
            main()
        result = str(result)
        assert 'SystemExit: 0' in result, result
