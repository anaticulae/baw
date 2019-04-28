# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019 by Helmut Konrad Fahrendholz. All rights reserved.
# Tis file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================
from contextlib import contextmanager
from functools import partial
from os.path import exists
from os.path import join
from subprocess import CompletedProcess
from subprocess import run

from baw.runtime import NO_EXECUTABLE
from baw.runtime import run_target
from baw.utils import FAILURE
from baw.utils import SUCCESS
from baw.utils import logging
from baw.utils import logging_error
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
    logging('git init')
    command = run(['git', 'init'])
    evaluate_git_error(command)


def git_add(root: str, pattern: str):
    """Stage items matching on given pattern

    Args:
        root(str): root of generated project
        pattern(str): pattern in linux-style"""
    assert exists(root)
    logging('git add')
    add = run_target(root, 'git add %s' % pattern, verbose=False)
    evaluate_git_error(add)


def git_commit(root, source, message):
    assert exists(root)
    message = '"%s"' % message
    logging('git commit')
    process = run_target(
        root, 'git commit %s -m %s' % (source, message), verbose=False)

    return process.returncode


def git_checkout(
        root,
        files,
        *,
        verbose: bool = False,
        virtual: bool = False,
):
    """Checkout files from git repository

    Args:
        root(str): root to generated project
        files(str/iterable): files to checkout
    Returns:
        0 if SUCCESS else FAILURE
    """
    runner = partial(run_target, verbose=verbose, virtual=virtual)
    to_reset = ' '.join(files) if not isinstance(files, str) else files
    logging('Reset %s' % to_reset)
    completed = runner(root, 'git checkout -q %s' % to_reset)

    if completed.returncode:
        msg = 'while checkout out %s\n%s' % (to_reset, str(completed))
        logging_error(msg)
    return completed.returncode


@contextmanager
def git_stash(
        root: str,
        *,
        verbose: bool = False,
        virtual: bool = False,
):
    """Save uncommited/not versonied content to improve testability

    Args:
        root(str): root of execution
        virtual(bool): run in virtual environment
    Returns:
        SUCCESS if everything was successfull
    Raises:
        Reraises all user execeptions
    """
    logging('Stash environment')
    cmd = 'git stash --include-untracked'
    completed = run_target(root, cmd, verbose=verbose, virtual=virtual)

    if completed.returncode:
        # Stashing an repository with not commit, produces an error
        exit(completed.returncode)

    nostash = (completed.returncode == 0 and
               'No local changes to save' in completed.stdout)
    if nostash:
        logging('No stash is required. Environment is already clean.')

    error = None
    try:
        yield  # let user do there job
    except Exception as error:  # pylint: disable=broad-except
        # exception is reraised after unstash
        pass

    if nostash:
        # reraise exception from user code
        if error:
            raise error
        return SUCCESS

    # unstash to recreate dirty environment
    cmd = 'git stash pop'
    completed = run_target(
        root,
        cmd,
        verbose=verbose,
        virtual=virtual,
    )
    if completed.returncode:
        logging_error(completed.stderr)

    # reraise except from user code
    if error:
        raise error
    return completed.returncode


def evaluate_git_error(process: CompletedProcess):
    """Raise exception depending on returncode of completed process

    Args:
        process(CompletedProcess): process to analyze returncode for raising
                                   depended exception.
    Raises:
        ChildProcessError when git is not installed
                               problems while initializing git repository
    """
    if process.returncode == NO_EXECUTABLE:
        raise ChildProcessError('Git is not installed')
    if process.returncode:
        raise ChildProcessError('Could not run git %s' % str(process))
