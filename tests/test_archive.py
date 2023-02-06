# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2023 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import baw
import baw.archive.test


def test_tested(testdir):
    root = testdir.tmpdir
    path = root.join('.baw')
    baw.file_create(path)
    name = baw.tmpname(15)
    baw.config.create(root, name, 'tested')
    hashed = name
    assert not baw.archive.test.is_tested(root, hashed)
    assert baw.archive.test.mark_tested(root, hashed)
    assert baw.archive.test.is_tested(root, hashed)
    assert baw.archive.test.mark_tested(root, hashed)
    assert baw.archive.test.is_tested(root, hashed)
    hashed = 'new'
    assert not baw.archive.test.is_tested(root, hashed)
    assert baw.archive.test.mark_tested(root, hashed)
    assert baw.archive.test.is_tested(root, hashed)
