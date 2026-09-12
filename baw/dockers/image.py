# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2022-2023 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import sys

import docker.errors
import requests
import semver
import utilo

import baw.dockers


def tags(matched: str) -> list:
    matched = f'{matched}:'
    collected = []
    with baw.dockers.client() as connected:
        images = connected.images.list()
        for item in images:
            if not item.tags:
                continue
            if not any(matched in item for item in item.tags):
                continue
            collected.extend(item.tags)
    return collected


def get_tags(image, base=None, org=None, limit=10, timeout=5):
    """\
    >>> len(get_tags('alpine')) > 5
    True
    """
    if base is None:
        if "/" not in image:
            image = f"library/{image}"
        url = f"https://hub.docker.com/v2/repositories/{image}/tags"
    else:
        url = f"https://api.github.com/repos/{org}/{image}/tags"
    utilo.debug(url)
    try:
        response = requests.get(
            url,
            params={"per_page": limit},
            timeout=timeout,
        )
    except requests.RequestException as error:
        utilo.error('could not connect to docker repository')
        utilo.exitx(error)
    try:
        response.raise_for_status()
    except requests.RequestException as error:
        utilo.exitx(error)
    tags_json = response.json()
    if base is None:
        result = [tag["name"] for tag in tags_json['results']]
    else:
        result = [tag["name"] for tag in tags_json]
    result = [item for item in result if is_tag_valid(item)]
    return result


def is_tag_valid(item) -> bool:
    """\
    >>> is_tag_valid('1.2.')
    True
    >>> is_tag_valid('1')
    True
    >>> is_tag_valid('20230612')
    True
    >>> is_tag_valid('latest')
    False
    >>> is_tag_valid('edge')
    False
    """
    if utilo.isnumber(item):
        return True
    if item.count('.') in {1, 2}:
        return True
    return False


def exists(name: str) -> int:
    utilo.log(f'check: {name}')
    if check_baseimage(name):
        baw.error(f'could not find image: {name}')
        sys.exit(baw.FAILURE)
    utilo.log('OK')
    return baw.SUCCESS


def version_max(taglist, prerelease: bool = False):
    """\
    >>> version_max(['169.254.149.20:6001/arch_python_git_baw:v1.25.0-2-gafbfdd0',
    ... '169.254.149.20:6001/arch_python_git_baw:v1.25.0-1-g7d87b32',
    ... '169.254.149.20:6001/arch_python_git_baw:1.24.1',
    ... '169.254.149.20:6001/arch_python_git_baw:v1.25.0',
    ... '169.254.149.20:6001/arch_python_git_baw:v1.24.1-2-g2d835b6',
    ... ])
    ['v1.25.0', '1.24.1']
    >>> version_max(['169.254.149.20:6001/arch_python_git_baw:v1.25.0-2-gafbfdd0',
    ... '169.254.149.20:6001/arch_python_git_baw:v1.25.0-1-g7d87b32',
    ... '169.254.149.20:6001/arch_python_git_baw:1.24.1',
    ... '169.254.149.20:6001/arch_python_git_baw:v1.25.0',
    ... '169.254.149.20:6001/arch_python_git_baw:v1.24.1-2-g2d835b6',
    ... ], prerelease=True)
    ['v1.25.0', 'v1.25.0-2-gafbfdd0', 'v1.25.0-1-g7d87b32', '1.24.1', 'v1.24.1-2-g2d835b6']
    """
    taglist = [
        item.rsplit(':', 1)[1] if ':' in item else item for item in taglist
    ]
    if not prerelease:
        # remove pre releases
        taglist = [item for item in taglist if '-' not in item]
    taglist.sort(
        key=parse,
        reverse=True,
    )
    return taglist


def parse(item: str):
    """\
    >>> parse('v1.2.3')
    Version(major=1, minor=2, patch=3, prerelease=None, build=None)
    >>> parse('latest')
    Version(major=0, minor=0, patch=0, prerelease=None, build=None)
    """
    if item[0] == 'v':
        item = item[1:]
    try:
        parsed = semver.Version.parse(item)
    except ValueError:
        # TODO: CHANGE LATER
        parsed = semver.Version.parse('0.0.0')
    return parsed


def check_baseimage(image: str) -> bool:
    with baw.dockers.client() as client:
        try:
            client.images.get(image)
        except docker.errors.ImageNotFound:
            return False
    return True
