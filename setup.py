#!/usr/bin/env python
###############################################################################
#                                Kiwi Project                                 #
#                                    2019                                     #
#                          Helmut Konrad Fahrendholz                          #
#                             kiwi@derspanier.de                              #
###############################################################################

import io
from collections import OrderedDict
from re import search

from setuptools import setup

with io.open('README.md', 'rt', encoding='utf8') as fp:
    readme = fp.read()

with io.open('baw/__init__.py', 'rt', encoding='utf8') as fp:
    version = search(r'__version__ = \'(.*?)\'', fp.read()).group(1)

setup(
    name='baw',
    version=version,
    project_urls=OrderedDict((
        # ('Documentation', 'http://flask.pocoo.org/docs/'),
    )),
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
