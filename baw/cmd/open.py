# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019-2023 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
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


def openme(root: str, path: str = None, prints: bool = False):
    if path == 'this':
        open_this(prints=prints)
    elif path == 'tests':
        open_tests(root, prints=prints)
    elif path == 'tmp':
        open_tmp(root, prints=prints)
    elif path == 'venv':
        open_venv(root, prints=prints)
    elif path == 'lasttest':
        open_lasttest(root, prints=prints)
    elif path == 'generated':
        open_generated(root, prints)
    elif path == 'project':
        root = baw.project.determine_root(os.getcwd())
        open_this(root, prints=prints)


def open_generated(root: str, console: bool = False):
    name = os.path.split(root)[1]
    generated = os.path.join(baw.config.bawtmp(), name)
    # generated = resinf.generated(project=name)
    if console:
        baw.log(generated)
        return
    if not os.path.exists(generated):
        baw.error(f'resource: {generated} not generated')
        sys.exit(baw.FAILURE)
    open_this(generated)


def open_tmp(root: str, prints: bool = False):
    name = os.path.split(root)[1]
    tmpdir = os.path.join(baw.config.bawtmp(), 'tmp', name)
    open_this(tmpdir, prints=prints)


def open_venv(root: str, prints: bool = False):
    name = os.path.split(root)[1]
    tmpdir = os.path.join(baw.config.bawtmp(), 'venv', name)
    open_this(tmpdir, prints=prints)


def open_lasttest(root: str, prints: bool = False):
    name = os.path.split(root)[1]
    tmpdir = os.path.join(baw.config.bawtmp(), 'tmp', name)
    directories = list(glob.glob(f'{tmpdir}/**/', recursive=True))
    directories = [item for item in directories if 'pytest_cache' not in item]
    directories.sort(key=lambda x: os.stat(x).st_mtime)
    try:
        last = directories[-1]
    except IndexError:
        baw.error(f'could not find any test {root}')
        return
    open_this(last, prints=prints)


def open_tests(root: str, prints: bool = False):
    tests = os.path.join(root, 'tests')
    open_this(tests, prints=prints)


def open_this(path=None, prints: bool = False):
    if path is None:
        path = os.getcwd()
    path = str(path)
    if not os.path.exists(path):
        baw.error(f'path does not exists: {path}')
        sys.exit(baw.FAILURE)
    # convert for windows
    path = path.replace('/', '\\')
    if prints:
        baw.log(path)
        return
    cmd = f'explorer {path}'
    completed = baw.runtime.run(
        cmd,
        cwd=path,
    )
    # dont know why windows returns 1
    assert completed.returncode == 1, completed
