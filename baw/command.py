#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019 by Helmut Konrad Fahrendholz. All rights reserved.
# Tis file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================
"""Define structure of command line interface."""

from argparse import REMAINDER
from argparse import ArgumentParser
from dataclasses import dataclass


@dataclass
class Command:
    shortcut: str = ''
    longcut: str = ''
    message: str = ''
    args: dict = None

    def __iter__(self):
        for item in [self.shortcut, self.longcut, self.message, self.args]:
            yield item


ALL = Command('-a', '--all', 'Clean and run all expect of publishing')
BUILD = Command('-b', '--build', 'Run build tasks')
CLEAN = Command('-c', '--clean', 'Delete build-, temp- and cache-folder')
CLEAN_VENV = Command(
    longcut='--clean_venv', message='Clean virtual environment')
DOC = Command('-d', '--doc', 'Generate documentation with Sphinx')
IDE = Command(longcut='--ide', message='Generate workspace and open vscode')
INSTALL = Command('-in', '--install', 'Run install task')
INIT = Command('-i', '--init',
               'Initialize .baw project - shortcut name [--with_cmd]', {
                   'nargs': REMAINDER,
               })
# run tests, increment version, commit, git tag and push to package index
DOCKER = Command('-do', '--docker', 'Run commands in docker environment')
FORMAT = Command(longcut='--format', message='Format repository')
PUSH = Command('-p', '--publish', 'Push release to repository')
RAW = Command(longcut='--raw', message='Do not modify stdout/stderr')
RELEASE = Command(
    longcut='--release',
    message='Test, commit and and tag as new release.',
    args={
        'nargs': '?',
        'const': 'auto',
        'choices': [
            'major',
            'minor',
            'patch',
            'noop',
            'auto',
        ],
    })
DROP_RELEASE = Command(longcut='--drop_release', message='Remove last release')
REPORT = Command('-re', '--report', 'Write module status in html report')
RUN = Command('-ru', '--run', 'Run application')
SYNC = Command(
    longcut='--sync',
    message='Sync dependencies',
    args={
        'nargs': '?',
        'const': 'dev',
        'choices': [
            'dev',
            'doc',
            'all',
        ],
    })
UPGRADE = Command(longcut='--upgrade', message='Upgrade requirements.txt')
TEST = Command(
    longcut='--test',
    message='Run tests and coverage',
    args={
        'nargs': '?',
        'action': 'append',
        'choices': [
            'cov',
            'fast',
            'long',
            'pdb',
            'stash',
        ],
    })
VENV = Command(longcut='--virtual', message='Run commands in venv')
# TODO count V to determine verbosity. -VVV
VERBOSE = Command(longcut='--verbose', message='Extend verbosity of logging')
VERSION = Command('-v', '--version', 'Show version of this program')


def create_parser():  # noqa: Z21
    """Create parser out of defined dictonary with command-line-definiton.

    Returns created argparser
    """
    parser = ArgumentParser(prog='baw')
    todo = (
        ALL,
        BUILD,
        CLEAN,
        CLEAN_VENV,
        DOC,
        DOCKER,
        DROP_RELEASE,
        FORMAT,
        IDE,
        INIT,
        INSTALL,
        PUSH,
        RAW,
        RELEASE,
        REPORT,
        RUN,
        SYNC,
        TEST,
        UPGRADE,
        VENV,
        VERBOSE,
        VERSION,
    )
    for shortcut, longcut, msg, args in todo:
        shortcuts = (shortcut, longcut) if shortcut else (longcut,)
        add = parser.add_argument
        if args:
            args['help'] = msg
            add(*shortcuts, **args)
        else:
            add(*shortcuts, action='store_true', help=msg)
    return parser


def parse():
    """Parse arguments from sys-args and return the result as dictonary."""
    parser = create_parser()
    args = vars(parser.parse_args())
    need_help = not any(args.values())
    if need_help:
        parser.print_help()
    return args
