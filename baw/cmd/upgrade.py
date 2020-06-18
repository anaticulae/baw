#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019-2020 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================

import concurrent.futures
import os
import re

import baw.cmd.sync
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
        requirements = os.path.join(root, baw.utils.REQUIREMENTS_TXT)
        failure = upgrade_requirements(root)
        requirements_dev = os.path.join(root, baw.utils.REQUIREMENTS_DEV)
        if not os.path.exists(requirements_dev) or packages == 'requirements':
            requirements_dev = None
        failure_dev = REQUIREMENTS_UP_TO_DATE
        if requirements_dev:
            failure_dev = upgrade_requirements(root, baw.utils.REQUIREMENTS_DEV)

        # requirements.txt is uptodate, no update requireded
        if failure == REQUIREMENTS_UP_TO_DATE and failure_dev == REQUIREMENTS_UP_TO_DATE:
            return baw.utils.SUCCESS
        devupgade_failure = failure_dev not in (REQUIREMENTS_UP_TO_DATE,
                                                baw.utils.SUCCESS)
        upgrade_failure = failure not in (REQUIREMENTS_UP_TO_DATE,
                                          baw.utils.SUCCESS)
        if upgrade_failure or devupgade_failure:
            baw.utils.logging_error('Error while upgrading requirements')
            return baw.utils.FAILURE

        from baw.cmd import sync_and_test
        failure = sync_and_test(
            root,
            generate=generate,  # generate test data
            packages='dev',  # minimal requirements is required
            quiet=True,
            stash=False,
            sync=True,  # install new packages
            test=not notests,
            testconfig=None,
            verbose=False,
            virtual='BOTH',  # sync virtual and non virtual environment
        )
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
            baw.utils.logging_error('Upgrading failed')
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


REQUIREMENTS_UP_TO_DATE = 100


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
    requirements_path = os.path.join(root, requirements)
    msg = 'Path does not exists %s' % requirements_path

    if not os.path.exists(requirements_path):
        msg = 'Could not locate any requirements: %s' % requirements_path
        baw.utils.logging_error(msg)
        return baw.utils.FAILURE
    baw.utils.logging('\nStart upgrading requirements: %s' % requirements_path)

    content = baw.utils.file_read(requirements_path)
    if not content.strip():
        baw.utils.logging(f'Empty: {requirements_path}. Skipping replacement.')
        # stop further synchonizing process and quit with SUCCESS
        return REQUIREMENTS_UP_TO_DATE

    upgraded = determine_new_requirements(root, content, virtual=virtual)
    if upgraded is None:
        return baw.utils.FAILURE
    replaced = baw.requirements.replace(content, upgraded)

    if replaced == content:
        baw.utils.logging('Requirements are up to date.\n')
        return REQUIREMENTS_UP_TO_DATE

    baw.utils.file_replace(requirements_path, replaced)

    baw.utils.logging('Upgrading finished')

    return baw.utils.SUCCESS


def installed_version(content: str):
    searched = re.search(r'INSTALLED: (?P<installed>[\w|\d|\.]+)', content)
    if not searched:
        return None
    return searched.group('installed')


def available_version(content: str):
    searched = re.search(r'\w+\s\((?P<available>[\w|\d|\.]+)', content)
    if not searched:
        return None
    return searched.group('available')


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
        baw.utils.logging_error('could not parse requirements')
        return None

    sync_error = False
    equal = {}
    greater = {}
    for source, sink in [(parsed.equal, equal), (parsed.greater, greater)]:
        sync_error |= collect_new_packages(root, source, sink, virtual)
    if sync_error:
        return None
    return baw.requirements.NewRequirements(equal=equal, greater=greater)


def collect_new_packages(root, source, sink, virtual):
    sync_error = False
    with concurrent.futures.ThreadPoolExecutor(max_workers=18) as executor:
        todo = {
            executor.submit(
                baw.cmd.sync.check_dependency,
                root,
                package,
                virtual=virtual,
            ): (package, version) for package, version in source.items()
        }
        for future in concurrent.futures.as_completed(todo):
            (package, version) = todo[future]
            try:
                dependency = future.result()
            except ValueError:
                baw.utils.logging_error(f'package: {package} is not available')
            except RuntimeError:
                baw.utils.logging_error('could not reach package repository')
                sync_error = True
            else:
                available = available_version(dependency)
                if available != version:
                    sink[package] = (version, available)  #(old, new)
    return sync_error
