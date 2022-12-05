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

import baw.cmd.image.clean
import baw.cmd.image.dockerfiles
import baw.cmd.info
import baw.cmd.utils
import baw.config
import baw.dockers
import baw.dockers.container
import baw.dockers.dockfile
import baw.dockers.image
import baw.git
import baw.utils


def create(  # pylint:disable=W0613
    root: str,
    name: str = None,
    dockerfile: str = None,
    generate: bool = False,
    verbose: bool = False,
    venv: bool = False,
):
    root = baw.cmd.utils.determine_root(root)
    if dockerfile:
        dockerfile = baw.utils.forward_slash(dockerfile)
        if '/' not in dockerfile:
            dockerfile = os.path.join(os.getcwd(), dockerfile)
        with dockerfile_resolve_gitdescribe(dockerfile, root) as dock:
            result = dockerfile_build(
                root,
                dockerfile=dock,
                name=name,
            )
        return result
    tagname = tag(root, generate)
    with baw.cmd.image.dockerfiles.generate(
            root,
            inject=generate,
    ) as path:
        result = baw.dockers.dockfile.build(
            dockerfile=path,
            tagname=tagname,
        )
    return result


def dockerfile_build(root, dockerfile, name=None) -> int:
    if not name:
        baw.git.ensure_git()
        name = baw.git.describe(root)
    result = baw.dockers.dockfile.build(
        dockerfile=dockerfile,
        tagname=name,
    )
    return result


REFRENCE = '<<GITDESCRIBE>>'


@contextlib.contextmanager
def dockerfile_resolve_gitdescribe(dockerfile: str, root: str):
    content = baw.utils.file_read(dockerfile)
    if REFRENCE not in content:
        yield dockerfile
        return
    current = baw.git.describe(root)
    baw.utils.log(f'REPLACE {REFRENCE} {current} in {dockerfile}')
    content = content.replace(REFRENCE, current)
    # tmp file must be in the same path as dockerfile to COPY correctly
    newpath = os.path.join(os.path.split(dockerfile)[0], 'dockertmp')
    baw.utils.file_create(
        newpath,
        content=content,
    )
    yield newpath
    os.unlink(newpath)


def create_git_hash(root: str, name=None):  # pylint:disable=W0613
    root = baw.cmd.utils.determine_root(root)
    path = os.path.join(root, 'Dockerfile')
    if not os.path.exists(path):
        baw.utils.error(f'missing Dockerfile: {path}')
        sys.exit(baw.utils.FAILURE)
    tagname = baw.git.describe(root)
    result = baw.dockers.dockfile.build(
        dockerfile=path,
        tagname=tagname,
    )
    return result


TEST_TAG = '/try_'


def tag(root: str, generate: bool = False) -> str:
    """\
    >>> tag(__file__)
    '.../try_baw:...'
    >>> tag(__file__, generate=True)
    '.../try_gen_baw:...'
    """
    root = baw.cmd.utils.determine_root(root)
    testing = baw.config.docker_testing()
    name = baw.cmd.info.requirement_hash(root, verbose=True)
    # use different hash if data generation is enabled
    gen = 'gen_' if generate else ''
    result = f'{testing}{TEST_TAG}{gen}{name}'
    return result


def run(args: dict):
    root = baw.cmd.utils.get_root(args)
    action = args.get('action')
    if action == 'create':
        return create(
            root,
            dockerfile=args['dockerfile'],
            name=args['name'],
            generate=args.get('generate'),
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
        return baw.dockers.container.run(
            cmd=cmd,
            image=name,
            generate=args.get('generate'),
        )
    if action == 'check':
        name = args['name']
        return baw.dockers.image.exists(name)
    return baw.utils.FAILURE


CHOICES = 'create update delete clean githash run check'.split()


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
        help='tag generated image',
    )
    cli.add_argument(
        '--cmd',
        help='run cmd inside container',
    )
    cli.add_argument(
        '--dockerfile',
        help='use this dockerfile',
    )
    cli.add_argument(
        '--generate',
        action='store_true',
        help='generate test data',
    )
    cli.set_defaults(func=run)
