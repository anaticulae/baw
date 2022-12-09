#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019-2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================

import baw.archive.test
import baw.cmd.complex
import baw.cmd.lint
import baw.cmd.release.drop
import baw.cmd.release.pack
import baw.git
import baw.runtime
import baw.utils


def release(  # pylint:disable=R1260
    root: str,
    *,
    release_type: str = 'auto',
    stash: bool = True,
    sync: bool = True,
    test: bool = True,
    verbose: bool = False,
    venv: bool = True,
    require_clean: bool = True,
    no_linter: bool = False,
) -> int:
    """Running release. Running test, commit and tag.

    Args:
        root(str): generated project
        release_type(str): major x.0.0
                           minor 0.x.0
                           patch 0.0.x
                           noop  0.0.0 do nothing
                           auto  let semantic release decide
        stash(bool): stash uncommitted content before running release
        sync(bool): if True synchronize dependencies before runnig test
        test(bool): running test suite before release: first release
                    0.0.0 does not require any testing.
        verbose(bool): log additional output
        venv(bool): run in venv environment
        require_clean(bool): check that repository is clean
        no_linter(bool): skip running linter
    Return:
        0 if success else > 0

    Process:
        1. Run complete testsuite
        2. Run Semantic release to create changelog, commit the changelog as
           release-message and create a version tag.
    """
    baw.utils.verbose('require release?', verbose=verbose)
    if returncode := require_release(root, venv):
        # break release cycle on master
        return baw.utils.SUCCESS
    baw.utils.verbose('check repository', verbose=verbose)
    if returncode := check_repository(root, require_clean):
        return returncode
    if not no_linter:
        baw.utils.verbose('run linter', verbose=verbose)
        if returncode := baw.cmd.lint.run_linter(root, verbose, venv):
            return returncode
    baw.utils.verbose('run test', verbose=verbose)
    if returncode := run_test(root, sync, test, stash, verbose, venv):
        return returncode
    if returncode := baw.cmd.release.pack.run(
            root,
            verbose,
            release_type,
            venv=venv,
    ):
        return returncode
    return baw.utils.SUCCESS


def require_release(root, venv):
    current_head = baw.git.headtag(root, venv=venv)
    if not current_head:
        return baw.utils.SUCCESS
    if current_head.isnumeric():
        # may a year: 2022
        return baw.utils.SUCCESS
    baw.utils.log(f'No release is required, head is already: {current_head}')
    return baw.utils.FAILURE


def check_repository(root, require_clean: bool):
    if not require_clean:
        return baw.utils.SUCCESS
    # do not release modified repository
    if baw.git.is_modified(root=root):
        baw.utils.error('repository is not clean')
        return baw.utils.FAILURE
    return baw.utils.SUCCESS


def run_test(
    root: str,
    sync: bool,
    test: bool,
    stash: bool,
    verbose: bool,
    venv: bool,
):
    if not sync and not test:
        return baw.utils.SUCCESS
    # do not run hashed on first release, cause there is no any tagged
    # version.
    hashed = baw.git.headhash(root)
    require_test = not hashed or not baw.archive.test.tested(root, hashed)
    if require_test:
        returncode = baw.cmd.complex.sync_and_test(
            root,
            generate=True,
            longrun=True,
            packages='dev',
            stash=stash,
            sync=sync,
            test=test,
            testconfig=['-n', 'auto'],
            verbose=verbose,
            venv=venv,
        )
        return returncode
    baw.utils.log('release was already tested successfully')
    return baw.utils.SUCCESS


def run(args: dict) -> int:
    root = baw.cmd.utils.get_root(args)
    # always publish after release
    args['publish'] = True
    venv = args.get('venv', True)
    # overwrite venv flag if given
    novenv = args.get('no_venv', False)
    no_linter = args.get('no_linter', False)
    sync = not args.get('no_sync', False)
    if novenv:
        baw.utils.log('do not use venv')
        venv = False
    if not baw.runtime.installed('semantic-release', root, venv=venv):
        return baw.utils.FAILURE
    test = True
    # do not test before releasing
    notest = args.get('no_test', False)
    if notest:
        test = False
    if args.get('release') == 'drop':
        result = baw.cmd.release.drop.run(
            root,
            venv=venv,
            verbose=args['verbose'],
        )
        return result
    # run release
    result = release(
        root=root,
        release_type=args['release'],
        verbose=args['verbose'],
        test=test,
        venv=venv,
        no_linter=no_linter,
        sync=sync,
    )
    return result


def extend_cli(parser):
    parser = parser.add_parser('release', help='Test, commit, tag and publish')
    parser.add_argument(
        'release',
        help='Test, commit, tag and publish',
        nargs='?',
        choices='major minor patch noop auto drop'.split(),
        default='auto',
    )
    parser.add_argument('--no_install', action='store_true', help='skip insta')
    parser.add_argument('--no_test', action='store_true', help='skip tests')
    parser.add_argument('--no_venv', action='store_true', help='skip venv')
    parser.add_argument('--no_linter', action='store_true', help='skip linter')
    parser.add_argument('--no_sync', action='store_true', help='skip sync')
    parser.set_defaults(func=run)
