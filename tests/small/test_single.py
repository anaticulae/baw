# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2022-2023 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import baw.utils
import tests

MESSAGES = """
ALA
WASD
BASD
ALA
ALA
"""

EXPECTED = """\
ALA
BASD
WASD
"""


def test_bsa_single_small_document(testdir):
    single = testdir.tmpdir.join('single.txt')
    baw.utils.file_create(single, MESSAGES)
    improved = testdir.tmpdir.join('simple.txt')
    cmd = f'cat {single} | baw_single  > {improved}'
    tests.run(cmd, cwd=testdir.tmpdir)
    result = baw.utils.file_read(improved)
    assert result == EXPECTED


def test_bsa_single_huge_document(testdir):
    single = testdir.tmpdir.join('single.txt')
    raw = '\n'.join(str(item).zfill(10) for item in range(500000))
    baw.utils.file_create(single, raw)
    improved = testdir.tmpdir.join('simple.txt')
    cmd = f'cat {single} | baw_single  > {improved}'
    tests.run(cmd, cwd=testdir.tmpdir)
    result = baw.utils.file_read(improved).strip()
    assert result == raw
