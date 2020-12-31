# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import re
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
    try:
        # --bisect HEAD~10
        args.remove(commits[0])
        args.remove('--bisect')
    except ValueError:
        # --bisect=HEAD~10
        # TODO: CHECK GOOD BAD?
        args.remove(f'--bisect={commits[0]}')
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

    important = collect_findings(completed.stdout)
    baw.utils.log(baw.utils.NEWLINE.join(important))

    # finish bisect
    baw.runtime.run_target(
        root,
        command='git bisect reset',
        cwd=root,
        verbose=verbose,
        virtual=virtual,
    )
    return baw.utils.SUCCESS


HASH = r'^\[{0,1}[a-z0-9]{40}\]{0,1}'


def collect_findings(log) -> list:
    """\
    >>> collect_findings('95281ec351e36a45bc6b1ec39f7f8061a6db1851 is the first bad commit')
    ['95281ec351e36a45bc6b1ec39f7f8061a6db1851 is the first bad commit']
    >>> collect_findings('[b96f38e3e3ac2555477197bb51adb4d68a6d7281] test(debug): add more debugging information')
    ['[b96f38e3e3ac2555477197bb51adb4d68a6d7281] test(debug): add more debugging information']
    """
    result = []
    for line in log.splitlines():
        if not re.search(HASH, line):
            continue
        result.append(line)
    return result
