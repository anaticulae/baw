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

import baw.cmd.utils
import baw.config
import baw.project
import baw.runtime
import baw.utils


def evaluate(args: dict):
    root = baw.cmd.utils.get_root(args)
    value = args['info'][0]
    prints(
        root=root,
        value=value,
        verbose=args.get('verbose', False),
    )
    return baw.utils.SUCCESS


def prints(root, value: str, verbose: bool = False):
    if value == 'tmp':
        print_tmp(root)
        return
    if value == 'venv':
        print_venv(root)
        return
    if value == 'covreport':
        print_covreport(root)
        return
    if value == 'requirement':
        if verbose:
            name = baw.config.shortcut(root)
            baw.utils.log(f'{name}-', end='')
        baw.utils.log(print_requirement_hash(root))
        return
    if value == 'name':
        baw.utils.log(baw.config.name(root))
        sys.exit(baw.utils.SUCCESS)
    if value == 'shortcut':
        baw.utils.log(baw.config.shortcut(root))
        sys.exit(baw.utils.SUCCESS)


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


def print_requirement_hash(root: str) -> str:
    """\
    >>> import baw
    >>> str(print_requirement_hash(baw.ROOT))
    '...'
    """
    todo = 'Jenkinsfile requirements.txt requirements.dev requirements.extra'.split()  # yapf:disable
    content = ''
    for fname in todo:
        path = os.path.join(root, fname)
        if not os.path.exists(path):
            continue
        content += baw.utils.file_read(path)
    hashed = baw.utils.binhash(content)
    return hashed


def extend_cli(parser):
    info = parser.add_parser('info', help='Print project information')
    info.add_argument(
        'info',
        help='Print project information',
        nargs=1,
        choices='name shortcut venv tmp covreport requirement'.split(),
    )
    info.set_defaults(func=evaluate)
