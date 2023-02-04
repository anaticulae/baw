# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2023 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import baw.git

MESSAGE = """\
test(baseline): adjust baseline
"""


def pre(root: str):
    if not baw.git.is_clean(root, verbose=False):
        baw.exitx(f'could not baseline, repo is not clean: {root}')
    return baw.SUCCESS


def commit(root: str) -> int:
    if baw.git.is_clean(root, verbose=False):
        baw.log('baseline: nothing changed')
        return baw.SUCCESS
    returnvalue = baw.git.commit(
        root,
        source='tests/**',
        message=MESSAGE,
    )
    return returnvalue
