# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import sys

import baw.git
import baw.runtime
import baw.utils


def cli(
        root: str,
        commits: list,
        virtual: bool = False,
        verbose: bool = False,
):
    args = list(sys.argv)
    if not len(commits) in (1, 2):
        baw.utils.error(f'invalid commit definition {commits}')
        exit(baw.utils.INPUT_ERROR)
    if len(commits) == 1:
        bad, good = 'HEAD', commits[0]
    else:
        bad, good = commits
        args.remove(commits[1])
    args.remove(commits[0])
    args.remove('--bisect')
    args = args[1:]
    if not args:
        baw.utils.error('nothing to bisect')
        exit(baw.utils.INPUT_ERROR)
    verify = ' '.join(args)

    completed = bisect(
        root,
        verify=verify,
        bad=bad,
        good=good,
        virtual=virtual,
        verbose=verbose,
    )
    return completed


def bisect(
        root: str,
        verify: str,
        bad: str,
        good: str,
        virtual: bool = False,
        verbose: bool = False,
) -> int:
    cmd = f'git bisect start {bad} {good} && git bisect run sh -c "baw {verify}"'
    completed = baw.runtime.run_target(
        root,
        command=cmd,
        cwd=root,
        verbose=verbose,
        virtual=virtual,
    )
    baw.utils.log(completed.stdout)
    baw.runtime.run_target(
        root,
        command='git bisect reset',
        cwd=root,
        verbose=verbose,
        virtual=virtual,
    )

    return completed.returncode
