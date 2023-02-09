# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019-2023 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import contextlib
import functools
import os
import subprocess
import sys

import git

import baw
import baw.config
import baw.resources
import baw.runtime
import baw.utils

GIT_EXT = '.git'
GIT_REPO_EXCLUDE = '.git/info/exclude'


def init(root: str):
    """Init git repository. Do nothing if repo already exists.

    Args:
        root(str): generated project
    """
    gitdir = os.path.join(root, GIT_EXT)
    if os.path.exists(gitdir):
        baw.utils.skip('git init')
        return
    baw.log('git init')
    cmd = subprocess.run(  # nosec
        ['git', 'init'],
        check=False,
        capture_output=True,
    )
    evaluate_git_error(cmd)


def add(
    root: str,
    pattern: str,
    update: bool = False,
    verbose: bool = False,
):
    """Stage items matching on given pattern

    Args:
        root(str): root of generated project
        pattern(str): pattern in linux-style
        update(bool): if True, do not change working tree
        verbose(bool): increase verbosity
    """
    assert os.path.exists(root)
    update: str = '-u ' if update else ''
    raw = f'git add {update}{pattern}'
    if verbose:
        baw.log(raw)
    cmd = baw.runtime.run_target(
        root,
        cmd=raw,
        verbose=verbose,
    )
    evaluate_git_error(cmd)


def commit(root, source, message, tag: str = None, verbose: int = 0):
    assert os.path.exists(root)
    message = f'"{message}"'
    if verbose:
        baw.log('git commit')
    # support multiple files
    if not isinstance(source, str):
        source = ' '.join(source)
    process = baw.runtime.run_target(
        root,
        f'git commit {source} -m {message}',
        verbose=verbose,
    )
    if process.returncode:
        return process.returncode
    if tag:
        # -a: ensure to make annotated tag to use with `git describe`
        process = baw.runtime.run_target(
            root,
            f'git tag -a {tag} -m {message}',
            verbose=verbose,
        )
        if process.returncode:
            baw.completed(process)
            sys.exit(baw.FAILURE)
    return process.returncode


def is_clean(root, verbose: bool = True):
    update_gitignore(root, verbose=verbose)
    process = baw.runtime.run_target(
        root,
        'git status',
        verbose=verbose,
    )
    assert not process.returncode
    return 'nothing to commit, working tree clean' in process.stdout


def modified(root: str, verbose: bool = False):
    completed = baw.runtime.run_target(
        root,
        'git status -s -b',
        verbose=verbose,
    )
    if completed.returncode:
        baw.completed(completed)
        return None
    result = completed.stdout.strip()
    return result


def reset(
    root: str,
    files: str,
    *,
    verbose: bool = False,
    venv: bool = False,
) -> int:
    """Reset files from git repository.

    Args:
        root(str): root to generated project
        files(str or iterable): files to reset
        verbose(bool): increase logging
        venv(bool): run in venv environment
    Returns:
        0 if baw.SUCCESS else FAILURE
    """
    to_reset = ' '.join(files) if not isinstance(files, str) else files
    baw.log(f'Reset {to_reset}')
    completed = baw.runtime.run_target(
        root,
        cmd=f'git checkout -q {to_reset}',
        verbose=verbose,
        venv=venv,
    )
    if completed.returncode:
        msg = f'while checkout out {to_reset}\n{completed}'
        baw.error(msg)
    return completed.returncode


def checkout(
    root: str,
    branch: str,
) -> int:
    """Checkout head from git repository.

    Args:
        root(str): root to generated project
        branch(str): state to reach
    Returns:
        0 if SUCCESS else FAILURE
    """
    cmd = f'git checkout {branch}'
    completed = baw.runtime.run(cmd, cwd=root)
    if completed.returncode:
        msg = f'while checkout {branch}'
        baw.error(msg)
    return completed.returncode


def push(root: str) -> int:
    server = tokenizes(root)
    repo = git.Repo(
        root,
        search_parent_directories=True,
    )
    branch = repo.active_branch
    try:
        repo.git.push(server, branch)
    except git.GitCommandError as error:
        baw.error('while pushing')
        baw.error(error)
        return baw.FAILURE
    return baw.SUCCESS


