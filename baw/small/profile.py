# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2022-2023 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import argparse
import os
import sys
import time

import baw.cmd.utils
import baw.gix
import baw.run
import baw.runtime
import baw.utils

# TODO: RENAME TO BISECT?


def main():
    root = baw.cmd.utils.determine_root(os.getcwd())
    if not baw.gix.is_clean(root, verbose=False):
        baw.error(f'not clean, abort: {root}')
        sys.exit(baw.FAILURE)
    parser = create_parser()
    args = parse_args(parser)
    profile(root, args[0], args[1])
    return baw.SUCCESS


def profile(root, cmd, ranges, lookback: int = 20000) -> list:
    todo = commits(root, ranges)
    timed = []
    states = []
    for index, (commit, headline) in enumerate(todo, start=1):
        baw.log(f'\n{index}|{len(todo)}')
        baw.log(f'>>> {headline}')
        baw.log(f'git checkout {commit} in {root}')
        if baw.gix.checkout(root, commit):
            sys.exit(baw.FAILURE)
        current = time.time()
        baw.log(f'run: {cmd}')
        processed = baw.runtime.run(cmd, cwd=root)
        if processed.returncode == 127:
            baw.error(f'invalid cmd: {cmd}')
            sys.exit(baw.FAILURE)
        if processed.returncode:
            # the head is not important, we what to see the tail
            baw.error(processed.stdout[-lookback:])
            baw.error(processed.stderr[-lookback:])
        #     sys.exit(baw.FAILURE)
        states.append(processed.returncode)
        diff = round(time.time() - current, 4)
        baw.log(f'done: {diff}')
        timed.append(diff)
    baw.log('\n\nDONE:\n========================')
    for index, (state, commit, timed) in enumerate(zip(states, todo, timed)):
        raw = 'X' if state else ' '
        baw.log(f'{commit[0][0:15]}:{raw}:   {int(timed)}      '
                f'{commit[1][0:30]}')
    # checkout(root, commit=todo[0])
    baw.gix.checkout(root, branch='master')
    return timed


def commits(root, ranges) -> list:
    count = len(ranges)
    cmd = 'git log --pretty=format:\"%H %s\" '
    cmd += r'| grep -E "(feat|fix|test|refactor)\(" '
    cmd += f'| head -n {count}'
    # grep detects the first n-commits and close the inpipe ealier bevore
    # all data is processed. This is not a problem for us.
    no_error = ['grep: write error: Illegal seek\n']
    completed = baw.runtime.run_target(
        root,
        cmd=cmd,
        cwd=root,
        skip_error_message=no_error,
        verbose=False,
    )
    if completed.stderr:
        # see above
        completed.stderr = completed.stderr.replace(no_error[0], '')
    stdout = completed.stdout.strip()
    if completed.returncode or completed.stderr:
        baw.error(completed)
        sys.exit(baw.FAILURE)
    result = [line.split(maxsplit=1) for line in stdout.splitlines()]
    return result


def parse_args(parser) -> tuple:
    args = vars(parser.parse_args())
    cmd = args.get('cmd', 'ls -R | wc - l')
    ranges = int(args.get('range', 1))
    ranges: list = list(range(ranges))
    return cmd, ranges


def create_parser():
    parser = argparse.ArgumentParser(prog='baw_profile')
    # TODO: ADD VERBOSE AND FAIL FAST FLAG
    parser.add_argument('cmd', help='cmd to profile')
    parser.add_argument(
        'range',
        help='commit to verify',
        nargs='?',
        default='1',
    )
    return parser
