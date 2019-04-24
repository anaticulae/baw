#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019 by Helmut Konrad Fahrendholz. All rights reserved.
# Tis file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================
"""Test to create a virtual environment and running tests in virtual
environment afterwards.
 """
from os.path import exists
from os.path import join
from textwrap import dedent

from baw.runtime import VIRTUAL_FOLDER
from baw.utils import SUCCESS
from baw.utils import package_address
from tests import REQUIREMENTS
from tests import example  # required for fixture
from tests import run
from tests import skip_cmd
from tests import skip_longrun
from tests.test_test import project_with_test


@skip_cmd
@skip_longrun
def test_creating_virtual_environment(example):
    """Creating virtual environment."""
    completed = run(
        'baw --virtual',
        cwd=example,
    )
    assert completed.returncode == SUCCESS, completed.stderr

    virtual = join(example, VIRTUAL_FOLDER)
    msg = 'Virtual folder does not exists: %s' % virtual
    assert exists(virtual), msg


@skip_cmd
@skip_longrun
def test_running_test_in_virtual_environment(project_with_test):
    """Running test-example in virtual environment"""
    # install requirements first and run test later
    cmd = 'baw --virtual --sync' + ' && baw --test'  #python -mpytest tests -v'
    completed = run(cmd, project_with_test)

    assert completed.returncode == SUCCESS, completed.stderr
