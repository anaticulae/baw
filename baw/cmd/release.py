#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019 by Helmut Konrad Fahrendholz. All rights reserved.
# Tis file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================

from contextlib import contextmanager
from os import unlink
from tempfile import TemporaryFile

from baw.config import shortcut
from baw.resources import SETUP_CFG
from baw.runtime import run_target
from baw.utils import FAILURE
from baw.utils import logging
from baw.utils import logging_error
from baw.utils import SUCCESS

# semantic release returns this message if no new release is provided, cause
# of the absent of new features/bugfixes.
NO_RELEASE_MESSAGE = 'No release will be made.'


def release(
        root: str,
        *,
        release_type: str = 'auto',
        stash: bool = False,
        verbose: bool = False,
        sync: bool = True,
        virtual: bool = True,
):
    """Running release. Running test, commit and tag.

    Args:
        root(str): generated project
        release_type(str): major x.0.0
                           minor 0.x.0
                           patch 0.0.x
                           noop  0.0.0 do nothing
                           auto  let semantic release decide
        stash(bool): git stash to test on a clean git directory
        verbose(bool): log additional output
        virtual(bool): run in virtual environment
    Return:
        0 if success else > 0

    Process:
        1. Run complete testsuite
        2. Run Semantic release to create changelog, commit the changelog as
           release-message and create a version tag.
    """
    if sync:
        from baw.cmd.sync import sync as run_sync
        ret = run_sync(
            root,
            verbose=verbose,
            virtual=virtual,
        )
        if ret:
            logging_error('\nSync failed, could not release.\n')
            return ret

    from baw.cmd.test import run_test  # break cyclic imports
    ret = run_test(
        root,
        longrun=True,
        stash=stash,
        verbose=verbose,
        virtual=virtual,
    )
    if ret:
        logging_error('\nTests failed, could not release.\n')
        return ret

    logging("Update version tag")
    with temp_semantic_config(root) as config:
        # Only release with type if user select one. If the user does select
        # a release-type let semantic release decide.
        release_type = '' if release_type == 'auto' else '--%s' % release_type
        cmd = 'semantic-release version %s --config="%s"'
        cmd = cmd % (release_type, config)
        completed = run_target(root, cmd, verbose=verbose)
        logging(completed.stdout)
        if NO_RELEASE_MESSAGE in completed.stdout:
            logging_error('Abort release')
            return FAILURE

    if completed.returncode:
        logging_error('while running semantic-release')
        return completed.returncode

    logging("Update Changelog")

    return SUCCESS


@contextmanager
def temp_semantic_config(root: str):
    short = shortcut(root)
    replaced = SETUP_CFG.replace('$_SHORT_$', short)
    if replaced == SETUP_CFG:
        logging_error('while replacing template')
        exit(FAILURE)
    with TemporaryFile(mode='w', delete=False) as fp:
        fp.write(replaced)
        fp.seek(0)
    yield fp.name

    # remove file
    unlink(fp.name)
