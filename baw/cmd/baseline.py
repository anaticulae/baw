# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2023 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import baw
import baw.cmd.test
import baw.gix

MESSAGE = """\
test(baseline): adjust baseline
"""


def pre(root: str):
    if not baw.gix.is_clean(root, verbose=False):
        baw.log(baw.gix.modified(root))
        baw.exitx(f'could not baseline, repo is not clean: {root}')
    return baw.SUCCESS


def commit(root: str, push: bool = True) -> int:
    if baw.gix.is_clean(root, verbose=False):
        baw.log('baseline: nothing changed')
        return baw.SUCCESS
    baw.gix.add(
        root,
        'tests/**',
        update=True,
    )
    returnvalue = baw.gix.commit(
        root,
        source='',
        message=MESSAGE,
    )
    if returnvalue:
        return returnvalue
    if push:
        returnvalue = baw.gix.push(root)
    return returnvalue


def test(root):
    pre(root)
    baw.cmd.test.run_test(root, alls=True)
    if commit(root):
        return baw.FAILURE
    return baw.SUCCESS


def run(args: dict):
    root = baw.cmd.utils.get_root(args)
    if args['baseline'] == 'test':
        return test(root)
    return baw.FAILURE


def extend_cli(parser):
    baseline = parser.add_parser('baseline', help='Run baseline command')
    baseline.add_argument(
        'baseline',
        help='Use baseline operation',
        choices='test clean'.split(),
        nargs='?',
        default='test',
    )
    baseline.set_defaults(func=run)
