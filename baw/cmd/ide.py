# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019-2021 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================
"""The purpose of this module is to setup the development environment of
the user and start the ide afterwards. """

import os

import baw.config
import baw.project
import baw.resources
import baw.runtime
import baw.utils

WORKSPACE_NAME = '..code-workspace'


def ide_open(root: str, packages: tuple = None) -> int:
    """Generate vscode workspace and run afterwards."""
    detected = baw.project.determine_root(root)
    if detected is None:
        baw.utils.logging_error(f'could not locate .baw project in: {root}')
        return baw.utils.FAILURE
    root = detected

    baw.utils.logging('generate')
    generate_workspace(root, packages=packages)
    generate_sort_config(root)
    generate_conftest(root)

    baw.utils.logging('open')
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
    rcfile = baw.utils.forward_slash(baw.resources.RCFILE_PATH)
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

    replaced = baw.resources.template_replace(
        root,
        baw.resources.CODE_WORKSPACE,
        folders=folders,
        rcfile=rcfile,
        isort=isortfile,
    )
    baw.utils.file_replace(output, replaced)


def generate_conftest(root: str):
    """Generate conftest file if not exists, or update if file smaller
    than the new one"""

    testpath = os.path.join(root, 'tests')
    if not os.path.exists(testpath):
        return
    output = os.path.join(testpath, 'conftest.py')
    if not os.path.exists(output):
        baw.utils.file_create(output, baw.resources.CONFTEST_TEMPLATE)
        return

    if len(baw.utils.file_read(output)) < len(baw.resources.CONFTEST_TEMPLATE):
        baw.utils.file_replace(output, baw.resources.CONFTEST_TEMPLATE)


def generate_sort_config(root: str):
    output = sort_configuration(root)
    replaced = baw.resources.template_replace(
        root,
        baw.resources.ISORT_TEMPLATE,
    )
    baw.utils.file_replace(output, replaced)


def start(root):
    """Run vscode"""
    output = workspace_configuration(root)
    cmd = f'code {output} &'
    completed = baw.runtime.run_target(
        root,
        cmd,
        runtimelog=False,
        verbose=False,
    )
    return completed.returncode


def sort_configuration(root: str) -> str:
    config = os.path.join(baw.utils.tmp(root), '.isort.cfg')
    forward = baw.utils.forward_slash(config)
    return forward


def workspace_configuration(root: str):
    """Path to generated workspace configuration"""
    return baw.utils.forward_slash(os.path.join(root, '..code-workspace'))
