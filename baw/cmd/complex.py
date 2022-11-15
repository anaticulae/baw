# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019-2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import baw.cmd.sync
import baw.cmd.test
import baw.utils


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
    venv: bool = False,
):
    verbose = False if quiet else verbose
    if sync:
        ret = baw.cmd.sync.sync(
            root,
            packages=packages,
            verbose=verbose,
            venv=venv,
        )
        if ret:
            baw.utils.error('\nSync failed, could not release.\n')
            return ret
    if not test:
        return baw.utils.SUCCESS
    ret = baw.cmd.test.run_test(
        root,
        generate=generate,
        fast=test,
        longrun=longrun,
        quiet=quiet,
        stash=stash,
        testconfig=testconfig,
        verbose=verbose,
        venv=venv,
    )
    if ret:
        if not quiet:
            baw.utils.error('Tests failed.')
        return ret
    return baw.utils.SUCCESS
