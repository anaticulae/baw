#!/usr/bin/env python
#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019-2020 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================
""" Run this setup script to install baw on your local maschine or
virtual environment."""

import collections
import os
import re

import setuptools

THIS = os.path.dirname(__file__)

README = open(
    os.path.join(THIS, 'README.md'),
    mode='r',
    newline='\n',
).read()

VERSION_FILE = open(
    os.path.join(THIS, 'baw/__init__.py'),
    mode='r',
    newline='\n',
).read()

VERSION = re.search(r'__version__ = \'(.*?)\'', VERSION_FILE).group(1)

TEMPLATES = os.path.join(THIS, 'templates')


def data_files():
    collector = collections.defaultdict(list)
    for to_copy in [TEMPLATES]:
        result = []
        for root, _, files in os.walk(to_copy):
            for item in files:
                # if any([test in root + item for test in filter]):
                #     continue
                absolut = os.path.join(root, item)
                common = os.path.commonpath([THIS, to_copy])
                current = absolut.replace(common, '').replace('\\', '/')
                current = current.lstrip('/')
                base, _ = os.path.split(current)
                collector[base].append(current)

    result = [(prefix, current) for prefix, current in collector.items()]

    result.append(('.', [
        'CHANGELOG.md',
        'README.md',
        'requirements-dev.txt',
        'requirements-doc.txt',
    ]))
    return result


if __name__ == "__main__":
    setuptools.setup(
        author='Helmut Konrad Fahrendholz',
        author_email='helmi3000@outlook.com',
        data_files=data_files(),
        description='A simple console-application to manage project complexity.',
        include_package_data=True,
        long_description=README,
        name='baw',
        platforms='any',
        url='https://dev.baw.checkitweg.de',
        version=VERSION,
        zip_safe=False,  # create 'zip'-file if True. Don't do it!
        classifiers=[
            'Programming Language :: Python :: 3.8',
        ],
        entry_points={
            'console_scripts': ['baw = baw:main'],
        },
        packages=[
            'baw',
            'baw.cmd',
            'baw.project',
        ],
    )
