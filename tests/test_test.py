# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2021-2023 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import os
import textwrap

import baw.utils
import tests
import tests.fixtures.project


@tests.hasbaw
@tests.hasgit
@tests.longrun
def test_creating_project(tmpdir):
    """Creating project without venv environment"""
    ensure_gituser()
    completed = tests.run(
        'baw --verbose init xkcd "Longtime project"',
        cwd=tmpdir,
    )
    error = f'{completed.stderr}\n{completed.stdout}'
    assert completed.returncode == baw.SUCCESS, error
    assert os.path.exists(os.path.join(tmpdir, '.git'))


@tests.hasbaw
@tests.hasgit
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
    """) % (tests.fixtures.project.EXAMPLE_PROJECT_NAME, python_file)
    write = example.join('tests/my_test.py')
    baw.utils.file_create(write, test_me)
    assert os.path.exists(write)
    empty_python = example.join(
        tests.fixtures.project.EXAMPLE_PROJECT_NAME,
        f'{python_file}.py',
    )
    baw.utils.file_create(empty_python)
    assert os.path.exists(empty_python)
    # install requirements first and run test later
    cmd = 'baw test'
    completed = tests.run(cmd, example)

    assert not completed.returncode, completed.stderr + completed.stdout


def test_cmd_junit_xml(simple):  # pylint:disable=W0621
    expected = os.path.join(simple[1], 'myreport.xml')
    # -n1: avoid xdist runtime error, TODO: VERIFY THIS
    simple[0](f'test --junit_xml={expected} -n1')
    assert os.path.exists(expected)


def test_cmd_test_skip(simple, capsys):
    simple[0]('test skip')
    stdout = tests.stdout(capsys)
    assert 'skip tests...' in stdout


SIMPLE = """
def test_all():
    pass
"""


def test_cmd_test_all(simple):
    root = simple[1]
    baw.utils.file_create(
        os.path.join(root, 'tests/test_simple.py'),
        content=SIMPLE,
    )
    simple[0]('test all -n1')
    # TODO: ENABLE LATER
    # assert 'test_all PASSED' in stdout or 'test_all PASSED' in stderr


def ensure_gituser():
    baw.runtime.run('git config --global user.name "Your Name"')
    baw.runtime.run('git config --global user.email "you@example.com"')
