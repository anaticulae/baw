#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019-2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================

import importlib.metadata
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
import baw.cmd.ide
import baw.cmd.init
import baw.cmd.lint
import baw.cmd.open
import baw.cmd.plan
import baw.cmd.test
import baw.cmd.upgrade
import baw.cmd.utils
import baw.config
import baw.dockers
import baw.project
import baw.runtime
import baw.utils


def run_main():  # pylint:disable=R0911,R1260,too-many-branches
    start = time.time()
    args = baw.cli.parse()
    if not any(args):
        return baw.utils.SUCCESS
    if run_version(args):
        return baw.utils.SUCCESS
    if args.get('venv', False):
        if failure := run_venv(args):
            return failure
    if args.get('bisect', False):
        if failure := run_bisect(args):
            return failure
    # setup virtual flag, verify this!
    run_environment(args)
    func = args.get('func')
    if func:
        # TODO: REMOVE ALL METHOD BELOW
        return func(args)
    if not args.get('ide', False):
        # --ide is a very long running task, sometimes 'endless'.
        # Therefore it is senseless to measure the runtime.
        baw.utils.print_runtime(start)
    return baw.utils.SUCCESS


def run_version(args) -> bool:
    if not args.get('version'):
        return False
    try:
        live = importlib.metadata.version('baw')
    except importlib.metadata.PackageNotFoundError as notfound:
        raise ValueError('baw not installed/no metadata') from notfound
    baw.utils.log(live)
    return True


def run_environment(args):
    if baw.config.venv_always():
        # overwrite venv selection
        args['venv'] = True
    root = setup_environment(
        args['raw'],
        args.get('venv', False),
    )
    return root


def run_open(args):
    directory = run_environment(args)
    printme = args['print']
    baw.cmd.open.openme(
        root=directory,
        path=args['path'],
        prints=printme,
    )
    sys.exit(baw.utils.SUCCESS)


def run_ide(args):
    # # create a new git repository with template code
    # open vscode
    root = run_environment(args)
    packages = None
    if args['package']:
        packages = tuple(args['package'])
    if returncode := baw.cmd.ide.ide_open(
            root=root,
            packages=packages,
    ):
        return returncode
    return baw.utils.SUCCESS


def run_bisect(args):
    commits = args['bisect']
    cmds = list(sys.argv)[1:]
    cmds.remove('--bisect')
    cmds.remove(commits)
    root = baw.cmd.utils.get_root(args)
    result = baw.cmd.bisect.cli(
        root,
        commits=commits,
        args=cmds,
        verbose=args.get('verbose', False),
        venv=args.get('venv', False),
    )
    return result


def run_venv(args):
    root = baw.cmd.utils.get_root(args)
    result = baw.runtime.create(
        root,
        clean=args.get('clean', '') in 'venv all',
        verbose=args.get('verbose', False),
    )
    return result


def run_clean(args):
    root = baw.cmd.utils.get_root(args)
    clean = args['clean']
    docs = clean == 'docs'
    resources = clean == 'resources'
    tests = clean == 'tests'
    tmp = clean == 'tmp'
    venv = clean == 'venv'
    all_ = clean == 'all'
    if clean == 'ci':
        docs = True
        resources = True
        tests = True
        tmp = True
    result = baw.cmd.clean.clean(
        docs=docs,
        resources=resources,
        tests=tests,
        tmp=tmp,
        venv=venv,
        all_=all_,
        root=root,
    )
    return result


def run_test(args):
    root = baw.cmd.utils.get_root(args)
    testconfig = create_testconfig(args)
    selected = args['test']
    generate = selected == 'generate'
    generate |= args['generate']  # TODO: REMOVE LEGACY
    result = baw.cmd.test.run_test(
        root=root,
        coverage=args['cov'],
        docs=selected == 'docs',
        fast=selected == 'fast',
        longrun=selected == 'long',
        nightly=selected == 'nightly',
        alls=selected == 'all',
        pdb=args['pdb'],
        generate=generate,
        stash=args['stash'],
        instafail=args['instafail'],
        testconfig=testconfig,
        noinstall=args.get('no_install', False),
        verbose=args.get('verbose', False),
        venv=args.get('venv', False),
    )
    return result


def create_testconfig(args: dict) -> list:
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
    if args['config']:
        testconfig += args['config']
    if args['junit_xml']:
        testconfig += [f'--junit-xml="{args["junit_xml"]}"']
    return testconfig


def run_doc(args: dict):
    root = baw.cmd.utils.get_root(args)
    result = baw.cmd.doc.doc(
        root=root,
        verbose=args.get('verbose', False),
        venv=args.get('venv', False),
    )
    return result


def run_lint(args: dict):
    root = baw.cmd.utils.get_root(args)
    result = baw.cmd.lint.lint(
        root=root,
        scope=args['action'],
        verbose=args.get('verbose', False),
        venv=args.get('venv', False),
    )
    return result


def run_plan(args: dict):
    root = baw.cmd.utils.get_root(args)
    result = baw.cmd.plan.action(
        root=root,
        plan=args.get('plan_operation'),
    )
    return result


# TODO: add matrix with excluding cmds, eg. --init --drop_release


def setup_environment(raw, venv):  # pylint: disable=W0621
    if venv:
        # expose venv flag
        os.environ['VENV'] = "TRUE"
    if raw:
        # expose raw out flag
        os.environ[baw.utils.PLAINOUTPUT] = "TRUE"
    root = os.getcwd()
    return root


def main():
    """Entry point of script"""
    try:
        sys.exit(baw.dockers.switch_docker())
    except KeyboardInterrupt:
        baw.utils.log('\nOperation cancelled by user')
    except Exception as msg:  # pylint: disable=broad-except
        baw.utils.error(msg)
        stack_trace = traceback.format_exc()
        baw.utils.log(baw.utils.forward_slash(stack_trace))
    sys.exit(baw.utils.FAILURE)
