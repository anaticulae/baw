#!/usr/bin/env python
#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019 by Helmut Konrad Fahrendholz. All rights reserved.
# Tis file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================
""" Run this setup script to install baw on your local maschine or virtual
environment.
"""

from collections import defaultdict
from os import walk
from os.path import commonpath
from os.path import dirname
from os.path import join
from os.path import split
from re import search

from setuptools import setup

from baw.utils import file_read
from baw.utils import ROOT

THIS = dirname(__file__)
README = file_read(join(THIS, 'README.md'))

VERSION_FILE = file_read(join(THIS, 'baw/__init__.py'))
VERSION = search(r'__version__ = \'(.*?)\'', VERSION_FILE).group(1)

TEMPLATES = join(THIS, 'templates')


def data_files():
    collector = defaultdict(list)
    for to_copy in [TEMPLATES]:
        result = []
        for root, _, files in walk(to_copy):
            for item in files:
                # if any([test in root + item for test in filter]):
                #     continue
                absolut = join(root, item)
                common = commonpath([THIS, to_copy])
                current = absolut.replace(common, '').replace('\\', '/')
                current = current.lstrip('/')
                base, _ = split(current)
                collector[base].append(current)

    result = [(prefix, current) for prefix, current in collector.items()]

    result.append(('.', [
        'CHANGELOG.md',
        'README.md',
        'requirements-dev.txt',
    ]))
    return result


if __name__ == "__main__":
    setup(
        author='Helmut Konrad Fahrendholz',
        author_email='kiwi@derspanier.de',
        data_files=data_files(),
        description='A simple console-application to manage project complexity',
        include_package_data=True,
        install_requires=[],
        license='BSD',
        long_description=README,
        name='baw',
        platforms='any',
        setup_requires=[],
        tests_require=[],
        url='https://dev.baw.checkitweg.de',
        version=VERSION,
        zip_safe=False,  # create 'zip'-file if True. Don't do it!
        classifiers=[
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
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
