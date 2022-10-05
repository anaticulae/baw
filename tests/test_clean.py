# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019-2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================
"""Test clean command."""

import os

import baw.utils
import tests


@tests.longrun
def test_clean_files_and_dirs(tmpdir):
    """Create some files and folder and clean them afterwards.

    1. Create project
    2. Create some folder
    3. Create .coverage-files
    4. Run clean
    5. Check result
    """
    assert not tests.file_count(tmpdir)  # clean directory

    for item in ['.git', 'build', baw.utils.TMP]:
        os.makedirs(os.path.join(tmpdir, item))
    assert tests.file_count(tmpdir) == 3

    for item in ['.coverage', 'do_not_clean.txt']:
        baw.utils.file_create(os.path.join(tmpdir, item))
    assert tests.file_count(tmpdir) == 5

    nested_file = os.path.join(tmpdir, 'build', '.coverage')
    baw.utils.file_create(nested_file)
    assert os.path.exists(nested_file)

    # yapf:disable
    baw.utils.file_create(os.path.join(tmpdir, '.baw'), """
    [project]
    short = test
    name = this is just a test
    """)
    # yapf:enable

    completed = tests.run('baw clean all', tmpdir)
    assert not completed.returncode, completed.stderr

    cleaned_project = set(os.listdir(tmpdir))
    # .gitdir remains
    assert cleaned_project == {'.git', 'do_not_clean.txt', '.baw'}
