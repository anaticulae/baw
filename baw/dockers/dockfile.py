# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2022-2023 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import os
import re
import sys

import docker.errors
import utilo

import baw
import baw.dockers
import baw.dockers.image
import baw.utils


def build(dockerfile: str, tagname: str) -> int:
    image = parse_baseimage(dockerfile)
    if not image:
        baw.error(f'empty image: {tagname} {dockerfile}')
        return baw.FAILURE
    if not baw.dockers.image.check_baseimage(image):
        baw.error(f'could not find baseimage {image} in {dockerfile}')
        baw.error(parse_baseimage(dockerfile))
        baw.error(utilo.file_read(dockerfile))
        sys.exit(baw.FAILURE)
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
        log_error(error)
        return baw.FAILURE
    return baw.SUCCESS


def log_error(error):
    for line in error.build_log:
        try:
            baw.error(line['stream'].rstrip())
        except KeyError:
            pass


def log_service(done):
    done = done[1]
    for line in done:
        try:
            baw.log(line['stream'], end='')
        except KeyError:
            pass


def parse_baseimage(path: str):
    lines = utilo.file_read(path).splitlines()
    for line in lines:
        if not line:
            continue
        if line.startswith('FROM '):
            return line.split(' ')[1].strip()
    raise ValueError(f'could not find `FROM ` in {path}')


# yapf:disable
IMAGE = re.compile(r"""
    (?:FROM|image)
    [\:]?[\ ]{1,3}
    (?P<quote_opt>'{0,1})
        (((?P<repo>\S{5,})){0,1}(?P<image>\S{5,})\:(?P<version>\S{3,}))
    (?P=quote_opt)
""", flags=re.VERBOSE)
# yapf:enable


def docker_image_upgrade(
    path: str,
    prerelease: bool = False,
    always: bool = False,
) -> str:
    # TODO: ENABLE LATER
    r"""\
    >>> IMAGE.findall('\nFROM ghcr.io/anaticulae/baw:447bf27')
    [('', 'ghcr.io/anaticulae/baw:...', 'ghcr.io/anaticula', 'ghcr.io/anaticula', 'e/baw', '...')]

    # >>> import baw.pipefile;
    # >>> docker_image_upgrade(baw.pipefile.jenkinsfile(__file__), always=True)
    # '@Library(...pipeline{...}\n'
    """
    parsed = base_image(path)
    if not parsed:
        baw.error(f'could not parse: {path}')
        return None
    base, name, version = base_name_version(parsed)
    org = project_org()
    content = utilo.file_read(path)
    result = content
    baw.utils.verbose(f'>>> search: {parsed}')
    tagx = baw.dockers.image.get_tags(image=name, base=base, org=org)
    maxed = baw.dockers.image.version_max(
        tagx,
        prerelease=prerelease,
    )
    if not maxed:
        baw.error(f'could not upgrade docker image: {parsed}')
        sys.exit(baw.FAILURE)
    version_new = parsed.replace(version, maxed[0])
    result = result.replace(parsed, version_new, 1)
    if result == content and not always:
        # nothing changed
        return None
    return result


def project_org():
    """\
    >>> project_org()
    'anaticulae'
    """
    completed = utilo.run('git remote get-url origin')
    stdout: str = completed.stdout.strip()
    # git@github.com:anaticulae/baw.git
    result = stdout.split(':')[1].split('/')[0]
    return result


def base_name_version(line) -> tuple:
    """\
    >>> base_name_version('ghcr.io/anaticulae/baw:447bf27')
    ('ghcr.io/anaticulae', 'baw', '447bf27')
    """
    try:
        base, image = line.rsplit('/', maxsplit=1)
    except ValueError:
        base, image = None, line
    try:
        name, version = image.split(':')
    except ValueError:
        name, version = image, 'latest'
    return base, name, version


def files(path: str):
    """\
    >>> files(__file__)
    ['Dockerfile', 'baw/templates/Dockerfile',...erfile', 'env/test/Dockerfile']
    """
    root = utilo.baw_root(path)
    result = [
        item for item in utilo.file_list(
            root,
            absolute=False,
        ) if utilo.file_name(item).lower() == 'dockerfile'
    ]
    return result


def base_image(path):
    for line in utilo.file_read(path).splitlines():
        line = line.strip()
        # Ignore comments
        if not line or line.startswith("#"):
            continue
        match = re.match(r"^FROM\s+(\S+)", line, re.I)
        if match:
            return match.group(1)
    return None
