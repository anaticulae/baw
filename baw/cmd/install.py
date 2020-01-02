# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019-2020 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

from baw.runtime import run_target
from baw.utils import logging


def install(root: str, virtual: bool, verbose: bool = False):
    # -f always install newest one
    command = 'python setup.py install -f'

    completed = run_target(
        root, command, root, verbose=verbose, virtual=virtual)

    logging(completed.stdout)

    return completed.returncode
