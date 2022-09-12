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

import os

import baw.runtime
import baw.utils
import tests
from tests.test_test import project_with_test  # pylint: disable=W0611


@tests.cmds
@tests.longrun
def test_create_venv(example, monkeypatch):
    """Creating virtual environment."""
    tests.run_command(
        '--virtual',
        monkeypatch=monkeypatch,
    )
    # TODO: ENSURE THAT CORRECT VENV IS CREATED?
    venv = baw.runtime.venv(example, creates=False)
    assert os.path.exists(venv), f'venv folder does not exists: {venv}'


@tests.hasbaw
@tests.cmds
@tests.nightly
def test_run_test_in_venv(project_with_test):  # pylint: disable=W0621
    """Running test-example in virtual environment"""
    # install requirements first and run test later
    cmd = 'baw --virtual sync' + ' && baw test'  #python -mpytest tests -v'
    completed = tests.run(cmd, project_with_test)
    assert completed.returncode == baw.utils.SUCCESS, completed.stderr
