# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019-2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import glob
import os
import sys

import baw.config
import baw.project
import baw.runtime
import baw.utils


def openme(root: str, path: str = None, console: bool = False):
    if path == 'this':
        open_this()
    elif path == 'tests':
        open_tests(root)
    elif path == 'tmp':
        open_tmp(root)
    elif path == 'lasttest':
        open_lasttest(root)
    elif path == 'generated':
        open_generated(root, console)
    elif path == 'project':
        root = baw.project.determine_root(os.getcwd())
        open_this(root)


def open_generated(root: str, console: bool = False):
    try:
        import power  # pylint:disable=C0415
    except ImportError:
        baw.utils.error('require power')
        sys.exit(baw.utils.FAILURE)
    name = os.path.split(root)[1]
    generated = power.generated(project=name)
    if console:
        baw.utils.log(generated)
        return
    if not os.path.exists(generated):
        baw.utils.error(f'resource: {generated} not generated')
        sys.exit(baw.utils.FAILURE)
    open_this(generated)


def open_tmp(root: str):
    name = os.path.split(root)[1]
    tmpdir = os.path.join(baw.config.bawtmp(), 'tmp', name)
    open_this(tmpdir)


def open_lasttest(root: str):
    name = os.path.split(root)[1]
    tmpdir = os.path.join(baw.config.bawtmp(), 'tmp', name)
    directories = list(glob.glob(f'{tmpdir}/**/', recursive=True))
    directories = [item for item in directories if 'pytest_cache' not in item]
    directories.sort(key=lambda x: os.stat(x).st_mtime)
    try:
        last = directories[-1]
    except IndexError:
        baw.utils.error(f'could not find any test {root}')
        return
    open_this(last)


def open_tests(root: str):
    tests = os.path.join(root, 'tests')
    open_this(tests)


def open_this(path=None):
    if path is None:
        path = os.getcwd()
    path = str(path)
    if not os.path.exists(path):
        baw.utils.error(f'path does not exists: {path}')
        sys.exit(baw.utils.FAILURE)
    # convert for windows
    path = path.replace('/', '\\')
    cmd = f'explorer {path}'
    completed = baw.runtime.run(
        cmd,
        cwd=path,
    )
    # dont know why windows returns 1
    assert completed.returncode == 1, completed
