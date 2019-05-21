# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

from os import getcwd

from baw.runtime import run_target
from baw.utils import SUCCESS
from baw.utils import forward_slash


def open_this(root: str):
    path = getcwd()

    cmd = 'explorer %s' % path
    completed = run_target(
        root,
        cmd,
        cwd=path,
        skip_error_code={1},
        verbose=False,
    )

    exit(SUCCESS)  # avoid printing runtime
