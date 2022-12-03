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

import baw.config
import baw.dockers.image
import baw.git
import baw.project
import baw.runtime
import baw.utils


def docker_image_upgrade(root: str) -> str:
    """\
    >>> docker_image_upgrade(__file__)
    '.../arch_python_git_baw:v...'
    """
    jenkins = baw.utils.file_read(jenkinsfile(root))
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


ENVIRONMENT = re.compile(r'environment\{(.{5,}?)\}', flags=re.DOTALL)


def docker_env(root: str) -> dict:
    """\
    >>> import baw.project; docker_env(baw.project.determine_root(__file__)) is None
    True
    """
    path = jenkinsfile(root)
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


# @Library('caelum@d84cdc61c790353ffe9a62d9af6b1ac2f8c27d4d') _
LIBRARY = "@Library('caelum@"
LIBRARY_END = "') _"


def library(root: str, verbose: False):
    path = jenkinsfile(root)
    if not os.path.exists(path):
        baw.utils.error(f'could not find Jenkinsfile: {path}')
        return baw.utils.FAILURE
    current = baw.utils.file_read(path)
    newest = library_newest(verbose=verbose)
    if newest in current:
        baw.utils.error(f'already newst caelum: {newest}')
        return baw.utils.FAILURE
    init_lib = LIBRARY not in current
    header = f'{LIBRARY}{newest}{LIBRARY_END}\n\n'
    if init_lib:
        baw.utils.log(f'caelum library: init {newest}')
        current = header + current
    else:
        baw.utils.log(f'caelum library: upgrade {newest}')
        # remove old library
        _, current = current.split(LIBRARY_END, 1)
        # append new library
        current = header + current.lstrip()
    baw.utils.file_replace(
        path,
        content=current,
    )
    msg = 'chore(Jenkins): upgrade pipe library'
    if init_lib:
        msg = 'chore(Jenkins): add pipe library'
    baw.git.commit(root, source=path, message=msg)
    return baw.utils.SUCCESS


def image_newest() -> str:
    """\
    >>> image_newest()
    '.../...:...'
    """
    repository = os.environ.get(
        'BAW_PIPELINE_REPO',
        '169.254.149.20:6001',
    )
    imagename = os.environ.get(
        'BAW_PIPELINE_NAME',
        'arch_python_baw',
    )
    version = os.environ.get(
        'BAW_PIPELINE_VERSION',
        '0.15.1',
    )
    result = f'{repository}/{imagename}:{version}'
    return result


def library_newest(verbose: bool = False) -> str:
    base = baw.config.gitea_server()
    user = 'caelum'
    repo = 'jenkins'
    branch = 'master'
    url = f'{base}/api/v1/repos/{user}/{repo}/branches/{branch}'
    cmd = f'curl {url}'
    if verbose:
        baw.utils.log(cmd)
    completed = baw.runtime.run(cmd=cmd, cwd=os.getcwd())
    if baw.config.testing():
        return 'd84cdc61c790353ffe9a62d9af6b1ac2f8c27d4d'
    if completed.returncode:
        baw.utils.error(completed)
        sys.exit(completed.returncode)
    stdout = completed.stdout
    # "id":"d84cdc61c790353ffe9a62d9af6b1ac2f8c27d4d"
    matched = re.search(r'"id"\:"(\w{40})"', stdout)
    commit = matched[1]
    return commit
