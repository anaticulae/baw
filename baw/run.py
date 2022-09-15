#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019-2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================

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
import baw.cmd.info
import baw.cmd.init
import baw.cmd.install
import baw.cmd.lint
import baw.cmd.open
import baw.cmd.plan
import baw.cmd.release
import baw.cmd.sync
import baw.cmd.test
import baw.cmd.upgrade
import baw.config
import baw.execution
import baw.project
import baw.runtime
import baw.utils


def run_main():  # pylint:disable=R0911
    start = time.time()
    args = baw.cli.parse()
    if not any(args.values()):
        return baw.utils.SUCCESS
    if run_version(args):
        return baw.utils.SUCCESS
    directory = run_environment(args)
    if run_open(directory, args):
        return baw.utils.SUCCESS
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
            run_upgrade,
            run_clean,
            run_sync,
            run_test,
            run_doc,
            run_install,
            run_release,
            run_publish,
            run_lint,
            run_plan,
            run_info,
    ):
        if returncode := method(root=root, args=args):
            return returncode
    if not args.get('ide', False):
        # --ide is a very long running task, sometimes 'endless'.
        # Therefore it is senseless to measure the runtime.
        baw.utils.print_runtime(start)
    return baw.utils.SUCCESS


def switch_docker():
    """Use docker environment to run command."""
    usedocker = '--docker' in sys.argv
    if not usedocker:
        return run_main()
    root = os.getcwd()
    # use docker to run cmd
    argv = [item for item in sys.argv if item != '--docker']
    if argv:
        # TODO: REMOVE THIS HACK
        argv[0] = argv[0].split('/')[-1]
    usercmd = ' '.join(argv)
    image = baw.config.docker_image(root=root)
    # TODO: MOVE TO CONFIG OR SOMETHING ELSE
    volume = f'-v {os.getcwd()}:/var/test'
    docker = f'docker run --rm {volume} {image} "{usercmd}"'
    completed = baw.runtime.run(docker, cwd=root)
    if completed.returncode:
        baw.utils.error(docker)
        if completed.stdout:
            baw.utils.error(completed.stdout)
        baw.utils.error(completed.stderr)
    else:
        baw.utils.log(completed.stdout)
        if completed.stderr:
            baw.utils.error(completed.stderr)
    return completed.returncode


def run_version(args) -> bool:
    if not args['version']:
        return False
    baw.utils.log(baw.__version__)
    return True


def run_environment(args):
    if baw.config.venv_always():
        # overwrite virtual selection
        args['virtual'] = True
    root = setup_environment(
        args['upgrade'],
        args.get('release', ''),
        args['raw'],
        args.get('virtual', False),
    )
    return root


def run_open(directory, args):
    if not args.get('open', False):
        return False
    printme = args.get('print', False)
    baw.cmd.open.openme(directory, args['path'], console=printme)
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


def run_upgrade(root, args):
    if not args.get('upgrade', False):
        return baw.utils.SUCCESS
    result = baw.cmd.upgrade.upgrade(
        root=root,
        verbose=args.get('verbose', False),
        virtual=False,
        packages=args['upgrade'],
    )
    return result


def run_clean(root, args):
    clean = args.get('clean', '')
    if not clean:
        return baw.utils.SUCCESS
    result = baw.cmd.clean.clean(
        docs=clean == 'docs',
        resources=clean == 'resources',
        tests=clean == 'tests',
        tmp=clean == 'tmp',
        venv=clean == 'venv',
        all_=clean == 'all',
        root=root,
    )
    return result


def run_sync(root, args):
    if not args.get('sync', False):
        return baw.utils.SUCCESS
    result = baw.cmd.sync.sync(
        root=root,
        packages=args.get('packages'),
        minimal=args.get('minimal', False),
        verbose=args.get('verbose', False),
        virtual=args.get('virtual', False),
    )
    return result


def run_test(root: str, args):
    if not args.get('test', False):
        return baw.utils.SUCCESS
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
    result = baw.cmd.test.run_test(
        root=root,
        coverage=args['cov'],
        docs='docs' in args['test'],
        fast='fast' in args['test'],
        longrun='long' in args['test'],
        nightly='nightly' in args['test'],
        pdb=args['pdb'],
        generate=args['generate'],
        stash=args['stash'],
        instafail=args['instafail'],
        testconfig=testconfig,
        noinstall=args.get('no_install', False),
        verbose=args.get('verbose', False),
        virtual=args.get('virtual', False),
    )
    return result


def run_doc(root: str, args: dict):
    if not args.get('doc', False):
        return baw.utils.SUCCESS
    result = baw.cmd.doc.doc(
        root=root,
        verbose=args.get('verbose', False),
        virtual=args.get('virtual', False),
    )
    return result


def run_install(root: str, args: dict):
    if not args.get('install', False):
        return baw.utils.SUCCESS
    result = baw.cmd.install.install(
        root=root,
        virtual=args.get('virtual', False),
        verbose=args.get('verbose', False),
        dev=args.get('dev', False),
        remove=args.get('remove', False),
    )
    return result


def run_release(root: str, args: dict):
    if not args.get('release', False):
        return baw.utils.SUCCESS
    # always publish after release
    args['publish'] = True
    virtual = args.get('virtual', True)
    # overwrite virtual flag if given
    novenv = args.get('no_venv', False)
    no_linter = args.get('no_linter', False)
    if novenv:
        baw.utils.log('do not use venv')
        virtual = False
    test = True
    # do not test before releasing
    notest = args.get('no_test', False)
    if notest:
        test = False
    if args.get('release') == 'drop':
        result = baw.cmd.release.drop(
            root,
            verbose=args['verbose'],
            virtual=virtual,
        )
        return result
    # run release
    result = baw.cmd.release.release(
        root=root,
        release_type=args['release'],
        test=test,
        virtual=virtual,
        no_linter=no_linter,
    )
    return result


def run_publish(root: str, args: dict):
    if not args.get('publish', False) or args.get('release', None) == 'drop':
        return baw.utils.SUCCESS
    virtual = True
    # overwrite virtual flag if given
    novenv = args.get('no_venv', False)
    if novenv:
        baw.utils.log('do not use venv')
        virtual = False
    result = baw.execution.publish(
        root=root,
        verbose=args.get('verbose', False),
        virtual=virtual,
    )
    return result


def run_lint(root: str, args: dict):
    if not args.get('lint', False):
        return baw.utils.SUCCESS
    result = baw.cmd.lint.lint(
        root=root,
        scope=args['lint'],
        verbose=args.get('verbose', False),
        virtual=args.get('virtual', False),
    )
    return result


def run_plan(root: str, args: dict):
    if not args.get('plan', False):
        return baw.utils.SUCCESS
    result = baw.cmd.plan.action(
        root=root,
        plan=args.get('plan_operation'),
    )
    return result


def run_info(root: str, args: dict):
    if not args.get('info', False):
        return baw.utils.SUCCESS
    value = args['info'][0]
    baw.cmd.info.prints(
        root=root,
        value=value,
    )
    return baw.utils.SUCCESS


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
        sys.exit(switch_docker())
    except KeyboardInterrupt:
        baw.utils.log('\nOperation cancelled by user')
    except Exception as msg:  # pylint: disable=broad-except
        baw.utils.error(msg)
        stack_trace = traceback.format_exc()
        baw.utils.log(baw.utils.forward_slash(stack_trace))
    sys.exit(baw.utils.FAILURE)
