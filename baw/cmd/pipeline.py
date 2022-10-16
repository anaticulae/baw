# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import os

import baw.cmd.utils
import baw.git
import baw.resources
import baw.run
import baw.utils


def init(
    root: str,
    verbose: bool = False,
    venv: bool = False,
):
    source = jenkinsfile(root)
    if os.path.exists(source):
        baw.utils.error(f'Jenkinsfile already exists: {source}')
        return baw.utils.FAILURE
    replaced = create_jenkinsfile(root)
    with baw.git.stash(root, verbose=verbose, venv=venv):
        baw.utils.file_create(
            source,
            content=replaced,
        )
        baw.git.add(root, 'Jenkinsfile')
        failure = baw.git.commit(
            root,
            source=source,
            message='chore(ci): add Jenkinsfile',
            verbose=verbose,
        )
        if failure:
            return failure
    baw.utils.log('Jenkinsfile added')
    return baw.utils.SUCCESS


def upgrade(
    root: str,
    verbose: bool = False,
    venv: bool = False,
):
    source = jenkinsfile(root)
    if not os.path.exists(source):
        baw.utils.error(f'Jenkinsfile does not exists: {source}')
        return baw.utils.FAILURE
    replaced = create_jenkinsfile(root)
    before = baw.utils.file_read(source)
    if replaced.strip() == before.strip():
        baw.utils.error('Jenkinsfile unchanged, skip upgrade')
        return baw.utils.FAILURE
    with baw.git.stash(root, verbose=verbose, venv=venv):
        baw.utils.file_replace(
            source,
            content=replaced,
        )
        failure = baw.git.commit(
            root,
            source=source,
            message='chore(ci): upgrade Jenkinsfile',
            verbose=False,
        )
        if failure:
            return failure
    baw.utils.log('Jenkinsfile upgraded')
    return baw.utils.SUCCESS


def create_jenkinsfile(root: str):
    newest = image_newest()
    args = image_args()
    replaced = baw.resources.template_replace(
        root,
        template=baw.resources.JENKINSFILE,
        docker_image_test_name=newest,
        docker_image_test_args=args,
    )
    return replaced


def jenkinsfile(root: str):
    return os.path.join(root, 'Jenkinsfile')


def image_newest() -> str:
    """\
    >>> image_newest()
    '.../...:...'
    """
    repository = os.environ.get(
        'BAW_PIPELINE_REPO',
        '169.254.149.20:6001',
    )
    imagename = os.environ.get(
        'BAW_PIPELINE_NAME',
        'arch_python_baw',
    )
    version = os.environ.get(
        'BAW_PIPELINE_VERSION',
        '0.8.1',
    )
    result = f'{repository}/{imagename}:{version}'
    return result


def image_args() -> str:
    """\
    >>> image_args()
    '...'
    """
    result = os.environ.get(
        'BAW_PIPELINE_TEST_ARGS',
        '-v $WORKSPACE:/var/workdir:ro',
    )
    return result


def run(args: dict):
    root = baw.cmd.utils.get_root(args)
    action = args.get('action')
    if action == 'init':
        return init(
            root,
            verbose=args.get('verbose'),
            venv=args.get('venv'),
        )
    if action == 'upgrade':
        return upgrade(
            root,
            verbose=args.get('verbose'),
            venv=args.get('venv'),
        )
    if action == 'test':
        baw.utils.error('not implemented')
    return baw.utils.FAILURE


def extend_cli(parser):
    cli = parser.add_parser('pipe', help='Run pipline task')
    cli.add_argument(
        'action',
        help='manage the jenkins file',
        nargs='?',
        const='test',
        choices='init upgrade test'.split(),
    )
    cli.set_defaults(func=run)
