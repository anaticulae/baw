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

import docker

import baw.cmd.image
import baw.dockers.container
import baw.run
import baw.utils


@contextlib.contextmanager
def client():
    base_url = 'http://169.254.149.20:2375'
    result = docker.DockerClient(base_url=base_url)
    yield result
    result.close()


def switch_docker():
    """Use docker environment to run cmd."""
    dockerx, dockenx = docker_docken(sys.argv)
    if not dockerx and not dockenx:
        return baw.run.run_main()
    root = os.getcwd()
    image = baw.cmd.image.tag(
        root,
        generate=dockenx,
    )
    environment = parse_env(sys.argv)
    usercmd = prepare_cmd(sys.argv)
    volumes = determine_volumes()
    result = baw.dockers.container.run(
        cmd=usercmd,
        image=image,
        volumes=volumes,
        environment=environment,
        generate=dockenx,
        outdir=True,
    )
    return result


def docker_docken(argv):
    dockerx, dockenx = False, False
    for item in argv:
        # avoid conflicts with --dockerfile for example
        dockerx |= '--docker=' in item or item == '--docker'
        dockenx |= '--docken=' in item or item == '--docken'
    return dockerx, dockenx


def parse_env(argv):
    r"""\
    >>> parse_env(['C:\\usr\\python\\310\\Scripts\\baw', '--docker=PW=10', 'test', 'docs', '--junit_xml=C:/usr/git/var/outdir/test.xml'])
    ['PW=10']
    """
    for item in argv:
        if '--docker=' in item:
            return item.split('--docker=')[1].split(';')
        if '--docken=' in item:
            return item.split('--docken=')[1].split(';')
    return None


def prepare_cmd(argv: list) -> str:
    r"""\
    >>> prepare_cmd(['C:\\usr\\python\\310\\Scripts\\baw', '--docker', 'test', '-n1'])
    'baw test -n1'
    >>> prepare_cmd(['/var/tmp/baw', '--docker', 'test', '-n1'])
    'baw test -n1'
    >>> prepare_cmd(['C:\\usr\\python\\310\\Scripts\\baw', '--docker=PW=10', 'test', 'docs', '--junit_xml=C:/usr/git/var/outdir/test.xml'])
    'baw test docs --junit_xml=/var/outdir/test.xml'
    """
    docki = lambda x: '--docker' in x or '--docken' in x
    # use docker to run cmd
    argv = [item for item in argv if not docki(item)]
    if argv:
        # TODO: REMOVE THIS HACK
        if '\\' in argv[0]:
            # windows
            argv[0] = argv[0].split('\\')[-1]
        else:
            # linux
            argv[0] = argv[0].split('/')[-1]
    usercmd = ' '.join(argv)
    # workaround
    usercmd = baw.utils.fixup_windows(usercmd)
    return usercmd


def determine_volumes() -> str:
    # TODO: MOVE TO CONFIG OR SOMETHING ELSE
    return '/var/workdir'
