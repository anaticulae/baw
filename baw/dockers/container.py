# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2022-2023 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import os

import docker.errors

import baw
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
    outdir: bool = False,
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
            volume_inject(container, volumes, gitdir)
            baw.log('start container')
            container.start()
            failure = verify(container)
            if failure:
                baw.error(cmd)
            if not failure and outdir:
                receive_data(container, outdir)
            baw.log('stop container')
            # TODO: VERIFY THIS
            container.stop()
            baw.log('remove container')
            container.remove()
        except docker.errors.ContainerError as error:
            baw.error(error.stderr.decode('utf8'))
            return baw.FAILURE
    if failure:
        return baw.FAILURE
    return baw.SUCCESS


def volume_inject(container, volumes, gitdir):
    # TODO: GIT DIR IS ALWAYS REQUIRED TO RUN TESTS PROPERLY,
    # THINK ABOUT LATER
    gitdir = True
    if gitdir and not volumes:
        # use default volume
        volumes = baw.dockers.determine_volumes()
    if not volumes:
        return
    content = tar_content(
        content=os.getcwd(),
        git_include=gitdir,
    )
    baw.log(f'put into container: {volumes}')
    container.put_archive(
        path=volumes,
        data=content,
    )


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
        return container
    except docker.errors.ImageNotFound:
        root = os.getcwd()
        build_image(root, generate)
    try:
        container = connected.containers.create(
            image,
            command=f'"{cmd}"',
            environment=environment,
        )
    except docker.errors.ImageNotFound as error:
        # mostly base image is not created
        baw.error(f'could not create container: {image}')
        baw.exitx(error)
    return container


def build_image(root: str, generate: bool = False):
    """Build image if container image does not exists."""
    baw_image_create = 'baw image create'
    if generate:
        baw_image_create += ' --generate'
    baw.log(baw_image_create)
    completed = baw.runtime.run(
        cmd=baw_image_create,
        cwd=root,
        # live=True, # live does not return completed
    )
    if completed.returncode:
        baw.error(f'could not create image: {root}')
        baw.completed(completed)
        baw.exitx()
    else:
        baw.log(completed.stdout)
        if completed.stderr.strip():
            baw.error(completed.stderr)


def receive_data(container, outdir: bool = True):
    outdir: str = outdir if isinstance(outdir, str) else '/var/outdir'
    baw.log('receive data...')
    with baw.utils.tmpdir() as tmp:
        base = os.path.join(tmp, 'content.tar')
        with open(base, 'wb') as fp:
            try:
                bits, stat = container.get_archive(outdir)
            except docker.errors.NotFound:
                baw.error(f'could not find: {outdir}')
                return
            baw.utils.verbose(stat)
            for chunk in bits:
                fp.write(chunk)
        # untar content
        cmd = f'tar -xf {fixup_path(base)}'
        completed = baw.runtime.run(cmd, cwd=os.getcwd())
        if completed.returncode:
            baw.error(f'untar failed: {cmd}')
            baw.completed(completed)
    baw.log('done')


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
        baw.log(decoded, end='')
    return failure


def tar_content(
    content,
    *,
    git_include: bool = False,
) -> str:
    assert os.path.exists(content), str(content)
    if not baw.runtime.hasprog('tar'):
        baw.exitx('tar is not installed, could not tar')
    # tar  cvf abc.tar --exclude-vcs --exclude-vcs-ignores --exclude=build/* .
    with baw.utils.tmpdir() as tmp:
        base = os.path.join(tmp, 'content.tar')
        tar = fixup_path(base)
        content = baw.forward_slash(content, save_newline=False)
        do_not_tar = ignore(git_include)
        cmd = f'tar cvf {tar} {do_not_tar} .'
        baw.log(cmd)
        completed = baw.runtime.run(cmd, content)
        if completed.returncode:
            baw.error(f'tar failed: {cmd}')
            baw.completed(completed)
        content = baw.utils.file_read_binary(base)
    return content


def fixup_path(path: str):
    path = baw.forward_slash(path, save_newline=False)
    path = path.replace('C:/', '/c/')
    return path


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
