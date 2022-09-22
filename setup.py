#!/usr/bin/env python
#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019-2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================
""" Run this setup script to install baw on your local maschine or
venv environment."""

import os
import re

import setuptools

ROOT = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(ROOT, 'README.md'), 'rt', encoding='utf8') as fp:
    README = fp.read()
with open(os.path.join(ROOT, 'baw/__init__.py'), 'rt', encoding='utf8') as fp:
    VERSION = re.search(r'__version__ = \'(.*?)\'', fp.read()).group(1)
with open(os.path.join(ROOT, "requirements.txt"), encoding='utf8') as fp:
    REQUIRES = [line for line in fp.readlines() if line and '#' not in line]

if __name__ == "__main__":
    setuptools.setup(
        author='Helmut Konrad Fahrendholz',
        author_email='helmi3000@outlook.com',
        description='A simple console-application to manage project complexity.',
        include_package_data=True,
        install_requires=REQUIRES,
        long_description=README,
        name='baw',
        platforms='any',
        url='https://dev.baw.checkitweg.de',
        version=VERSION,
        zip_safe=False,  # create 'zip'-file if True. Don't do it!
        classifiers=[
            'Programming Language :: Python :: 3.8',
        ],
        packages=[
            'baw',
            'baw.archive',
            'baw.cmd',
            'baw.project',
            'baw.requires',
            'baw.small',
            'baw.templates',
            'baw.templates.docs',
        ],
        entry_points={
            'console_scripts': [
                'baw = baw.run:main',
                'baw_cprofile_show = baw.small.cprofile:main',
                'baw_profile = baw.small.profile:main',
                'baw_regen = baw.small.regen:main',
                'baw_single = baw.small.single:main',
                'baw_semantic_release = baw.small.version:main',
            ],
        },
    )
