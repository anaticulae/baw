# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019-2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import concurrent.futures
import os
import sys

from baw.config import sources
from baw.config import testing
from baw.runtime import run_target
from baw.utils import FAILURE
from baw.utils import SUCCESS
from baw.utils import error
from baw.utils import log


def format_repository(root: str, verbose: bool = False, virtual: bool = False):
    for item in [format_source, format_imports]:
        failure = item(root, verbose=verbose, virtual=virtual)
        if failure:
            return failure
    return SUCCESS


def installed(program: str, root: str, virtual: bool = False):
    done = run_target(
        root,
        command=f'which {program}',
        virtual=virtual,
        verbose=False,
    )
    if done.returncode == SUCCESS:
        return True
    error(f'not installed: {program}')
    error(f'venv: {virtual}')
    error(f'python: {sys.executable}')
    error(f'path: {" ".join(sys.path)}')
    return False


def format_source(root: str, verbose: bool = False, virtual: bool = False):
    if not installed('yapf', root=root, virtual=virtual):
        return FAILURE
    command = 'yapf -i --style=google setup.py'
    failure = run_target(root, command, verbose=False, virtual=virtual)
    if failure.returncode:
        error(failure)
        return failure.returncode
    # run in parallel if not testing with pytest
    # TODO: yapf does not run on virtual environment properly
    parallel = '-p' if not testing() and not virtual else ''
    # python = baw.config.python(root, virtual=False)
    command = f'yapf -r -i --style=google {parallel} --no-local-style'
    return format_(root, cmd=command, verbose=verbose, virtual=virtual)


def format_imports(root: str, verbose: bool = False, virtual: bool = False):
    if not installed('isort', root=root, virtual=virtual):
        return FAILURE
    project_sources = sources(root)
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
    # python = baw.config.python(root, virtual=False)
    cmd = f'isort {isort}'
    return format_(
        root,
        cmd=cmd,
        info='sort imports',
        verbose=verbose,
        virtual=virtual,
    )


def format_(
    root: str,
    cmd: str,
    info: str = 'format source',
    *,
    verbose: bool = False,
    virtual: bool = False,
):
    log(info)
    folder = sources(root)

    # check that `tests` path exists
    testpath = os.path.join(root, 'tests')
    if os.path.exists(testpath):
        folder.append('tests')

    with concurrent.futures.ThreadPoolExecutor(max_workers=12) as executor:
        waitfor = []
        for item in folder:
            source = os.path.join(root, item)
            command = f'{cmd} {source}'
            if verbose:
                log(command)
            waitfor.append(
                executor.submit(
                    run_target,
                    root=root,
                    command=command,
                    cwd=source,
                    virtual=virtual,
                    verbose=verbose,
                ))
        for future in concurrent.futures.as_completed(waitfor):
            completed = future.result()
            if completed.returncode:
                error(f'error while formatting {completed.stderr}')
                return FAILURE
    log(f'{info}: complete\n')
    return SUCCESS
