# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020-2023 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import re
import sys

import baw.runtime
import baw.utils


def cli(
    root: str,
    commits: str,
    args: list,
    venv: bool = False,
    verbose: bool = False,
):
    baw.log(commits)
    commits = commits.split('^')
    if len(commits) == 1:
        bad, good = 'HEAD', commits[0]
    else:
        bad, good = commits
        # args.remove(commits[1])
    # TODO: CHECK GOOD BAD?
    if not args:
        baw.error('nothing to bisect')
        sys.exit(baw.utils.INPUT_ERROR)
    verify = ' '.join(args)
    completed = bisect(
        root,
        verify=verify,
        bad=bad,
        good=good,
        venv=venv,
        verbose=verbose,
    )
    return completed


def bisect(
    root: str,
    verify: str,
    bad: str,
    good: str,
    venv: bool = False,
    verbose: bool = False,
) -> int:
    cmd = f'git bisect start {bad} {good} && git bisect run sh -c "baw {verify}"'
    completed = baw.runtime.run_target(
        root,
        cmd=cmd,
        cwd=root,
        verbose=verbose,
        venv=venv,
    )

    important = collect_findings(completed.stdout)
    baw.log(baw.NEWLINE.join(important))

    # finish bisect
    baw.runtime.run_target(
        root,
        cmd='git bisect reset',
        cwd=root,
        verbose=verbose,
        venv=venv,
    )
    return baw.SUCCESS


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
