#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019-2021 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================
"""Init command of command line utility

Initialize a new repository due init. Add content afterwards and stash it.
"""

import os

import baw.cmd.plan
import baw.config
import baw.git
import baw.resources
import baw.utils

ADDITONAL_REQUIREMENTS = []


def init(
        root: str,
        shortcut: str,
        name: str,
        cmdline: bool = False,
        *,
        verbose: bool = False,
) -> int:
    """Init project due generatig file and folder

    Args:
        root(str): root of generated project
        shortcut(str): short name of project
        name(str): long name of generated project, used in documentation
        cmdline(bool): add default cmdline template to use project as cli
        verbose(bool): increase logging
    Raises:
        ValueError: if project already exists
    Returns:
        SUCCESS or return code of failed process
    """
    baw_path = os.path.join(root, baw.utils.BAW_EXT)
    if os.path.exists(baw_path):
        baw.utils.logging_error('Project %s already exists.' % baw_path)
        raise ValueError(baw.utils.FAILURE)

    # Escape ' to avoid errors in generated code
    name = name.replace("'", r'\'')

    baw.git.git_init(root)
    create_folder(root)
    baw.config.create(root, shortcut, name)
    create_python(root, shortcut, cmdline=cmdline)
    create_files(root)
    create_requirements(root)

    baw.git.update_gitignore(root)

    from baw.cmd.format import format_repository

    baw.utils.logging()  # write newline
    completed = format_repository(root, verbose=verbose, virtual=False)
    if completed:
        return completed

    baw.git.git_add(root, '*')

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

    # TODO: Think aboud activating later? Add test flag?
    # Reduces times of creating from 8 to 2 secs
    # quality = baw.cmd.plan.code_quality(root)
    # baw.cmd.plan.create(
    #     root,
    #     linter=quality.rating,
    #     coverage=quality.coverage,
    # )
    # baw.cmd.plan.create(root)

    return baw.utils.SUCCESS


def create_folder(root: str):
    """Copy folder-structure into created project

    Args:
        root(str): project root of generated project
    """
    for item in baw.resources.FOLDERS:
        create = os.path.join(root, item)
        if os.path.exists(create):
            continue
        os.makedirs(create)
        baw.utils.logging('Create folder %s' % item)


def create_files(root: str):
    """Copy file to generated template. Before copying, replce template vars

    Args:
        root(str): generated project location
    """
    for item, content in baw.resources.FILES:
        create = os.path.join(root, item)
        replaced = baw.resources.template_replace(root, content)

        operation_type = 'template' if content != replaced else 'copy'
        if os.path.exists(create):
            baw.utils.skip('%s %s' % (operation_type, item))
            continue

        baw.utils.logging('%s %s' % (operation_type, item))
        parent = os.path.dirname(create)
        os.makedirs(parent, exist_ok=True)
        baw.utils.file_create(create, content=replaced)


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
        cmdline(bool): if True, create command line template
    """
    # TODO: DIRTY
    python_project = os.path.join(root, shortcut)
    os.makedirs(python_project, exist_ok=True)
    baw.utils.file_create(
        os.path.join(python_project, '__init__.py'), baw.resources.INIT)

    entry_point = ''
    entry_point_package = ''
    if cmdline:
        python_cmdline = os.path.join(python_project, 'cli')
        os.makedirs(python_cmdline, exist_ok=True)
        main_replaced = baw.resources.template_replace(
            root,
            baw.resources.MAIN_CMD,
        )
        init_replaced = baw.resources.template_replace(
            root,
            baw.resources.INIT_CMD,
        )
        baw.utils.file_create(
            os.path.join(python_project, '__main__.py'),
            main_replaced,
        )
        baw.utils.file_create(
            os.path.join(python_cmdline, '__init__.py'),
            init_replaced,
        )
        entry_point = baw.resources.template_replace(
            root,
            baw.resources.ENTRY_POINT,
        )
        entry_point_package = "'%s.cli'," % shortcut

        ADDITONAL_REQUIREMENTS.append(f'utila=={utila_current()}')

    replaced = baw.resources.template_replace(root, baw.resources.SETUP_PY)
    replaced = replaced.replace("{%ENTRY_POINT%}", entry_point)
    replaced = replaced.replace("{%ENTRY_POINT_PACKAGE%}", entry_point_package)

    baw.utils.file_create(os.path.join(root, 'setup.py'), replaced)


def create_requirements(root: str):
    baw.utils.logging('add requirements')
    content = ''
    for item in ADDITONAL_REQUIREMENTS:
        content += item + baw.utils.NEWLINE
    baw.utils.file_append(
        os.path.join(root, baw.utils.REQUIREMENTS_TXT),
        content,
    )


def utila_current() -> str:
    """Determine current version of `utila` package."""
    default = "1.11.0"
    try:
        import utila
        # extend linter white list, cause __version__ is not available for
        # linter if utila is not installed.
        return utila.__version__  # pylint:disable=E1101
    except ImportError:
        return default
