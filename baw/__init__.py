#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019 by Helmut Konrad Fahrendholz. All rights reserved.
# Tis file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================

from os import getcwd
from sys import exc_info
from time import time
from traceback import format_exc

from baw.cmd import doc
from baw.cmd import init as project_init
from baw.cmd import sync
from baw.cmd import sync_files
from baw.cmd import test
from baw.cmd.init import git_add
from baw.command import parse
from baw.execution import clean as project_clean
from baw.execution import clean_virtual
from baw.execution import publish
from baw.execution import release
from baw.execution import root as project_root
from baw.execution import run
from baw.runtime import create as create_virtual
from baw.utils import FAILURE
from baw.utils import flush
from baw.utils import forward_slash
from baw.utils import handle_error
from baw.utils import logging
from baw.utils import logging_error
from baw.utils import print_runtime
from baw.utils import SUCCESS

__version__ = '0.5.2'


def run_main():
    start = time()
    args = parse()
    if not any(args.values()):
        return SUCCESS

    if args['version']:
        print(__version__)
        return SUCCESS

    verbose = args['verbose']
    virtual = args['virtual']
    init = args['init']
    clean = args['clean']
    clean_venv = args['clean_venv']

    root = getcwd()
    if clean_venv:
        clean_virtual(root)

    if virtual:
        failure = create_virtual(root, clean=clean)
        if failure:
            return failure

    if init:
        with handle_error(ValueError, code=FAILURE):  #  No GIT found, exit 1
            project_init(root, *args['init'])
            sync_files(root)
            git_add(root, '*')

            release(
                root,
                verbose=verbose,
                virtual=virtual,
                stash=False,  # Nothing to stash at the first time
            )

    with handle_error(ValueError, code=FAILURE):
        root = project_root(getcwd())

    if clean:
        project_clean(root)

    ret = 0
    if args['sync']:
        ret += sync(root, virtual=virtual, verbose=verbose)

    if args['test']:
        ret += test(
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
        ret += doc(root, virtual=virtual)

    if args['release']:
        release_type = args['release']
        ret += release(root, virtual=virtual, release_type=release_type)

    if args['publish']:
        ret += publish(root, virtual=virtual)

    if args['run']:
        ret += run(root, virtual=virtual)

    print_runtime(start)
    return ret


def main():
    """Entry point of script"""
    try:
        exit(run_main())
    except KeyboardInterrupt:
        print('\nOperation cancelled by user')
    except Exception as error:
        logging_error(error)
        stack_trace = format_exc()
        logging(forward_slash(stack_trace))
    exit(FAILURE)
