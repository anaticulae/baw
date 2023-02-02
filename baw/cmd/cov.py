# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2023 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import os

import baw
import baw.config


def upgrade(root):
    if cov_max(root):
        baw.exitx(f'max cov reached: {root}', returncode=baw.SUCCESS)
    return baw.SUCCESS


def cov_max(root) -> bool:
    """\
    >>> cov_max(__file__)  # change after having 100% in baw
    False
    """
    current = baw.config.coverage_min(root)
    if current == 100:
        return True
    return False


def print_cov(root):
    root = baw.determine_root(os.getcwd())
    current = baw.config.coverage_min(root)
    baw.log(current)
    return baw.SUCCESS


def run(args: dict):
    action = args['cov']
    root = baw.determine_root(os.getcwd())
    if action == 'upgrade':
        return upgrade(root)
    if action == 'print':
        return print_cov(root)
    return baw.FAILURE


def extend_cli(parser):
    cov = parser.add_parser('cov', help='Manage test coverage')
    cov.add_argument(
        'cov',
        help='',
        nargs='?',
        default='print',
        choices='print upgrade'.split(),
    )
    cov.set_defaults(func=run)
