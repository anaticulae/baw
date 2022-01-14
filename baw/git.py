# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019-2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import sys
from contextlib import contextmanager
from functools import partial
from os.path import exists
from os.path import join
from subprocess import CompletedProcess
from subprocess import run

import baw.resources
import baw.runtime
from baw.utils import SUCCESS
from baw.utils import error
from baw.utils import file_replace
from baw.utils import log
from baw.utils import skip

GIT_EXT = '.git'
GIT_REPO_EXCLUDE = '.git/info/exclude'


def git_init(root: str):
    """Init git-repository if not exists, If .git exists, return

    Args:
        root(str): generated project"""
    git_dir = join(root, GIT_EXT)
    if exists(git_dir):
        skip('git init')
        return
    log('git init')
    command = run(['git', 'init'], check=False)
    evaluate_git_error(command)


def git_add(root: str, pattern: str):
    """Stage items matching on given pattern

    Args:
        root(str): root of generated project
        pattern(str): pattern in linux-style"""
    assert exists(root)
    log('git add')
    cmd = baw.runtime.run_target(root, 'git add %s' % pattern, verbose=False)
    evaluate_git_error(cmd)


def add(root: str, pattern: str):
    return git_add(root, pattern)


def git_commit(root, source, message, verbose: int = 0):
    assert exists(root)
    message = '"%s"' % message
    if verbose:
        log('git commit')
    # support multiple files
    if not isinstance(source, str):
        source = ' '.join(source)
    process = baw.runtime.run_target(
        root,
        'git commit %s -m %s' % (source, message),
        verbose=verbose,
    )
    return process.returncode


def commit(root, source, message, verbose: int = 0):
    return git_commit(root, source, message, verbose)


def is_clean(root, verbose: bool = True):
    process = baw.runtime.run_target(root, 'git status', verbose=verbose)
    assert not process.returncode
    return 'nothing to commit, working tree clean' in process.stdout


def git_checkout(
    root: str,
    files: str,
    *,
    verbose: bool = False,
    virtual: bool = False,
) -> int:
    """Checkout files from git repository

    Args:
        root(str): root to generated project
        files(str or iterable): files to checkout
        verbose(bool): increase logging
        virtual(bool): run in virtual environment
    Returns:
        0 if SUCCESS else FAILURE
    """
    # TODO: RENAME TO GIT_RESET
    runner = partial(baw.runtime.run_target, verbose=verbose, virtual=virtual)
    to_reset = ' '.join(files) if not isinstance(files, str) else files
    log('Reset %s' % to_reset)
    completed = runner(root, 'git checkout -q %s' % to_reset)

    if completed.returncode:
        msg = 'while checkout out %s\n%s' % (to_reset, str(completed))
        error(msg)
    return completed.returncode


@contextmanager
def git_stash(
    root: str,
    *,
    verbose: bool = False,
    virtual: bool = False,
) -> int:
    """Save uncommited/not versonied content to improve testability

    Args:
        root(str): root of execution
        virtual(bool): run in virtual environment
        verbose(bool): increase logging
    Yields:
        Context: to run user operation which requires stashed environment.
    Returns:
        SUCCESS if everything was successfull
    Raises:
        Reraises all user execeptions
    """
    log('Stash environment')
    cmd = 'git stash --include-untracked'
    completed = baw.runtime.run_target(
        root,
        cmd,
        verbose=verbose,
        virtual=virtual,
    )
    if completed.returncode:
        error(completed.stdout)
        error(completed.stderr)
        # Stashing an repository with not commit, produces an error
        sys.exit(completed.returncode)

    nostash = (not completed.returncode and
               'No local changes to save' in completed.stdout)
    if nostash:
        log('No stash is required. Environment is already clean.')

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
        return SUCCESS
    # unstash to recreate dirty environment
    cmd = 'git stash pop'
    completed = baw.runtime.run_target(
        root,
        cmd,
        verbose=verbose,
        virtual=virtual,
    )
    if completed.returncode:
        error(completed.stderr)
    # reraise except from user code
    if err:
        raise err
    return completed.returncode


def git_headtag(root: str, virtual: bool, verbose: bool = False):
    command = 'git tag --points-at HEAD'
    completed = baw.runtime.run_target(
        root,
        command,
        root,
        # ignore error when collecting head on empty repository
        skip_error_code={129},
        skip_error_message=["error: malformed object name 'HEAD'"],
        verbose=verbose,
        virtual=virtual,
    )
    # could not collect any git tag of current head
    if completed.returncode:
        return None
    return completed.stdout.strip()


def git_headhash(root: str) -> str:
    cmd = 'git rev-parse --verify HEAD'
    completed = baw.runtime.run_target(root, cmd, verbose=False)
    if completed.returncode:
        return None
    return completed.stdout.strip()


def git_modified(root: str) -> bool:
    cmd = 'git status -z'
    completed = baw.runtime.run_target(root, cmd, verbose=False)
    if completed.returncode:
        return True
    if completed.stdout.strip():
        return True
    return False


def update_gitignore(root: str, verbose: bool = False):
    if verbose:
        log('sync gitexclude')
    file_replace(join(root, GIT_REPO_EXCLUDE), baw.resources.GITIGNORE)
    return SUCCESS


def update_userdata(username='supermario', email='test@test.com'):
    cmd = f'git config --global user.email "{email}" user.name="{username}"'
    process = run(cmd, check=False)
    evaluate_git_error(process)


def evaluate_git_error(process: CompletedProcess):
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
