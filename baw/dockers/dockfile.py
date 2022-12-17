# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import os
import re
import sys

import docker.errors

import baw.dockers
import baw.dockers.image
import baw.utils


def build(dockerfile: str, tagname: str) -> int:
    image = parse_baseimage(dockerfile)
    if baw.dockers.image.check_baseimage(image):
        baw.utils.error(f'could not find baseimage {image} in {dockerfile}')
        baw.utils.error(parse_baseimage(dockerfile))
        baw.utils.error(baw.utils.file_read(dockerfile))
        sys.exit(baw.utils.FAILURE)
    path = os.path.split(dockerfile)[0]
    try:
        with baw.dockers.client() as client:
            done = client.images.build(
                path=path,
                dockerfile=dockerfile,
                tag=tagname,
            )
            log_service(done)
    except docker.errors.BuildError as error:
        for line in error.build_log:
            baw.utils.error(line)
        return baw.utils.FAILURE
    return baw.utils.SUCCESS


def log_service(done):
    done = done[1]
    for line in done:
        try:
            baw.utils.log(line['stream'], end='')
        except KeyError:
            pass


def parse_baseimage(path: str):
    lines = baw.utils.file_read(path).splitlines()
    for line in lines:
        if line.startswith('FROM '):
            return line.split(' ')[1].strip()
    raise ValueError(f'could not find `FROM ` in {path}')


# yapf:disable
IMAGE = re.compile(r"""
    image
    [\:]?[\ ]{1,3}
    (?P<quote_opt>'{0,1})
        ((?P<repo>\S{5,})/(?P<image>\S{5,})\:(?P<version>\S{3,}))
    (?P=quote_opt)
""", flags=re.VERBOSE)
# yapf:enable


def docker_image_upgrade(
    path: str,
    prerelease: bool = False,
    always: bool = False,
) -> str:
    r"""\
    >>> import baw;
    >>> docker_image_upgrade(baw.jenkinsfile(__file__), always=True)
    'pipeline{...}\n'
    """
    content = baw.utils.file_read(path)
    parsed = IMAGE.findall(content)
    if not parsed:
        return None
    result = content
    for find in parsed:
        # ("'", '169.254.149.20:6001/arch_python_git_baw:v1.20.0',
        # '169.254.149.20:6001', 'arch_python_git_baw', 'v1.20.0')
        repo, image = find[2], find[3]
        matched = f'{repo}/{image}'
        tagx = baw.dockers.image.tags(matched)
        maxed = baw.dockers.image.version_max(
            tagx,
            prerelease=prerelease,
        )
        if not maxed:
            baw.utils.error(f'could not upgrade docker image: {matched}')
            sys.exit(baw.utils.FAILURE)
        version_new = f'{matched}:{maxed[0]}'
        result = result.replace(find[1], version_new, 1)
    if result == content and not always:
        # nothing changed
        return None
    return result
