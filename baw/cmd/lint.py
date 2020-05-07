# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019-2020 by Helmut Konrad Fahrendholz. All rights reserved.
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
import os

from baw.config import sources
from baw.resources import RCFILE_PATH
from baw.runtime import run_target
from baw.utils import logging


class Scope:
    ALL = enum.auto()
    MINIMAL = enum.auto()
    TODO = enum.auto()

    @staticmethod
    def from_str(name):
        # TODO: REPLACE WITH PYTHONIC WAY
        name = name.upper()
        if name == 'ALL':
            return Scope.ALL
        if name == 'MINIMAL':
            return Scope.MINIMAL
        if name == 'TODO':
            return Scope.TODO
        raise ValueError(name)


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
        scope = Scope.from_str(scope)
    code = ' '.join(sources(root))

    testpath = os.path.join(root, 'tests')
    linttest = testpath if os.path.exists(testpath) else ''

    cmd = f'pylint {code} {linttest} '
    if scope in (Scope.ALL, Scope.MINIMAL):
        cmd += f'--rcfile={RCFILE_PATH} '
    if scope == Scope.MINIMAL:
        # :fixme (W0511):
        # Used when a warning note as fixme, todo or xxx is detected.
        cmd += '-d W0511'
    if scope == Scope.TODO:
        cmd += '--disable=all --enable=W0511'

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
