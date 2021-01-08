#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019-2021 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================

import os
from collections import OrderedDict
from functools import partial
from sys import exc_info
from time import time
from traceback import format_exc

import baw.cmd.bisect
import baw.cmd.lint
import baw.cmd.upgrade
from baw.cli import parse
from baw.cmd import clean_project
from baw.cmd import clean_virtual
from baw.cmd import doc
from baw.cmd import drop
from baw.cmd import format_repository
from baw.cmd import ide_open
from baw.cmd import init as project_init
from baw.cmd import install
from baw.cmd import open_this
from baw.cmd import release
from baw.cmd import run_test
from baw.cmd.init import get_init_args
from baw.cmd.plan import action
from baw.cmd.sync import sync
from baw.execution import publish
from baw.execution import run
from baw.git import git_add
from baw.git import update_gitignore
from baw.project import determine_root
from baw.runtime import create as create_venv
from baw.utils import FAILURE
from baw.utils import PLAINOUTPUT
from baw.utils import SUCCESS
from baw.utils import forward_slash
from baw.utils import handle_error
from baw.utils import logging
from baw.utils import logging_error
from baw.utils import print_runtime

__version__ = '0.13.0'


def run_main():  # pylint:disable=R1260,too-many-locals,too-many-branches
    start = time()
    args = parse()
    if not any(args.values()):
        return SUCCESS
    cwd = os.getcwd()

    if args['version']:
        logging(__version__)
        return SUCCESS
    verbose, virtual = args['verbose'], args['virtual']
    root = setup_environment(
        args['upgrade'],
        args['release'],
        args['raw'],
        virtual,
    )

    if args['release']:
        # always publish after release
        args['publish'] = True

    if args['init']:
        with handle_error(ValueError, code=FAILURE):  #  No GIT found, exit 1
            init_args = get_init_args(args)
            project_init(root, *init_args)

    if args['ide']:
        packages = tuple(args['ide']) if args['ide'] != [None] else None
        returncode = ide_open(root=root, packages=packages)
        if returncode:
            return returncode

    root = determine_root(os.getcwd())
    if root is None:
        return FAILURE

    if args['commits']:
        return baw.cmd.bisect.cli(
            root,
            args['commits'],
            verbose=verbose,
            virtual=virtual,
        )

    link = partial

    fmap = OrderedDict([
        ('clean_venv', link(clean_virtual, root=root)),
        ('format',
         link(format_repository, root=root, verbose=verbose, virtual=virtual)),
        ('virtual',
         link(create_venv, root=root, clean=args['clean'], verbose=verbose)),
        ('drop', link(drop, root=root)),
        (
            'upgrade',
            link(
                baw.cmd.upgrade.upgrade,
                root=root,
                verbose=verbose,
                notests=args['notests'],
                virtual=True,
                packages=args['upgrade'],
            ),
        ),
    ])

    for argument, process in fmap.items():
        if not args[argument]:
            continue
        failure = process()
        if failure:
            return failure

    ret = 0
    workmap = OrderedDict([
        ('open', link(open_this, root=root)),
        ('clean', link(clean_project, root=cwd)),
        ('sync',
         link(
             sync,
             root,
             packages=args.get('packages'),
             minimal=args.get('minimal', False),
             virtual=virtual,
             verbose=verbose,
         )),
        ('test',
         testcommand(root=root, args=args, verbose=verbose, virtual=virtual)),
        ('doc', link(doc, root=root, virtual=virtual, verbose=verbose)),
        ('install', link(install, root=root, virtual=virtual)),
        ('release', link(release, root=root, release_type=args['release'])),
        ('publish', link(publish, root=root, verbose=verbose)),
        ('run', link(run, root=root, virtual=virtual)),
        ('lint',
         link(
             baw.cmd.lint.lint,
             root=root,
             scope=args['lint'],
             verbose=verbose,
             virtual=virtual,
         )),
        ('plan', link(action, root=root, plan=args['plan'])),
    ])

    for argument, process in workmap.items():
        if args[argument]:
            try:
                ret += process()
            except TypeError as error:
                logging_error(f'{process} does not return exitcode')
                logging_error(error)
                ret += FAILURE

    if not args['ide']:
        # --ide is a very long running task, sometimes 'endless'.
        # Therefore it is senseless to measure the runtime.
        print_runtime(start)
    return ret


def testcommand(root: str, args, *, verbose: bool, virtual: bool):
    if not args['test']:
        return None
    call = partial(
        run_test,
        root=root,
        coverage='cov' in args['test'],
        fast='fast' in args['test'],
        longrun='long' in args['test'],
        nightly='nightly' in args['test'],
        pdb='pdb' in args['test'],
        generate='generate' in args['test'],
        stash='stash' in args['test'],
        testconfig=args['testconfig'] if args['testconfig'] else [],
        verbose=verbose,
        virtual=virtual,
    )
    return call


# TODO: add matrix with excluding cmds, eg. --init --drop_release


def setup_environment(upgrade, release, raw, virtual):  # pylint: disable=W0621
    if upgrade or release:
        # Upgrade, release command requires always virtual environment
        virtual = True

    if virtual:
        # expose virtual flag
        os.environ['VIRTUAL'] = "TRUE"

    if raw:
        # expose raw out flag
        os.environ[PLAINOUTPUT] = "TRUE"

    root = os.getcwd()
    return root


def main():
    """Entry point of script"""
    try:
        exit(run_main())
    except KeyboardInterrupt:
        logging('\nOperation cancelled by user')
    except Exception as error:  # pylint: disable=broad-except
        logging_error(error)
        stack_trace = format_exc()
        logging(forward_slash(stack_trace))
    exit(FAILURE)
