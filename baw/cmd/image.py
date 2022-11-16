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

import baw.cmd.info
import baw.cmd.utils
import baw.config
import baw.runtime
import baw.utils


def create(  # pylint:disable=W0613
    root: str,
    verbose: bool = False,
    venv: bool = False,
):
    root = baw.cmd.utils.determine_root(root)
    tag_new = tag(root)
    with dockerfile(root) as path:
        todo = [
            f'build -t {tag_new} -f {path} .',
            f'push {tag_new}',
        ]
        if returncode := docker_run(todo, root):
            return returncode
    return baw.utils.SUCCESS


def docker_run(
    todo: list,
    root: str,
    service: bool = True,
) -> int:
    if isinstance(todo, str):
        todo = [todo]
    if service:
        return docker_service(todo, root)
    if not baw.runtime.hasprog('docker'):
        baw.utils.error('require docker')
        return baw.utils.FAILURE
    for job in todo:
        cmd = f'docker {job}'
        completed = baw.runtime.run(cmd, cwd=root)
        if completed.returncode:
            if completed.stdout:
                baw.utils.error(completed.stdout)
            baw.utils.error(completed.stderr)
            return baw.utils.FAILURE
    return baw.utils.SUCCESS


def docker_service(todo: list, root: str) -> int:  # pylint:disable=W0613
    return baw.utils.SUCCESS


def tag(root: str) -> str:
    """\
    >>> tag(__file__)
    '.../try_baw_...'
    """
    root = baw.cmd.utils.determine_root(root)
    testing = baw.config.docker_testing()
    name = baw.cmd.info.requirement_hash(root, verbose=True)
    result = f'{testing}/try_{name}'
    return result


@contextlib.contextmanager
def dockerfile(root: str):
    name = baw.cmd.info.requirement_hash(root, verbose=True)
    # use own tmpfile cause TemporaryFile(delete=True) seems no supported
    # at linux, parameter delete is missing.
    config = os.path.join(root, name)
    content = (header(root) + baw.utils.NEWLINE * 2 + requirements(root) + SYNC)
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
    image = baw.cmd.pipeline.docker_image(root)
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
