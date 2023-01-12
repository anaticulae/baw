# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2022-2023 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
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
    environment: list = None,
    *,
    generate: bool = False,
    gitdir: bool = False,
) -> int:
    failure = False
    with baw.dockers.client() as connected:
        container = create(
            image,
            cmd,
            connected,
            environment=environment,
            generate=generate,
        )
        try:
            # TODO: GIT DIR IS ALWAYS REQUIRED TO RUN TESTS PROPERLY,
            # THINK ABOUT LATER
            gitdir = True
            if gitdir and not volumes:
                # use default volume
                volumes = baw.dockers.determine_volumes()
            if volumes:
                content = tar_content(content=os.getcwd(), git_include=gitdir)
                container.put_archive(
                    path=volumes,
                    data=content,
                )
            baw.utils.log('start container')
            container.start()
            failure = verify(container)
            if failure:
                baw.utils.error(cmd)
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


def create(
    image: str,
    cmd: str,
    connected,
    environment: list = None,
    generate: bool = False,
):
    try:
        container = connected.containers.create(
            image,
            command=f'"{cmd}"',
            environment=environment,
        )
    except docker.errors.ImageNotFound:
        baw_image_create = 'baw image create'
        if generate:
            baw_image_create += ' --generate'
        root = os.getcwd()
        baw.utils.log(baw_image_create)
        completed = baw.runtime.run(
            cmd=baw_image_create,
            cwd=root,
            # live=True, # live does not return completed
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
            environment=environment,
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


def tar_content(
    content,
    *,
    git_include: bool = False,
) -> str:
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
        do_not_tar = ignore(git_include)
        cmd = f'tar cvf {tar} {do_not_tar} .'
        completed = baw.runtime.run(cmd, content)
        if completed.returncode:
            baw.utils.error(f'tar failed: {cmd}')
            if completed.stdout:
                baw.utils.error(completed.stdout)
            if completed.stdout:
                baw.utils.error(completed.stderr)
        content = baw.utils.file_read_binary(base)
    return content


def ignore(git_include: bool = False):
    """\
    >>> ignore()
    '--exclude=build/* --exclude=.git/* --one-file-system -P '
    >>> ignore(git_include=True)
    '--exclude=build/* --one-file-system -P '
    """
    result = '--exclude=build/* '
    if not git_include:
        result += '--exclude=.git/* '
    result += '--one-file-system -P '
    return result
