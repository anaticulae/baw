# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2021-2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import os
import textwrap

import pytest

import baw.utils
import tests


@tests.hasbaw
@tests.hasgit
@tests.cmds
def test_creating_project(tmpdir):
    """Creating project without virtual environment"""
    completed = tests.run(
        'baw init xkcd "Longtime project"',
        cwd=tmpdir,
    )
    error = f'{completed.stderr}\n{completed.stdout}'
    assert completed.returncode == baw.utils.SUCCESS, error
    assert os.path.exists(os.path.join(tmpdir, '.git'))


@tests.hasbaw
@tests.hasgit
@tests.cmds
@tests.longrun
def test_test_with_import(example):
    """Ensure that import project package while writing tests need no additonal
    configuration on sys.path

    Hint:
        baw --test must run in root. This is ensured by this test.
        If baw --test is not runned in root, the sys path contains only
        projectname/tests but we need projectname.
    """
    # EXAMPLE_PROJECT_NAME is equal to package name
    python_file = 'samba'
    test_me = textwrap.dedent("""\
        def test_me():
            import %s.%s
    """) % (tests.EXAMPLE_PROJECT_NAME, python_file)
    write = example.join('tests/my_test.py')
    baw.utils.file_create(write, test_me)
    assert os.path.exists(write)
    empty_python = example.join(tests.EXAMPLE_PROJECT_NAME, f'{python_file}.py')
    baw.utils.file_create(empty_python)
    assert os.path.exists(empty_python)
    # install requirements first and run test later
    cmd = 'baw test'
    completed = tests.run(cmd, example)

    assert not completed.returncode, completed.stderr + completed.stdout


@pytest.fixture
def project_with_test(example):
    """Create project with one test case"""
    test_me = textwrap.dedent("""\
        def test_me():
            # Empty passing test
            pass
    """)
    write = example.join('tests/my_test.py')
    baw.utils.file_create(write, test_me)
    assert os.path.exists(write)
    return example
