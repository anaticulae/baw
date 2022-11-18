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
import docker.errors

import baw.config
import baw.run
import baw.utils


@contextlib.contextmanager
def client():
    base_url = 'http://169.254.149.20:2375'
    result = docker.DockerClient(base_url=base_url)
    yield result
    result.close()


def image_run(  # pylint:disable=W0613
    cmd,
    image: str,
    volume: str = '/var/workspace/',
) -> int:
    with client() as connected:
        try:
            result = connected.containers.run(
                image,
                command=f'"{cmd}"',
                stderr=True,
                remove=True,
            )
        except docker.errors.ContainerError as error:
            baw.utils.error(error.stderr.decode('utf8'))
            return baw.utils.FAILURE
        else:
            log = result.decode('utf8')
            baw.utils.log(log)
        return baw.utils.SUCCESS


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


IGNORE = '--exclude=build/* --exclude=.git/*'
IGNORE += '--one-file-system -P '


def tar_content(content) -> str:
    assert os.path.exists(content), str(content)
    if not baw.runtime.hasprog('tar'):
        baw.utils.error('tar is not installed, could not tar')
        sys.exit(baw.utils.FAILURE)
    # tar  cvf abc.tar --exclude-vcs --exclude-vcs-ignores --exclude=build/* .
    with baw.utils.tmpdir() as tmp:
        base = os.path.join(tmp, 'content.tar')
        tar = baw.utils.forward_slash(base, save_newline=False)
        tar = tar.replace('C:/', '/c/')
        content = baw.utils.forward_slash(content, save_newline=False)
        cmd = f'tar cvf {tar} {IGNORE} .'
        completed = baw.runtime.run(cmd, content)
        if completed.returncode:
            baw.utils.error(f'tar failed: {cmd}')
            if completed.stdout:
                baw.utils.error(completed.stdout)
            if completed.stdout:
                baw.utils.error(completed.stderr)
        content = baw.utils.file_read_binary(base)
    return content
