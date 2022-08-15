#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019-2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================

import contextlib
import os
import re
import sys
from os.path import exists
from os.path import join
from urllib.request import URLError
from urllib.request import urlopen

import baw.config
import baw.requirements
import baw.utils
from baw.git import update_gitignore
from baw.runtime import run_target
from baw.utils import FAILURE
from baw.utils import REQUIREMENTS_EXTRA
from baw.utils import error
from baw.utils import get_setup
from baw.utils import log
from baw.utils import package_address


def sync(
    root: str,
    packages: str = 'dev',
    *,
    minimal: bool = False,
    virtual: bool = False,
    verbose: bool = False,
) -> int:
    """Sync packages which are defined in requirements.txt
    Args:
        root(str): root path of project to sync
        packages(str): decide which packages should be synchronized:
                        - dev/ minimal dev environment, formater, linter, test
                        - doc/ Sphinx
                        - extra
                        - all
        minimal(bool): if True use minimal version in requirement file
        virtual(bool): if True sync the virtual environment
                       if BOTH sync virtual and local environment
                       if False sync local environment
        verbose(bool): if True, increase verbosity of logging
    Returns:
        summed exit code of sync processes
    """
    baw.utils.check_root(root)
    ret = 0
    log()
    ret += update_gitignore(root, verbose=verbose)
    # NOTE: Should we use Enum?
    if virtual == 'BOTH':
        for item in [True, False]:
            ret += sync_dependencies(
                root,
                packages=packages,
                minimal=minimal,
                virtual=item,
                verbose=verbose,
            )
            if ret:
                # Fast fail, if one failes, don't check the rest
                return ret
    else:
        ret += sync_dependencies(
            root,
            packages=packages,
            minimal=minimal,
            virtual=virtual,
            verbose=verbose,
        )
    return ret


def check_dependency(
    root: str,
    package: str,
    *,
    virtual: bool,
    verbose: bool = False,
):
    """Check if packages need an upgrade."""
    (adress, internal, external) = get_setup()

    pip_index = '%s:%d' % (adress, internal)
    extra_url = '%s:%d' % (adress, external)

    # if not connected(pip_index, extra_url):
    #     msg = f"Could not reach index {pip_index} or {extra_url}"
    #     raise RuntimeError(msg)

    python = baw.config.python(root, virtual=virtual)
    for index in [pip_index, extra_url]:
        pip = f'{python} -mpip search --index {index} {package}'
        completed = run_target(
            root,
            pip,
            verbose=verbose,
            virtual=virtual,
            skip_error_code=[23, 2],  # package not found
        )
        if completed.returncode == 23:
            # Package not available
            continue
        if completed.returncode == 2:
            error(f'not reachable: {index} for package {package}')
            error(completed.stderr)
            sys.exit(completed.returncode)
            continue
        if completed.returncode and completed.stderr:
            error(completed.stderr)

        if completed.stdout:
            if f'{package} ' not in completed.stdout:
                # nltk (3.5)  - 3.5
                # INSTALLED: 3.5 (latest)
                # skip finding nltk_data when searching for nltk
                continue
            return completed.stdout
    raise ValueError(f'Could not check dependencies {package}')


def sync_dependencies(
    root: str,
    packages: str,
    *,
    minimal: bool = False,
    verbose: bool = False,
    virtual: bool = False,
) -> int:
    baw.utils.check_root(root)
    log('sync virtual' if virtual else 'sync local')
    resources = determine_resources(root, packages)
    pip_index, extra_url = package_address()
    if not connected(pip_index, extra_url):
        baw.utils.error('could not reach package index')
        return FAILURE
    required = required_installation(
        root,
        resources,
        minimal=minimal,
        verbose=verbose,
        virtual=virtual,
    )
    if not required.equal and not required.greater:
        return baw.utils.SUCCESS
    log(f'\nrequire update:\n{required}')
    # create temporary requirements file
    requirements = os.path.join(baw.utils.tmp(root), 'requirements.txt')
    baw.utils.file_replace(requirements, str(required))
    cmd, pip = get_install_cmd(
        root,
        requirements,
        verbose,
        pip_index,
        extra_url,
        virtual=virtual,
    )
    if verbose:
        log(cmd)
    completed = run_target(
        root,
        cmd,
        cwd=root,
        verbose=False,
        virtual=virtual,
    )
    baw.utils.file_remove(requirements)
    if 'NewConnectionError' in completed.stdout:
        error('Could not reach server: %s' % pip)
        return completed.returncode
    if completed.stdout:
        for message in completed.stdout.splitlines():
            if should_skip(message, verbose=verbose):
                continue
            if verbose:
                log(message)
    if completed.returncode and completed.stderr:
        error(completed.stderr)
    log()
    return completed.returncode


