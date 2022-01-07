# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019-2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import os
import sys

import baw.project
import baw.runtime
import baw.utils


def openme(root: str, path: str = None):
    if path == 'this':
        open_this()
    elif path == 'tests':
        open_tests(root)
    elif path == 'tmp':
        open_tmp(root)
    elif path == 'generated':
        open_generated(root)
    elif path == 'project':
        root = baw.project.determine_root(os.getcwd())
        open_this(root)


def open_generated(root: str):
    try:
        import power  # pylint:disable=C0415
    except ImportError:
        baw.utils.error('require power')
        sys.exit(baw.utils.FAILURE)
    name = os.path.split(root)[1]
    generated = power.generated(project=name)
    if not os.path.exists(generated):
        baw.utils.error(f'resource: {generated} not generated')
        sys.exit(baw.utils.FAILURE)
    open_this(generated)


def open_tmp(root: str):
    name = os.path.split(root)[1]
    # C:\tmp\tmp\kiwi\rawmaker\.tmp
    # TODO: REMOVE HARD CODED PATH
    tests = os.path.join('C:/tmp/tmp/kiwi', name, '.tmp')
    open_this(tests)


def open_tests(root: str):
    tests = os.path.join(root, 'tests')
    open_this(tests)


def open_this(path=None):
    if path is None:
        path = os.getcwd()
    path = str(path)
    # convert for windows
    path = path.replace('/', '\\')
    cmd = f'explorer {path}'
    completed = baw.runtime.run(
        cmd,
        cwd=path,
    )
    # dont know why windows returns 1
    assert completed.returncode == 1, completed
