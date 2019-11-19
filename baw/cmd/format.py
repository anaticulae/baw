# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import concurrent.futures
import functools
import os

from baw.config import sources
from baw.runtime import run_target
from baw.utils import FAILURE
from baw.utils import SUCCESS
from baw.utils import logging
from baw.utils import logging_error


def format_repository(root: str, verbose: bool = False, virtual: bool = False):
    for item in [format_source, format_imports]:
        failure = item(root, verbose=verbose, virtual=virtual)
        if failure:
            return failure
    return SUCCESS


def format_source(root: str, verbose: bool = False, virtual: bool = False):
    command = 'yapf -r -i --style=google -p'
    return format_(root, cmd=command, verbose=verbose, virtual=virtual)


def format_imports(root: str, verbose: bool = False, virtual: bool = False):
    project_sources = sources(root)
    short = ' -p '.join(project_sources)
    isort = [
        "-o",
        "pytest",
        '-p',
        short,
        "-p",
        "tests",
        "-ot",
        "-y",
        "-sl",  # force single line
        "-ns",  # override default skip of __init__
        "__init__.py",
        "-rc",  # recursive
    ]
    isort = 'isort %s' % (' '.join(isort))
    return format_(
        root,
        cmd=isort,
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
    todo = []
    folder = sources(root)

    # check that `tests` path exists
    testpath = os.path.join(root, 'tests')
    if os.path.exists(testpath):
        folder.append('tests')
    for item in folder:
        source = os.path.join(root, item)
        command = f'{cmd} {source}'
        runnable = functools.partial(
            run_target,
            root=root,
            command=command,
            cwd=source,
            virtual=virtual,
            verbose=verbose,
        )
        todo.append(runnable)

    with concurrent.futures.ThreadPoolExecutor(max_workers=12) as executor:
        waitfor = []
        for runme in todo:
            logging(f'{info}: {runme.keywords["cwd"]}')
            waitfor.append(executor.submit(runme))

        for future in concurrent.futures.as_completed(waitfor):
            completed = future.result()
            if completed.returncode:
                logging_error(f'error while formatting {completed}')
                return FAILURE

    logging('format complete\n')
    return SUCCESS
