#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019 by Helmut Konrad Fahrendholz. All rights reserved.
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

from baw.cmd import clean_project
from baw.cmd import clean_virtual
from baw.cmd import doc
from baw.cmd import drop
from baw.cmd import format_repository
from baw.cmd import ide_open
from baw.cmd import init as project_init
from baw.cmd import lint as run_lint
from baw.cmd import release
from baw.cmd import run_test
from baw.cmd import sync
from baw.cmd import upgrade
from baw.cmd.init import get_init_args
from baw.command import parse
from baw.execution import install
from baw.execution import publish
from baw.execution import run
from baw.git import git_add
from baw.git import update_gitignore
from baw.project import find_root
from baw.runtime import create as create_venv
from baw.utils import FAILURE
from baw.utils import PLAINOUTPUT
from baw.utils import SUCCESS
from baw.utils import forward_slash
from baw.utils import handle_error
from baw.utils import logging
from baw.utils import logging_error
from baw.utils import print_runtime

__version__ = '0.7.3'


def run_main():
    start = time()
    args = parse()
    if not any(args.values()):
        return SUCCESS

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

    if args['init']:
        with handle_error(ValueError, code=FAILURE):  #  No GIT found, exit 1
            init_args = get_init_args(args)
            project_init(root, *init_args)

    # project must be init, if not, derminate here
    with handle_error(ValueError, code=FAILURE):
        # if cwd is in child location of the project, the root is set to
        # project root
        root = find_root(os.getcwd())

    link = partial

    fmap = OrderedDict([
        ('clean_venv', link(clean_virtual, root=root)),
        ('format',
         link(format_repository, root=root, verbose=verbose, virtual=virtual)),
        ('virtual',
         link(create_venv, root=root, clean=args['clean'], verbose=verbose)),
        ('drop', link(drop, root=root)),
        ('upgrade', link(upgrade, root=root, verbose=verbose, virtual=True)),
    ])

    for argument, action in fmap.items():
        if args[argument]:
            failure = action()
            if failure:
                return failure

    ret = 0
    workmap = OrderedDict([
        ('clean', link(clean_project, root=root)),
        ('sync',
         link(
             sync,
             root,
             packages=args['sync'],
             virtual=virtual,
             verbose=verbose)),
        ('test',
         testcommand(root=root, args=args, verbose=verbose, virtual=virtual)),
        ('doc', link(doc, root=root, virtual=virtual, verbose=verbose)),
        ('install', link(install, root=root, virtual=virtual)),
        ('release', link(release, root=root, release_type=args['release'])),
        ('publish', link(publish, root=root)),
        ('run', link(run, root=root, virtual=virtual)),
        ('lint', link(run_lint, root=root, verbose=verbose, virtual=virtual)),
        ('ide', link(ide_open, root=root)),
    ])

    for argument, action in workmap.items():
        if args[argument]:
            ret += action()

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
        pdb='pdb' in args['test'],
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
