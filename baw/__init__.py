#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019 by Helmut Konrad Fahrendholz. All rights reserved.
# Tis file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================

from os import environ
from os import getcwd
from sys import exc_info
from time import time
from traceback import format_exc

from baw.cmd import clean_project
from baw.cmd import clean_virtual
from baw.cmd import doc
from baw.cmd import drop_release
from baw.cmd import format_repository
from baw.cmd import ide_open
from baw.cmd import init as project_init
from baw.cmd import release
from baw.cmd import run_test
from baw.cmd import sync
from baw.cmd import sync_files
from baw.cmd import upgrade
from baw.command import parse
from baw.execution import find_root
from baw.execution import install
from baw.execution import publish
from baw.execution import run
from baw.git import git_add
from baw.runtime import create as create_virtual
from baw.utils import FAILURE
from baw.utils import PLAINOUTPUT
from baw.utils import SUCCESS
from baw.utils import forward_slash
from baw.utils import handle_error
from baw.utils import logging
from baw.utils import logging_error
from baw.utils import print_runtime

__version__ = '0.7.2'


def run_main():
    start = time()
    args = parse()
    if not any(args.values()):
        return SUCCESS

    if args['version']:
        logging(__version__)
        return SUCCESS

    clean = args['clean']
    clean_venv = args['clean_venv']
    drop_release_ = args['drop_release']
    format_ = args['format']
    ide = args['ide']
    init = args['init']
    raw = args['raw']
    release_ = args['release']
    upgrade_ = args['upgrade']
    verbose = args['verbose']
    virtual = args['virtual']

    if upgrade_ or release_:
        # Upgrade, release command requires always virtual environment
        virtual = True

    if virtual:
        # expose virtual flag
        environ['VIRTUAL'] = "TRUE"
    if raw:
        # expose raw out flag
        environ[PLAINOUTPUT] = "TRUE"

    root = getcwd()

    if init:
        with handle_error(ValueError, code=FAILURE):  #  No GIT found, exit 1
            # TODO: Very dirty
            init_args = args['init']
            # with_cmd = False
            if len(init_args) > 3:
                logging_error('To many inputs: %s' % args['init'])
                return FAILURE
            if len(init_args) == 3:
                if init_args[2] != '--with_cmd':
                    logging_error('--with_cmd allowed, not %s' % init_args[2])
                    return FAILURE
                # with_cmd = True
                # init_args = init_args[:2]
                init_args[2] = True

            project_init(root, *init_args)

            sync_files(root)
            git_add(root, '*')

            # Deactivate options to reach fast reaction
            release(
                root,
                verbose=verbose,
                stash=False,  # Nothing to stash at the first time
                sync=False,  # No sync for first time needed
                virtual=False,  # No virtual for first time needed
            )

    # project must be init, if not, derminate here
    with handle_error(ValueError, code=FAILURE):
        # if cwd is in child location of the project, the root is set to
        # project root
        root = find_root(getcwd())

    if clean_venv:
        clean_virtual(root)

    if format_:
        failure = format_repository(
            root,
            verbose=verbose,
            virtual=virtual,
        )
        if failure:
            return failure

    if virtual:
        failure = create_virtual(root, clean=clean)
        if failure:
            return failure

    if drop_release_:
        return drop_release(root)

    if upgrade_:
        failure = upgrade(root, verbose=verbose, virtual=True)
        print_runtime(start)
        exit(failure)

    if clean:
        clean_project(root)

    ret = 0
    packages = args['sync']
    if packages:
        ret += sync(root, packages=packages, virtual=virtual, verbose=verbose)

    if args['test']:
        ret += run_test(
            root,
            coverage='cov' in args['test'],
            fast='fast' in args['test'],
            longrun='long' in args['test'],
            pdb='pdb' in args['test'],
            stash='stash' in args['test'],
            verbose=verbose,
            virtual=virtual,
        )

    if args['doc']:
        ret += doc(root, virtual=virtual, verbose=verbose)

    if args['install']:
        ret += install(root, virtual=virtual)

    if release_:
        release_type = args['release']
        ret += release(root, release_type=release_type)

    if args['publish']:
        ret += publish(root)

    if args['run']:
        ret += run(root, virtual=virtual)

    if ide:
        ide_open(root)
    print_runtime(start)
    return ret


# TODO: add matrix with excluding cmds, eg. --init --drop_release


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
