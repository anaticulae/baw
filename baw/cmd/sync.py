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

from baw.resources import GITIGNORE
from baw.runtime import run_target
from baw.utils import check_root
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

    requirements_dev = 'requirements-dev.txt'
    resources = ['requirements.txt', requirements_dev]
    # make path absolute in project
    resources = [join(root, item) for item in resources]
    resources = [item for item in resources if exists(item)]

    if not exists(join(root, requirements_dev)):
        resources.append(join(ROOT, requirements_dev))

    try:
        pip_index = environ['HELPY_INT_DIRECT']
        extra_url = environ['HELPY_EXT_DIRECT']
    except KeyError as error:
        logging_error('Global var %s does not exist' % error)
        exit(1)

    pip_source = '--index-url %s --extra-index-url %s' % (pip_index, extra_url)

    ret = 0
    for item in resources:
        cmd = 'python -mpip install %s -U -r %s' % (pip_source, item)
        logging(cmd)

        completed = run_target(
            root,
            cmd,
            cwd=root,
            verbose=verbose,
            virtual=virtual,
        )

        if completed.stdout:
            for item in completed.stdout.splitlines():
                if not verbose and 'Requirement already' in item:
                    logging('.', end='')
                    continue
                logging(item)
            logging()
            # logging(completed.stdout)
        if completed.returncode and completed.stderr:
            pass
            # logging_error(completed.stderr)
        ret += completed.returncode
    return ret


def sync_files(root: str):
    logging('sync gitexclude')
    file_replace(join(root, GIT_REPO_EXCLUDE), GITIGNORE)
    return 0
