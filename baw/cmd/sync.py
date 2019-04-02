#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019 by Helmut Konrad Fahrendholz. All rights reserved.
# Tis file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================

from os import environ
from os.path import exists
from os.path import join
from urllib.request import URLError
from urllib.request import urlopen

from baw.resources import GITIGNORE
from baw.runtime import run_target
from baw.utils import check_root
from baw.utils import FAILURE
from baw.utils import file_replace
from baw.utils import GIT_REPO_EXCLUDE
from baw.utils import logging
from baw.utils import logging_error
from baw.utils import NEWLINE
from baw.utils import package_address
from baw.utils import ROOT


def sync(root: str, virtual: bool = False, verbose: bool = False):
    check_root(root)
    ret = 0
    logging()
    ret += sync_files(root)
    ret += sync_dependencies(root, virtual=virtual, verbose=verbose)
    return ret


def sync_dependencies(
        root: str,
        *,
        verbose: bool = False,
        virtual: bool = False,
):
    check_root(root)
    logging('sync dependencies')
    logging()
    requirements_dev = 'requirements-dev.txt'
    resources = ['requirements.txt', requirements_dev]
    # make path absolute in project
    resources = [join(root, to_install) for to_install in resources]
    resources = [to_install for to_install in resources if exists(to_install)]

    if not exists(join(root, requirements_dev)):
        resources.append(join(ROOT, requirements_dev))

    pip_index, extra_url = package_address()

    if not connected(pip_index, extra_url):
        return FAILURE

    pip = '--index-url %s --extra-index-url %s' % (pip_index, extra_url)
    config = '--retries 2'
    ret = 0
    for to_install in resources:
        cmd = 'python -mpip install %s -U %s -r %s' % (pip, config, to_install)
        logging(cmd)

        completed = run_target(
            root,
            cmd,
            cwd=root,
            verbose=False,
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
                logging(to_install)
            logging()
        if verbose and completed.returncode and completed.stderr:
            logging_error(completed.stderr)
        ret += completed.returncode
    return ret


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


def sync_files(root: str):
    logging('sync gitexclude')
    file_replace(join(root, GIT_REPO_EXCLUDE), GITIGNORE)
    return 0
