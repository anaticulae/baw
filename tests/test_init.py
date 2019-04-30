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
from os.path import join

from pytest import fixture
from pytest import mark
from pytest import raises

from baw import main
from tests import assert_run
from tests import skip_cmd
from tests import skip_longrun
from tests import skip_nonvirtual


@skip_cmd
def test_init_project_in_empty_folder(testdir):  #pylint: disable=W0613
    """Run --init in empty folder

    Intitialize project and check if documentation is generated."""
    with assert_run('baw --init xcd "I Like This Project"'):
        assert exists('docs/pages/bugs.rst')
        assert exists('docs/pages/changelog.rst')
        assert exists('docs/pages/readme.rst')
        assert exists('docs/pages/todo.rst')


@skip_cmd
@skip_longrun
def test_doc_command(testdir):  #pylint: disable=W0613
    """Run --doc command to generate documentation."""
    with assert_run('baw --init xcd "I Like This Project"'):
        pass
    with assert_run('baw --doc'):
        assert exists('docs/html')


@skip_cmd
@skip_longrun
@skip_nonvirtual
def test_escaping_single_collon(testdir):
    """Generate project with ' in name and test install"""
    with assert_run('baw --init xcd "I\'ts magic"'):
        pass
    with assert_run('pip install --editable .'):
        pass


@fixture
def project_example(testdir):
    with assert_run('baw --init xcd "I Like This Project"'):
        pass
    with assert_run('baw --virtual'):
        pass
    return testdir


@mark.parametrize('command', [
    ['--init', 'myroject', '"This is a beautyful project'],
    ['--init', 'myroject', '"This is a beautyful project"', '--with_cmd'],
])
def test_run_complex_command(testdir, monkeypatch, command):  # pylint: disable=W0613
    """Run help and version and format command to reach basic test coverage"""

    with monkeypatch.context() as context:
        # Remove all environment vars
        # baw is removed as first arg
        context.setattr(sys, 'argv', ['baw'] + command)
        with raises(SystemExit) as result:
            main()
        result = str(result)
        assert 'SystemExit: 0' in result, result
