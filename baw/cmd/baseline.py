# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2023 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import contextlib
import os

import baw
import baw.cmd.test
import baw.config
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
    baw.log('baseline: something changed')
    baw.git_add(
        root,
        'tests/**',
        update=True,
    )
    baw.log('baseline: commit')
    returnvalue = baw.git_commit(
        root,
        source='',
        message=MESSAGE,
    )
    if returnvalue:
        return returnvalue
    if push:
        baw.log('baseline: push')
        returnvalue = baw.gix.push(root)
    return returnvalue


def test(root, worker: int = 32):
    pre(root)
    testconfig = [f'-n={worker}']
    with enable_baseline():
        baw.log('baseline: determining...')
        baw.cmd.test.run_test(
            root,
            testconfig=testconfig,
            alls=True,
        )
    if commit(
            root,
            push=True,
    ):
        return baw.FAILURE
    return baw.SUCCESS


@contextlib.contextmanager
def enable_baseline():
    baw.log('enable overwriting: BASELINE_REPLACE')
    # TODO: REMOVE LATER
    os.environ['DEV_GIT_REPLACE'] = "1"
    os.environ['BASELINE_REPLACE'] = "1"
    yield


def run(args: dict):
    root = baw.cmd.utils.get_root(args)
    if args['baseline'] == 'test':
        worker = args.get('n', os.cpu_count())
        return test(
            root,
            worker=worker,
        )
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
    baseline.add_argument(
        '-n',
        help='process count; use auto to select os.cpu_count',
        default='auto',
    )
    baseline.set_defaults(func=run)
