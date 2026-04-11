# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2022-2023 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import os
import sys

import baw.config
import baw.project
import baw.utils


def get_root(args):
    directory = run_environment(args)
    root = determine_root(directory)
    if not root:
        return sys.exit(baw.FAILURE)
    return root


def run_environment(args):
    root = setup_environment(args['raw'],)
    return root


def setup_environment(raw):  # pylint: disable=W0621
    if raw:
        # expose raw out flag
        os.environ[baw.utils.PLAINOUTPUT] = "TRUE"
    root = os.getcwd()
    return root


def determine_root(directory) -> str | None:
    root = baw.project.determine_root(directory)
    if not root:
        baw.error(f'require .baw file: {directory}')
        return None
    return root
