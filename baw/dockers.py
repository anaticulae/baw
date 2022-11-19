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

import baw.cmd.image
import baw.config
import baw.run
import baw.utils


@contextlib.contextmanager
def client():
    base_url = 'http://169.254.149.20:2375'
    result = docker.DockerClient(base_url=base_url)
    yield result
    result.close()


def image_run(
    cmd,
    image: str,
    volumes: str = '/var/workdir',
) -> int:
    with client() as connected:
        try:
            container = connected.containers.create(
                image,
                command=f'"{cmd}"',
            )
            content = tar_content(os.getcwd())
            container.put_archive(
                path=volumes,
                data=content,
            )
            baw.utils.log('start container')
            container.start()
            out = container.logs(stdout=True, stderr=True, stream=True)
            for line in out:
                baw.utils.log(line.decode('utf8'), end='')
            # TODO: VERIFY THIS
            container.stop()
            container.remove()
        except docker.errors.ContainerError as error:
            baw.utils.error(error.stderr.decode('utf8'))
            return baw.utils.FAILURE
        return baw.utils.SUCCESS


def switch_docker():
    """Use docker environment to run command."""
    usedocker = '--docker' in sys.argv
    if not usedocker:
        return baw.run.run_main()
    root = os.getcwd()
    image = baw.cmd.image.tag(root)
    usercmd = prepare_cmd(sys.argv)
    volumes = determine_volumes()
    result = image_run(
        cmd=usercmd,
        image=image,
        volumes=volumes,
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


def determine_volumes() -> str:
    # TODO: MOVE TO CONFIG OR SOMETHING ELSE
    return '/var/workdir'


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