def required_installation(
    root,
    txts: list,
    minimal: bool = False,
    virtual: bool = False,
    verbose: bool = False,
):
    current = pip_list(root, verbose=verbose, virtual=virtual)
    requested = [
        baw.requirements.parse(baw.utils.file_read(item)) for item in txts
    ]
    missing = [
        baw.requirements.diff(current, item, minimal) for item in requested
    ]
    result = baw.requirements.Requirements()
    for item in missing:
        result.equal.update(item.equal)  # pylint:disable=E1101
        if minimal:
            result.equal.update(item.greater)  # pylint:disable=E1101
        else:
            result.greater.update(item.greater)  # pylint:disable=E1101
    # TODO: REMOVE DUPLICATED
    for key in result.greater:
        with contextlib.suppress(KeyError):
            # remove duplicated requirement out of `equal requirement`
            result.equal.pop(key)
            continue
        baw.utils.log(f'duplicated requirement: {key}')
    return result


def determine_resources(root: str, packages: str) -> list:
    """Determine requirements depending on `packages` choice.

    Args:
        root(str): root of generated project
        packages(str): select package to install
    Returns:
        list of absolute paths to requirements.txt's

    Choices(packages):
        - all: install project, test and doc environment
        - dev: install pytest, pycov etc.
        - doc: install Sphinx requirements
        - requirements: only install project requirements.txt
    """
    resources = []
    requirements_dev = 'baw/requires/requirements-dev.txt'
    requirements_doc = 'baw/requires/requirements-doc.txt'
    if packages == 'dev':
        resources.append(requirements_dev)
    if packages == 'doc':
        resources.append(requirements_doc)
    if packages == 'all':
        resources.append(requirements_dev)
        resources.append(requirements_doc)
    # Requirements_dev is a `global` file from baw project. This file is not
    # given in child project, it is referenced from global baw. Pay attention
    # to the difference of ROOT (baw) and root(project).
    # make path absolute in project
    resources = [join(baw.ROOT, to_install) for to_install in resources]
    if packages in ('dev', 'all'):
        if os.path.exists(os.path.join(root, 'requirements.dev')):
            resources.append(os.path.join(root, 'requirements.dev'))
    if packages in ('extra', 'all'):
        if os.path.exists(os.path.join(root, REQUIREMENTS_EXTRA)):
            resources.append(os.path.join(root, REQUIREMENTS_EXTRA))

    # local project file
    local_requirement = join(root, baw.utils.REQUIREMENTS_TXT)
    if exists(local_requirement):
        resources.append(local_requirement)
    return resources


def get_install_cmd(
    root: str,
    to_install: str,
    verbose: bool,
    pip_index: str,
    extra_url: str,
    virtual: bool,
):
    trusted = host(pip_index)
    warning = '' if verbose else '--no-warn-conflicts'
    pip = f'--index-url {pip_index} --extra-index-url {extra_url} '
    pip += f'--trusted {trusted}'
    config = '--retries 2 --disable-pip-version-check'
    python = baw.config.python(root, virtual=virtual)
    # prepare command
    cmd = f'{python} -mpip install {warning} {pip} '
    cmd += f'-U {config} '
    cmd += f'-r {to_install} '
    return cmd, pip


HOST = re.compile(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}')


def host(url: str) -> str:
    """\
    >>> host('http://169.254.149.20:6103')
    '169.254.149.20'
    """
    if searched := HOST.search(url):
        return searched[0]
    return None


def pip_list(
    root,
    verbose: bool = False,
    virtual: bool = False,
) -> baw.requirements.Requirements:
    python = baw.config.python(root, virtual=virtual)
    cmd = f'{python} -mpip list --format=freeze'
    if verbose:
        log(cmd)
    completed = run_target(
        root,
        cmd,
        cwd=root,
        verbose=False,
        virtual=virtual,
    )
    if completed.returncode and completed.stderr:
        error(completed.stderr)
        sys.exit(completed.returncode)
    content = completed.stdout
    parsed = baw.requirements.parse(content)
    return parsed


def connected(internal: str, external: str) -> bool:
    """Test connect to internal and external server. Send a simple http-request
    and check the resonse.

    Args:
        internal(str): adress of internal pip server
        external(str): adress of external pip server
    Returns:
        True if boths connection are green, if not False
    Hint:
        Log the failure of a connection process also
    """
    result = True
    for item in [internal, external]:
        try:
            with urlopen(item) as response:
                response.read()
        except URLError:
            result = False
            error('Could not reach %s' % item)
    return result


def should_skip(msg: str, verbose: bool = False):
    if not verbose and 'Requirement already' in msg:
        log('.', end='')
        return True
    return False
