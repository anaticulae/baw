# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020-2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import os

import baw.config
import baw.utils


def test_archive_path(root: str) -> str:
    tmpdir = baw.config.project_tmpdir(root)
    return os.path.join(tmpdir, 'tested')


def tested(root: str, hashed: str) -> bool:
    assert hashed.strip(), 'require hashed value'
    archive = test_archive_path(root)
    if not os.path.exists(archive):
        return False
    content = baw.utils.file_read(archive)
    lines = content.splitlines()
    if any(line.strip() == hashed for line in lines):
        return True
    return False


def mark_tested(root: str, hashed: str) -> bool:
    assert hashed.strip(), 'require hashed value'
    if tested(root, hashed):
        return True
    archive = test_archive_path(root)
    # add newline to separate hash values in file
    hashed = f'{hashed}\n'
    if os.path.exists(archive):
        baw.utils.file_append(archive, hashed)
    else:
        baw.utils.file_create(archive, hashed)
    return True
