#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019-2021 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================

import collections
import functools
import os
import sys
import time
import traceback

import baw
import baw.cli
import baw.cmd
import baw.cmd.bisect
import baw.cmd.clean
import baw.cmd.doc
import baw.cmd.format
import baw.cmd.ide
import baw.cmd.init
import baw.cmd.install
import baw.cmd.lint
import baw.cmd.open
import baw.cmd.plan
import baw.cmd.release
import baw.cmd.sync
import baw.cmd.test
import baw.cmd.upgrade
import baw.execution
import baw.project
import baw.runtime
import baw.utils


def run_main():  # pylint:disable=R1260,too-many-locals,too-many-branches,R0911
    start = time.time()
    args = baw.cli.parse()
    if not any(args.values()):
        return baw.utils.SUCCESS
    if run_version(args):
        return baw.utils.SUCCESS
    directory, verbose, virtual = run_environment(args)
    if run_open(directory, args):
        return baw.utils.SUCCESS
    if args['release']:
        # always publish after release
        args['publish'] = True
    # create a new git repository with template code
    run_init_project(directory, args)
    # open vscode
    if returncode := run_ide(directory, args):
        return returncode
    if not (root := determine_root(directory)):
        return baw.utils.FAILURE
    for method in (
            run_bisect,
            run_format,
            run_venv,
            run_drop,
            run_upgrade,
    ):
        if returncode := method(root=root, args=args):
            return returncode

    link = functools.partial
    clean = args.get('clean', False)
    cwd = os.getcwd()
    ret = 0
    workmap = collections.OrderedDict([
        ('clean',
         link(
             baw.cmd.clean.clean,
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
        ('doc',
         link(
             baw.cmd.doc.doc,
             root=root,
             virtual=virtual,
             verbose=verbose,
         )),
        ('install', link(baw.cmd.install.install, root=root, virtual=virtual)),
        ('release',
         link(
             baw.cmd.release.release,
             root=root,
             release_type=args['release'],
         )),
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


def run_version(args) -> bool:
    if not args['version']:
        return False
    baw.utils.log(baw.__version__)
    return True


def run_environment(args):
    verbose, virtual = args.get('verbose', False), args.get('virtual', False)
    root = setup_environment(
        args['upgrade'],
        args['release'],
        args['raw'],
        virtual,
    )
    return root, verbose, virtual


def run_open(directory, args):
    if not args.get('open', False):
        return False
    baw.cmd.open.openme(directory, args['path'])
    return True


def run_init_project(directory, args):
    if not args.get('init', False):
        return
    #  No GIT found, exit 1
    with baw.utils.handle_error(ValueError, code=baw.utils.FAILURE):
        shortcut, description, cmdline = (
            args['shortcut'],
            args['description'],
            args['cmdline'],
        )
        baw.cmd.init.init(
            directory,
            shortcut,
            name=description,
            cmdline=cmdline,
        )


def run_ide(directory, args):
    if not args.get('ide', False):
        return baw.utils.SUCCESS
    packages = tuple(args['ide']) if args['ide'] != [None] else None
    if returncode := baw.cmd.ide.ide_open(
            root=directory,
            packages=packages,
    ):
        return returncode
    return baw.utils.SUCCESS


def determine_root(directory):
    root = baw.project.determine_root(directory)
    if not root:
        baw.utils.error('require .baw file')
        return None
    return root


def run_bisect(root, args):
    if not args.get('commits', False):
        return baw.utils.SUCCESS
    return baw.cmd.bisect.cli(
        root,
        args['commits'],
        verbose=args.get('verbose', False),
        virtual=args.get('virtual', False),
    )


def run_format(root, args):
    if not args.get('format', False):
        return baw.utils.SUCCESS
    result = baw.cmd.format.format_repository(
        root,
        verbose=args.get('verbose', False),
        virtual=args.get('virtual', False),
    )
    return result


def run_venv(root, args):
    if not args.get('virtual', False):
        return baw.utils.SUCCESS
    result = baw.runtime.create(
        root,
        clean=args.get('clean', '') in 'venv all',
        verbose=args.get('verbose', False),
    )
    return result


def run_drop(root, args):
    if not args.get('drop', False):
        return baw.utils.SUCCESS
    result = baw.cmd.release.drop(
        root,
        verbose=args.get('verbose', False),
        virtual=args.get('virtual', False),
    )
    return result


def run_upgrade(root, args):
    if not args.get('upgrade', False):
        return baw.utils.SUCCESS
    result = baw.cmd.upgrade.upgrade(
        root=root,
        verbose=args.get('verbose', False),
        notests=args['notests'],
        virtual=False,
        packages=args['upgrade'],
    )
    return result


def testcommand(root: str, args, *, verbose: bool, virtual: bool):
    if 'test' not in args:
        return None
    testconfig = []
    if args['n'] != '1':
        testconfig += [f'-n={args["n"]}']
    if args['k']:
        kselected = args["k"]
        if '.' in kselected:
            testconfig += [f'--pyargs {kselected}']
        else:
            testconfig += [f'-k {kselected}']
    if args['x']:
        testconfig += ['-x ']
    if args['testconfig']:
        testconfig += args['testconfig']
    call = functools.partial(
        baw.cmd.test.run_test,
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
