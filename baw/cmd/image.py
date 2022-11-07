# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import contextlib
import os
import sys

import baw.cmd.utils
import baw.config
import baw.utils
import baw.cmd.info


def create(
    root: str,
    verbose: bool = False,
    venv: bool = False,
):
    with dockerfile(root) as path:
        pass
    return baw.utils.SUCCESS


def tag(root: str) -> str:
    """\
    >>> tag(__file__)
    '.../TRY_baw-...'
    """
    root = baw.cmd.utils.determine_root(root)
    testing = baw.config.docker_testing()
    name = baw.cmd.info.requirement_hash(root, verbose=True)
    result = f'{testing}/TRY_{name}'
    return result


@contextlib.contextmanager
def dockerfile(root: str):
    name = baw.cmd.info.requirement_hash(root, verbose=True)
    # use own tmpfile cause TemporaryFile(delete=True) seems no supported
    # at linux, parameter delete is missing.
    config = os.path.join(root, name)
    content = (header(root) + baw.utils.NEWLINE * 2 + requirements(root) +
               baw.utils.NEWLINE * 2 + SYNC)
    baw.utils.file_replace(config, content)
    yield config
    # remove file
    os.unlink(config)


def header(root: str) -> str:
    """\
    >>> header(__file__)
    'FROM .../...'
    """
    root = baw.cmd.utils.determine_root(root)
    if not root:
        sys.exit(baw.utils.FAILURE)
    image = baw.config.docker_image(root)
    result = f'FROM {image}'
    return result


def requirements(root: str) -> str:
    r"""\
    >>> requirements(__file__)
    'COPY requirements.txt .\nCOPY requirements.dev .\n'
    """
    root = baw.cmd.utils.determine_root(root)
    if not root:
        sys.exit(baw.utils.FAILURE)
    result = ''
    for item in 'requirements.txt requirements.dev requirements.all'.split():
        path = os.path.join(root, item)
        if not os.path.exists(path):
            continue
        result += f'COPY {item} .{baw.utils.NEWLINE}'
    return result


SYNC = """
RUN baw sync all
"""


def run(args: dict):
    root = baw.cmd.utils.get_root(args)
    action = args.get('action')
    if action == 'create':
        return create(
            root,
            verbose=args.get('verbose'),
            venv=args.get('venv'),
        )
    if action == 'update':
        baw.utils.error('not implemented')
    if action == 'delete':
        baw.utils.error('not implemented')
    return baw.utils.FAILURE


def extend_cli(parser):
    cli = parser.add_parser(
        'image',
        help='Create docker environment',
    )
    cli.add_argument(
        'action',
        help='manage the docker image',
        nargs='?',
        const='create',
        choices='create update delete'.split(),
    )
    cli.set_defaults(func=run)
