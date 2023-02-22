# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019-2023 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
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


def ide_open(root: str, packages: tuple = None) -> int:
    """Generate vscode workspace and run afterwards."""
    detected = baw.project.determine_root(root)
    if detected is None:
        baw.error(f'could not locate .baw project in: {root}')
        return baw.FAILURE
    root = detected

    baw.log('generate')
    generate_workspace(root, packages=packages)
    if baw.project.ispython(root):
        generate_sort_config(root)
        generate_conftest(root)

    baw.log('open')
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
    rcfile = baw.forward_slash(baw.resources.RCFILE_PATH)
    isortfile = sort_configuration(root)
    if packages is None:
        # pylint:disable=C0209
        folders = """\
            {
                "name": "%s",
                "path": "%s"
            }
        """ % (name, baw.forward_slash(root, save_newline=False))
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
            path = baw.forward_slash(path, save_newline=False)
            if not os.path.exists(path):
                baw.error(f'{path} does not exists')
                continue
            folders.append('{ "name": "%s", "path" : "./%s",},' % (name, path))  # pylint:disable=C0209
        folders: str = baw.NEWLINE.join(folders)
    # write template
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
    forward = baw.forward_slash(config)
    return forward


def workspace_configuration(root: str):
    """Path to generated workspace configuration."""
    config = os.path.join(baw.utils.tmp(root), '..code-workspace')
    return baw.forward_slash(config)


def extend_cli(parser):
    ides = parser.add_parser('ide', help='Create Workspace and open IDE')
    ides.set_defaults(func=baw.run.run_ide)
    ides.add_argument(
        'package',
        help='Open selective package(s)',
        nargs='*',
        default=[],
    )
