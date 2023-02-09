#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019-2023 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================
"""Run every function which is used by `baw`."""

import baw.cmd.utils
import baw.config
import baw.gix
import baw.run
import baw.runtime
import baw.utils

# TODO: Use twine for uploading packages
SDIST_UPLOAD_WARNING = ('WARNING: Uploading via this cmd is deprecated, '
                        'use twine to upload instead '
                        '(https://pypi.org/p/twine/)')


def publish(
    root: str,
    *,
    pre: bool = False,
    venv: bool = True,
    verbose: bool = False,
):
    """Push release to defined repository

    Hint:
        publish run's always in venv environment
    """
    baw.log('publish start')
    if failure := can_publish(root, pre=pre, verbose=verbose):
        return failure
    url = baw.config.package_testing() if pre else baw.config.package_address()[0]  # yapf:disable
    distribution = distribution_format()
    python = baw.config.python(root)
    cmd = f'{python} setup.py {distribution} upload -r {url}'
    if verbose:
        baw.log(f'build dist: {cmd}')
    completed = baw.runtime.run_target(
        root,
        cmd,
        root,
        verbose=verbose,
        skip_error_message=[SDIST_UPLOAD_WARNING],
        venv=venv,
    )
    if completed.returncode == baw.SUCCESS:
        if pre:
            log_prerelease(root)
        baw.log('publish completed')
    else:
        baw.error(completed.stderr)
        baw.error('publish failed')
    return completed.returncode


def can_publish(
    root: str,
    pre: bool = False,
    verbose: bool = False,
) -> int:
    tag = baw.gix.headtag(root, venv=False, verbose=verbose)
    if tag and pre:
        baw.error('Stable release already published')
        return baw.SUCCESS
    if not tag and not pre:
        baw.error('Could not find release-git-tag. Aborting publishing.')
        return baw.FAILURE
    return baw.SUCCESS


def log_prerelease(root):
    import utila.quick
    baw.log(baw.config.shortcut(root) + '-', end='')
    baw.log(utila.quick.git_hash(root))


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
        baw.log('do not use venv')
        venv = False
    result = publish(
        root=root,
        pre=args['pre'],
        venv=venv,
        verbose=args['verbose'],
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
    created.add_argument('--pre', action='store_true')
    created.add_argument('--no_venv', action='store_true')
    created.set_defaults(func=run)
