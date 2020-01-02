#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019-2020 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================

from os.path import exists
from os.path import join
from urllib.request import URLError
from urllib.request import urlopen

from baw.git import update_gitignore
from baw.runtime import run_target
from baw.utils import FAILURE
from baw.utils import REQUIREMENTS_TXT
from baw.utils import ROOT
from baw.utils import check_root
from baw.utils import get_setup
from baw.utils import logging
from baw.utils import logging_error
from baw.utils import package_address


def sync(
        root: str,
        packages: str = 'dev',
        *,
        virtual: bool = False,
        verbose: bool = False,
):
    """
    Args:
        packages(str): decide which packages should be synchronized:
                        - dev/ minimal dev environment, formater, linter, test
                        - doc/ Sphinx
                        - all
    """
    check_root(root)
    ret = 0
    logging()
    ret += update_gitignore(root, verbose=verbose)

    # HACK: Use ENUM
    if virtual == 'BOTH':
        for item in [True, False]:
            ret += sync_dependencies(
                root,
                packages=packages,
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
            virtual=virtual,
            verbose=verbose,
        )
    return ret


def check_dependency(
        root: str,
        package: str,
        *,
        virtual: bool,
):
    (adress, internal, external) = get_setup()

    pip_index = '%s:%d' % (adress, internal)
    extra_url = '%s:%d' % (adress, external)

    if not connected(pip_index, extra_url):
        msg = "Could not reach index %s or %s" % (pip_index, extra_url)
        raise RuntimeError(msg)

    for index in [pip_index, extra_url]:
        pip = 'python -mpip search --retries 2 --index %s %s' % (index, package)
        completed = run_target(
            root,
            pip,
            verbose=False,
            virtual=virtual,
            skip_error_code=[23],  # package not found
        )
        if completed.returncode == 23:
            # Package not available
            continue
        if completed.returncode and completed.stderr:
            logging_error(completed.stderr)

        if completed.stdout:
            return completed.stdout
    raise ValueError('Could not check dependencies %s' % (package))


def sync_dependencies(
        root: str,
        packages: str,
        *,
        verbose: bool = False,
        virtual: bool = False,
):
    check_root(root)
    logging('sync dependencies')

    resources = determine_resources(root, packages)

    pip_index, extra_url = package_address()
    if not connected(pip_index, extra_url):
        return FAILURE

    ret = 0
    for to_install in resources:
        cmd, pip = get_install_cmd(to_install, verbose, pip_index, extra_url)

        completed = run_target(
            root,
            cmd,
            cwd=root,
            verbose=verbose,
            virtual=virtual,
        )
        if 'NewConnectionError' in completed.stdout:
            logging_error('Could not reach server: %s' % pip)
            ret += 1
            break
        if completed.stdout:
            for message in completed.stdout.splitlines():
                if should_skip(message, verbose=verbose):
                    continue
                if verbose:
                    logging(message)
        if completed.returncode and completed.stderr:
            logging_error(completed.stderr)
        ret += completed.returncode
    logging()
    logging()
    return ret


def determine_resources(root: str, packages: str):
    """Detemine requirements depending on package choice

    Args:
        root(str): root of generated project
        packages(str): select package to install

    Choices:
        - all:
        - dev:
        - doc:
        - requirements: only install requirements.txt
    """
    resources = []
    requirements_dev = 'requirements-dev.txt'
    requirements_doc = 'requirements-doc.txt'
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
    resources = [join(ROOT, to_install) for to_install in resources]

    # local project file
    local_requirement = join(root, REQUIREMENTS_TXT)
    # TODO: Always install requirements?
    if exists(local_requirement):
        resources.append(local_requirement)
    return resources


def get_install_cmd(to_install, verbose, pip_index, extra_url):
    warning = '' if verbose else '--no-warn-conflicts'
    pip = '--index-url %s --extra-index-url %s' % (pip_index, extra_url)
    config = '--retries 2 --disable-pip-version-check'

    cmd = 'python -mpip install %s %s -U %s -r %s' % (
        warning,
        pip,
        config,
        to_install,
    )
    return cmd, pip


def connected(internal, external):
    """Test connect to internal and external server. Send a simple http-request
    and check the resonse

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
            logging_error('Could not reach %s' % item)
    return result


def should_skip(msg: str, verbose: bool = False):
    if not verbose and 'Requirement already' in msg:
        logging('.', end='')
        return True
    return False
