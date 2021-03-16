# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019-2021 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================
"""Test clean command."""

import os

import baw.utils
import tests


@tests.skip_cmd
def test_clean_files_and_dirs(tmpdir):
    """Create some files and folder and clean them afterwards.

    1. Create project
    2. Create some folder
    3. Create .coverage-files
    4. Run clean
    5. Check result
    """
    assert tests.file_count(tmpdir) == 0  # clean directory

    for item in ['.git', 'build', baw.utils.TMP]:
        os.makedirs(os.path.join(tmpdir, item))
    assert tests.file_count(tmpdir) == 3

    for item in ['.coverage', 'do_not_clean.txt']:
        baw.utils.file_create(os.path.join(tmpdir, item))
    assert tests.file_count(tmpdir) == 5

    nested_file = os.path.join(tmpdir, 'build', '.coverage')
    baw.utils.file_create(nested_file)
    assert os.path.exists(nested_file)

    completed = tests.run('baw clean all', tmpdir)
    assert completed.returncode == 0, completed.stderr

    cleaned_project = set(os.listdir(tmpdir))
    assert cleaned_project == {'.git', 'do_not_clean.txt'}  # .gitdir remains
