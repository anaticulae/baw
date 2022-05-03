#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019-2022 by Helmut Konrad Fahrendholz. All rights reserved.
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
    },
)
BISECT = Command(
    longcut='--bisect',
    message='run git bisect',
    args={
        'nargs': '+',
        'dest': 'commits',
    },
)
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
    },
)
# run tests, increment version, commit, git tag and push to package index
DOCKER = Command(longcut='--docker', message='Use docker environment')
FORMAT = Command(longcut='--format', message='Format repository')
RAW = Command(longcut='--raw', message='Do not modify stdout/stderr')
DROP_RELEASE = Command(longcut='--drop', message='Remove last release')
REPORT = Command('-re', '--report', 'Write module status in html report')
RUN = Command('-ru', '--run', 'Run application')
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
    },
)

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
        LINT,
        NOTESTS,
        RAW,
        REPORT,
        RUN,
        TEST_CONFIG,
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
    cmds = parser.add_subparsers()
    add_open_options(cmds)
    add_clean_options(cmds)
    add_upgrade_option(cmds)
    add_init_options(cmds)
    add_plan_options(cmds)
    add_sync_options(cmds)
    add_test_options(cmds)
    add_release_options(cmds)
    add_publish_options(cmds)
    add_install_option(cmds)
    add_pipeline_option(cmds)
    return parser


def add_upgrade_option(parser):
    plan = parser.add_parser('upgrade', help='Upgrade requirements.txt/dev/ext')
    plan.add_argument(
        'upgrade',
        help='Select packages to upgrade',
        choices=[
            'dev',
            'requirements',
            'extra',
            'all',
        ],
        nargs='?',
        default='requirements',
    )


def add_clean_options(parser):
    plan = parser.add_parser('clean', help='Remove generated content')
    plan.add_argument(
        'clean',
        help='Remove different type of content',
        choices=['all', 'docs', 'resources', 'tests', 'tmp', 'venv'],
        nargs='?',
        default='tests',
    )


def add_release_options(parser):
    # TODO: MOVE TO release.py
    release = parser.add_parser('release', help='Test, commit, tag and publish')
    release.add_argument(
        'release',
        help='Test, commit, tag and publsih',
        nargs='?',
        choices='major minor patch noop auto'.split(),
        default='auto',
    )
    release.add_argument('--no_install', action='store_true')
    release.add_argument('--no_test', action='store_true')
    release.add_argument('--no_venv', action='store_true')


def add_publish_options(parser):
    publish = parser.add_parser('publish', help='Push release to repository')
    publish.add_argument(
        'publish',
        nargs='?',
        default='dest',
        help='Push release to this repository',
    )
    publish.add_argument('--no_venv', action='store_true')


def add_open_options(parser):
    plan = parser.add_parser('open', help='Open directory')
    plan.add_argument(
        'path',
        help='Goal',
        choices='this project generated tests tmp'.split(),
        nargs='?',
        default='project',
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
        '--no_install',
        help='do not run setup before testing',
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


def add_install_option(parser):
    test = parser.add_parser('install', help='Run install task')
    test.add_argument(
        '--remove',
        help='remove current version before',
        action='store_true',
    )
    test.add_argument(
        '--dev',
        help='install in development mode',
        action='store_true',
    )


def add_pipeline_option(parser):
    sync = parser.add_parser('jenkins', help='Run pipline task')
    sync.add_argument(
        'create',
        help='generate jenkins file',
        nargs='?',
        const='test',
        choices='test generate nightly release'.split(),
    )


def parse():
    """Parse arguments from sys-args and return the result as dictionary."""
    parser = create_parser()
    args = vars(parser.parse_args())
    args['sync'] = 'sync' in sys.argv
    args['plan'] = 'plan' in sys.argv
    args['init'] = 'init' in sys.argv
    args['open'] = 'open' in sys.argv
    args['install'] = 'install' in sys.argv
    if 'upgrade' not in sys.argv:
        args['upgrade'] = False
    args['jenkins'] = 'jenkins' in sys.argv
    # require help?
    need_help = not any(args.values())
    if need_help:
        parser.print_help()
    return args
