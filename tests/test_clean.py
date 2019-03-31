"""Test clean command."""
from os import listdir
from os import makedirs
from os.path import exists
from os.path import join

import pytest

from baw.utils import file_create
from tests import run


def test_clean_files_and_dirs(tmpdir):
    """Create some files and folder and clean them afterwards.

    1. Create project
    2. Create some folder
    3. Create .coverage-files
    4. Run clean
    5. Check result
    """
    assert not len(listdir(tmpdir))  # clean directory

    for item in ['.git', 'build', TMP]:
        makedirs(join(tmpdir, item))

    assert len(listdir(tmpdir)), 3

    for item in ['.coverage', 'do_not_clean.txt']:
        file_create(join(tmpdir, item))
    assert len(listdir(tmpdir)), 5

    nested_file = join(tmpdir, 'build', '.coverage')
    file_create(nested_file)
    assert exists(nested_file)

    completed = run('baw --clean', tmpdir)
    assert completed.returncode == 0, completed.stderr

    cleaned_project = set(listdir(tmpdir))
    assert cleaned_project == {'.git', 'do_not_clean.txt'}  # .gitdir remains
