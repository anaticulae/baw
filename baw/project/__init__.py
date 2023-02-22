#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019-2023 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================

import os

import baw.utils


def determine_root(path) -> str:
    current = str(path)
    while not os.path.exists(os.path.join(current, baw.utils.BAW_EXT)):  # pylint:disable=W0149
        current, base = os.path.split(current)
        if not str(base).strip():
            return None
    return current


def ispython(root: str) -> str:
    """\
    >>> ispython(determine_root(__path__))
    True
    """
    for item in 'setup.py'.split():  # pylint:disable=consider-using-any-or-all
        if os.path.exists(os.path.join(root, item)):
            return True
    return False
