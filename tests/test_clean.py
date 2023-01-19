# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019-2023 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================
"""Test clean cmd."""

import os

import baw.utils
import tests


@tests.longrun
def test_clean_files_and_dirs(simple):
    """Create some files and folder and clean them afterwards.

    1. Create project
    2. Create some folder
    3. Create .coverage-files
    4. Run clean
    5. Check result
    """
    root = simple[1]
    base = tests.file_count(root)
    for item in ('build', baw.utils.TMP):
        os.makedirs(os.path.join(root, item))
    assert tests.file_count(root) == base + 2

    for item in ('.coverage', 'do_not_clean.txt'):
        baw.utils.file_create(os.path.join(root, item))
    assert tests.file_count(root) == base + 2 + 2

    nested_file = os.path.join(root, 'build', '.coverage')
    baw.utils.file_create(nested_file)
    assert os.path.exists(nested_file)
    # run clean task
    simple[0]('clean all')
    cleaned_project = set(os.listdir(root))
    # .gitdir remains
    assert len(cleaned_project) == base + 2 + 2 - 3
