# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019-2021 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
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
import sys

import baw.utils
from baw.config import sources
from baw.resources import RCFILE_PATH
from baw.runtime import run_target
from baw.utils import logging


class Scope(enum.Enum):
    ALL = enum.auto()
    MINIMAL = enum.auto()
    TODO = enum.auto()


def lint(
    root: str,
    scope: Scope = Scope.ALL,
    verbose: bool = False,
    virtual: bool = False,
    log_always: bool = True,
) -> int:
    """Run statical code analysis on `root`.

    Args:
        root(str): root of analysed project
        scope(Mode): select included findings - all, use RCFILE_PATH;
                    minimal, exclude todos from analysis; todo, exclude
                    all expect todos.
        verbose(bool): increase logging
        virtual(bool): run command in virtual environment
        log_always(bool): suppress logging if False and process completed
                          successful
    Returns:
        Returncode of linter process.
    """
    if isinstance(scope, str):
        scope = Scope[scope.upper()]
    code = ' '.join(sources(root))

    testpath = os.path.join(root, 'tests')
    linttest = testpath if os.path.exists(testpath) else ''
    run_in = f'{code} {linttest} '

    # TODO: ADD TO RETURNCODE LATER
    bandit_ = functools.partial(bandit, root, run_in, virtual, log_always,
                                verbose)
    pylint_ = functools.partial(pylint, root, scope, run_in, virtual,
                                log_always, verbose)
    _, returncode = baw.utils.fork(*[bandit_, pylint_], process=True)
    return returncode


def pylint(root, scope, run_in, virtual, log_always: bool, verbose: int) -> int:
    python = baw.config.python(root, virtual=virtual)
    spelling = baw.config.spelling(root)
    pylint_ = baw.config.pylint(root)
    cmd = f'{python} -mpylint {run_in}'
    if scope in (Scope.ALL, Scope.MINIMAL):
        cmd += f'--rcfile={RCFILE_PATH} '
    cmd += '-d R0801 '  # disable duplicated code check
    cmd += '-d R0902 '  # too many instance attributes
    if scope == Scope.MINIMAL:
        # :fixme (W0511):
        # Used when a warning note as fixme, todo or xxx is detected.
        cmd += '-d W0511 '
    if scope == Scope.TODO:
        cmd += '--disable=all --enable=W0511 '
    # Wrong hanging indentation before block
    cmd += ' -d C0330 '
    if spelling:
        cmd += '--spelling-dict=en_US '
        try:
            path = os.environ['PYLINT_SPELLING']
        except KeyError:
            baw.utils.logging_error('require global env: `PYLINT_SPELLING`')
            sys.exit(baw.utils.FAILURE)
        cmd += f'--spelling-private-dict-file={path} '
    if pylint_:
        cmd += f'{pylint_} '
    cmd = cmd.strip()
    completed = run_target(
        root,
        cmd,
        cwd=root,
        virtual=virtual,
        verbose=verbose,
    )
    if log_always or completed.returncode:
        logging(completed.stderr)
        logging(completed.stdout)
    return completed.returncode


def bandit(root, run_in, virtual, log_always: bool, verbose: int) -> int:
    python = baw.config.python(root, virtual=virtual)
    cmd = f'{python} -mbandit {run_in} -r '
    cmd += '--skip B101'  # skip assert is used

    completed = run_target(
        root,
        cmd,
        cwd=root,
        virtual=virtual,
        verbose=verbose,
    )
    if completed.returncode:
        logging(completed.stderr)
        logging(completed.stdout)
    else:
        if log_always:
            logging('bandit complete')
    return completed.returncode
