# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019-2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import contextlib
import functools
import os
import subprocess
import sys

import baw.resources
import baw.runtime
import baw.utils

GIT_EXT = '.git'
GIT_REPO_EXCLUDE = '.git/info/exclude'


def init(root: str):
    """Init git repository. Do nothing if repo already exists.

    Args:
        root(str): generated project"""
    git_dir = os.path.join(root, GIT_EXT)
    if os.path.exists(git_dir):
        baw.utils.skip('git init')
        return
    baw.utils.log('git init')
    command = subprocess.run(  # nosec
        ['git', 'init'],
        check=False,
        capture_output=True,
    )
    evaluate_git_error(command)


def add(
    root: str,
    pattern: str,
    verbose: bool = False,
):
    """Stage items matching on given pattern

    Args:
        root(str): root of generated project
        pattern(str): pattern in linux-style
        verbose(bool): increase verbosity
    """
    assert os.path.exists(root)
    if verbose:
        baw.utils.log('git add')
    cmd = baw.runtime.run_target(
        root,
        f'git add {pattern}',
        verbose=verbose,
    )
    evaluate_git_error(cmd)


def commit(root, source, message, tag: str = None, verbose: int = 0):
    assert os.path.exists(root)
    message = '"%s"' % message
    if verbose:
        baw.utils.log('git commit')
    # support multiple files
    if not isinstance(source, str):
        source = ' '.join(source)
    process = baw.runtime.run_target(
        root,
        'git commit %s -m %s' % (source, message),
        verbose=verbose,
    )
    if not process.returncode and tag:
        process = baw.runtime.run_target(
            root,
            f'git tag {tag}',
            verbose=verbose,
        )
    return process.returncode


def is_clean(root, verbose: bool = True):
    process = baw.runtime.run_target(root, 'git status', verbose=verbose)
    assert not process.returncode
    return 'nothing to commit, working tree clean' in process.stdout


def checkout(
    root: str,
    files: str,
    *,
    verbose: bool = False,
    venv: bool = False,
) -> int:
    """Checkout files from git repository

    Args:
        root(str): root to generated project
        files(str or iterable): files to checkout
        verbose(bool): increase logging
        venv(bool): run in venv environment
    Returns:
        0 if baw.utils.SUCCESS else FAILURE
    """
    # TODO: RENAME TO GIT_RESET
    runner = functools.partial(
        baw.runtime.run_target,
        verbose=verbose,
        venv=venv,
    )
    to_reset = ' '.join(files) if not isinstance(files, str) else files
    baw.utils.log('Reset %s' % to_reset)
    completed = runner(root, 'git checkout -q %s' % to_reset)

    if completed.returncode:
        msg = 'while checkout out %s\n%s' % (to_reset, str(completed))
        baw.utils.error(msg)
    return completed.returncode


@contextlib.contextmanager
def stash(
    root: str,
    *,
    verbose: bool = False,
    venv: bool = False,
) -> int:
    """Save uncommited/not versonied content to improve testability

    Args:
        root(str): root of execution
        venv(bool): run in venv environment
        verbose(bool): increase logging
    Yields:
        Context: to run user operation which requires stashed environment.
    Returns:
        SUCCESS if everything was successfull
    Raises:
        Reraises all user execeptions
    """
    baw.utils.log('Stash environment')
    cmd = 'git stash --include-untracked'
    completed = baw.runtime.run_target(
        root,
        cmd,
        verbose=verbose,
        venv=venv,
    )
    if completed.returncode:
        baw.utils.error(completed.stdout)
        baw.utils.error(completed.stderr)
        # Stashing an repository with not commit, produces an error
        sys.exit(completed.returncode)

    nostash = (not completed.returncode and
               'No local changes to save' in completed.stdout)
    if nostash:
        baw.utils.log('No stash is required. Environment is already clean.')

    err = None
    try:
        yield  # let user do there job
    except Exception as msg:  # pylint: disable=broad-except
        # exception is reraised after unstash
        err = msg
    if nostash:
        # reraise exception from user code
        if err:
            raise err
        return baw.utils.SUCCESS
    # unstash to recreate dirty environment
    cmd = 'git stash pop'
    completed = baw.runtime.run_target(
        root,
        cmd,
        verbose=verbose,
        venv=venv,
    )
    if completed.returncode:
        baw.utils.error(completed.stderr)
    # reraise except from user code
    if err:
        raise err
    return completed.returncode


def headtag(root: str, venv: bool, verbose: bool = False):
    command = 'git tag --points-at HEAD'
    completed = baw.runtime.run_target(
        root,
        command,
        root,
        # ignore error when collecting head on empty repository
        skip_error_code={129},
        skip_error_message=["error: malformed object name 'HEAD'"],
        verbose=verbose,
        venv=venv,
    )
    # could not collect any git tag of current head
    if completed.returncode:
        return None
    return completed.stdout.strip()


def headhash(root: str) -> str:
    if not installed():
        return None
    cmd = 'git rev-parse --verify HEAD'
    completed = baw.runtime.run_target(root, cmd, verbose=False)
    if completed.returncode:
        return None
    return completed.stdout.strip()


def is_modified(root: str) -> bool:
    cmd = 'git status -z'
    completed = baw.runtime.run_target(root, cmd, verbose=False)
    if completed.returncode:
        return True
    if completed.stdout.strip():
        return True
    return False


def update_gitignore(root: str, verbose: bool = False):
    if verbose:
        baw.utils.log('sync gitexclude')
    exclude = os.path.join(root, GIT_REPO_EXCLUDE)
    if not os.path.exists(exclude):
        baw.utils.log(f'no git dir: {exclude}, skip update')
        return baw.utils.SUCCESS
    baw.utils.file_replace(
        exclude,
        baw.resources.GITIGNORE,
    )
    return baw.utils.SUCCESS


def update_userdata(username='supermario', email='test@test.com'):
    cmd = f'git config --global user.email "{email}" user.name="{username}"'
    process = subprocess.run(  # nosec
        cmd,
        check=False,
        shell=True,
        capture_output=True,
    )
    evaluate_git_error(process)


def evaluate_git_error(process: subprocess.CompletedProcess):
    """Raise exception depending on returncode of completed process

    Args:
        process(CompletedProcess): process to analyze returncode for raising
                                   depended exception.
    Raises:
        ChildProcessError: when git is not installed problems while
                           initializing git repository.
    """
    if process.returncode == baw.runtime.NO_EXECUTABLE:
        raise ChildProcessError('Git is not installed')
    if process.returncode:
        raise ChildProcessError(f'Could not run git: {process}')


@functools.lru_cache
def installed() -> bool:
    """\
    >>> str(installed())
    '...'
    """
    try:
        process = subprocess.run(  # nosec
            ['git', 'help'],
            capture_output=True,
            check=False,
        )
    except FileNotFoundError:
        return False
    if process.returncode == baw.utils.SUCCESS:
        return True
    return False
