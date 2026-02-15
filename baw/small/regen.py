# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2022-2023 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import argparse
import functools
import os

import baw.cmd.utils
import baw.config
import baw.runtime
import baw.utils


def main():
    root = baw.cmd.utils.determine_root(os.getcwd())
    parser = create_parser()
    cmd, worker = parse_args(parser)
    run(root, cmd, worker)
    return baw.SUCCESS


def run(root, cmd, worker: int = 1):
    # generated = resinf.generated(project=root)
    generated = os.path.join(baw.config.bawtmp(), root)
    assert os.path.exists(generated), str(generated)
    todo = []
    files = [str(item) for item in os.listdir(generated) if '_' in str(item)]
    for index, file_path in enumerate(files):
        path = os.path.join(generated, file_path)
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
    baw.log(logmsg)
    completed = baw.runtime.run(cmd=cmd, cwd=cwd)
    append_log(completed=completed, cwd=cwd)
    if not completed.returncode:
        return
    baw.error(f'{logmsg}\n{completed.stderr}\n{completed.stdout}')


def append_log(completed, cwd: str):
    logpath = os.path.join(cwd, 'generated.log')
    if not os.path.exists(logpath):
        baw.error(f'miss log path: {logpath}')
        return
    separator = '\n\n' + '=' * 30 + 'REGENREGENREGENREGEN' + '=' * 30 + '\n\n'
    baw.utils.file_append(logpath, separator)
    baw.utils.file_append(logpath, completed.stdout)
    baw.utils.file_append(logpath, completed.stderr)


def parse_args(parser) -> tuple:
    args = vars(parser.parse_args())
    cmd = args['cmd']
    worker = int(args.get('worker', 1))
    return cmd, worker


def create_parser():
    parser = argparse.ArgumentParser(prog='baw_regen')
    # TODO: ADD VERBOSE AND FAIL FAST FLAG
    parser.add_argument('cmd', help='cmd to run')
    parser.add_argument(
        'worker',
        help='number of parallel executor',
        nargs='?',
        default='1',
    )
    return parser
