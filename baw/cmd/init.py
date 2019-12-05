#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================
"""Init command of command line utility

Initialize a new repository due init. Add content afterwards and stash it.
"""
from os import makedirs
from os.path import dirname
from os.path import exists
from os.path import join

import utila

from baw.config import create_config
from baw.git import git_add
from baw.git import git_init
from baw.git import update_gitignore
from baw.resources import ENTRY_POINT
from baw.resources import FILES
from baw.resources import FOLDERS
from baw.resources import INIT
from baw.resources import INIT_CMD
from baw.resources import MAIN_CMD
from baw.resources import SETUP_PY
from baw.resources import template_replace
from baw.utils import BAW_EXT
from baw.utils import FAILURE
from baw.utils import INPUT_ERROR
from baw.utils import NEWLINE
from baw.utils import REQUIREMENTS_TXT
from baw.utils import SUCCESS
from baw.utils import file_append
from baw.utils import file_create
from baw.utils import logging
from baw.utils import logging_error
from baw.utils import skip

ADDITONAL_REQUIREMENTS = []


def init(
        root: str,
        shortcut: str,
        name: str,
        cmdline: bool = False,
        *,
        verbose: bool = False,
):
    """Init project due generatig file and folder

    Args:
        root(str): root of generated project
        shortcut(str): short name of project
        name(str): long name of generated project, used in documentation
    """
    baw_path = join(root, BAW_EXT)
    if exists(baw_path):
        logging_error('Project %s already exists.' % baw_path)
        raise ValueError(FAILURE)

    # Escape ' to avoid errors in generated code
    name = name.replace("'", r'\'')

    git_init(root)
    create_folder(root)
    create_config(root, shortcut, name)
    create_python(root, shortcut, cmdline=cmdline)
    create_files(root)
    create_requirements(root)

    update_gitignore(root)
    git_add(root, '*')

    from baw.cmd import release
    # Deactivate options to reach fast reaction
    release(
        root,
        stash=False,  # Nothing to stash at the first time
        sync=False,  # No sync for first time needed
        test=False,  # No testing for the first time needed
        verbose=verbose,
        virtual=False,  # No virtual for first time needed
    )
    return SUCCESS


def get_init_args(args):
    init_args = args['init']
    cmdline = False
    if len(init_args) > 3:
        raise ValueError('To many inputs: %s' % args['init'])
    if len(init_args) == 3:
        if init_args[2] != '--with_cmd':
            raise ValueError('--with_cmd allowed, not %s' % init_args[2])
        cmdline = True
    shortcut = init_args[0]
    if len(init_args) < 2:
        logging_error('missing project name')
        exit(INPUT_ERROR)
    name = init_args[1]

    return shortcut, name, cmdline


def create_folder(root: str):
    """Copy folder-structure into created project

    Args:
        root(str): project root of generated project
    """
    for item in FOLDERS:
        create = join(root, item)
        if exists(create):
            continue
        makedirs(create)
        logging('Create folder %s' % item)


def create_files(root: str):
    """Copy file to generated template. Before copying, replce template vars

    Args:
        root(str): generated project location
    """
    for item, content in FILES:
        create = join(root, item)
        replaced = template_replace(root, content)

        operation_type = 'template' if content != replaced else 'copy'
        if exists(create):
            skip('%s %s' % (operation_type, item))
            continue

        logging('%s %s' % (operation_type, item))
        parent = dirname(create)
        makedirs(parent, exist_ok=True)
        file_create(create, content=replaced)


def create_python(
        root: str,
        shortcut: str,
        *,
        cmdline: bool = False,
):
    """Create __init__.py with containing __version__-tag

    Args:
        root(str): project root of generated project
        shortcut(str): short name of generated project. Init file is located
                       in root/shortcut/__init__.py
    """
    # TODO: DIRTY
    python_project = join(root, shortcut)
    makedirs(python_project, exist_ok=True)
    file_create(join(python_project, '__init__.py'), INIT)

    entry_point = ''
    entry_point_package = ''
    if cmdline:
        python_cmdline = join(python_project, 'command')
        makedirs(python_cmdline, exist_ok=True)
        main_replaced = template_replace(root, MAIN_CMD)
        init_replaced = template_replace(root, INIT_CMD)

        file_create(join(python_project, '__main__.py'), main_replaced)
        file_create(join(python_cmdline, '__init__.py'), init_replaced)

        entry_point = template_replace(root, ENTRY_POINT)
        entry_point_package = "'%s.command'," % shortcut

        ADDITONAL_REQUIREMENTS.append(f'utila=={utila.__version__}')

    replaced = template_replace(root, SETUP_PY)
    replaced = replaced.replace("$_ENTRY_POINT_$", entry_point)
    replaced = replaced.replace("$_ENTRY_POINT_PACKAGE_$", entry_point_package)

    file_create(join(root, 'setup.py'), replaced)


def create_requirements(root: str):
    logging('add requirements')
    content = ''
    for item in ADDITONAL_REQUIREMENTS:
        content += item + NEWLINE

    file_append(join(root, REQUIREMENTS_TXT), content)
