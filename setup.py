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

from baw.utils import ROOT
from setuptools import setup

THIS = dirname(__file__)
with open(join(THIS, 'README.md'), 'rt', encoding='utf8') as fp:
    README = fp.read()

with open(join(THIS, 'baw/__init__.py'), 'rt', encoding='utf8') as fp:
    VERSION = search(r'__version__ = \'(.*?)\'', fp.read()).group(1)

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
                # result.append(current)
        # data_files.append((root_copy, result))
    result = []
    for prefix, current in collector.items():
        result.append((prefix, current))

    result.append(('.', [
        'CHANGELOG.md',
        'README.md',
        'requirements-dev.txt',
    ]))
    return result


print(data_files())

if __name__ == "__main__":
    setup(
        name='baw',
        version=VERSION,
        license='BSD',
        author='Helmut Konrad Fahrendholz',
        author_email='kiwi@derspanier.de',
        description='A simple console-application to manage project complexity',
        long_description=README,
        packages=[
            'baw',
            'baw.cmd',
            'baw.project',
        ],
        data_files=data_files(),
        include_package_data=True,
        zip_safe=False,  # create 'zip'-file if True. Don't do it!
        platforms='any',
        install_requires=[],
        setup_requires=[],
        tests_require=[],
        classifiers=[
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: 3.8',
        ],
        entry_points={
            'console_scripts': ['baw = baw:main'],
        },
    )

    # packages=find_packages(exclude=['tests', 'scrips']),
    # package_dir={'': '.'},
