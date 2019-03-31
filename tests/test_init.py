from os.path import exists
from os.path import join

from tests import assert_run
from tests import skip_longrunning


def test_init_project_in_empty_folder(tmpdir):
    """Run --init in empty folder

    Intitialize project and check if documentation is generated."""
    with assert_run('baw --init xcd "I Like This Project"', cwd=tmpdir):
        assert exists(join(tmpdir, 'docs/pages/bugs.rst'))
        assert exists(join(tmpdir, 'docs/pages/changelog.rst'))
        assert exists(join(tmpdir, 'docs/pages/readme.rst'))
        assert exists(join(tmpdir, 'docs/pages/todo.rst'))


@skip_longrunning
def test_doc_command(tmpdir):
    """Run --doc command to generate documentation."""
    with assert_run('baw --init xcd "I Like This Project"', cwd=tmpdir):
        pass
    with assert_run('baw --doc', cwd=tmpdir):
        assert exists(join(tmpdir, 'docs/html'))
