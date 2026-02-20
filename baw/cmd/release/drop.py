# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2022-2023 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import os
import re

import baw.config
import baw.gix
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
    baw.log('Start dropping release')
    if not can_drop(root, venv, verbose):
        return baw.FAILURE
    current_release = baw.gix.headtag(root, venv, verbose)
    baw.log(current_release)
    # remove the last release commit
    # git reset HEAD~1
    baw.log('Remove last commit')
    completed = baw.runtime.run_target(root, 'git reset HEAD~1')
    if completed.returncode:
        baw.error(f'while removing the last commit: {completed}')
        return completed.returncode
    # git checkout CHANGELOG.md, {{NAME}}/__init__..py
    completed = reset_resources(root, venv=venv, verbose=verbose)
    if completed:
        return completed
    # git tag -d HEAD
    if not baw.gix.tag_drop(current_release, root, venv=venv, verbose=verbose):
        return baw.FAILURE
    # TODO: ? remove upstream ? or just overwrite ?
    return baw.SUCCESS


def can_drop(root: str, venv: bool, verbose: bool) -> bool:
    baw.log('Detect current release:')
    if not (headtag := baw.gix.headtag(root, venv, verbose)):
        baw.error('No tag detected')
        return False
    matched = RELEASE_PATTERN.match(headtag)
    if not matched:
        baw.error(f'No release tag detected: {headtag}')
        return False
    default_release = baw.cmd.release.FIRST_RELEASE
    if headtag == default_release:
        baw.error(f'Could not remove {default_release} release')
        return False
    return True


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
    for item in (initpath, changelog):
        if not os.path.exists(os.path.join(root, item)):
            msg = f'Item {item} does not exists'
            baw.error(msg)
            returncode += 1
            continue
        to_reset.append(item)
    if returncode:
        return baw.FAILURE  # at least one path does not exist.
    if not to_reset:
        return baw.FAILURE
    completed = baw.gix.reset(
        root,
        to_reset,
        venv=venv,
        verbose=verbose,
    )
    return completed
