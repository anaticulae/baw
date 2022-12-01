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

import baw.project
import baw.utils

IMAGE = re.compile(r"image[ ]'((.{5,})/(.{5,})\:(.{3,}))'")


def docker_image(root: str) -> str:
    """Parse dockerimage from Jenkinsfile.

    image '169.254.149.20:6001/arch_python_git_baw:0.15.0'

    >>> import baw.project
    >>> docker_image(baw.project.determine_root(__file__))
    '...'
    """
    path = jenkinsfile(root)
    if not os.path.exists(path):
        baw.utils.error(f'require Jenkinsfile in {root}')
        sys.exit(baw.utils.FAILURE)
    jenkins = baw.utils.file_read(path)
    parsed = IMAGE.search(jenkins)
    if not parsed:
        return None
    result = parsed[1]
    return result


def docker_image_upgrade(root: str) -> str:
    """\
    >>> docker_image_upgrade(__file__)
    '.../arch_python_git_baw:v...'
    """
    jenkins = baw.utils.file_read(baw.jenkins.jenkinsfile(root))
    parsed = IMAGE.search(jenkins)
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
    result = jenkins.replace(parsed[1], version_new)
    return result


ENVIRONMENT = re.compile(r'environment\{(.{5,}?)\}', flags=re.DOTALL)


def docker_env(root: str) -> dict:
    """\
    >>> import baw.project; docker_env(baw.project.determine_root(__file__)) is None
    True
    """
    path = baw.jenkins.jenkinsfile(root)
    if not os.path.exists(path):
        baw.utils.error(f'require Jenkinsfile in {root}')
        sys.exit(baw.utils.FAILURE)
    jenkins = baw.utils.file_read(path)
    parsed = ENVIRONMENT.search(jenkins)
    if not parsed:
        return None
    content = parsed[1]
    result = {}
    for line in content.splitlines():
        line = line.strip()
        if not line:
            continue
        if line[0:2] == '//':
            continue
        try:
            value, var = line.split('=', maxsplit=1)
        except ValueError:
            baw.utils.error(f'could not parse: {line}')
            continue
        result[value.strip()] = var.strip("' ")
    return result


def jenkinsfile(root: str):
    """\
    >>> jenkinsfile(__file__)
    '...Jenkinsfile'
    """
    root = baw.project.determine_root(root)
    return os.path.join(root, 'Jenkinsfile')
