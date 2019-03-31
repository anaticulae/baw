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

from os.path import dirname
from os.path import join
from re import search

from setuptools import setup

THIS = dirname(__file__)
with open(join(THIS, 'README.md'), 'rt', encoding='utf8') as fp:
    readme = fp.read()

with open(join(THIS, 'baw/__init__.py'), 'rt', encoding='utf8') as fp:
    version = search(r'__version__ = \'(.*?)\'', fp.read()).group(1)

setup(
    name='baw',
    version=version,
    license='BSD',
    author='Helmut Konrad Fahrendholz',
    author_email='kiwi@derspanier.de',
    description='A simple console-application to manage project complexity',
    long_description=readme,
    packages=['baw'],
    include_package_data=True,
    zip_safe=True,
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
        'console_scripts': [
            'baw = baw.__main__:main',
        ],
    },
)
