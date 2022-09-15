# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import os

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
    newest = image_newest()
    replaced = baw.resources.template_replace(
        root,
        template=baw.resources.JENKINSFILE,
        docker_image_test=newest,
    )
    with baw.git.git_stash(root, verbose=verbose, virtual=venv):
        baw.utils.file_create(
            source,
            content=replaced,
        )
        failure = baw.git.commit(
            root,
            source=source,
            message='chore(ci): add Jenkinsfile',
            verbose=verbose,
        )
        if failure:
            return failure
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
    newest = image_newest()
    replaced = baw.resources.template_replace(
        root,
        template=baw.resources.JENKINSFILE,
        docker_image_test=newest,
    )
    before = baw.utils.file_read(source)
    if replaced.strip() == before.strip():
        baw.utils.error('Jenkinsfile unchanged, skip upgrade')
        return baw.utils.FAILURE
    with baw.git.git_stash(root, verbose=verbose, virtual=venv):
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


def jenkinsfile(root: str):
    return os.path.join(root, 'Jenkinsfile')


def image_newest() -> str:
    """\
    >>> image_newest()
    '.../...:...'
    """
    repository = '169.254.149.20:6001'
    imagename = 'test'
    version = '0.3.0'
    result = f'{repository}/{imagename}:{version}'
    return result


def run(args: dict):
    root = baw.run.get_root(args)
    if args.get('action') == 'init':
        return init(
            root,
            verbose=args.get('verbose'),
            venv=args.get('virtual'),
        )
    if args.get('action') == 'upgrade':
        return upgrade(
            root,
            verbose=args.get('verbose'),
            venv=args.get('virtual'),
        )
    if args.get('action') == 'test':
        baw.utils.error('not implemented')
    return baw.utils.FAILURE


def extend_cli(parser):
    cli = parser.add_parser('pipeline', help='Run pipline task')
    cli.add_argument(
        'action',
        help='manage the jenkins file',
        nargs='?',
        const='test',
        choices='init upgrade test'.split(),
    )
    cli.set_defaults(func=run)
