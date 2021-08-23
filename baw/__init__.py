#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019-2021 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================

ROOT = None

# pylint:disable=wrong-import-position

import collections
import functools
import os
import sys
import time
import traceback

import baw.__root__
import baw.cli
import baw.cmd
import baw.cmd.bisect
import baw.cmd.lint
import baw.cmd.plan
import baw.cmd.sync
import baw.cmd.upgrade
import baw.execution
import baw.project
import baw.runtime
import baw.utils

__version__ = '0.16.0'


def run_main():  # pylint:disable=R1260,too-many-locals,too-many-branches,R0911
    start = time.time()
    args = baw.cli.parse()
    if not any(args.values()):
        return baw.utils.SUCCESS
    cwd = os.getcwd()

    if args['version']:
        baw.utils.log(__version__)
        return baw.utils.SUCCESS
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
        with baw.utils.handle_error(
                ValueError, code=baw.utils.FAILURE):  #  No GIT found, exit 1
            shortcut, description, cmdline = args['shortcut'], args[
                'description'], args['cmdline']
            baw.cmd.init(root, shortcut, name=description, cmdline=cmdline)

    if args['ide']:
        packages = tuple(args['ide']) if args['ide'] != [None] else None
        returncode = baw.cmd.ide_open(root=root, packages=packages)
        if returncode:
            return returncode

    root = baw.project.determine_root(os.getcwd())
    if root is None:
        baw.utils.error('require .baw file')
        return baw.utils.FAILURE

    if args['commits']:
        return baw.cmd.bisect.cli(
            root,
            args['commits'],
            verbose=verbose,
            virtual=virtual,
        )

    link = functools.partial

    clean = args['clean'] if 'clean' in args else ''
    fmap = collections.OrderedDict([
        ('format',
         link(baw.cmd.format_repository,
              root=root,
              verbose=verbose,
              virtual=virtual)),
        ('virtual',
         link(
             baw.runtime.create,
             root=root,
             clean=clean in ('venv', 'all'),
             verbose=verbose,
         )),
        ('drop', link(baw.cmd.drop, root=root)),
        (
            'upgrade',
            link(
                baw.cmd.upgrade.upgrade,
                root=root,
                verbose=verbose,
                notests=args['notests'],
                virtual=False,
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
    workmap = collections.OrderedDict([
        ('open', link(baw.cmd.open_this, root=root)),
        ('clean',
         link(
             baw.cmd.clean_project,
             docs=clean == 'docs',
             resources=clean == 'resources',
             tests=clean == 'tests',
             tmp=clean == 'tmp',
             venv=clean == 'venv',
             all_=clean == 'all',
             root=cwd,
         )),
        ('sync',
         link(
             baw.cmd.sync.sync,
             root,
             packages=args.get('packages'),
             minimal=args.get('minimal', False),
             virtual=virtual,
             verbose=verbose,
         )),
        ('test',
         testcommand(root=root, args=args, verbose=verbose, virtual=virtual)),
        ('doc', link(baw.cmd.doc, root=root, virtual=virtual, verbose=verbose)),
        ('install', link(baw.cmd.install, root=root, virtual=virtual)),
        ('release',
         link(baw.cmd.release, root=root, release_type=args['release'])),
        ('publish', link(baw.execution.publish, root=root, verbose=verbose)),
        ('run', link(baw.execution.run, root=root, virtual=virtual)),
        ('lint',
         link(
             baw.cmd.lint.lint,
             root=root,
             scope=args['lint'],
             verbose=verbose,
             virtual=virtual,
         )),
        ('plan',
         link(baw.cmd.plan.action, root=root, plan=args.get('plan_operation'))),
    ])

    for argument, process in workmap.items():
        if argument in args and args[argument]:
            try:
                ret += process()
            except TypeError as msg:
                baw.utils.error(f'{process} does not return exitcode')
                baw.utils.error(msg)
                ret += baw.utils.FAILURE

    if not args['ide']:
        # --ide is a very long running task, sometimes 'endless'.
        # Therefore it is senseless to measure the runtime.
        baw.utils.print_runtime(start)
    return ret


def testcommand(root: str, args, *, verbose: bool, virtual: bool):
    if 'test' not in args:
        return None
    testconfig = []
    if args['n'] != '1':
        testconfig += [f'-n={args["n"]}']
    if args['k']:
        testconfig += [f'-k {args["k"]}']
    if args['x']:
        testconfig += ['-x ']
    if args['testconfig']:
        testconfig += args['testconfig']
    call = functools.partial(
        baw.cmd.run_test,
        root=root,
        coverage=args['cov'],
        fast='fast' in args['test'],
        longrun='long' in args['test'],
        nightly='nightly' in args['test'],
        pdb=args['pdb'],
        generate=args['generate'],
        stash=args['stash'],
        instafail=args['instafail'],
        testconfig=testconfig,
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
        os.environ[baw.utils.PLAINOUTPUT] = "TRUE"
    root = os.getcwd()
    return root


def main():
    """Entry point of script"""
    try:
        sys.exit(run_main())
    except KeyboardInterrupt:
        baw.utils.log('\nOperation cancelled by user')
    except Exception as msg:  # pylint: disable=broad-except
        baw.utils.error(msg)
        stack_trace = traceback.format_exc()
        baw.utils.log(baw.utils.forward_slash(stack_trace))
    sys.exit(baw.utils.FAILURE)
