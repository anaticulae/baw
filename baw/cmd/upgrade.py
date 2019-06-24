#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================

from os.path import exists
from os.path import join
from re import search

from baw.cmd.sync import check_dependency
from baw.git import git_checkout
from baw.git import git_commit
from baw.git import git_stash
from baw.utils import FAILURE
from baw.utils import REQUIREMENTS_TXT
from baw.utils import SUCCESS
from baw.utils import file_read
from baw.utils import file_replace
from baw.utils import logging
from baw.utils import logging_error


def upgrade(
        root: str,
        *,
        notests: bool = False,
        verbose: bool = False,
        virtual: bool = False,
):
    """Upgrade requirements"""
    with git_stash(root, verbose=verbose, virtual=virtual):
        requirements = join(root, REQUIREMENTS_TXT)
        failure = upgrade_requirements(root)

        # requirements.txt is uptodate, no update requireded
        if failure == REQUIREMENTS_UP_TO_DATE:
            return SUCCESS

        if failure:
            logging_error('Error while upgrading requirements')
            return failure

        from baw.cmd import sync_and_test

        failure = sync_and_test(
            root,
            packages='dev',  # minimal requirements is required
            quiet=True,
            stash=False,
            sync=True,  # install new packages
            testconfig=None,
            test=not notests,
            verbose=False,
            virtual='BOTH',  # sync virtual and non virtual environment
        )
        if failure:
            # reset requirement
            completed = git_checkout(
                root,
                requirements,
                verbose=verbose,
                virtual=virtual,
            )
            logging_error('Upgrading failed')
            assert not completed

            return failure

        failure = git_commit(
            root,
            source=requirements,
            message='chore(requirements): upgrade %s' % REQUIREMENTS_TXT)
        if failure:
            return failure
    return SUCCESS


REQUIREMENTS_UP_TO_DATE = 100


def upgrade_requirements(
        root: str,
        requirements: str = REQUIREMENTS_TXT,
        virtual: bool = False,
):
    """Take requirements.txt, replace version number with current available
    version on pip repository.

    Args:
        root(str): generated project
        requirements(str): relativ path to requirements
        virtual(bool): run in virtual environment
    Returns:
        SUCCESS if file was upgraded
    """
    requirements_path = join(root, requirements)
    msg = 'Path does not exists %s' % requirements_path

    if not exists(requirements_path):
        msg = 'Could not locate any requirements: %s' % requirements_path
        logging_error(msg)
        return FAILURE
    logging('\nStart upgrading requirements: %s' % requirements_path)

    content = file_read(requirements_path)
    if not content.strip():
        logging('Empty: %s. Skipping replacement.' % requirements_path)
        # stop further synchonizing process and quit with SUCCESS
        return REQUIREMENTS_UP_TO_DATE

    # parsed = parse_requirements(content)
    upgraded = determine_new_requirements(root, content, virtual=virtual)
    if upgraded == None:
        return FAILURE
    replaced = replace_requirements(content, upgraded)

    if replaced == content:
        logging('Requirements are up to date.\n')
        return REQUIREMENTS_UP_TO_DATE

    file_replace(requirements_path, replaced)

    logging('Upgrading finished')

    return SUCCESS


def installed_version(content: str):
    searched = search(r'INSTALLED: (?P<installed>[\w|\d|\.]+)', content)
    if not searched:
        return None
    return searched.group('installed')


def available_version(content: str):
    searched = search(r'\w+\s\((?P<available>[\w|\d|\.]+)', content)
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
) -> str:
    parsed = parse_requirements(requirements)
    result = {}
    sync_error = False
    for package, version in parsed.items():
        try:
            dependency = check_dependency(root, package, virtual=virtual)
        except ValueError:
            logging_error('Package `%s` is not available' % package)
        except RuntimeError:
            logging_error('Could not reach package repository')
            sync_error = True
        else:
            available = available_version(dependency)
            if available != version:
                result[package] = (version, available)  #(old, new)
    if sync_error:
        return None
    return result


def replace_requirements(requirements: str, new_requirements: dict) -> str:
    for package, [old, new] in new_requirements.items():
        if old:
            placeholder = '%s==%s' % (package, old)
        else:
            # no version was given for old package
            placeholder = '%s' % package

        replacement = '%s==%s' % (package, new)

        logging('Replace requirement:\n%s\n%s' % (placeholder, replacement))
        requirements = requirements.replace(placeholder, replacement)
    return requirements


# Example:

# PyYAML==5.1
# pdfminer.six==20181108

# # Internal packages
# iamraw==0.1.2
# serializeraw==0.1.0
# utila==0.5.3


def parse_requirements(content: str):
    assert isinstance(content, str)
    result = {}
    for line in content.splitlines():
        if '#' in line or not line:
            continue
        try:
            package, version = line.split('==')
            result[package] = version
        except ValueError:
            # packakge without version
            result[line] = ''
    return result
