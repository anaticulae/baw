#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019-2023 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================
"""Init cmd of cmd line utility

Initialize a new repository due init. Add content afterwards and stash it.
"""

import os

import baw.cmd
import baw.cmd.format
import baw.cmd.release
import baw.config
import baw.gix
import baw.resources
import baw.utils

ADDITONAL_REQUIREMENTS = []


def evaluate(args):
    directory = baw.cmd.utils.run_environment(args)
    #  No GIT found, exit 1
    with baw.utils.handle_error(ValueError, code=baw.FAILURE):
        shortcut, description, cmdline = (
            args['shortcut'],
            args['description'],
            args['cmdline'],
        )
        completed = init(
            directory,
            shortcut,
            name=description,
            cmdline=cmdline,
            verbose=args['verbose'],
        )
    return completed


def init(
    root: str,
    shortcut: str,
    name: str,
    cmdline: bool = False,
    *,
    verbose: bool = False,
    formatter: bool = False,
) -> int:
    """Init project due generatig file and folder

    Args:
        root(str): root of generated project
        shortcut(str): short name of project
        name(str): long name of generated project, used in documentation
        cmdline(bool): add default cmdline template to use project as cli
        verbose(bool): increase logging
        formatter(bool): run yapf and isort
    Raises:
        ValueError: if project already exists
    Returns:
        SUCCESS or return code of failed process
    """
    baw_path = os.path.join(root, baw.utils.BAW_EXT)
    if os.path.exists(baw_path):
        baw.error(f'Project {baw_path} already exists.')
        raise ValueError(baw.FAILURE)
    if not baw.runtime.installed('semantic-release', root):
        return baw.FAILURE
    # Escape ' to avoid errors in generated code
    name = name.replace("'", r'\'')
    baw.gix.init(root)
    create_folder(root)
    baw.config.create(root, shortcut, name)
    create_python(root, shortcut, cmdline=cmdline)
    create_files(root)
    create_requirements(root)
    baw.gix.update_gitignore(root)
    baw.log()  # write newline
    if formatter:
        # TODO: EXPOSE FORMATTER BY CLI FLAG
        completed = baw.cmd.format.format_repository(
            root,
            verbose=verbose,
            venv=False,
        )
        if completed:
            return completed
    if returncode := first_commit(root, verbose):
        return returncode
    # Deactivate options to reach fast reaction
    # TODO: Think aboud activating later? Add test flag?
    # Reduces times of creating from 8 to 2 secs
    # quality = baw.cmd.plan.code_quality(root)
    # baw.cmd.plan.create(
    #     root,
    #     linter=quality.rating,
    #     coverage=quality.coverage,
    # )
    # baw.cmd.plan.create(root)
    return baw.SUCCESS


def first_commit(root, verbose: bool) -> int:
    """This is a replacement for semantic_release cause project setup
    does not worker proper like in the past(4.1.1) anymore."""
    baw.git_add(
        root,
        '.',
        verbose=verbose,
    )
    returncode = baw.git_commit(
        root,
        source=' ',
        message=INIT,
        tag=baw.cmd.release.FIRST_RELEASE,
    )
    return returncode


INIT = """\
0.0.0 initial release

Automatically generated release.
"""


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
        baw.log(f'create folder {item}')


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
            baw.utils.skip(f'{operation_type} {item}')
            continue
        baw.log(f'{operation_type} {item}')
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
        cmdline(bool): if True, create cmd line template
    """
    # TODO: DIRTY
    python_project = os.path.join(root, shortcut)
    os.makedirs(python_project, exist_ok=True)
    baw.utils.file_create(
        os.path.join(python_project, '__init__.py'),
        baw.resources.INIT,
    )

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
        entry_point_package = f"'{shortcut}.cli',"

        ADDITONAL_REQUIREMENTS.append(f'utila=={utila_current()}')

    replaced = baw.resources.template_replace(root, baw.resources.SETUP_PY)
    replaced = replaced.replace("{{ENTRY_POINT}}", entry_point)
    replaced = replaced.replace("{{ENTRY_POINT_PACKAGE}}", entry_point_package)

    baw.utils.file_create(os.path.join(root, 'setup.py'), replaced)


def create_requirements(root: str):
    baw.log('add requirements')
    content = ''
    for item in ADDITONAL_REQUIREMENTS:
        content += item + baw.NEWLINE
    baw.utils.file_append(
        os.path.join(root, baw.utils.REQUIREMENTS_TXT),
        content,
    )


def utila_current() -> str:
    """Determine current version of `utila` package.
    >>> utila_current()
    '...'
    """
    import utila
    return utila.__version__


def extend_cli(parser):
    inix = parser.add_parser('init', help='Create .baw project')
    inix.add_argument('shortcut', help='Project name')
    inix.add_argument('description', help='Project description')
    inix.add_argument('--cmdline', action='store_true')
    inix.set_defaults(func=evaluate)
