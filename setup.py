#!/usr/bin/env python
#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019-2023 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================
"""Run this setup script to install baw on your local machine or
venv environment."""

import os
import re
import subprocess
import sys

import setuptools

ROOT = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(ROOT, 'README'), 'rt', encoding='utf8') as fp:
    README = fp.read()
with open(os.path.join(ROOT, 'baw/__init__.py'), 'rt', encoding='utf8') as fp:
    VERSION = re.search(r'__version__ = \'(.*?)\'', fp.read()).group(1)
with open(os.path.join(ROOT, "requirements.txt"), encoding='utf8') as fp:
    REQUIRES = [line for line in fp.readlines() if line and '#' not in line]
with open(os.path.join(ROOT, "LICENCE"), encoding='utf8') as fp:
    LICENCE = fp.read()

CLASSIFIERS = [
    'Programming Language :: Python :: 3.10',
    'Programming Language :: Python :: 3.11',
    'Programming Language :: Python :: 3.12',
    'Programming Language :: Python :: 3.13',
    'Programming Language :: Python :: 3.14',
]
PACKAGES = [
    'baw',
    'baw.archive',
    'baw.cmd',
    'baw.cmd.image',
    'baw.cmd.release',
    'baw.cmd.test',
    'baw.config',
    'baw.dockers',
    'baw.project',
    'baw.requirements',
    'baw.small',
    'baw.sync',
    'baw.templates',
    'baw.templates.docs',
]
ENTRY_POINTS = dict(console_scripts=[
    'baw = baw.__main__:run',
    'baw_cprofile_show = baw.small.cprofile:main',
    'baw_profile = baw.small.profile:main',
    'baw_regen = baw.small.regen:main',
    'baw_semantic_release = baw.small.version:main',
    'baw_single = baw.small.single:main',
])


def prerelease() -> str:
    """Compatible version tag with `git describe` with
       pip install version scheme.
    """
    try:
        completed = subprocess.run(
            'git describe'.split(),
            check=True,
            capture_output=True,
        )
    except subprocess.CalledProcessError:
        print('install git, no prerelease', file=sys.stderr)
        return None
    value = completed.stdout.strip().decode('utf8')
    # transform v2.40.1-5-gc1b4bee to 2.40.1.post5+gc1b4bee
    value = value[1:]
    value = value.replace('-', '.post', 1)
    value = value.replace('-g', '+g', 1)
    return value


def versions() -> str:
    if pre := prerelease():
        return pre
    return VERSION


if __name__ == "__main__":
    setuptools.setup(
        name='baw',
        author='Helmut Konrad Schewe',
        author_email='helmutus@outlook.com',
        description='A simple console-application to manage project complexity.',
        classifiers=CLASSIFIERS,
        entry_points=ENTRY_POINTS,
        include_package_data=True,
        install_requires=REQUIRES,
        licence=LICENCE,
        long_description=README,
        packages=PACKAGES,
        platforms='any',
        url='https://github.com/anaticulae/baw',
        version=versions(),
        zip_safe=False,  # create 'zip'-file if True. Don't do it!
    )
