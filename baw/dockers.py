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

import baw.config
import baw.run
import baw.utils


@contextlib.contextmanager
def client():
    base_url = 'http://169.254.149.20:2375'
    result = docker.DockerClient(base_url=base_url)
    yield result
    result.close()


def switch_docker():
    """Use docker environment to run command."""
    usedocker = '--docker' in sys.argv
    if not usedocker:
        return baw.run.run_main()
    root = os.getcwd()
    image = baw.config.docker_image(root=root)
    usercmd = prepare_cmd(sys.argv)
    volume = determine_volume()
    cmd = f'docker run --rm {volume} {image} "{usercmd}"'
    completed = baw.runtime.run(cmd, cwd=root)
    if completed.returncode:
        baw.utils.error(cmd)
        if completed.stdout:
            baw.utils.error(completed.stdout)
        baw.utils.error(completed.stderr)
    else:
        baw.utils.log(completed.stdout)
        if completed.stderr:
            baw.utils.error(completed.stderr)
    return completed.returncode


def prepare_cmd(argv: list) -> str:
    r"""\
    >>> prepare_cmd(['C:\\usr\\python\\310\\Scripts\\baw', '--docker', 'test', '-n1'])
    'baw test -n1'
    >>> prepare_cmd(['/var/tmp/baw', '--docker', 'test', '-n1'])
    'baw test -n1'
    """
    # use docker to run cmd
    argv = [item for item in argv if item != '--docker']
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


def determine_volume() -> str:
    # TODO: MOVE TO CONFIG OR SOMETHING ELSE
    volume = f'-v {os.getcwd()}:/var/workdir'
    return volume
