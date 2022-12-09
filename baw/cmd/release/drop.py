# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2022 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import functools
import os
import re

import baw.config
import baw.runtime
import baw.utils

RELEASE_PATTERN = re.compile(r'(?P<release>v\d+\.\d+\.\d+)')


def run(
    root: str,
    venv: bool = False,
    verbose: bool = False,
):
    """Remove the last release tag and commit.

    1. Check if last commit is a tagged release, if not abbort
    2. Remove last commit git reset HEAD~1
    3. Checkout CHANGELOG and __init__.py
    4. Remove tag
    """
    baw.utils.log('Start dropping release')
    # git tag --contains HEAD -> Answer the last commit
    baw.utils.log('Detect current release:')
    runner = functools.partial(
        baw.runtime.run_target,
        verbose=verbose,
        venv=venv,
    )
    completed = runner(root, 'git tag --contains HEAD')
    matched = RELEASE_PATTERN.match(completed.stdout)
    if not matched:
        baw.utils.error('No release tag detected')
        return baw.utils.FAILURE
    current_release = matched['release']
    # do not remove the first commit/release in the repository
    if current_release == DEFAULT_RELEASE:
        baw.utils.error(f'Could not remove {DEFAULT_RELEASE} release')
        return baw.utils.FAILURE
    baw.utils.log(current_release)
    # remove the last release commit
    # git reset HEAD~1
    baw.utils.log('Remove last commit')
    completed = runner(root, 'git reset HEAD~1')
    if completed.returncode:
        baw.utils.error(f'while removing the last commit: {completed}')
        return completed.returncode
    # git checkout CHANGELOG.md, {{NAME}}/__init__..py
    completed = reset_resources(root, venv=venv, verbose=verbose)
    if completed:
        return completed
    # git tag -d HEAD
    baw.utils.log('Remove release tag')
    completed = runner(root, f'git tag -d {current_release}')
    if completed.returncode:
        baw.utils.error(f'while remove tag: {completed}')
        return completed.returncode
    # TODO: ? remove upstream ? or just overwrite ?
    return baw.utils.SUCCESS


DEFAULT_RELEASE = 'v0.0.0'


def reset_resources(
    root: str,
    venv: bool = False,
    verbose: bool = False,
):
    short = baw.config.shortcut(root)
    initpath = os.path.join(short, '__init__.py')
    changelog = baw.config.changelog(root)
    to_reset = []
    returncode = 0
    for item in [initpath, changelog]:
        if not os.path.exists(os.path.join(root, item)):
            msg = f'Item {item} does not exists'
            baw.utils.error(msg)
            returncode += 1
            continue
        to_reset.append(item)
    if returncode:
        return baw.utils.FAILURE  # at least one path does not exist.
    if not to_reset:
        return baw.utils.FAILURE
    completed = baw.git.checkout(
        root,
        to_reset,
        venv=venv,
        verbose=verbose,
    )
    return completed
