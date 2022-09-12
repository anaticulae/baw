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
import baw.config
import baw.git
import baw.requirements
import baw.utils


def upgrade(
    root: str,
    *,
    notests: bool = False,
    verbose: bool = False,
    virtual: bool = False,
    generate: bool = True,
    packages: str = 'requirements',
) -> int:
    """Upgrade requirements

    force: upgrade dev requirements also
    """
    with baw.git.git_stash(root, verbose=verbose, virtual=virtual):
        returnvalue = check_upgrade(root, packages=packages)
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
            virtual='BOTH',  # sync virtual and non virtual environment
        )
        requirements = os.path.join(root, baw.utils.REQUIREMENTS_TXT)
        if requirements_dev:
            requirements = (requirements, requirements_dev)
        if failure:
            # reset requirement
            completed = baw.git.git_checkout(
                root,
                requirements,
                verbose=verbose,
                virtual=virtual,
            )
            baw.utils.error('Upgrading failed')
            assert not completed
            return failure
        failure = baw.git.git_commit(
            root,
            source=requirements,
            message=f'chore(requirements): upgrade {baw.utils.REQUIREMENTS_TXT}',
            verbose=verbose,
        )
        if failure:
            return failure
    return baw.utils.SUCCESS


def check_upgrade(root, packages):
    failure = upgrade_requirements(root)
    requirements_dev = os.path.join(root, baw.utils.REQUIREMENTS_DEV)
    if not os.path.exists(requirements_dev) or packages == 'requirements':
        requirements_dev = None
    failure_dev = REQUIREMENTS_UPTODATE
    if requirements_dev:
        failure_dev = upgrade_requirements(root, baw.utils.REQUIREMENTS_DEV)
    requirements_extra = os.path.join(root, baw.utils.REQUIREMENTS_EXTRA)
    check_extra = packages in 'extra all'
    if not os.path.exists(requirements_extra) or not check_extra:
        requirements_extra = None
    failure_extra = REQUIREMENTS_UPTODATE
    if requirements_extra:
        failure_extra = upgrade_requirements(root, baw.utils.REQUIREMENTS_EXTRA)
    # requirements.txt is uptodate, no update requireded
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
    virtual: bool = False,
) -> int:
    """Take requirements.txt, replace version number with current
    available version on pip repository.

    Args:
        root(str): generated project
        requirements(str): relativ path to requirements
        virtual(bool): run in virtual environment
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
        # stop further synchonizing process and quit with SUCCESS
        return REQUIREMENTS_UPTODATE
    upgraded = determine_new_requirements(root, content, virtual=virtual)
    if upgraded is None:
        return baw.utils.FAILURE
    replaced = baw.requirements.replace(content, upgraded)
    if replaced == content:
        baw.utils.log('Requirements are up to date.\n')
        return REQUIREMENTS_UPTODATE
    # write new requirements
    baw.utils.file_replace(req_path, replaced)
    baw.utils.log('Upgrading finished')
    return baw.utils.SUCCESS


def installed_version(content: str):
    searched = re.search(r'INSTALLED: (?P<installed>[\w|\d|\.]+)', content)
    if not searched:
        return None
    return searched.group('installed')


def available_version(content: str, package: str = None):
    pattern = r'\w+\s\((?P<available>[\w|\d|\.]+)'
    if package:
        package = re.escape(package)
        pattern = rf'\b{package}[ ]\((?P<available>[\w|\d|\.]+)'
    searched = re.search(pattern, content)
    if not searched:
        return None
    detected = searched.group('available')
    result = baw.requirements.fix_version(detected)
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
    virtual: bool = False,
) -> baw.requirements.NewRequirements:
    parsed = baw.requirements.parse(requirements)
    if parsed is None:
        baw.utils.error('could not parse requirements')
        return None

    sync_error = False
    equal = {}
    greater = {}
    for source, sink in [(parsed.equal, equal), (parsed.greater, greater)]:
        sync_error |= collect_new_packages(root, source, sink, virtual)
    if sync_error:
        return None
    return baw.requirements.NewRequirements(equal=equal, greater=greater)


def collect_new_packages(root, source, sink, virtual, verbose=False):
    sync_error = False
    parallel_worker = baw.config.pip_parallel_worker(root)
    with concurrent.futures.ThreadPoolExecutor(max_workers=parallel_worker) as executor: # yapf:disable
        todo = {
            executor.submit(
                baw.cmd.sync.check_dependency,
                root,
                package,
                virtual=virtual,
                verbose=verbose,
            ): (package, version) for package, version in source.items()
        }
        for future in concurrent.futures.as_completed(todo):
            (package, version) = todo[future]
            try:
                dependency = future.result()
            except ValueError:
                baw.utils.error(f'package: {package} is not available')
            except RuntimeError:
                baw.utils.error('could not reach package repository')
                sync_error = True
            else:
                available = available_version(dependency, package=package)
                installed = installed_version(dependency)
                if installed:
                    if baw.requirements.lower(installed, available):
                        available = installed
                if available != version:
                    sink[package] = (version, available)  #(old, new)
    return sync_error
