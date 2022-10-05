#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019-2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================
"""Run every function which is used by `baw`."""

import baw.config
from baw.git import git_headtag
from baw.runtime import run_target
from baw.utils import FAILURE
from baw.utils import SUCCESS
from baw.utils import error
from baw.utils import log
from baw.utils import package_address

# TODO: Use twine for uploading packages
SDIST_UPLOAD_WARNING = ('WARNING: Uploading via this command is deprecated, '
                        'use twine to upload instead '
                        '(https://pypi.org/p/twine/)')


def publish(root: str, verbose: bool = False, venv: bool = True):
    """Push release to defined repository

    Hint:
        publish run's always in venv environment
    """
    log('publish start')
    tag = git_headtag(root, venv=False, verbose=verbose)
    if not tag:
        error('Could not find release-git-tag. Aborting publishing.')
        return FAILURE
    url, _ = package_address()
    distribution = distribution_format()
    python = baw.config.python(root)
    command = f'{python} setup.py {distribution} upload -r {url}'
    if verbose:
        log(f'build distribution: {command}')
    completed = run_target(
        root,
        command,
        root,
        verbose=verbose,
        skip_error_message=[SDIST_UPLOAD_WARNING],
        venv=venv,
    )
    if completed.returncode == SUCCESS:
        log('publish completed')
    else:
        error(completed.stderr)
        error('publish failed')
    return completed.returncode


def distribution_format() -> str:
    # distribution = 'bdist_wheel --universal'
    # TODO: VERIFY THE BEST ONE
    # TODO: REQUIRES MANIFEST FILE TO COPY REQUIREMENTS
    # return 'sdist --format=gztar'
    return 'bdist_wheel --universal'
