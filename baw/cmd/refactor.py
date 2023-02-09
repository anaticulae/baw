# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2022-2023 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import re
import sys

import utila

import baw.cmd.utils
import baw.gix
import baw.resources
import baw.utils


def run(
    root: str,
    verbose: bool = True,
):
    if not baw.gix.is_clean(root, verbose=False):
        baw.error(f'clean before refactor: {root}')
        sys.exit(baw.FAILURE)
    changed = pattern_run(
        root,
        verbose=verbose,
    )
    if changed:
        baw.git_commit(
            root,
            source='.',
            message='refactor(replace): automated replacement',
            verbose=False,
        )
    else:
        baw.log('nothing todo')
    sys.exit(baw.SUCCESS)


def pattern_run(root: str, verbose: bool) -> bool:
    splitted = todo()
    changed = False
    for path in files(root):
        content = baw.utils.file_read(path)
        before = hash(content)
        for key, value in splitted.items():
            content = content.replace(key, value)
        if hash(content) != before:
            if verbose:
                baw.log(f'refactor: {path}')
            changed = True
        baw.utils.file_replace(path, content)
    return changed


def todo() -> dict:
    """\
    >>> len(todo()) > 10
    True
    """
    result = {}
    for line in baw.resources.REFACTOR.splitlines():
        line = line.strip()
        if not line:
            continue
        splitted = re.split(r'(.*?)[ ]{10,}(.*?)', line)
        try:
            result[splitted[1]] = splitted[3]
        except IndexError:
            baw.error(f'not enough spaces between: {line}')
            sys.exit(baw.FAILURE)
    return result


def files(root: str) -> list:
    collected = utila.file_list(
        path=root,
        include='py',
        recursive=True,
        absolute=True,
    )
    result = []
    for path in collected:
        if 'build' in path:
            continue
        result.append(path)
    return result


def evals(args: dict):
    root = baw.cmd.utils.get_root(args)
    baw.log(f'refactor: {root}')
    run(root=root,)


def extend_cli(parser):
    created = parser.add_parser(
        'refactor',
        help='Run refactor',
    )
    created.set_defaults(func=evals)
