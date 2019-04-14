#!/usr/bin/env python
# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019 by Helmut Konrad Fahrendholz. All rights reserved.
# Tis file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

from os import chdir
from os.path import abspath
from os.path import dirname
from os.path import join
from re import search

from baw.utils import UTF8
from setuptools import setup

ROOT = abspath(dirname(__file__))

with open(join(ROOT, 'README.md'), mode='rt', encoding=UTF8) as fp:
    README = fp.read()

with open(join(ROOT, '$_SHORT_$/__init__.py'), mode='rt', encoding=UTF8) as fp:
    VERSION = search(r'__version__ = \'(.*?)\'', fp.read()).group(1)

with open(join(ROOT, "requirements.txt"), mode='rt', encoding=UTF8) as fp:
    INSTALL_REQUIRES = [
        line for line in fp.readlines() if line and '#' not in line
    ]

def datafiles():
    return [('.', [
        'BUGS.md',
        'CHANGELOG.md',
        'README.md',
        'TODO.md',
        'requirements.txt',
    ])]

if __name__ == "__main__":
    # allow setup.py to run from another directory
    chdir(ROOT)
    setup(
        author='Helmut Konrad Fahrendholz',
        author_email='info@checkitweg.de',
        data_files=datafiles(),
        description='$_NAME_$',
        include_package_data=True,
        install_requires=INSTALL_REQUIRES,
        long_description=README,
        name='$_SHORT_$',
        platforms='any',
        setup_requires=[],
        tests_require=[],
        url='https://dev.package.checkitweg.de/$_SHORT_$',
        version=VERSION,
        zip_safe=False,  # create 'zip'-file if True. Don't do it!
        classifiers=[
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: 3.8',
        ],
        packages=[
            '$_SHORT_$',
            $_ENTRY_POINT_PACKAGE_$
        ],
        $_ENTRY_POINT_$
    )
