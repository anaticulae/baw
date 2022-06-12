# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import argparse
import functools
import os

import baw.run
import baw.runtime
import baw.utils


def main():
    root = baw.run.determine_root(os.getcwd())
    parser = create_parser()
    cmd, worker = parse_args(parser)
    run(root, cmd, worker)
    return baw.utils.SUCCESS


def run(root, cmd, worker: int = 1):
    import power
    generated = power.generated(project=root)
    assert os.path.exists(generated), str(generated)
    todo = []
    files = [str(item) for item in os.listdir(generated) if '_' in str(item)]
    for index, path in enumerate(files):
        path = os.path.join(generated, path)
        assert os.path.exists(path), str(path)
        progress = str(int(100.0 * (index / len(files)))).zfill(3)
        todo.append(functools.partial(
            single,
            cmd,
            path,
            progress,
        ))
    baw.utils.fork(*todo, worker=worker)


def single(cmd, cwd, progress: str):
    logmsg = f'"{progress} {cmd}" in {cwd}'
    baw.utils.log(logmsg)
    completed = baw.runtime.run(command=cmd, cwd=cwd)
    if not completed.returncode:
        return
    baw.utils.error(f'{logmsg}\n{completed.stderr}\n{completed.stdout}')


def parse_args(parser) -> tuple:
    args = vars(parser.parse_args())
    cmd = args['cmd']
    worker = int(args.get('worker', 1))
    return cmd, worker


def create_parser():
    parser = argparse.ArgumentParser(prog='baw_regen')
    # TODO: ADD VERBOSE AND FAIL FAST FLAG
    parser.add_argument('cmd', help='command to run')
    parser.add_argument(
        'worker',
        help='number of parallel executor',
        nargs='?',
        default='1',
    )
    return parser
