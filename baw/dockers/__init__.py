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

import docker

import baw.cmd.image
import baw.dockers.container
import baw.run


@contextlib.contextmanager
def client():
    base_url = 'http://169.254.149.20:2375'
    result = docker.DockerClient(base_url=base_url)
    yield result
    result.close()


def switch_docker():
    """Use docker environment to run cmd."""
    dockerx = '--docker' in sys.argv
    dockenx = '--docken' in sys.argv
    if not dockerx and not dockenx:
        return baw.run.run_main()
    root = os.getcwd()
    image = baw.cmd.image.tag(
        root,
        generate=dockenx,
    )
    usercmd = prepare_cmd(sys.argv)
    volumes = determine_volumes()
    result = baw.dockers.container.run(
        cmd=usercmd,
        image=image,
        volumes=volumes,
        generate=dockenx,
    )
    return result


def prepare_cmd(argv: list) -> str:
    r"""\
    >>> prepare_cmd(['C:\\usr\\python\\310\\Scripts\\baw', '--docker', 'test', '-n1'])
    'baw test -n1'
    >>> prepare_cmd(['/var/tmp/baw', '--docker', 'test', '-n1'])
    'baw test -n1'
    """
    # use docker to run cmd
    argv = [item for item in argv if item not in '--docker --docken']
    if argv:
        # TODO: REMOVE THIS HACK
        if '\\' in argv[0]:
            # windows
            argv[0] = argv[0].split('\\')[-1]
        else:
            # linux
            argv[0] = argv[0].split('/')[-1]
    usercmd = ' '.join(argv)
    return usercmd


def determine_volumes() -> str:
    # TODO: MOVE TO CONFIG OR SOMETHING ELSE
    return '/var/workdir'
