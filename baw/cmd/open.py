# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019-2020 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import os

import baw.runtime
import baw.utils


def open_this(root: str):
    path = os.getcwd()

    cmd = 'explorer %s' % path
    completed = baw.runtime.run_target(
        root,
        cmd,
        cwd=path,
        skip_error_code={1},
        verbose=False,
    )
    # dont know why windows returns 1
    assert completed.returncode == 1, completed
    # avoid printing runtime error
    exit(baw.utils.SUCCESS)
