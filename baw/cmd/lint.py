# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019-2020 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================
"""The purpose of this module is to run python linter safely."""

import os

from baw.config import sources
from baw.resources import RCFILE_PATH
from baw.runtime import run_target
from baw.utils import logging


def lint(root: str, verbose: bool = False, virtual: bool = False):
    code = ' '.join(sources(root))

    testpath = os.path.join(root, 'tests')
    linttest = testpath if os.path.exists(testpath) else ''

    cmd = f'pylint {code} {linttest} --rcfile={RCFILE_PATH}'

    completed = run_target(
        root,
        cmd,
        cwd=root,
        virtual=virtual,
        verbose=verbose,
    )
    logging(completed.stderr)
    logging(completed.stdout)

    return completed.returncode
