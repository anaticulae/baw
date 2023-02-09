#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019-2023 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================
"""Define structure of cmd line interface."""

import argparse
import sys

import baw.cmd.baseline
import baw.cmd.clean
import baw.cmd.cov
import baw.cmd.doc
import baw.cmd.format
import baw.cmd.generate
import baw.cmd.ide
import baw.cmd.image
import baw.cmd.info
import baw.cmd.install
import baw.cmd.lint
import baw.cmd.pipeline
import baw.cmd.publish
import baw.cmd.rebase
import baw.cmd.refactor
import baw.cmd.release
import baw.cmd.sh
import baw.cmd.sync
import baw.cmd.test
import baw.cmd.upgrade
import baw.run
import baw.utils


def create_parser():  # noqa: Z21
    """Create parser out of defined dictionary with cmd-line-definition.

    Returns created argparser
    """
    parser = argparse.ArgumentParser(prog='baw')
    add_parameter(parser)
    cmds = parser.add_subparsers(help='sub-cmd help')
    baw.cmd.init.extend_cli(cmds)
    baw.cmd.rebase.extend_cli(cmds)
    baw.cmd.ide.extend_cli(cmds)
    add_open_options(cmds)
    baw.cmd.doc.extend_cli(cmds)
    baw.cmd.clean.extend_cli(cmds)
    baw.cmd.upgrade.extend_cli(cmds)
    baw.cmd.sync.extend_cli(cmds)
    baw.cmd.install.extend_cli(cmds)
    baw.cmd.generate.extend_cli(cmds)
    baw.cmd.test.extend_cli(cmds)
    baw.cmd.format.extend_cli(cmds)
    baw.cmd.lint.extend_cli(cmds)
    baw.cmd.pipeline.extend_cli(cmds)
    baw.cmd.image.extend_cli(cmds)
    baw.cmd.refactor.extend_cli(cmds)
    add_shell_option(cmds)
    add_plan_options(cmds)
    baw.cmd.baseline.extend_cli(cmds)
    baw.cmd.cov.extend_cli(cmds)
    baw.cmd.release.extend_cli(cmds)
    baw.cmd.publish.extend_cli(cmds)
    baw.cmd.info.extend_cli(cmds)
    return parser


def parse():
    """Parse arguments from sys-args and return the result as dictionary."""
    parser = create_parser()
    args = parser.parse_args()
    # require help?
    need_help = not any(vars(args).values())
    if need_help:
        parser.print_help()
        sys.exit(baw.FAILURE)
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
        '--docken',
        action='store_true',
        help='Use docker generated environment',
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
    plan.set_defaults(func=baw.run.run_open)


def add_plan_options(parser):
    plan = parser.add_parser('plan', help='Manage release plans')
    plan.add_argument(
        'plan_operation',
        help='modify current release plan',
        choices=['new', 'close'],
    )
    plan.set_defaults(func=baw.run.run_plan)


def add_shell_option(parser):
    init = parser.add_parser('sh', help='Run shell cmd in env')
    init.add_argument('cmd', help='cmd')
    init.set_defaults(func=baw.cmd.sh.run_shell)
