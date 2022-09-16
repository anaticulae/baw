# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019-2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import os
import sys

import baw.config
import baw.project
import baw.runtime
import baw.utils


def prints(root, value: str):
    if value == 'tmp':
        print_tmp(root)
        return
    if value == 'venv':
        print_venv(root)
        return
    if value == 'covreport':
        print_covreport(root)
        return


def print_tmp(root: str):
    name: str = 'global'
    if not baw.config.venv_global():
        root = baw.project.determine_root(root)
        name = os.path.split(root)[1]
    tmpdir = os.path.join(baw.config.bawtmp(), 'tmp', name)
    baw.utils.log(tmpdir)
    sys.exit(baw.utils.SUCCESS)


def print_venv(root: str):
    tmpdir = baw.runtime.virtual(
        root,
        creates=False,
    )
    baw.utils.log(tmpdir)
    sys.exit(baw.utils.SUCCESS)


def print_covreport(root: str):
    result = os.path.join(
        baw.utils.tmp(root),
        'report',
    )
    baw.utils.log(result)
    sys.exit(baw.utils.SUCCESS)
