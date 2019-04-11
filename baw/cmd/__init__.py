#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019 by Helmut Konrad Fahrendholz. All rights reserved.
# Tis file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================

from baw.cmd.doc import doc
from baw.cmd.init import init
from baw.cmd.release import drop_release
from baw.cmd.release import release
from baw.cmd.sync import sync
from baw.cmd.sync import sync_files
from baw.cmd.test import run_test
from baw.cmd.upgrade import upgrade
from baw.utils import logging_error
from baw.utils import SUCCESS


def sync_and_test(
        root: str,
        *,
        quiet: bool = False,
        stash: bool = False,
        verbose: bool = False,
        virtual: bool = False,
):
    if quiet:
        verbose = False
    ret = sync(
        root,
        verbose=verbose,
        virtual=virtual,
    )
    if ret:
        logging_error('\nSync failed, could not release.\n')
        return ret

    ret = run_test(
        root,
        longrun=True,
        stash=stash,
        verbose=verbose,
        virtual=virtual,
        quiet=quiet,
    )
    if ret:
        logging_error('\nTests failed, could not release.\n')
        return ret
    return SUCCESS
