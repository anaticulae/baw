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
from os import environ
from os.path import exists
from os.path import join
from textwrap import dedent

import pytest
from baw.runtime import VIRTUAL_FOLDER
from tests import example
from tests import PROJECT
from baw.utils import package_address
from tests import example  # required for fixture
from tests import REQUIREMENTS
from tests import run
from tests import skip_longrunning
from tests import skip_cmd


@skip_cmd
@skip_longrunning
def test_creating_virtual_environment(example):
    """Creating virtual environment."""
    completed = run(
        'baw --virtual',
        cwd=example,
    )
    assert completed.returncode == 0, completed.stderr

    virtual = join(example, VIRTUAL_FOLDER)
    msg = 'Virtual folder does not exists: %s' % virtual
    assert exists(virtual), msg


@skip_cmd
def test_creating_project(tmpdir):
    """Creating project without virtual environment"""
    completed = run(
        'baw --init xkcd "Longtime project"',
        cwd=tmpdir,
    )
    assert completed.returncode == 0, completed.stderr
    assert exists(join(tmpdir, '.git'))


@pytest.fixture
def project_with_test(example):
    """Create project with one test case"""

    test_me = dedent("""\
        def test_me():
            # Empty passing test
            pass
    """)

    write = join(example, 'tests', 'my_test.py')
    with open(write, mode='w', encoding='utf8') as fp:
        fp.write(test_me)
    assert exists(write)
    return example


@skip_cmd
def test_running_test_in_virtual_environment(project_with_test):
    """Running test-example in virtual environment"""

     _, extra_url = package_address()
    source = '--index-url  %s' % (extra_url)
    pytest_install = 'python -mpip install -r %s %s' % (REQUIREMENTS, source)

    cmd = pytest_install + ' && baw --test'  #python -mpytest tests -v'
    completed = run(cmd, project_with_test)

    assert completed.returncode == 0
