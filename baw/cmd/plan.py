# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import os


def create():
    pass


def close():
    pass


def current(root: str) -> str:
    """Determine current open release plan name.

    Args:
        root: project root of analysed project
    Returns:
        current version number of newest release plan
        None if no release plan exists
    """
    # TODO: Validate versions
    listed = [item.replace('.rst', '') for item in os.listdir(releases(root))]
    versions = sorted([item for item in listed if '.' in item])
    if not versions:
        return None
    return versions[-1]


def releases(root: str) -> str:
    assert os.path.exists(root), root
    result = os.path.join(root, 'docs/releases')
    assert os.path.exists(result)
    return result
