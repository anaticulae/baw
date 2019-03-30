from tests import assert_run


def test_init_project_in_empty_folder(tmpdir):
    """Run --init in empty folder"""
    assert_run('baw --init xcd "I Like This Project"', cwd=tmpdir)
