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
import baw.cmd.publish
import baw.cmd.release
import baw.cmd.sync
import baw.cmd.test
import baw.cmd.upgrade
import baw.config
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
    directory = run_environment(args)
    if args.get('venv', False):
        if failure := run_venv(args):
            return failure
    if args.get('bisect', False):
        if failure := run_bisect(args):
            return failure
    func = args.get('func')
    if func:
        # TODO: REMOVE ALL METHOD BELOW
        return func(args)
    if not (root := determine_root(directory)):
        return baw.utils.FAILURE
    for method in (run_publish,):
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
    if not args.get('version'):
        return False
    baw.utils.log(baw.__version__)
    return True


def run_environment(args):
    if baw.config.venv_always():
        # overwrite venv selection
        args['venv'] = True
    root = setup_environment(
        args.get('upgrade', False),
        args.get('release', ''),
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


def run_init_project(args):
    directory = run_environment(args)
    #  No GIT found, exit 1
    with baw.utils.handle_error(ValueError, code=baw.utils.FAILURE):
        shortcut, description, cmdline = (
            args['shortcut'],
            args['description'],
            args['cmdline'],
        )
        completed = baw.cmd.init.init(
            directory,
            shortcut,
            name=description,
            cmdline=cmdline,
            verbose=args['verbose'],
        )
    return completed


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


def determine_root(directory):
    root = baw.project.determine_root(directory)
    if not root:
        baw.utils.error('require .baw file')
        return None
    return root


def run_bisect(args):
    commits = args['bisect']
    cmds = list(sys.argv)[1:]
    cmds.remove('--bisect')
    cmds.remove(commits)
    root = get_root(args)
    result = baw.cmd.bisect.cli(
        root,
        commits=commits,
        args=cmds,
        verbose=args.get('verbose', False),
        venv=args.get('venv', False),
    )
    return result


def run_format(args):
    root = get_root(args)
    result = baw.cmd.format.format_repository(
        root,
        verbose=args.get('verbose', False),
        venv=args.get('venv', False),
    )
    return result


def run_venv(args):
    root = get_root(args)
    result = baw.runtime.create(
        root,
        clean=args.get('clean', '') in 'venv all',
        verbose=args.get('verbose', False),
    )
    return result


def run_upgrade(args):
    root = get_root(args)
    result = baw.cmd.upgrade.upgrade(
        root=root,
        verbose=args.get('verbose', False),
        venv=False,
        packages=args['upgrade'],
    )
    return result


def run_clean(args):
    root = get_root(args)
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


def run_sync(args):
    root = get_root(args)
    result = baw.cmd.sync.sync(
        root=root,
        packages=args.get('packages'),
        minimal=args.get('minimal', False),
        verbose=args.get('verbose', False),
        venv=args.get('venv', False),
    )
    return result


def run_test(args):
    root = get_root(args)
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
    if args['config']:
        testconfig += args['config']
    if args['junit_xml']:
        testconfig += [f'--junit-xml="{args["junit_xml"]}"']
    result = baw.cmd.test.run_test(
        root=root,
        coverage=args['cov'],
        docs='docs' in args['test'],
        fast='fast' in args['test'],
        longrun='long' in args['test'],
        nightly='nightly' in args['test'],
        alls='all' in args['test'],
        pdb=args['pdb'],
        generate=args['generate'],
        stash=args['stash'],
        instafail=args['instafail'],
        testconfig=testconfig,
        noinstall=args.get('no_install', False),
        verbose=args.get('verbose', False),
        venv=args.get('venv', False),
    )
    return result


def run_doc(args: dict):
    root = get_root(args)
    result = baw.cmd.doc.doc(
        root=root,
        verbose=args.get('verbose', False),
        venv=args.get('venv', False),
    )
    return result


def run_install(args: dict):
    root = get_root(args)
    result = baw.cmd.install.install(
        root=root,
        venv=args.get('venv', False),
        verbose=args.get('verbose', False),
        dev=args.get('dev', False),
        remove=args.get('remove', False),
    )
    return result


def run_release(args: dict):
    root = get_root(args)
    # always publish after release
    args['publish'] = True
    venv = args.get('venv', True)
    # overwrite venv flag if given
    novenv = args.get('no_venv', False)
    no_linter = args.get('no_linter', False)
    if novenv:
        baw.utils.log('do not use venv')
        venv = False
    if not baw.runtime.installed('semantic-release', root, venv=venv):
        return baw.utils.FAILURE
    test = True
    # do not test before releasing
    notest = args.get('no_test', False)
    if notest:
        test = False
    if args.get('release') == 'drop':
        result = baw.cmd.release.drop(
            root,
            verbose=args['verbose'],
            venv=venv,
        )
        return result
    # run release
    result = baw.cmd.release.release(
        root=root,
        release_type=args['release'],
        verbose=args['verbose'],
        test=test,
        venv=venv,
        no_linter=no_linter,
    )
    return result


def run_publish(root: str, args: dict):
    if not args.get('publish', False) or args.get('release', None) == 'drop':
        return baw.utils.SUCCESS
    venv = True
    # overwrite venv flag if given
    novenv = args.get('no_venv', False)
    if novenv:
        baw.utils.log('do not use venv')
        venv = False
    result = baw.cmd.publish.publish(
        root=root,
        verbose=args.get('verbose', False),
        venv=venv,
    )
    return result


def run_lint(args: dict):
    root = get_root(args)
    result = baw.cmd.lint.lint(
        root=root,
        scope=args['action'],
        verbose=args.get('verbose', False),
        venv=args.get('venv', False),
    )
    return result


def run_plan(args: dict):
    root = get_root(args)
    result = baw.cmd.plan.action(
        root=root,
        plan=args.get('plan_operation'),
    )
    return result


def run_info(args: dict):
    root = get_root(args)
    value = args['info'][0]
    baw.cmd.info.prints(
        root=root,
        value=value,
        verbose=args.get('verbose', False),
    )
    return baw.utils.SUCCESS


# TODO: add matrix with excluding cmds, eg. --init --drop_release


def setup_environment(upgrade, release, raw, venv):  # pylint: disable=W0621
    if upgrade or release:
        # Upgrade, release command requires always venv environment
        venv = True
    if venv:
        # expose venv flag
        os.environ['venv'] = "TRUE"
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


def get_root(args):
    directory = run_environment(args)
    root = determine_root(directory)
    if not root:
        return sys.exit(baw.utils.FAILURE)
    return root
