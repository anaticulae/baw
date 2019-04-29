from os.path import exists
from os.path import join
from textwrap import dedent

import pytest

from baw.utils import SUCCESS
from baw.utils import file_create
from tests import EXAMPLE_PROJECT_NAME
from tests import example  # pylint: disable=W0611
from tests import run
from tests import skip_cmd


@skip_cmd
def test_creating_project(tmpdir):
    """Creating project without virtual environment"""
    completed = run(
        'baw --init xkcd "Longtime project"',
        cwd=tmpdir,
    )
    assert completed.returncode == SUCCESS, completed.stderr
    assert exists(join(tmpdir, '.git'))


@skip_cmd
def test_test_with_import(example):  # pylint: disable=W0621
    """Ensure that import project package while writing tests need no additonal
    configuration on sys.path

    Hint:
        baw --test must run in root. This is ensured by this test.
        If baw --test is not runned in root, the sys path contains only
        projectname/tests but we need projectname.
    """
    # EXAMPLE_PROJECT_NAME is eqaul to package name
    python_file = 'samba'
    test_me = dedent("""\
        def test_me():
            import %s.%s
    """) % (EXAMPLE_PROJECT_NAME, python_file)

    write = join(example, 'tests', 'my_test.py')
    file_create(write, test_me)
    assert exists(write)

    empty_python = join(example, EXAMPLE_PROJECT_NAME, '%s.py' % python_file)
    file_create(empty_python, '')
    assert exists(empty_python)

    # install requirements first and run test later
    cmd = 'baw --test'
    completed = run(cmd, example)

    assert completed.returncode == 0, completed.stderr + completed.stdout


@pytest.fixture
def project_with_test(example):  # pylint: disable=W0621
    """Create project with one test case"""

    test_me = dedent("""\
        def test_me():
            # Empty passing test
            pass
    """)

    write = join(example, 'tests', 'my_test.py')
    file_create(write, test_me)
    assert exists(write)
    return example
