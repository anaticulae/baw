# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019-2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import collections
import glob
import os
import shutil
import stat
import sys

import baw.config
import baw.runtime


def clean(  # pylint:disable=R1260
    root: str,
    docs: bool = False,
    resources: bool = False,
    tests: bool = False,
    tmp: bool = False,
    venv: bool = False,
    all_: bool = False,
):
    baw.utils.check_root(root)
    baw.utils.log('start cleaning')
    if all_:
        docs, resources, tests, tmp, venv = True, True, True, True, True
    if venv:
        clean_virtual(root)
    patterns = create_pattern(root, resources, tmp, tests, docs)
    # problems while deleting recursive
    ret = 0
    for pattern in patterns:
        if isinstance(pattern, ResourceDir):
            todo = [pattern.path]
        else:
            try:
                todo = glob.glob(root + '/**/' + pattern, recursive=True)
            except NotADirectoryError:
                todo = glob.glob(root + '**' + pattern, recursive=True)
            todo = sorted(todo, reverse=True)  # longtest path first, to avoid
        for item in todo:
            baw.utils.log(f'remove {item}')
            try:
                if os.path.isfile(item):
                    os.remove(item)
                else:
                    shutil.rmtree(item, onerror=remove_readonly)
            except OSError as fail:
                ret += 1
                baw.utils.error(fail)
    if ret:
        sys.exit(ret)
    baw.utils.log()  # Newline
    return baw.utils.SUCCESS


def create_pattern(
    root,
    resources: bool,
    tmp: bool,
    tests: bool,
    docs: bool,
) -> list:
    selected = []
    if resources:
        # TODO: HACK
        import power  # pylint:disable=import-outside-toplevel
        tmpdir = power.generated(project=os.path.split(root)[1])
        if os.path.exists(tmpdir):
            selected.append(ResourceDir(tmpdir))
    if tmp:
        selected.extend(TMP)
    if tests:
        selected.extend([
            '.pytest_cache',
            '.tmp/pytest_cache',
        ])
    if docs:
        selected.extend([
            'docs/.tmp',
            'html',
        ])
    return selected


TMP = """
*.egg
*.egg-info
*.swo
*.swp
.coverage
.pytest_cache
.swo
.swp
.tmp
.vscode
__pycache__
build
dist
nano.save
""".strip().splitlines()

ResourceDir = collections.namedtuple('ResourceDir', 'path')


def clean_virtual(root: str):
    """Clean virtual environment of given project

    Args:
        root(str): generated project
    Hint:
        Try to remove .virtual folder
    Raises:
        SystemExit if cleaning not work
    """
    virtual_path = baw.runtime.venv(root)
    if not os.path.exists(virtual_path):
        baw.utils.log(f'Virtual environment does not exist {virtual_path}')
        return
    baw.utils.log(f'Try to clean virtual environment {virtual_path}')
    try:
        shutil.rmtree(virtual_path)
    except OSError as fail:
        baw.utils.error(fail)
        sys.exit(baw.utils.FAILURE)
    baw.utils.log('Finished')


def remove_readonly(func, path, _):  # pylint:disable=W0613
    """Clear the readonly bit and reattempt the removal"""
    os.chmod(path, stat.S_IWRITE)
    func(path)
