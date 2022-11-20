# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import os
import sys

import docker.errors

import baw.cmd.image.clean
import baw.cmd.image.dockerfiles
import baw.cmd.info
import baw.cmd.utils
import baw.config
import baw.dockers
import baw.runtime
import baw.utils


def create(  # pylint:disable=W0613
    root: str,
    name: str = None,
    dockerfile: str = None,
    verbose: bool = False,
    venv: bool = False,
):
    root = baw.cmd.utils.determine_root(root)
    if dockerfile:
        dockerfile = baw.utils.forward_slash(dockerfile)
        if '/' not in dockerfile:
            dockerfile = os.path.join(os.getcwd(), dockerfile)
        return dockerfile_build(root, dockerfile, name)
    tagname = tag(root)
    with baw.cmd.image.dockerfiles.generate(root) as path:
        result = docker_build(
            dockerfile=path,
            tagname=tagname,
        )
    return result


def dockerfile_build(root, dockerfile, name=None) -> int:
    if not name:
        if not baw.runtime.hasprog('git'):
            baw.utils.error('install git')
            sys.exit(baw.utils.FAILURE)
        name = baw.runtime.run('git describe', cwd=root).stdout.strip()
    result = docker_build(
        dockerfile=dockerfile,
        tagname=name,
    )
    return result


def create_git_hash(root: str, name=None):  # pylint:disable=W0613
    root = baw.cmd.utils.determine_root(root)
    path = os.path.join(root, 'Dockerfile')
    if not os.path.exists(path):
        baw.utils.error(f'missing Dockerfile: {path}')
        sys.exit(baw.utils.FAILURE)
    tagname = baw.runtime.run('git describe', cwd=root).stdout.strip()
    result = docker_build(
        dockerfile=path,
        tagname=tagname,
    )
    return result


def docker_build(dockerfile: str, tagname: str) -> int:
    path = os.path.split(dockerfile)[0]
    try:
        with baw.dockers.client() as client:
            done = client.images.build(
                path=path,
                dockerfile=dockerfile,
                tag=tagname,
            )
            log_service(done)
    except docker.errors.BuildError as error:
        for line in error.build_log:
            baw.utils.error(line)
        return baw.utils.FAILURE
    return baw.utils.SUCCESS


def log_service(done):
    done = done[1]
    for line in done:
        try:
            baw.utils.log(line['stream'], end='')
        except KeyError:
            pass


TEST_TAG = '/try_'


def tag(root: str) -> str:
    """\
    >>> tag(__file__)
    '.../try_baw_...'
    """
    root = baw.cmd.utils.determine_root(root)
    testing = baw.config.docker_testing()
    name = baw.cmd.info.requirement_hash(root, verbose=True)
    result = f'{testing}{TEST_TAG}{name}'
    return result


def check_baseimage(root: str):
    image = baw.cmd.pipeline.docker_image(root)
    with baw.dockers.client() as client:
        try:
            client.images.get(image)
        except docker.errors.ImageNotFound:
            return image
    return None


def run(args: dict):
    root = baw.cmd.utils.get_root(args)
    action = args.get('action')
    if action == 'create':
        return create(
            root,
            dockerfile=args['dockerfile'],
            name=args['name'],
            verbose=args.get('verbose'),
            venv=args.get('venv'),
        )
    if action == 'update':
        baw.utils.error('not implemented')
    if action == 'delete':
        baw.utils.error('not implemented')
    if action == 'clean':
        return baw.cmd.image.clean.images()
    if action == 'githash':
        name = args['name']
        baw.utils.log(f'image name: {name}')
        return baw.cmd.image.create_git_hash(
            root,
            name=name,
        )
    if action == 'run':
        name = args['name']
        cmd = args['cmd']
        baw.utils.log(f'run name: {name}; cmd: {cmd}')
        return baw.dockers.image_run(
            cmd=cmd,
            image=name,
        )
    return baw.utils.FAILURE


CHOICES = 'create update delete clean githash run'.split()


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
        choices=CHOICES,
    )
    cli.add_argument(
        '--name',
        help='add image name',
    )
    cli.add_argument(
        '--cmd',
        help='run cmd inside container',
    )
    cli.add_argument(
        '--dockerfile',
        help='use this dockerfile',
    )
    cli.set_defaults(func=run)
