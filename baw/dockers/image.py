# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import semver

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


def version_max(taglist, prerelease: bool = False):
    """\
    >>> version_max(['169.254.149.20:6001/arch_python_git_baw:v1.25.0-2-gafbfdd0',
    ... '169.254.149.20:6001/arch_python_git_baw:v1.25.0-1-g7d87b32',
    ... '169.254.149.20:6001/arch_python_git_baw:1.24.1',
    ... '169.254.149.20:6001/arch_python_git_baw:v1.25.0',
    ... '169.254.149.20:6001/arch_python_git_baw:v1.24.1-2-g2d835b6',
    ... ])
    ['v1.25.0', '1.24.1']
    """
    taglist = [item.rsplit(':', 1)[1] for item in taglist]
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
    VersionInfo(major=1, minor=2, patch=3, prerelease=None, build=None)
    """
    if item[0] == 'v':
        item = item[1:]
    parsed = semver.VersionInfo.parse(item)
    return parsed
