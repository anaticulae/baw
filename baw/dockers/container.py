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

import baw.dockers
import baw.runtime
import baw.utils


def run(
    cmd,
    image: str,
    volumes: str = None,
    generate: bool = False,
) -> int:
    failure = False
    with baw.dockers.client() as connected:
        container = create(image, cmd, connected, generate)
        try:
            if volumes:
                content = tar_content(os.getcwd())
                container.put_archive(
                    path=volumes,
                    data=content,
                )
            baw.utils.log('start container')
            container.start()
            failure = verify(container)
            baw.utils.log('stop container')
            # TODO: VERIFY THIS
            container.stop()
            baw.utils.log('remove container')
            container.remove()
        except docker.errors.ContainerError as error:
            baw.utils.error(error.stderr.decode('utf8'))
            return baw.utils.FAILURE
    if failure:
        return baw.utils.FAILURE
    return baw.utils.SUCCESS


def create(image: str, cmd: str, connected, generate: bool = False):
    try:
        container = connected.containers.create(
            image,
            command=f'"{cmd}"',
        )
    except docker.errors.ImageNotFound:
        baw_image_create = 'baw image create'
        if generate:
            baw_image_create += ' --generate'
        root = os.getcwd()
        baw.utils.log(baw_image_create)
        completed = baw.runtime.run(
            command=baw_image_create,
            cwd=root,
        )
        if completed.returncode:
            baw.utils.error(f'could not create image: {root}')
            if completed.stdout.strip():
                baw.utils.log(completed.stdout)
            baw.utils.error(completed.stderr)
            sys.exit(baw.utils.FAILURE)
        else:
            baw.utils.log(completed.stdout)
            if completed.stderr.strip():
                baw.utils.error(completed.stderr)
        container = connected.containers.create(
            image,
            command=f'"{cmd}"',
        )
    return container


def verify(container) -> bool:
    failure = False
    out = container.logs(
        stdout=True,
        stderr=True,
        stream=True,
    )
    for line in out:
        decoded = line.decode('utf8')
        # TODO: IMPROVE THIS CHECK
        failure |= '[ERROR] Completed:' in decoded
        baw.utils.log(decoded, end='')
    return failure


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
