#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019-2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================
"""Test to create a virtual environment and running tests in virtual
environment afterwards.
 """

from os.path import exists

from baw.utils import SUCCESS
from tests import cmds
from tests import longrun
from tests import nightly
from tests import run
from tests import run_command
from tests.test_test import project_with_test  # pylint: disable=W0611


@cmds
@longrun
def test_create_venv(example, monkeypatch):
    """Creating virtual environment."""
    run_command('--virtual', monkeypatch=monkeypatch)
    # TODO: ADJUST THIS TEST LATER, TODO: PATH BAWTMP FOR THIS TEST?
    virtual = example.join('tmpdir/venv/xkcd')
    assert exists(virtual), 'venv folder does not exists: %s' % virtual


@cmds
@nightly
def test_run_test_in_venv(project_with_test):  # pylint: disable=W0621
    """Running test-example in virtual environment"""
    # install requirements first and run test later
    cmd = 'baw --virtual sync' + ' && baw test'  #python -mpytest tests -v'
    completed = run(cmd, project_with_test)

    assert completed.returncode == SUCCESS, completed.stderr
