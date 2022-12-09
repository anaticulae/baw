# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import contextlib
import os
import sys

import baw.cmd.info
import baw.cmd.pipeline
import baw.cmd.utils
import baw.pipelinefile
import baw.utils


@contextlib.contextmanager
def generate(root: str, inject: bool = False):
    name = baw.cmd.info.requirement_hash(root, verbose=True)
    name = name.replace(':', '_')
    # use own tmpfile cause TemporaryFile(delete=True) seems no supported
    # at linux, parameter delete is missing.
    config = os.path.join(root, name)
    content = header(root)
    content += baw.utils.NEWLINE * 2
    content += environments(root)
    content += requirements(root)
    content += SYNC
    if inject:
        content += resources(root)
    baw.utils.file_replace(
        config,
        content,
    )
    yield config
    # remove file
    os.unlink(config)


def header(root: str) -> str:
    """\
    >>> header(__file__)
    'FROM .../...'
    """
    root = baw.cmd.utils.determine_root(root)
    if not root:
        sys.exit(baw.utils.FAILURE)
    image = baw.pipelinefile.docker_image(root)
    result = f'FROM {image}'
    return result


FILES = 'requirements.txt requirements.dev requirements.all'.split()


def requirements(root: str) -> str:
    r"""\
    >>> requirements(__file__)
    'COPY requirements.txt /var/workdir/requirements.txt\nCOPY requirements.dev /var/workdir/requirements.dev\n'
    """
    root = baw.cmd.utils.determine_root(root)
    if not root:
        sys.exit(baw.utils.FAILURE)
    result = ''
    for item in FILES:
        path = os.path.join(root, item)
        if not os.path.exists(path):
            continue
        result += f'COPY {item} /var/workdir/{item}{baw.utils.NEWLINE}'
    return result


RESOURCES = ('.baw setup.py '
             'README.md README CHANGELOG.md CHANGELOG'
             ' tests').split()
# RESOURCES += ['.git']


def resources(root: str) -> str:
    r"""Copy resources to generate test data.

    >>> resources(__file__)
    ''
    """
    root = baw.cmd.utils.determine_root(root)
    if not root:
        sys.exit(baw.utils.FAILURE)
    conftest = os.path.join(root, 'tests/conftest.py')
    if not os.path.exists(conftest):
        return ''
    if 'RESOURCES' not in baw.utils.file_read(conftest):
        # resource generator step is not required
        return ''
    result = ''
    for item in baw.config.sources(root) + RESOURCES:
        path = os.path.join(root, item)
        if not os.path.exists(path):
            continue
        if os.path.isfile(path):
            result += f'COPY {item} /var/workdir/{item}{baw.utils.NEWLINE}'
        else:
            result += f'COPY {item}/ /var/workdir/{item}/{baw.utils.NEWLINE}'
    result += GENERATE
    return result


def environments(root: str) -> str:
    r"""\
    ENV RUNJOB="exit 1"
    >>> environments(__file__) # '...ENV GITEA_SERVER_URL=...\n'
    ''
    """
    root = baw.cmd.utils.determine_root(root)
    if not root:
        sys.exit(baw.utils.FAILURE)
    env = baw.pipelinefile.docker_env(root)
    if not env:
        return ''
    result = ''
    for key, value in env.items():
        result += f'ENV {key}="{value}"{baw.utils.NEWLINE}'
    return result


SYNC = """
RUN baw sync all
"""

GENERATE = """
# ensure to run with maximum computing power
ENV JENKINS_HOME="TRUE"
RUN baw generate all
"""
