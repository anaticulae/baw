# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

from os.path import join

from baw.config import shortcut
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
    command = 'yapf -r -i --style=google'
    return format_(root, cmd=command, verbose=verbose, virtual=virtual)


def format_imports(root: str, verbose: bool = False, virtual: bool = False):
    short = ' -p '.join(sources(root))
    isort = [
        "-o",
        "pytest",
        '-p',
        short,
        "-p",
        "tests",
        "-ot",
        "-k",  # keep direct
        "-sl",  # force single line
        "-ns",  # override default skip of __init__
        "__init__.py",
        "-rc",  # recursive
    ]
    isort = 'isort %s' % (' '.join(isort))
    return format_(root, cmd=isort, verbose=verbose, virtual=virtual)


def format_(
        root: str,
        cmd: str,
        *,
        verbose: bool = False,
        virtual: bool = False,
):
    short = shortcut(root)
    for item in [short, 'tests']:
        source = join(root, item)
        command = '%s %s' % (cmd, source)
        logging('Format source %s' % source)

        completed = run_target(
            root,
            command,
            source,
            virtual=virtual,
            verbose=verbose,
        )
        if completed.returncode:
            logging_error('Error while fromating\n%s' % str(completed))
            return FAILURE
    logging('Format complete')
    return SUCCESS
