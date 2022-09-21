#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019-2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================

import contextlib
import functools
import os
import re
import sys

import baw.archive.test
import baw.cmd.complex
import baw.cmd.lint
import baw.config
import baw.git
import baw.resources
import baw.runtime
import baw.utils

# semantic release returns this message if no new release is provided, cause
# of the absent of new features/bugfixes.
NO_RELEASE_MESSAGE = 'No release will be made.'


def release(
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
    if returncode := require_release(root, venv):
        return returncode
    if returncode := check_repository(root, require_clean):
        return returncode
    if not no_linter:
        if returncode := run_linter(root, verbose, venv):
            return returncode
    if returncode := run_test(root, sync, test, stash, verbose, venv):
        return returncode
    if returncode := publish(root, verbose, release_type):
        return returncode
    return baw.utils.SUCCESS


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
    # TODO :MOVE THIS
    import baw.run  # pylint:disable=W0621
    parser.set_defaults(func=baw.run.run_release)


def require_release(root, venv):
    current_head = baw.git.git_headtag(root, venv=venv)
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
    if baw.git.git_modified(root=root):
        baw.utils.error('repository is not clean')
        return baw.utils.FAILURE
    return baw.utils.SUCCESS


def run_linter(root: str, verbose: bool, venv: bool) -> int:
    if not baw.config.fail_on_finding(root):
        return baw.utils.SUCCESS
    # run linter step before running test and release
    if returncode := baw.cmd.lint.lint(
            root,
            baw.cmd.lint.Scope.MINIMAL,
            verbose=verbose,
            venv=venv,
            log_always=False,
    ):
        baw.utils.error('could not release, solve this errors first.')
        baw.utils.error('turn `fail_on_finding` off to release with errors')
        return returncode
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
    hashed = baw.git.git_headhash(root)
    require_test = not hashed or not baw.archive.test.tested(root, hashed)
    if require_test:
        ret = baw.cmd.complex.sync_and_test(
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
        return ret
    baw.utils.log('release was already tested successfully')
    return baw.utils.SUCCESS


def publish(root, verbose, release_type):
    baw.utils.log("Update version tag")
    with temp_semantic_config(root) as config:
        # Only release with type if user select one. If the user does select
        # a release-type let semantic release decide.
        release_type = '' if release_type == 'auto' else '--%s' % release_type
        cmd = f'semantic-release version {release_type} --config="{config}"'
        completed = baw.runtime.run_target(
            root,
            cmd,
            verbose=verbose,
        )
        baw.utils.log(completed.stdout)
        if NO_RELEASE_MESSAGE in completed.stdout:
            baw.utils.error('abort release')
            baw.utils.log('ensure that some (feat) are commited')
            baw.utils.log('use: `baw release minor` to force release')
            return baw.utils.FAILURE
    if completed.returncode:
        baw.utils.error('while running semantic-release')
        baw.utils.error(completed.stderr)
        return completed.returncode
    return baw.utils.SUCCESS


@contextlib.contextmanager
def temp_semantic_config(root: str):
    short = baw.config.shortcut(root)
    replaced = baw.resources.SETUP_CFG.replace('{{SHORT}}', short)
    if replaced == baw.resources.SETUP_CFG:
        baw.utils.error('while replacing template')
        sys.exit(baw.utils.FAILURE)
    # use own tmpfile cause TemporaryFile(delete=True) seems no supported
    # at linux, parameter delete is missing.
    tmp = baw.utils.tmpfile()
    baw.utils.file_create(tmp, replaced)
    yield tmp
    # remove file
    os.unlink(tmp)


RELEASE_PATTERN = r'(?P<release>v\d+\.\d+\.\d+)'

DEFAULT_RELEASE = 'v0.0.0'


def drop(
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
    matched = re.match(RELEASE_PATTERN, completed.stdout)
    if not matched:
        baw.utils.error('No release tag detected')
        return baw.utils.FAILURE
    current_release = matched['release']
    # do not remove the first commit/release in the repository
    if current_release == DEFAULT_RELEASE:
        baw.utils.error('Could not remove %s release' % DEFAULT_RELEASE)
        return baw.utils.FAILURE
    baw.utils.log(current_release)
    # remove the last release commit
    # git reset HEAD~1
    baw.utils.log('Remove last commit')
    completed = runner(root, 'git reset HEAD~1')
    if completed.returncode:
        baw.utils.error('while removing the last commit: %s' % str(completed))
        return completed.returncode
    # git checkout CHANGELOG.md, {{NAME}}/__init__..py
    completed = reset_resources(root, venv=venv, verbose=verbose)
    if completed:
        return completed
    # git tag -d HEAD
    baw.utils.log('Remove release tag')
    completed = runner(root, 'git tag -d %s' % current_release)
    if completed.returncode:
        baw.utils.error('while remove tag: %s' % str(completed))
        return completed.returncode
    # TODO: ? remove upstream ? or just overwrite ?
    return baw.utils.SUCCESS


def reset_resources(
    root: str,
    venv: bool = False,
    verbose: bool = False,
):
    short = baw.config.shortcut(root)
    initpath = os.path.join(short, '__init__.py')
    changelog = 'CHANGELOG.md'
    to_reset = []
    ret = 0
    for item in [initpath, changelog]:
        if not os.path.exists(os.path.join(root, item)):
            msg = 'Item %s does not exists' % item
            baw.utils.error(msg)
            ret += 1
            continue
        to_reset.append(item)
    if ret:
        return baw.utils.FAILURE  # at least one path does not exist.
    if not to_reset:
        return baw.utils.FAILURE
    completed = baw.git.git_checkout(
        root,
        to_reset,
        venv=venv,
        verbose=verbose,
    )
    return completed
