#!/usr/bin/env python
#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019 by Helmut Konrad Fahrendholz. All rights reserved.
# Tis file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================

from os.path import dirname
from os.path import join
from re import search

from setuptools import setup

ROOT = dirname(__file__)
with open(join(ROOT, 'README.md'), 'rt', encoding='utf8') as fp:
    README = fp.read()

with open(join(ROOT, '$_SHORT_$/__init__.py'), 'rt', encoding='utf8') as fp:
    VERSION = search(r'__version__ = \'(.*?)\'', fp.read()).group(1)

if __name__ == "__main__":
    setup(
        name='$_SHORT_$',
        version=VERSION,
        author='Helmut Konrad Fahrendholz',
        author_email='kiwi@derspanier.de',
        description='$_NAME_$',
        long_description=README,
        packages=[
            '$_SHORT_$',
        ],
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
    )
