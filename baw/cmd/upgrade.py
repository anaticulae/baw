#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019-2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================

import concurrent.futures
import os
import re

import baw.cmd.complex
import baw.cmd.sync
import baw.cmd.utils
import baw.config
import baw.git
import baw.requirements
import baw.requirements.check
import baw.requirements.parser
import baw.requirements.upgrade
import baw.utils


def upgrade(
    root: str,
    *,
    notests: bool = True,
    verbose: bool = False,
    venv: bool = False,
    generate: bool = True,
    pre: bool = True,
    packages: str = 'requirements',
) -> int:
    """Upgrade requirements

    force: upgrade dev requirements also
    """
    with baw.git.stash(root, verbose=verbose, venv=venv):
        returnvalue = check_upgrade(root, packages=packages, pre=pre)
        if returnvalue in (baw.utils.SUCCESS, baw.utils.FAILURE):
            return returnvalue
        requirements_dev = returnvalue
        failure = baw.cmd.complex.sync_and_test(
            root,
            generate=generate,  # generate test data
            packages='dev',  # minimal requirements is required
            quiet=True,
            stash=False,
            sync=not notests,  # install new packages
            test=not notests,
            testconfig=None,
            verbose=verbose,
            venv=venv,
        )
        requirements = os.path.join(root, baw.utils.REQUIREMENTS_TXT)
        if requirements_dev:
            requirements = (requirements, requirements_dev)
        if failure:
            # reset requirement
            completed = baw.git.checkout(
                root,
                requirements,
                verbose=verbose,
                venv=venv,
            )
            baw.utils.error('Upgrading failed')
            assert not completed
            return failure
        failure = baw.git.commit(
            root,
            source=requirements,
            message=f'chore(requirements): upgrade {baw.utils.REQUIREMENTS_TXT}',
            verbose=verbose,
        )
        if failure:
            return failure
    return baw.utils.SUCCESS


def check_upgrade(root, packages, pre: bool = False):
    failure = upgrade_requirements(root, pre=pre)
    requirements_dev = os.path.join(root, baw.utils.REQUIREMENTS_DEV)
    if not os.path.exists(requirements_dev) or packages == 'requirements':
        requirements_dev = None
    failure_dev = REQUIREMENTS_UPTODATE
    if requirements_dev:
        failure_dev = upgrade_requirements(
            root,
            requirements=baw.utils.REQUIREMENTS_DEV,
            pre=pre,
        )
    requirements_extra = os.path.join(root, baw.utils.REQUIREMENTS_EXTRA)
    check_extra = packages in 'extra all'
    if not os.path.exists(requirements_extra) or not check_extra:
        requirements_extra = None
    failure_extra = REQUIREMENTS_UPTODATE
    if requirements_extra:
        failure_extra = upgrade_requirements(
            root,
            requirements=baw.utils.REQUIREMENTS_EXTRA,
            pre=pre,
        )
    # requirements.txt is up-to-date, no update required
    if all((
            failure == REQUIREMENTS_UPTODATE,
            failure_dev == REQUIREMENTS_UPTODATE,
            failure_extra == REQUIREMENTS_UPTODATE,
    )):
        return baw.utils.SUCCESS
    if failure not in (REQUIREMENTS_UPTODATE, baw.utils.SUCCESS):
        baw.utils.error('Error while upgrading requirements')
        return baw.utils.FAILURE
    if failure_dev not in (REQUIREMENTS_UPTODATE, baw.utils.SUCCESS):
        baw.utils.error('Error while upgrading dev requirements')
        return failure_dev
    return requirements_dev


REQUIREMENTS_UPTODATE = 100


def upgrade_requirements(
    root: str,
    requirements: str = baw.utils.REQUIREMENTS_TXT,
    pre: bool = False,
    venv: bool = False,
) -> int:
    """Take requirements.txt, replace version number with current
    available version on pip repository.

    Args:
        root(str): generated project
        requirements(str): relative path to requirements
        pre(bool): include pre-releases
        venv(bool): run in venv environment
    Returns:
        SUCCESS if file was upgraded
    """
    req_path = os.path.join(root, requirements)
    msg = f'Path does not exists {req_path}'
    if not os.path.exists(req_path):
        msg = f'Could not locate any requirements: {req_path}'
        baw.utils.error(msg)
        return baw.utils.FAILURE
    baw.utils.log(f'\nStart upgrading requirements: {req_path}')
    content = baw.utils.file_read(req_path)
    if not content.strip():
        baw.utils.log(f'Empty: {req_path}. Skipping replacement.')
        # stop further synchronizing process and quit with SUCCESS
        return REQUIREMENTS_UPTODATE
    upgraded = determine_new_requirements(root, content, venv=venv, pre=pre)
    if upgraded is None:
        return baw.utils.FAILURE
    replaced = baw.requirements.upgrade.replace(content, upgraded)
    if replaced == content:
        baw.utils.log('Requirements are up to date.\n')
        return REQUIREMENTS_UPTODATE
    # write new requirements
    baw.utils.file_replace(req_path, replaced)
    baw.utils.log('Upgrading finished')
    return baw.utils.SUCCESS


