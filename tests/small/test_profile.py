# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import os

import baw
import baw.git
import baw.small.profile


def test_commits():
    ranges = list(range(5))
    commits = baw.small.profile.commits(baw.ROOT, ranges=ranges)
    expected = (0,)
    if baw.git.installed():
        expected = (5,)
        if os.environ.get('JENKINS_HOME', False):
            # reduced checkout may only check out a single version or may
            # a single non feature commit(0)
            expected = (5, 1, 0)
    assert len(commits) in expected
