# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019-2023 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import concurrent.futures
import os

import baw.cmd.utils
import baw.config
import baw.runtime
import baw.utils


def evaluate(args):
    root = baw.cmd.utils.get_root(args)
    result = format_repository(
        root,
        verbose=args.get('verbose', False),
        venv=args.get('venv', False),
    )
    return result


def format_repository(root: str, verbose: bool = False, venv: bool = False):
    for item in [format_source, format_imports]:
        failure = item(root, verbose=verbose, venv=venv)
        if failure:
            return failure
    return baw.utils.SUCCESS


def format_source(root: str, verbose: bool = False, venv: bool = False):
    if not baw.runtime.installed('yapf', root=root, venv=venv):
        return baw.utils.FAILURE
    cmd = 'yapf -i --style=google setup.py'
    failure = baw.runtime.run_target(
        root,
        cmd,
        verbose=False,
        venv=venv,
    )
    if failure.returncode:
        baw.utils.error(failure)
        return failure.returncode
    # run in parallel if not testing with pytest
    # TODO: yapf does not run on venv environment properly
    parallel = '-p' if not baw.config.testing() and not venv else ''
    template_skip = '-e *.tpy'
    # python = baw.config.python(root, venv=False)
    cmd = f'yapf -r -i --style=google {template_skip} {parallel} --no-local-style'
    return format_(root, cmd=cmd, verbose=verbose, venv=venv)


def format_imports(root: str, verbose: bool = False, venv: bool = False):
    if not baw.runtime.installed('isort', root=root, venv=venv):
        return baw.utils.FAILURE
    project_sources = baw.config.sources(root)
    short = ' -p '.join(project_sources)
    isort = [
        "-o",
        "pytest",
        '-p',
        short,
        "-p",
        "tests",
        "--ot",
        "--sl",  # force single line
        "--ns",  # override default skip of __init__
        "__init__.py",
        "--line-width 999",  # do not break imports
    ]
    isort: str = ' '.join(isort)
    # python = baw.config.python(root, venv=False)
    cmd = f'isort {isort}'
    return format_(
        root,
        cmd=cmd,
        info='sort imports',
        verbose=verbose,
        venv=venv,
    )


def format_(
    root: str,
    cmd: str,
    info: str = 'format source',
    *,
    verbose: bool = False,
    venv: bool = False,
):
    baw.utils.log(info)
    folder = baw.config.sources(root)

    # check that `tests` path exists
    testpath = os.path.join(root, 'tests')
    if os.path.exists(testpath):
        folder.append('tests')

    with concurrent.futures.ThreadPoolExecutor(max_workers=12) as executor:
        waitfor = []
        for item in folder:
            source = os.path.join(root, item)
            cmdx = f'{cmd} {source}'
            if verbose:
                baw.utils.log(cmdx)
            waitfor.append(
                executor.submit(
                    baw.runtime.run_target,
                    root=root,
                    cmd=cmdx,
                    cwd=source,
                    venv=venv,
                    verbose=verbose,
                ))
        for future in concurrent.futures.as_completed(waitfor):
            completed = future.result()
            if completed.returncode:
                baw.utils.error(f'error while formatting {completed.stderr}')
                return baw.utils.FAILURE
    baw.utils.log(f'{info}: complete\n')
    return baw.utils.SUCCESS


def extend_cli(parser):
    test = parser.add_parser('format', help='Format code')
    test.add_argument(
        '--imports',
        help='run isort',
        action='store_true',
    )
    test.add_argument(
        '--code',
        help='run yapf',
        action='store_true',
    )
    test.set_defaults(func=evaluate)
