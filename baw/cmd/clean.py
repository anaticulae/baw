# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019-2023 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import collections
import glob
import os
import shutil
import stat
import sys

import resinf

import baw
import baw.cmd.utils
import baw.config
import baw.gix
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
    baw.log('start cleaning')
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
            baw.log(f'remove {item}')
            try:
                if os.path.isfile(item):
                    os.remove(item)
                else:
                    shutil.rmtree(item, onerror=remove_readonly)
            except OSError as fail:
                ret += 1
                baw.error(fail)
    if ret:
        sys.exit(ret)
    baw.log()  # Newline
    return baw.SUCCESS


def clean_git(root: str):
    baw.gix.ensure_git('could not clean')
    completed = baw.runtime.run_target(
        root=root,
        cmd='git clean -xf',
        cwd=root,
        verbose=False,
    )
    baw.completed(completed)


def clean_docs(root: str):
    doctmp = baw.config.docpath(root, mkdir=False)
    if not os.path.exists(doctmp):
        baw.log(f'no docs generated: {doctmp}')
        return
    baw.log(f'clean docs {doctmp}')
    try:
        shutil.rmtree(doctmp)
    except OSError as fail:
        baw.error(fail)
        sys.exit(baw.FAILURE)
    baw.log('finished')


def create_pattern(
    root,
    resources: bool,
    tmp: bool,
    tests: bool,
) -> list:
    selected = []
    if resources:
        selected.extend(generated(root))
    if tmp:
        selected.extend(TMP)
    if tests:
        selected.extend(TESTS)
    return selected


def generated(root) -> list:
    project = os.path.split(root)[1]
    tmpdir = resinf.generated(project=project)
    selected = []
    if os.path.exists(tmpdir):
        selected.append(ResourceDir(tmpdir))
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
outdir
dist
nano.save
pytest.ini
""".strip().splitlines()

TESTS = """
.pytest_cache
.tmp/pytest_cache
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
        baw.log(f'venv environment does not exist {venv_path}')
        return
    baw.log(f'clean venv: {venv_path}')
    try:
        shutil.rmtree(venv_path)
    except OSError as fail:
        baw.error(fail)
        sys.exit(baw.FAILURE)
    baw.log('done')


def remove_readonly(func, path, _):  # pylint:disable=W0613
    """Clear the readonly bit and reattempt the removal"""
    os.chmod(path, stat.S_IWRITE)
    func(path)


def run(args):
    root = baw.cmd.utils.get_root(args)
    xclean = args['clean']
    docs = xclean == 'docs'
    resources = xclean == 'resources'
    tests = xclean == 'tests'
    tmp = xclean == 'tmp'
    venv = xclean == 'venv'
    all_ = xclean == 'all'
    if xclean == 'ci':
        docs = True
        resources = True
        tests = True
        tmp = True
    result = clean(
        docs=docs,
        resources=resources,
        tests=tests,
        tmp=tmp,
        venv=venv,
        all_=all_,
        root=root,
    )
    return result


def extend_cli(parser):
    plan = parser.add_parser('clean', help='Remove generated content')
    plan.add_argument(
        'clean',
        help='Remove different type of content',
        choices=['all', 'docs', 'resources', 'tests', 'tmp', 'venv', 'ci'],
        nargs='?',
        default='tests',
    )
    plan.set_defaults(func=run)
