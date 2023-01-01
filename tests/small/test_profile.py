# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2022-2023 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
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
            # a single non feature commit(0).
            # Skip testing result cause it is repository dependent.
            return
    assert len(commits) in expected
