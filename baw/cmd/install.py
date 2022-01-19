# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019-2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import baw.config
from baw.runtime import run_target
from baw.utils import error
from baw.utils import log


def install(
    root: str,
    *,
    dev: bool = False,
    remove: bool = False,
    virtual: bool = False,
    verbose: bool = False,
):
    if remove:
        remove_current(root, virtual=virtual, verbose=verbose)
    # -f always install newest one
    python = baw.config.python(root, virtual=virtual)
    if dev:
        # TODO: USE PIP FOR BOTH?
        command = f'{python} -mpip install -e .'
    else:
        command = f'{python} setup.py install -f'
    # run target
    completed = run_target(
        root,
        command,
        root,
        verbose=verbose,
        virtual=virtual,
    )
    if completed.returncode:
        log(completed.stdout)
        error(completed.stderr)
    if not verbose:
        log('done')
    return completed.returncode


def remove_current(root: str, virtual: bool = False, verbose: bool = False):
    package = baw.config.shortcut(root)
    while range(10):
        cmd = f'pip uninstall {package} --yes'
        completed = run_target(
            root,
            command=cmd,
            verbose=verbose,
            virtual=virtual,
        )
        if completed.stderr:
            break
