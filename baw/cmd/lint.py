# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019-2023 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================
"""The purpose of this module is to run statical code analysis on
selected project.

There are three different options to run the linter: all, todo and
minimal:

* all: every check out of RCFILE_PATH is executed
* todo: only todos are collected
* minimal: everything expect of todo is collected"""

import enum
import functools
import os

import baw
import baw.config
import baw.resources
import baw.runtime
import baw.utils


class Scope(enum.Enum):
    ALL = enum.auto()
    MINIMAL = enum.auto()
    TODO = enum.auto()

    @staticmethod
    def from_str(scope: str):
        if isinstance(scope, str):
            scope = Scope[scope.upper()]
        return scope


def run_linter(root: str, verbose: bool, venv: bool) -> int:
    if not baw.config.basic(root):
        return baw.utils.SUCCESS
    if not baw.config.fail_on_finding(root):
        return baw.utils.SUCCESS
    # run linter step before running test and release
    if returncode := lint(
            root,
            scope=Scope.MINIMAL,
            verbose=verbose,
            venv=venv,
            log_always=False,
    ):
        baw.utils.error('could not release, solve this errors first.')
        baw.utils.error('turn `fail_on_finding` off to release with errors')
        return returncode
    return baw.utils.SUCCESS


def lint(
    root: str,
    scope: Scope = Scope.ALL,
    verbose: bool = False,
    venv: bool = False,
    log_always: bool = True,
) -> int:
    """Run statical code analysis on `root`.

    Args:
        root(str): root of analysed project
        scope(Mode): select included findings - all, use RCFILE_PATH;
                    minimal, exclude todos from analysis; todo, exclude
                    all expect todos.
        verbose(bool): increase logging
        venv(bool): run cmd in venv environment
        log_always(bool): suppress logging if False and process completed
                          successful
    Returns:
        Returncode of linter process.
    """
    scope = Scope.from_str(scope)
    code = ' '.join(baw.config.sources(root))
    testpath = os.path.join(root, 'tests')
    linttest = testpath if os.path.exists(testpath) else ''
    run_in = f'{code} {linttest} '
    # TODO: ADD TO RETURNCODE LATER
    bandit_ = functools.partial(bandit, root, run_in, venv, log_always, verbose)
    pylint_ = functools.partial(pylint, root, scope, run_in, venv, log_always,
                                verbose)
    returncode = baw.utils.fork(
        *[bandit_, pylint_],
        process=True,
        returncode=True,
    )
    return returncode


def pylint(root, scope, run_in, venv, log_always: bool, verbose: int) -> int:
    python = baw.config.python(root, venv=venv)
    spelling = baw.config.spelling(root)
    pylint_ = baw.config.pylint(root)
    cmd = f'{python} -mpylint {run_in}'
    if scope in (Scope.ALL, Scope.MINIMAL):
        cmd += f'--rcfile={baw.resources.RCFILE_PATH} '
    cmd += '-d R0801 '  # disable duplicated code check
    cmd += '-d R0902 '  # too many instance attributes
    cmd += '-d R0912 '  # too many branches
    if scope == Scope.MINIMAL:
        # :fixme (W0511):
        # Used when a warning note as fixme, todo or xxx is detected.
        cmd += '-d W0511 '
    if scope == Scope.TODO:
        cmd += '--disable=all --enable=W0511 '
    if spelling:
        cmd += '--spelling-dict=en_US '
        path = baw.config.pylint_spelling()
        cmd += f'--spelling-private-dict-file={path} '
    if pylint_:
        cmd += f'{pylint_} '
    cmd = cmd.strip()
    completed = baw.runtime.run_target(
        root,
        cmd,
        cwd=root,
        venv=venv,
        verbose=verbose,
    )
    if log_always or completed.returncode:
        baw.completed(completed, force=True)
    return completed.returncode


def bandit(root, run_in, venv, log_always: bool, verbose: int) -> int:
    python = baw.config.python(root, venv=venv)
    cmd = f'{python} -mbandit {run_in} -r '
    cmd += '--skip B101'  # skip assert is used
    cmd += ',B404'  # import subprocess

    completed = baw.runtime.run_target(
        root,
        cmd,
        cwd=root,
        venv=venv,
        verbose=verbose,
    )
    if completed.returncode:
        baw.completed(completed)
    elif log_always:
        baw.utils.log('bandit complete')
    return completed.returncode


def extend_cli(parser):
    lints = parser.add_parser('lint', help='Statical code analysis')
    lints.add_argument(
        'action',
        help='what shall we do',
        choices='all minimal todo'.split(),
        nargs='?',
        default='minimal',
    )
    lints.set_defaults(func=baw.run.run_lint)
