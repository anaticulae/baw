# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import sys

import baw.cmd.utils
import baw.run
import baw.runtime
import baw.utils


def run_shell(args: dict):
    cmd = args['cmd']
    root = baw.cmd.utils.get_root(args)
    completed = baw.runtime.run_target(
        root=root,
        cmd=cmd,
        cwd=root,
        verbose=False,
        debugging=True,
        venv=args['venv'],
    )
    if completed.returncode:
        sys.exit(completed.returncode)
    sys.exit(baw.utils.SUCCESS)
