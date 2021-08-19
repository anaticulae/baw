# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019-2021 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

from baw.cmd.sync import sync as run_sync
from baw.cmd.test import run_test
from baw.utils import SUCCESS
from baw.utils import logging_error


def sync_and_test(
    root: str,
    packages: str = 'all',
    testconfig=None,
    *,
    longrun: bool = False,
    quiet: bool = False,
    generate: bool = False,
    stash: bool = False,
    sync: bool = False,
    test: bool = True,
    verbose: bool = False,
    virtual: bool = False,
):
    verbose = False if quiet else verbose
    if sync:
        ret = run_sync(
            root,
            packages=packages,
            verbose=verbose,
            virtual=virtual,
        )
        if ret:
            logging_error('\nSync failed, could not release.\n')
            return ret

    if not test:
        return SUCCESS

    ret = run_test(
        root,
        generate=generate,
        longrun=longrun,
        quiet=quiet,
        stash=stash,
        testconfig=testconfig,
        verbose=verbose,
        virtual=virtual,
    )
    if ret:
        if not quiet:
            logging_error('Tests failed.')
        return ret
    return SUCCESS
