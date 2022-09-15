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

import baw.config
import baw.runtime
import baw.utils


def format_repository(root: str, verbose: bool = False, virtual: bool = False):
    for item in [format_source, format_imports]:
        failure = item(root, verbose=verbose, virtual=virtual)
        if failure:
            return failure
    return baw.utils.SUCCESS


def format_source(root: str, verbose: bool = False, virtual: bool = False):
    if not baw.runtime.installed('yapf', root=root, virtual=virtual):
        return baw.utils.FAILURE
    command = 'yapf -i --style=google setup.py'
    failure = baw.runtime.run_target(
        root,
        command,
        verbose=False,
        virtual=virtual,
    )
    if failure.returncode:
        baw.utils.error(failure)
        return failure.returncode
    # run in parallel if not testing with pytest
    # TODO: yapf does not run on virtual environment properly
    parallel = '-p' if not baw.config.testing() and not virtual else ''
    template_skip = '-e *.tpy'
    # python = baw.config.python(root, virtual=False)
    command = f'yapf -r -i --style=google {template_skip} {parallel} --no-local-style'
    return format_(root, cmd=command, verbose=verbose, virtual=virtual)


def format_imports(root: str, verbose: bool = False, virtual: bool = False):
    if not baw.runtime.installed('isort', root=root, virtual=virtual):
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
            command = f'{cmd} {source}'
            if verbose:
                baw.utils.log(command)
            waitfor.append(
                executor.submit(
                    baw.runtime.run_target,
                    root=root,
                    command=command,
                    cwd=source,
                    virtual=virtual,
                    verbose=verbose,
                ))
        for future in concurrent.futures.as_completed(waitfor):
            completed = future.result()
            if completed.returncode:
                baw.utils.error(f'error while formatting {completed.stderr}')
                return baw.utils.FAILURE
    baw.utils.log(f'{info}: complete\n')
    return baw.utils.SUCCESS
