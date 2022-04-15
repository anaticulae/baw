# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import argparse
import os
import sys
import time

import baw.git
import baw.run
import baw.runtime
import baw.utils

# TODO: RENAME TO BISECT?


def main():
    root = baw.run.determine_root(os.getcwd())
    if not baw.git.is_clean(root, verbose=False):
        baw.utils.error(f'not clean, abort: {root}')
        sys.exit(baw.utils.FAILURE)
    parser = create_parser()
    args = parse_args(parser)
    profile(root, args[0], args[1])
    return baw.utils.SUCCESS


def profile(root, cmd, ranges, lookback: int = 20000) -> list:
    todo = git_commits(root, ranges)
    timed = []
    states = []
    for index, (commit, headline) in enumerate(todo, start=1):
        baw.utils.log(f'\n{index}|{len(todo)}')
        baw.utils.log(f'>>> {headline}')
        baw.utils.log(f'git checkout {commit} in {root}')
        if git_checkout(root, commit):
            sys.exit(baw.utils.FAILURE)
        current = time.time()
        baw.utils.log(f'run: {cmd}')
        processed = baw.runtime.run(cmd, cwd=root)
        if processed.returncode == 127:
            baw.utils.error(f'invalid command: {cmd}')
            sys.exit(baw.utils.FAILURE)
        if processed.returncode:
            # the head is not important, we what to see the tail
            baw.utils.error(processed.stdout[-lookback:])
            baw.utils.error(processed.stderr[-lookback:])
        #     sys.exit(baw.utils.FAILURE)
        states.append(processed.returncode)
        diff = time.time() - current
        baw.utils.log(f'done: {int(diff)}')
        timed.append(diff)
    baw.utils.log('\n\nDONE:\n========================')
    for index, (state, commit, timed) in enumerate(zip(states, todo, timed)):
        state = 'X' if state else ' '
        baw.utils.log(f'{commit[0][0:15]}:{state}:   {int(timed)}      '
                      f'{commit[1][0:30]}')
    # git_checkout(root, commit=todo[0])
    git_checkout(root, commit='master')
    return timed


def git_commits(root, ranges) -> list:
    """\
    >>> len(git_commits('.', list(range(5))))
    5
    """
    count = len(ranges)
    cmd = ("git log  --pretty=format:\"%H %s\" | "
           rf'grep -E "(feat|fix|test|refactor)\(" | head -n {count}')
    completed = baw.runtime.run_target(
        root,
        command=cmd,
        cwd=root,
        verbose=False,
    )
    stdout = completed.stdout.strip()
    if completed.returncode:
        baw.utils.error(completed)
        sys.exit(baw.utils.FAILURE)
    result = [line.split(maxsplit=1) for line in stdout.splitlines()]
    return result


def git_checkout(
    root: str,
    commit: str,
) -> int:
    """Checkout he from git repository

    Args:
        root(str): root to generated project
        commit(str): state to reach
    Returns:
        0 if SUCCESS else FAILURE
    """
    cmd = f'git checkout {commit}'
    completed = baw.runtime.run(cmd, cwd=root)
    if completed.returncode:
        msg = f'while checkout {commit}'
        baw.utils.error(msg)
    return completed.returncode


def parse_args(parser) -> tuple:
    args = vars(parser.parse_args())
    cmd = args.get('cmd', 'ls -R | wc - l')
    ranges = int(args.get('range', 1))
    ranges: list = list(range(ranges))
    return cmd, ranges


def create_parser():
    parser = argparse.ArgumentParser(prog='baw_profile')
    # TODO: ADD VERBOSE AND FAIL FAST FLAG
    parser.add_argument('cmd', help='command to profile')
    parser.add_argument(
        'range',
        help='commit to verify',
        nargs='?',
        default='1',
    )
    return parser