def tag_drop(
    tag: str,
    root: str,
    venv: bool = False,
    verbose: bool = False,
) -> bool:
    baw.log(f'Remove tag: {tag}')
    completed = baw.runtime.run_target(
        root=root,
        cmd=f'git tag -d {tag}',
        venv=venv,
        verbose=verbose,
    )
    if completed.returncode:
        baw.error(f'while remove tag: {completed}')
        return False
    return True


@contextlib.contextmanager
def stash(
    root: str,
    *,
    verbose: bool = False,
    venv: bool = False,
) -> int:
    """Save uncommited/not versonied content to improve testability.

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
    if is_clean(root, verbose=verbose):
        yield
        return baw.SUCCESS
    baw.log('Stash environment')
    cmd = 'git stash --include-untracked'
    completed = baw.runtime.run_target(
        root,
        cmd,
        verbose=verbose,
        venv=venv,
    )
    if completed.returncode:
        baw.completed(completed)
        # Stashing an repository with no commit, produces an error
        sys.exit(completed.returncode)
    nostash = (not completed.returncode and
               'No local changes to save' in completed.stdout)
    if nostash:
        baw.log('No stash is required. Environment is already clean.')
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
        return baw.SUCCESS
    # unstash to recreate dirty environment
    stash_pop(root, venv, verbose)
    # reraise except from user code
    if err:
        raise err
    return completed.returncode


def stash_pop(root: str, venv: bool, verbose: bool = False) -> int:
    cmd = 'git stash pop'
    completed = baw.runtime.run_target(
        root,
        cmd,
        verbose=verbose,
        venv=venv,
    )
    if completed.returncode:
        baw.error(completed.stderr)
    return completed.returncode


def headtag(root: str, venv: bool, verbose: bool = False):
    """Determine tag of current head of branch.

    Return None if no Tag is given.
    """
    cmd = 'git tag --points-at HEAD'
    completed = baw.runtime.run_target(
        root,
        cmd,
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
    update_gitignore(root)
    cmd = 'git status -z'
    completed = baw.runtime.run_target(
        root,
        cmd,
        verbose=False,
    )
    if completed.returncode:
        return True
    if completed.stdout.strip():
        return True
    return False


def describe(root: str) -> str:
    if not installed():
        baw.error('install git')
        sys.exit(baw.FAILURE)
    completed = baw.runtime.run('git describe', cwd=root)
    if completed.returncode:
        baw.completed(completed)
        sys.exit(baw.FAILURE)
    name = completed.stdout.strip()
    return name


def branchname(root: str) -> str:
    """\
    >>> import baw.project;
    >>> branchname(baw.project.determine_root(__file__))
    '...'
    """
    if not installed():
        baw.error('install git')
        sys.exit(baw.FAILURE)
    branches = baw.runtime.run('git branch', cwd=root).stdout.strip()
    branches = [item for item in branches.splitlines() if item.startswith('*')]
    # * develop
    name = branches[0].split('*')[1].strip()
    return name


def update_gitignore(root: str, verbose: bool = False):
    if verbose:
        baw.log('sync gitexclude')
    exclude = os.path.join(root, GIT_REPO_EXCLUDE)
    if not os.path.exists(exclude):
        baw.log(f'no git dir: {exclude}, skip update')
        return baw.SUCCESS
    baw.utils.file_replace(
        exclude,
        baw.resources.GITIGNORE,
    )
    return baw.SUCCESS


def update_userdata(username='supermario', email='test@test.com'):
    cmd = f'git config --global user.email "{email}" user.name="{username}"'
    process = subprocess.run(  # nosec
        cmd,
        check=False,
        shell=True,
        capture_output=True,
    )
    evaluate_git_error(process)


def tokenizes(root: str) -> str:
    """\
    >>> tokenizes(baw.project.determine_root(__file__))
    'http://.../baw.git'
    """
    token = baw.config.gitea_token()
    domain = baw.config.gitea_server()
    if token:
        token += '@'
    owner = 'caelum'
    name = baw.config.shortcut(root)
    protocol = 'http://'
    result = f'{protocol}{token}{domain}/{owner}/{name}.git'  # TODO: ENABLE LATER
    return result


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
    if process.returncode == baw.SUCCESS:
        return True
    return False


def ensure_git(error: str = None):
    if baw.runtime.hasprog('git'):
        return
    if error:
        baw.error(f'git is not installed: {error}')
    else:
        baw.error('git is not installed')
    sys.exit(baw.FAILURE)
