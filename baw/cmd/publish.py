#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019-2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================
"""Run every function which is used by `baw`."""

import baw.cmd.utils
import baw.config
import baw.git
import baw.run
import baw.runtime
import baw.utils

# TODO: Use twine for uploading packages
SDIST_UPLOAD_WARNING = ('WARNING: Uploading via this cmd is deprecated, '
                        'use twine to upload instead '
                        '(https://pypi.org/p/twine/)')


def publish(root: str, verbose: bool = False, venv: bool = True):
    """Push release to defined repository

    Hint:
        publish run's always in venv environment
    """
    baw.utils.log('publish start')
    tag = baw.git.headtag(root, venv=False, verbose=verbose)
    if not tag:
        baw.utils.error('Could not find release-git-tag. Aborting publishing.')
        return baw.utils.FAILURE
    url, _ = baw.utils.package_address()
    distribution = distribution_format()
    python = baw.config.python(root)
    cmd = f'{python} setup.py {distribution} upload -r {url}'
    if verbose:
        baw.utils.log(f'build dist: {cmd}')
    completed = baw.runtime.run_target(
        root,
        cmd,
        root,
        verbose=verbose,
        skip_error_message=[SDIST_UPLOAD_WARNING],
        venv=venv,
    )
    if completed.returncode == baw.utils.SUCCESS:
        baw.utils.log('publish completed')
    else:
        baw.utils.error(completed.stderr)
        baw.utils.error('publish failed')
    return completed.returncode


def distribution_format() -> str:
    # distribution = 'bdist_wheel --universal'
    # TODO: VERIFY THE BEST ONE
    # TODO: REQUIRES MANIFEST FILE TO COPY REQUIREMENTS
    # return 'sdist --format=gztar'
    return 'bdist_wheel --universal'


def run(args: dict):
    root = baw.cmd.utils.get_root(args)
    venv = args['venv']
    # overwrite venv flag if given
    novenv = args.get('no_venv', False)
    if novenv:
        baw.utils.log('do not use venv')
        venv = False
    result = publish(
        root=root,
        verbose=args.get('verbose', False),
        venv=venv,
    )
    return result


def extend_cli(parser):
    created = parser.add_parser('publish', help='Push release to repository')
    created.add_argument(
        'publish',
        nargs='?',
        default='dest',
        help='Push release to this repository',
    )
    created.add_argument('--no_venv', action='store_true')
    created.set_defaults(func=run)
