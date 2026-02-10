# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2022-2023 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
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
import baw.gix
import baw.utils


def create(  # pylint:disable=W0613
    root: str,
    name: str = None,
    dockerfile: str = None,
    generate: bool = False,
    install: bool = False,
    verbose: bool = False,
    venv: bool = False,
):
    root = baw.cmd.utils.determine_root(root)
    if dockerfile:
        dockerfile = ensure_dockerfile_path(dockerfile)
        with dockerfile_resolve_gitdescribe(dockerfile) as dock:
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
            install=install,
    ) as path:
        result = baw.dockers.dockfile.build(
            dockerfile=path,
            tagname=tagname,
        )
    return result


def ensure_dockerfile_path(dockerfile):
    dockerfile = baw.forward_slash(dockerfile)
    if '/' not in dockerfile:
        # make absolute?
        dockerfile = os.path.join(os.getcwd(), dockerfile)
    return dockerfile


def dockerfile_build(root, dockerfile, name=None) -> int:
    if not name:
        baw.gix.ensure_git()
        name = baw.gix.describe(root)
    result = baw.dockers.dockfile.build(
        dockerfile=dockerfile,
        tagname=name,
    )
    return result


REFRENCE = '<<GITDESCRIBE>>'

PIPREF = '<<PIPREF>>'

PIPSTABLE = '<<PIPSTABLE>>'


@contextlib.contextmanager
def dockerfile_resolve_gitdescribe(dockerfile: str):
    content = baw.utils.file_read(dockerfile)
    described = describe(dockerfile)
    if no_replace := described == content:  # pylint:disable=W0612
        yield dockerfile
        return
    # tmp file must be in the same path as dockerfile to COPY correctly
    newpath = os.path.join(os.path.split(dockerfile)[0], 'dockertmp')
    baw.utils.file_create(
        newpath,
        content=described,
    )
    yield newpath
    os.unlink(newpath)


def describe(dockerfile: str) -> str:
    content = baw.utils.file_read(dockerfile)
    root = baw.determine_root(dockerfile)
    if REFRENCE in content:
        current = baw.gix.describe(root)
        baw.log(f'REPLACE {REFRENCE} {current} in {dockerfile}')
        content = content.replace(REFRENCE, current)
    if PIPREF in content:
        pipref = baw.cmd.info.pip_version(root, verbose=True)
        baw.log(f'REPLACE {PIPREF} {pipref} in {dockerfile}')
        content = content.replace(PIPREF, pipref)
    if PIPSTABLE in content:
        stable = baw.project.version.determine(root, verbose=True)
        baw.log(f'REPLACE {PIPSTABLE} {stable} in {dockerfile}')
        content = content.replace(PIPSTABLE, stable)
    return content


def create_git_hash(root: str, name=None):  # pylint:disable=W0613
    root = baw.cmd.utils.determine_root(root)
    path = os.path.join(root, 'Dockerfile')
    if not os.path.exists(path):
        baw.error(f'missing Dockerfile: {path}')
        sys.exit(baw.FAILURE)
    tagname = baw.gix.describe(root)
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


def newest(name: str) -> int:
    if baw.dockers.image.check_baseimage(name):
        return baw.FAILURE
    name = name.rsplit(':', maxsplit=1)[0]
    tags = baw.dockers.image.tags(name)
    maxtag = baw.dockers.image.version_max(tags)
    result = f'{name}:{maxtag[0]}'
    baw.log(result)
    return baw.SUCCESS


def upgrade(
    root: str,
    dockerfile: str,
    prerelease: bool = False,
) -> int:
    path = os.path.abspath(dockerfile)
    if not os.path.exists(path):
        baw.error(f'could not upgrade, path does not exists: {path}')
        return baw.FAILURE
    baw.log(f'start upgrading: {path}')
    replaced = baw.dockers.dockfile.docker_image_upgrade(
        path,
        prerelease=prerelease,
    )
    if not replaced:
        baw.log(f'already up-to-date: {path}')
        return baw.SUCCESS
    with baw.git_stash(root):
        baw.utils.file_replace(path, replaced)
        baw.git_commit(
            root,
            path,
            message='chore(upgrade): upgrade images',
        )
        baw.log(f'upgraded: {path}')
    return baw.SUCCESS


def run(args: dict):  # pylint:disable=R0911
    root = baw.cmd.utils.get_root(args)
    action = args.get('action')
    if action == 'create':
        return create(
            root,
            dockerfile=args['dockerfile'],
            name=args['name'],
            generate=args.get('generate'),
            install=args.get('install'),
            verbose=args.get('verbose'),
            venv=args.get('venv'),
        )
    if action == 'upgrade':
        return upgrade(
            dockerfile=args['dockerfile'],
            root=root,
            prerelease=args['prerelease'],
        )
    if action == 'delete':
        baw.error('not implemented')
    if action == 'clean':
        return baw.cmd.image.clean.images()
    if action == 'githash':
        name = args['name']
        baw.log(f'image name: {name}')
        return baw.cmd.image.create_git_hash(
            root,
            name=name,
        )
    if action == 'run':
        name = args['name']
        cmd = args['cmd']
        env = args['env']
        if env:
            env = env.split(';')
        baw.log(f'run name: {name}; cmd: {cmd}; env: {env};')
        return baw.dockers.container.run(
            cmd=cmd,
            image=name,
            environment=env,
            generate=args.get('generate'),
            gitdir=args['gitdir'],
            outdir=args['outdir'],
        )
    if action == 'check':
        name = args['name']
        return baw.dockers.image.exists(name)
    if action == 'newest':
        return newest(args['name'])
    baw.error(f'nothing selected: {args}')
    return baw.FAILURE


CHOICES = 'create upgrade delete clean githash run check newest'.split()


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
        '--env',
        help='overwrite env: PASSWORD=xxx;BASE=hello',
    )
    cli.add_argument(
        '--dockerfile',
        help='use this dockerfile',
    )
    cli.add_argument(
        '--install',
        action='store_true',
        help='run baw install task before',
    )
    cli.add_argument(
        '--generate',
        action='store_true',
        help='generate test data',
    )
    cli.add_argument(
        '--gitdir',
        action='store_true',
        help='copy git dir into docker container',
    )
    cli.add_argument(
        '--outdir',
        action='store_true',
        help='copy /var/outdir from container to this cwd',
    )
    cli.add_argument(
        '--prerelease',
        action='store_true',
        help='use pre-releases while upgrading',
    )
    cli.set_defaults(func=run)
