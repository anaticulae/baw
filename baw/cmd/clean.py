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


def clean(  # pylint:disable=R1260,too-many-branches
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
        clean_venv(root)
    if docs:
        clean_docs(root)
    if tmp:
        clean_git(root)
    patterns = create_pattern(root, resources, tmp, tests)
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


def clean_git(root: str):
    if not baw.runtime.hasprog('git'):
        baw.utils.error('git is not installed, could not clean')
        return
    completed = baw.runtime.run_target(
        root=root,
        command='git clean -xf',
        cwd=root,
        verbose=False,
    )
    if completed.stdout:
        baw.utils.log(completed.stdout)
    if completed.stderr:
        baw.utils.error(completed.stderr)


def clean_docs(root: str):
    doctmp = baw.config.docpath(root, mkdir=False)
    if not os.path.exists(doctmp):
        baw.utils.log(f'no docs generated: {doctmp}')
        return
    baw.utils.log(f'clean docs {doctmp}')
    try:
        shutil.rmtree(doctmp)
    except OSError as fail:
        baw.utils.error(fail)
        sys.exit(baw.utils.FAILURE)
    baw.utils.log('finished')


def create_pattern(
    root,
    resources: bool,
    tmp: bool,
    tests: bool,
) -> list:
    selected = []
    if resources:
        # TODO: HACK
        try:
            import power  # pylint:disable=import-outside-toplevel
            tmpdir = power.generated(project=os.path.split(root)[1])
            if os.path.exists(tmpdir):
                selected.append(ResourceDir(tmpdir))
        except ModuleNotFoundError as error:
            baw.utils.error(f'install power to clean resources: {error}')
    if tmp:
        selected.extend(TMP)
    if tests:
        selected.extend([
            '.pytest_cache',
            '.tmp/pytest_cache',
        ])
    return selected


TMP = """
*.egg
*.egg-info
*.log
*.stackdump
*.swo
*.swp
..code-workspace
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
pytest.ini
""".strip().splitlines()

ResourceDir = collections.namedtuple('ResourceDir', 'path')


def clean_venv(root: str):
    """Clean venv environment of given project

    Args:
        root(str): generated project
    Hint:
        Try to remove .venv folder
    Raises:
        SystemExit if cleaning not work
    """
    venv_path = baw.runtime.virtual(root)
    if not os.path.exists(venv_path):
        baw.utils.log(f'venv environment does not exist {venv_path}')
        return
    baw.utils.log(f'clean venv: {venv_path}')
    try:
        shutil.rmtree(venv_path)
    except OSError as fail:
        baw.utils.error(fail)
        sys.exit(baw.utils.FAILURE)
    baw.utils.log('done')


def remove_readonly(func, path, _):  # pylint:disable=W0613
    """Clear the readonly bit and reattempt the removal"""
    os.chmod(path, stat.S_IWRITE)
    func(path)
