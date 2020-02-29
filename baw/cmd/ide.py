# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019-2020 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================
"""The purpose of this module is to setup the development environment of the
user and start the ide afterwards. """
import os
from os.path import exists
from os.path import join

import baw.config
from baw.resources import CODE_WORKSPACE as TEMPLATE
from baw.resources import CONFTEST_TEMPLATE
from baw.resources import ISORT_TEMPLATE
from baw.resources import RCFILE_PATH
from baw.resources import template_replace
from baw.runtime import run_target
from baw.utils import FAILURE
from baw.utils import file_create
from baw.utils import file_read
from baw.utils import file_replace
from baw.utils import forward_slash
from baw.utils import logging
from baw.utils import logging_error
from baw.utils import tmp

WORKSPACE_NAME = '..code-workspace'


def ide_open(root: str, packages: tuple = None) -> int:
    """Generate vscode workspace and run afterwards"""
    detected = determine_root(root)
    if detected is None:
        logging_error(f'could not locate .baw project in: {root}')
        return FAILURE
    root = detected

    logging('generate')
    generate_workspace(root, packages=packages)
    generate_sort_config(root)
    generate_conftest(root)

    logging('open')
    returncode = start(root)
    return returncode


def generate_workspace(root: str, packages: tuple = None):
    """Generate workspace configuration depending on selected
    `packages`. Packages enables to generate only a part of the
    project.

    If package is None, all folders of the project are included.
    If package is given as a tuple, the package folder, test folder,
    docs and resources is generated.

    Args:
        root(str): path to project root
        packages(tuple): tuple of packages
    """
    name = baw.config.name(root)
    output = workspace_configuration(root)
    rcfile = forward_slash(RCFILE_PATH)
    isortfile = sort_configuration(root)

    if packages is None:
        folders = """\
            {
                "name": "%s",
                "path": "."
            }
        """ % name
    else:
        packages = sorted(packages)
        todo = []
        for item in packages:
            todo.append((item, item))
            todo.append(('tests', f'tests/{item}_'))
        todo.append(('docs', 'docs'))
        todo.append(('resources', 'tests/resources'))
        folders = []
        for (name, path) in todo:
            if not os.path.exists(path):
                baw.utils.logging_error(f'{path} does not exists')
                continue
            folders.append('{ "name": "%s", "path" : "./%s",},' % (name, path))
        folders = baw.utils.NEWLINE.join(folders)  # pylint:disable=R0204

    replaced = template_replace(
        root,
        TEMPLATE,
        folders=folders,
        rcfile=rcfile,
        isort=isortfile,
    )
    file_replace(output, replaced)


def generate_conftest(root: str):
    """Generate conftest file if not exists, or update if file smaller
    than the new one"""

    testpath = os.path.join(root, 'tests')
    if not os.path.exists(testpath):
        return
    output = join(testpath, 'conftest.py')
    if not exists(output):
        file_create(output, CONFTEST_TEMPLATE)
        return

    if len(file_read(output)) < len(CONFTEST_TEMPLATE):
        file_replace(output, CONFTEST_TEMPLATE)


def generate_sort_config(root: str):
    output = sort_configuration(root)
    replaced = template_replace(root, ISORT_TEMPLATE)
    file_replace(output, replaced)


def start(root):
    """Run vscode"""
    output = workspace_configuration(root)
    cmd = f'code {output} &'
    completed = run_target(
        root,
        cmd,
        runtimelog=False,
        verbose=False,
    )
    return completed.returncode


def sort_configuration(root: str):
    return forward_slash(join(tmp(root), '.isort.cfg'))


def workspace_configuration(root: str):
    """Path to generated workspace configuration"""
    return forward_slash(join(root, '..code-workspace'))


def determine_root(path) -> str:
    current = str(path)
    while not os.path.exists(os.path.join(current, '.baw')):
        current, base = os.path.split(current)
        if not str(base).strip():
            return None
    return current
