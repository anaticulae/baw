# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019-2023 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import baw.config
import baw.runtime
import baw.utils


def evaluate(args: dict):
    root = baw.cmd.utils.get_root(args)
    result = install(
        root=root,
        venv=args.get('venv', False),
        verbose=args.get('verbose', False),
        dev=args.get('dev', False),
        remove=args.get('remove', False),
    )
    return result


def install(
    root: str,
    *,
    dev: bool = False,
    remove: bool = False,
    venv: bool = False,
    verbose: bool = False,
):
    if remove:
        remove_current(root, venv=venv, verbose=verbose)
    # -f always install newest one
    python = baw.config.python(root, venv=venv)
    cmd = f'{python} '
    cmd += '-mpip install -e .' if dev else 'setup.py install -f'
    # run target
    completed = baw.runtime.run_target(
        root,
        cmd,
        root,
        verbose=verbose,
        venv=venv,
    )
    if completed.returncode:
        baw.utils.log(completed.stdout)
        baw.utils.error(completed.stderr)
    if not verbose:
        baw.utils.log('done')
    return completed.returncode


def remove_current(root: str, venv: bool = False, verbose: bool = False):
    package = baw.config.shortcut(root)
    for _ in range(10):
        cmd = f'pip uninstall {package} --yes'
        completed = baw.runtime.run_target(
            root,
            cmd=cmd,
            verbose=verbose,
            venv=venv,
        )
        if completed.stderr:
            break


def extend_cli(parser):
    test = parser.add_parser('install', help='Run install task')
    test.add_argument(
        '--remove',
        help='remove current version before',
        action='store_true',
    )
    test.add_argument(
        '--dev',
        help='install in development mode',
        action='store_true',
    )
    test.set_defaults(func=evaluate)
