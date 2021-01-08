# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019-2021 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================
"""Test clean command."""
from os import listdir
from os import makedirs
from os.path import exists
from os.path import join

from baw.utils import TMP
from baw.utils import file_create
from tests import file_count
from tests import run
from tests import skip_cmd


@skip_cmd
def test_clean_files_and_dirs(tmpdir):
    """Create some files and folder and clean them afterwards.

    1. Create project
    2. Create some folder
    3. Create .coverage-files
    4. Run clean
    5. Check result
    """
    assert file_count(tmpdir) == 0  # clean directory

    for item in ['.git', 'build', TMP]:
        makedirs(join(tmpdir, item))
    assert file_count(tmpdir) == 3

    for item in ['.coverage', 'do_not_clean.txt']:
        file_create(join(tmpdir, item))
    assert file_count(tmpdir) == 5

    nested_file = join(tmpdir, 'build', '.coverage')
    file_create(nested_file)
    assert exists(nested_file)

    completed = run('baw --clean', tmpdir)
    assert completed.returncode == 0, completed.stderr

    cleaned_project = set(listdir(tmpdir))
    assert cleaned_project == {'.git', 'do_not_clean.txt'}  # .gitdir remains
