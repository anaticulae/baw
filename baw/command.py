#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019 by Helmut Konrad Fahrendholz. All rights reserved.
# Tis file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================
"""Define structure of command line interface."""

from argparse import ArgumentParser
from argparse import REMAINDER
from dataclasses import dataclass


@dataclass
class Command:
    shortcut: str
    longcut: str
    message: str
    args: dict = None

    def __iter__(self):
        for item in [self.shortcut, self.longcut, self.message, self.args]:
            yield item


ALL = Command('-a', '--all', 'Clean and run all exepect of publishing')
BUILD = Command('-b', '--build', 'Run build tasks')
CLEAN = Command('-c', '--clean', 'Delete build-, temp- and cache-folder')
CLEAN_VENV = Command('-cv', '--clean_venv', 'Clean virtual environment')
DOC = Command('-d', '--doc', 'Generate documentation with Sphinx')
INIT = Command('-i', '--init',
               'Initialize .baw project - shortcut name [--with_cmd]', {
                   'nargs': REMAINDER,
               })
# run tests, increment version, commit, git tag and push to package index
DOCKER = Command('-do', '--docker', 'Run commands in docker environment')
FORMAT = Command('-f', '--format', 'Format repository')
PUSH = Command('-p', '--publish', 'Push release to repository')
RAW = Command('-ra', '--raw', 'Dont not modify stdout/stderr')
RELEASE = Command(
    '-r', '--release', 'Test and tag commit as new release', {
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
REPORT = Command('-re', '--report', 'Write module status in html report')
RUN = Command('-ru', '--run', 'Run application')
SYNC = Command('-s', '--sync', 'Sync dependencies')
TEST = Command(
    '-t', '--test', 'Run tests and coverage', {
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
VENV = Command('-vi', '--virtual', 'Run commands in virtual environment')
VERBOSE = Command('-ver', '--verbose', 'Extend verbosity of logging')
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
        FORMAT,
        INIT,
        PUSH,
        RAW,
        RELEASE,
        REPORT,
        RUN,
        SYNC,
        TEST,
        VENV,
        VERBOSE,
        VERSION,
    )
    for shortcut, longcut, msg, args in todo:
        shortcuts = (shortcut, longcut)
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
