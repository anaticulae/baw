# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019 by Helmut Konrad Fahrendholz. All rights reserved.
# Tis file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

from functools import partial

from baw.runtime import run_target
from baw.utils import logging
from baw.utils import logging_error


def checkout_file(
        root,
        files,
        *,
        verbose: bool = False,
        virtual: bool = False,
):
    """Checkout files from git repository

    Args:
        root(str): root to generated project
        files(str/iterable): files to checkout
    Returns:
        0 if SUCCESS else FAILURE
    """
    runner = partial(run_target, verbose=verbose, virtual=virtual)
    to_reset = ' '.join(files) if not isinstance(files, str) else files
    logging('Reset %s' % to_reset)
    completed = runner(root, 'git checkout -q %s' % to_reset)

    if completed.returncode:
        msg = 'while checkout out %s\n%s' % (to_reset, str(completed))
        logging_error(msg)
    return completed.returncode
