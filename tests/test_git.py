# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2023 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import baw.cmd.release
import baw.git


def test_commit_with_tag(simple):
    """Regression test to tag/annoate commit to use with git describe."""
    root = simple[1]
    tagged = baw.git.describe(root)
    assert tagged == baw.cmd.release.FIRST_RELEASE


def test_modified(simple):
    root = simple[1]
    assert baw.git_isclean(root)
    baw.runtime.run_target(root, 'touch ABC')
    assert not baw.git_isclean(root)
    modified = baw.git.modified(root)
    expected = '## master\n?? ABC'
    assert modified == expected
