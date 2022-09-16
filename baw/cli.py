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
import sys

import baw.cmd.doc
import baw.cmd.ide
import baw.cmd.lint
import baw.cmd.pipeline
import baw.cmd.release
import baw.run
import baw.utils


def create_parser():  # noqa: Z21
    """Create parser out of defined dictionary with command-line-definition.

    Returns created argparser
    """
    parser = argparse.ArgumentParser(prog='baw')
    add_parameter(parser)
    cmds = parser.add_subparsers(help='sub-command help')
    baw.cmd.ide.extend_cli(cmds)
    baw.cmd.doc.extend_cli(cmds)
    add_open_options(cmds)
    add_clean_options(cmds)
    add_upgrade_option(cmds)
    add_init_options(cmds)
    add_plan_options(cmds)
    add_sync_options(cmds)
    add_test_options(cmds)
    baw.cmd.release.extend_cli(cmds)
    add_publish_options(cmds)
    add_install_option(cmds)
    baw.cmd.pipeline.extend_cli(cmds)
    baw.cmd.lint.extend_cli(cmds)
    add_format_option(cmds)
    add_info_option(cmds)
    return parser


def parse():
    """Parse arguments from sys-args and return the result as dictionary."""
    parser = create_parser()
    args = parser.parse_args()
    # require help?
    need_help = not any(vars(args).values())
    if need_help:
        parser.print_help()
        sys.exit(baw.utils.FAILURE)
    args = vars(args)
    return args


def add_parameter(parser):
    # run tests, increment version, commit, git tag and push to package index
    parser.add_argument(
        '--all',
        action='store_true',
        help='Clean and run all expect of publishing',
    )
    parser.add_argument(
        '--bisect',
        help='Git bisect, use ^ to separate good and bad commit',
    )
    parser.add_argument(
        '--docker',
        action='store_true',
        help='Use docker environment',
    )
    parser.add_argument(
        '--raw',
        action='store_true',
        help='Do not modify stdout/stderr',
    )
    parser.add_argument(
        '--venv',
        action='store_true',
        help='Use virtual environment',
    )
    # TODO count V to determine verbosity. -VVV
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Extend verbosity of logging',
    )
    parser.add_argument(
        '-v',
        '--version',
        action='store_true',
        help='Show version of this program',
    )


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
    plan.set_defaults(func=baw.run.run_upgrade)


def add_clean_options(parser):
    plan = parser.add_parser('clean', help='Remove generated content')
    plan.add_argument(
        'clean',
        help='Remove different type of content',
        choices=['all', 'docs', 'resources', 'tests', 'tmp', 'venv'],
        nargs='?',
        default='tests',
    )
    plan.set_defaults(func=baw.run.run_clean)


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
        choices='this project generated tests tmp venv lasttest'.split(),
        nargs='?',
        default='project',
    )
    plan.add_argument(
        '--print',
        help='print path to console',
        action='store_true',
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
    sync.set_defaults(func=baw.run.run_sync)


def add_plan_options(parser):
    plan = parser.add_parser('plan', help='Manage release plans')
    plan.add_argument(
        'plan_operation',
        help='modify current release plan',
        choices=['new', 'close'],
    )
    plan.set_defaults(func=baw.run.run_plan)


def add_init_options(parser):
    init = parser.add_parser('init', help='Create .baw project')
    init.add_argument('shortcut', help='Project name')
    init.add_argument('description', help='Project description')
    init.add_argument('--cmdline', action='store_true')
    init.set_defaults(func=baw.run.run_init_project)


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
        '--config',
        help='overwrite pytest invocation',
        nargs=1,
    )
    test.add_argument(
        '--junit_xml',
        help='junit-xml for pytest',
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
        choices='docs fast long nightly skip'.split(),
    )
    test.set_defaults(func=baw.run.run_test)


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
    test.set_defaults(func=baw.run.run_install)


def add_format_option(parser):
    test = parser.add_parser('format', help='Format code')
    test.add_argument(
        '--imports',
        help='run isort',
        action='store_true',
    )
    test.add_argument(
        '--code',
        help='run yapf',
        action='store_true',
    )
    test.set_defaults(func=baw.run.run_format)


def add_info_option(parser):
    info = parser.add_parser('info', help='Print project information')
    info.add_argument(
        'info',
        help='Print project information',
        nargs=1,
        choices='venv tmp covreport'.split(),
    )
    info.set_defaults(func=baw.run.run_info)