def installed_version(content: str):
    searched = re.search(
        r'INSTALLED: (?P<installed>[\w|\d|\.]+(\+[\d\w]{1,10})?)',
        content,
    )
    if not searched:
        return None
    return searched.group('installed')


def available_version(content: str, package: str = None):
    pattern = r'\w+\s\((?P<available>[\w\d\.\+]+)\)'
    if package:
        package = re.escape(package)
        pattern = rf'\b{package}[ ]\((?P<available>[\w\d\.\+]+)\)'
    searched = re.search(pattern, content)
    if not searched:
        return None
    detected = searched.group('available')
    result = baw.requirements.parser.fix_version(detected)
    return result


def next_version(content) -> str:
    # TODO: Check later, check if version is newer, do we want to downgrade?
    installed = installed_version(content)
    available = available_version(content)
    if installed != available:
        return available
    return available


def determine_new_requirements(
    root: str,
    requirements: str,
    *,
    pre: bool = False,
    venv: bool = False,
) -> baw.requirements.NewRequirements:
    parsed = baw.requirements.parser.parse(requirements)
    if parsed is None:
        baw.utils.error('could not parse requirements')
        return None
    sync_error = False
    equal = {}
    greater = {}
    for source, sink in [(parsed.equal, equal), (parsed.greater, greater)]:
        sync_error |= collect_new_packages(
            root,
            source,
            sink,
            pre=pre,
            venv=venv,
        )
    if sync_error:
        return None
    return baw.requirements.NewRequirements(equal=equal, greater=greater)


def collect_new_packages(  # pylint:disable=R0914
    root,
    source,
    sink,
    *,
    pre=False,
    venv=False,
    verbose=False,
) -> bool:
    sync_error = False
    worker = baw.config.pip_parallel_worker(root)
    with concurrent.futures.ThreadPoolExecutor(max_workers=worker) as executor:
        todo = {
            executor.submit(
                baw.cmd.sync.check_dependency,
                root,
                package,
                pre=pre,
                venv=venv,
                verbose=verbose,
            ): (package, version) for package, version in source.items()
        }
        for future in concurrent.futures.as_completed(todo):
            (package, version) = todo[future]
            try:
                dependency = future.result()
            except ValueError:
                if not pre:
                    baw.utils.error(f'package: {package} is not available')
            except RuntimeError:
                baw.utils.error('could not reach package repository')
                sync_error = True
            else:
                available = available_version(dependency, package=package)
                installed = installed_version(dependency)
                if installed:
                    if baw.requirements.check.lower(
                            current=installed,
                            new=available,
                    ):
                        available = installed
                if available != version:
                    if '.post' in available and not pre:
                        # installed pre-version and upgrade without --pre
                        # command. Do not upgrade with pre-release without
                        # --pre flag.
                        msg = f'do not upgrade: {available} without --pre'
                        baw.utils.log(msg)
                        continue
                    sink[package] = (version, available)  #(old, new)
    return sync_error


def run(args):
    root = baw.cmd.utils.get_root(args)
    result = upgrade(
        root=root,
        packages=args['upgrade'],
        pre=args['pre'],
        venv=False,
        verbose=args['verbose'],
    )
    return result


def extend_cli(parser):
    plan = parser.add_parser('upgrade', help='Upgrade requirements.txt/dev/ext')
    plan.add_argument(
        'upgrade',
        help='Select packages to upgrade',
        choices=[
            'dev',
            'requirements',
            'extra',
            'all',
        ],
        nargs='?',
        default='requirements',
    )
    plan.add_argument(
        '--pre',
        action='store_true',
        help='Include pre-releases in upgrade process',
    )
    plan.set_defaults(func=run)
