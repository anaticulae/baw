# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2022-2023 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import os

import baw.cmd.utils
import baw.dockers.image
import baw.gix
import baw.pipefile
import baw.project
import baw.resources
import baw.run
import baw.utils


def init(
    root: str,
    verbose: bool = False,
    venv: bool = False,
):
    source = baw.pipefile.jenkinsfile(root)
    if os.path.exists(source):
        baw.error(f'Jenkinsfile already exists: {source}')
        return baw.FAILURE
    replaced = create_jenkinsfile(root)
    with baw.git_stash(root, verbose=verbose, venv=venv):
        baw.utils.file_create(
            source,
            content=replaced,
        )
        baw.git_add(root, 'Jenkinsfile')
        failure = baw.git_commit(
            root,
            source=source,
            message='chore(Jenkins): add Jenkinsfile',
            verbose=verbose,
        )
        if failure:
            return failure
    baw.log('Jenkinsfile added')
    return baw.SUCCESS


def upgrade(
    root: str,
    verbose: bool = False,
    venv: bool = False,
):
    source = baw.pipefile.jenkinsfile(root)
    if not os.path.exists(source):
        baw.error(f'Jenkinsfile does not exists: {source}')
        return baw.FAILURE
    replaced = baw.pipefile.upgrade(root, always=True)
    before = baw.utils.file_read(source)
    if replaced.strip() == before.strip():
        baw.log('Jenkinsfile unchanged, skip upgrade')
        return baw.SUCCESS
    with baw.git_stash(root, verbose=verbose, venv=venv):
        baw.utils.file_replace(
            source,
            content=replaced,
        )
        failure = baw.git_commit(
            root,
            source=source,
            message='chore(Jenkins): upgrade Jenkinsfile',
            verbose=verbose,
        )
        if failure:
            return failure
    baw.log('Jenkinsfile upgraded')
    return baw.SUCCESS


def create_jenkinsfile(root: str):
    newest = baw.pipefile.image_newest()
    args = image_args()
    replaced = baw.resources.template_replace(
        root,
        template=baw.resources.JENKINSFILE,
        docker_image_test_name=newest,
        docker_image_test_args=args,
    )
    return replaced


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
    if action in {'image', 'upgrade'}:  # TODO: REMOVE UPGRADE LATER
        return upgrade(
            root,
            verbose=args.get('verbose'),
            venv=args.get('venv'),
        )
    if action == 'library':
        return baw.pipefile.library(
            root,
            verbose=args['verbose'],
        )
    if action == 'test':
        baw.error('not implemented')
    return baw.FAILURE


def extend_cli(parser):
    cli = parser.add_parser('pipe', help='Run pipline task')
    # TODO: USE UPGRADE LATER TO RUN IMAGE AND LIBRARY
    cli.add_argument(
        'action',
        help='manage the jenkins file',
        nargs='?',
        const='test',
        choices='init image library upgrade test'.split(),
    )
    cli.set_defaults(func=run)
