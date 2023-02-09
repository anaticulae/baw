# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019-2023 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import os
import re
import sys

import utila
import utila.quick

import baw.cmd.image
import baw.cmd.utils
import baw.config
import baw.git
import baw.project
import baw.runtime
import baw.utils


def evaluate(args: dict):
    root = baw.cmd.utils.get_root(args)
    value = args['info'][0]
    returncode = prints(
        root=root,
        value=value,
        verbose=args.get('verbose', False),
    )
    return returncode


def prints(root, value: str, verbose: bool = False) -> int:  # pylint:disable=R1260,R0911
    if value == 'tmp':
        print_tmp(root)
        return baw.SUCCESS
    if value == 'venv':
        print_venv(root)
        return baw.SUCCESS
    if value == 'covreport':
        print_covreport(root)
        return baw.SUCCESS
    if value == 'requirement':
        baw.log(requirement_hash(
            root,
            verbose=verbose,
        ))
        return baw.SUCCESS
    if value == 'name':
        baw.log(baw.config.name(root))
        return baw.SUCCESS
    if value == 'shortcut':
        baw.log(baw.config.shortcut(root))
        return baw.SUCCESS
    if value == 'sources':
        baw.log(' '.join(baw.config.sources(root) + ['tests']))
        return baw.SUCCESS
    if value == 'pip':
        baw.log(pip_version(root, verbose=verbose))
        return baw.SUCCESS
    if value == 'image':
        baw.log(baw.cmd.image.tag(root))
        return baw.SUCCESS
    if value == 'describe':
        baw.log(baw.git.describe(root))
        return baw.SUCCESS
    if value == 'stable':
        baw.log(baw.project.version.determine(root, verbose=verbose))
        return baw.SUCCESS
    if value == 'branch':
        baw.log(baw.git.branchname(root))
        return baw.SUCCESS
    if value == 'cov':
        print_cov()
        return baw.SUCCESS
    if value == 'clean':
        if baw.git.is_clean(root, verbose=False):
            baw.log('very clean')
            return baw.SUCCESS
        baw.log('not clean\n')
        # log data
        baw.log(baw.runtime.run('git status', root).stdout)
        return baw.FAILURE
    return baw.FAILURE


def print_tmp(root: str):
    name: str = 'global'
    if not baw.config.venv_global():
        root = baw.project.determine_root(root)
        name = os.path.split(root)[1]
    tmpdir = os.path.join(baw.config.bawtmp(), 'tmp', name)
    baw.log(tmpdir)
    sys.exit(baw.SUCCESS)


def pip_version(root: str, verbose: bool = False):
    """\
    >>> import baw;pip_version(baw.ROOT)
    '...'
    >>> pip_version(baw.ROOT, verbose=True)
    'baw==...'
    """
    current = utila.quick.git_hash(root)
    result = current
    if verbose:
        name = utila.baw_name(root)
        result = f'{name}=={result}'
    return result


def print_venv(root: str):
    tmpdir = baw.runtime.virtual(
        root,
        creates=False,
    )
    baw.log(tmpdir)
    sys.exit(baw.SUCCESS)


def print_covreport(root: str):
    result = os.path.join(
        baw.utils.tmp(root),
        'report',
    )
    baw.log(result)
    sys.exit(baw.SUCCESS)


def print_cov() -> int:
    completed = utila.run('baw test --cov --no_report')
    if completed.returncode:
        return completed.returncode
    coverage = re.search(
        r'Total coverage: (?P<coverage>\d{1,3}\.\d{2})',
        completed.stdout,
    )
    if not coverage:
        sys.exit(baw.FAILURE)
    result = float(coverage['coverage'])
    baw.log(result)
    sys.exit(baw.SUCCESS)


def requirement_hash(root: str, verbose: bool = False) -> str:
    """\
    >>> import baw
    >>> requirement_hash(baw.ROOT)
    '...'
    >>> requirement_hash(baw.ROOT, verbose=True)
    'baw:...'
    """
    todo = ('Jenkinsfile requirements.txt requirements.dev '
            'requirements.extra tests/conftest.py').split()
    content = ''
    for fname in todo:
        path = os.path.join(root, fname)
        if not os.path.exists(path):
            continue
        content += baw.utils.file_read(path)
    hashed = str(baw.utils.binhash(content))
    if verbose:
        name = baw.config.shortcut(root)
        hashed = f'{name}:{hashed}'
    return hashed


CHOISES = ('name shortcut sources venv tmp '
           'covreport requirement image clean describe stable '
           'branch pip cov').split()


def extend_cli(parser):
    info = parser.add_parser('info', help='Print project information')
    info.add_argument(
        'info',
        help='Print project information',
        nargs=1,
        choices=CHOISES,
    )
    info.set_defaults(func=evaluate)
