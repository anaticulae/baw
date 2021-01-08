#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019-2021 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================

import os

import baw.utils


def determine_root(path) -> str:
    current = str(path)
    while not os.path.exists(os.path.join(current, baw.utils.BAW_EXT)):
        current, base = os.path.split(current)
        if not str(base).strip():
            return None
    return current
