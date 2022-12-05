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


IMAGE = re.compile(r"image[\:]?[ ]{1,3}'{0,1}((.{5,})/(.{5,})\:(.{3,}))'{0,1}")


def docker_image_upgrade(path: str) -> str:
    r"""\
    >>> import baw; docker_image_upgrade(baw.jenkinsfile(__file__))
    'pipeline{...}\n'
    """
    content = baw.utils.file_read(path)
    parsed = IMAGE.search(content)
    if not parsed:
        return None
    repo, image, _ = parsed[2], parsed[3], parsed[4]
    matched = f'{repo}/{image}'
    tagx = baw.dockers.image.tags(matched)
    maxed = baw.dockers.image.version_max(tagx)
    if not maxed:
        baw.utils.error(f'could not upgrade docker image: {matched}')
        sys.exit(baw.utils.FAILURE)
    version_new = f'{matched}:{maxed[0]}'
    result = content.replace(parsed[1], version_new)
    return result
