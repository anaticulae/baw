#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019-2023 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================
"""Test to create a venv environment and running tests in venv
environment afterwards.
 """

import os

import baw.runtime
import tests


@tests.longrun
def test_create_venv(example, monkeypatch):
    """Creating venv environment."""
    tests.baaw(
        '--venv',
        monkeypatch=monkeypatch,
    )
    # TODO: ENSURE THAT CORRECT VENV IS CREATED?
    venv = baw.runtime.virtual(example, creates=False)
    assert os.path.exists(venv), f'venv folder does not exists: {venv}'


@tests.hasbaw
@tests.nightly
def test_run_test_in_venv(project_with_test):
    """Running test-example in venv environment"""
    for cmd in ('baw --venv sync all', 'pip list' ,'baw --venv test'):
        # install requirements first and run test later
        completed = tests.run(cmd, project_with_test)
        assert completed.returncode == baw.SUCCESS, completed.stderr
