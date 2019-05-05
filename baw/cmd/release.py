#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================
from contextlib import contextmanager
from functools import partial
from os import unlink
from os.path import exists
from os.path import join
from re import match
from tempfile import TemporaryFile

import baw.cmd
from baw.config import shortcut
from baw.git import git_checkout
from baw.resources import SETUP_CFG
from baw.runtime import run_target
from baw.utils import FAILURE
from baw.utils import SUCCESS
from baw.utils import logging
from baw.utils import logging_error

# semantic release returns this message if no new release is provided, cause
# of the absent of new features/bugfixes.
NO_RELEASE_MESSAGE = 'No release will be made.'


def release(
        root: str,
        *,
        release_type: str = 'auto',
        stash: bool = True,
        sync: bool = True,
        verbose: bool = False,
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
        verbose(bool): log additional output
        virtual(bool): run in virtual environment
    Return:
        0 if success else > 0

    Process:
        1. Run complete testsuite
        2. Run Semantic release to create changelog, commit the changelog as
           release-message and create a version tag.
    """
    ret = baw.cmd.sync_and_test(
        root,
        longrun=True,
        packages='dev',
        stash=stash,
        sync=sync,
        testconfig=None,
        verbose=verbose,
        virtual=virtual,
    )
    if ret:
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


RELEASE_PATTERN = r'(?P<release>v\d+\.\d+\.\d+)'

DEFAULT_RELEASE = 'v0.0.0'


def drop(
        root: str,
        virtual: bool = False,
        verbose: bool = False,
):
    """Remove the last release tag and commit

    1. Check if last commit is a tagged release, if not abbort
    2. Remove last commit git reset HEAD~1
    3. Checkout CHANGELOG and __init__.py
    4. Remove tag
    """
    logging('Start dropping release')

    # git tag --contains HEAD -> Answer the last commit
    logging('Detect current release:')
    runner = partial(run_target, verbose=verbose, virtual=virtual)
    completed = runner(root, 'git tag --contains HEAD')
    matched = match(RELEASE_PATTERN, completed.stdout)
    if not matched:
        logging_error('No release tag detected')
        return FAILURE
    current_release = matched['release']

    # do not remove the first commit/release in the repository
    if current_release == DEFAULT_RELEASE:
        logging_error('Could not remove %s release' % DEFAULT_RELEASE)
        return FAILURE
    logging(current_release)

    # remove the last release commit
    # git reset HEAD~1
    logging('Remove last commit')
    completed = runner(root, 'git reset HEAD~1')
    if completed.returncode:
        logging_error('while removing the last commit: %s' % str(completed))
        return completed.returncode

    # git checkout CHANGELOG.md, $_NAME_$/__init__..py
    completed = reset_resources(root, virtual=virtual, verbose=verbose)
    if completed:
        return completed

    # git tag -d HEAD
    logging('Remove release tag')
    completed = runner(root, 'git tag -d %s' % current_release)
    if completed.returncode:
        logging_error('while remove tag: %s' % str(completed))
        return completed.returncode

    # TODO: ? remove upstream ? or just overwrite ?
    return SUCCESS


def reset_resources(
        root: str,
        virtual: bool = False,
        verbose: bool = False,
):
    short = shortcut(root)
    initpath = join(short, '__init__.py')
    changelog = 'CHANGELOG.md'

    to_reset = []
    ret = 0
    for item in [initpath, changelog]:
        if not exists(join(root, item)):
            msg = 'Item %s does not exists' % item
            logging_error(msg)
            ret += 1
            continue
        to_reset.append(item)
    if ret:
        return FAILURE  # at least one path does not exist.
    if not to_reset:
        return FAILURE

    completed = git_checkout(root, to_reset, virtual=virtual, verbose=verbose)
    return completed
