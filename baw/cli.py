#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019-2021 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================
"""Define structure of command line interface."""

import argparse
import dataclasses
import sys


@dataclasses.dataclass
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
DOC = Command(longcut='--doc', message='Generate documentation with Sphinx')
IDE = Command(
    longcut='--ide',
    message='generate workspace and open vscode',
    args={
        'nargs': '?',
        'dest': 'ide',
        'action': 'append',
    })
BISECT = Command(
    longcut='--bisect',
    message='run git bisect',
    args={
        'nargs': '+',
        'dest': 'commits',
    })
LINT = Command(
    longcut='--lint',
    message='Run statical code analysis.',
    args={
        'nargs': '?',
        'const': 'minimal',
        'choices': [
            'all',
            'minimal',
            'todo',
        ],
    })
INSTALL = Command(longcut='--install', message='Run install task')
# run tests, increment version, commit, git tag and push to package index
DOCKER = Command(longcut='--docker', message='Use docker environment')
FORMAT = Command(longcut='--format', message='Format repository')
PUSH = Command(longcut='--publish', message='Push release to repository')
RAW = Command(longcut='--raw', message='Do not modify stdout/stderr')
OPEN = Command(longcut='--open', message='Open current folder in explorer')
RELEASE = Command(
    longcut='--release',
    message='Test, commit and tag as new release.',
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
DROP_RELEASE = Command(longcut='--drop', message='Remove last release')
REPORT = Command('-re', '--report', 'Write module status in html report')
RUN = Command('-ru', '--run', 'Run application')
UPGRADE = Command(
    longcut='--upgrade',
    args={
        'nargs': '?',
        'const': 'requirements',
        'choices': [
            'dev',
            'requirements',
            'extra',
            'all',
        ],
    },
    message='Upgrade requirements.txt/dev/ext',
)
NOTESTS = Command(
    longcut='--notests',
    message='Do not run test suite',
)
TEST_CONFIG = Command(
    longcut='--testconfig',
    message='parametrize test command',
    args={
        'dest': 'testconfig',
        'nargs': '+'
    })

VENV = Command(longcut='--virtual', message='Run commands in venv')
# TODO count V to determine verbosity. -VVV
VERBOSE = Command(longcut='--verbose', message='Extend verbosity of logging')
VERSION = Command('-v', '--version', 'Show version of this program')


def create_parser():  # noqa: Z21
    """Create parser out of defined dictionary with command-line-definition.

    Returns created argparser
    """
    parser = argparse.ArgumentParser(prog='baw')
    todo = (
        ALL,
        BISECT,
        BUILD,
        DOC,
        DOCKER,
        DROP_RELEASE,
        FORMAT,
        IDE,
        INSTALL,
        LINT,
        NOTESTS,
        OPEN,
        PUSH,
        RAW,
        RELEASE,
        REPORT,
        RUN,
        TEST_CONFIG,
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

    commands = parser.add_subparsers()
    add_clean_options(commands)
    add_init_options(commands)
    add_plan_options(commands)
    add_sync_options(commands)
    add_test_options(commands)
    return parser


def add_clean_options(parser):
    plan = parser.add_parser('clean', help='remove generated content')
    plan.add_argument(
        'clean',
        help='remove different type of content',
        choices=['all', 'docs', 'resources', 'tests', 'tmp', 'venv'],
        nargs='?',
        default='tests',
    )


def add_sync_options(parser):
    sync = parser.add_parser('sync', help='Synchronize project requirements')
    sync.add_argument(
        '--minimal',
        help='use minimal required requirements',
        action='store_true',
    )
    sync.add_argument(
        'packages',
        help='Sync dependencies. Choices: dev(minimal), doc(sphinx), '
        'packages(requirements.txt only), all(dev, doc, packages)',
        nargs='?',
        const='dev',
        choices=['all', 'dev', 'doc', 'extra', 'requirements'],
    )


def add_plan_options(parser):
    plan = parser.add_parser('plan', help='Manage release plans')
    plan.add_argument(
        'plan_operation',
        help='modify current release plan',
        choices=['new', 'close'],
    )


def add_init_options(parser):
    init = parser.add_parser('init', help='Create .baw project')
    init.add_argument('shortcut', help='Project name')
    init.add_argument('description', help='Project description')
    init.add_argument('--cmdline', action='store_true')


def add_test_options(parser):
    test = parser.add_parser('test', help='Run unit tests')
    test.add_argument(
        '-n',
        help='process count; use auto to select os.cpu_count',
        default='auto',
    )
    test.add_argument(
        '-k',
        help='pattern to select tests to run',
    )
    test.add_argument(
        '--cov',
        help='test coverage',
        action='store_true',
    )
    test.add_argument(
        '--generate',
        help='test data generator',
        action='store_true',
    )
    test.add_argument(
        '--stash',
        help='stash repository before running tests',
        action='store_true',
    )
    test.add_argument(
        '--pdb',
        help='start interactive pdb after error occurs',
        action='store_true',
    )
    test.add_argument(
        '--instafail',
        help='print error while running pytest',
        action='store_true',
    )
    test.add_argument(
        '-x',
        help='fail fast after first error',
        action='store_true',
    )
    test.add_argument(
        'test',
        help='',
        nargs='?',
        default='fast',
        choices=['fast', 'long', 'nightly', 'skip'],
    )


def parse():
    """Parse arguments from sys-args and return the result as dictionary."""
    parser = create_parser()
    args = vars(parser.parse_args())

    args['sync'] = 'sync' in sys.argv
    args['plan'] = 'plan' in sys.argv
    args['init'] = 'init' in sys.argv

    need_help = not any(args.values())
    if need_help:
        parser.print_help()
    return args
