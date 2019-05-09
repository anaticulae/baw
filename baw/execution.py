#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================
"""Run every function which is used by `baw`."""
from os import environ

from baw.config import commands
from baw.git import git_headtag
from baw.runtime import run_target
from baw.utils import FAILURE
from baw.utils import SUCCESS
from baw.utils import check_root
from baw.utils import get_setup
from baw.utils import logging
from baw.utils import logging_error

# TODO: Use twine for uploading packages
SDIST_UPLOAD_WARNING = ('WARNING: Uploading via this command is deprecated, '
                        'use twine to upload instead '
                        '(https://pypi.org/p/twine/)')


def publish(root: str):
    """Push release to defined repository

    Hint:
        publish run's always in virtual environment
    """
    tag = git_headtag(root, virtual=True)
    if not tag:
        logging_error('Could not find release-git-tag. Aborting publishing.')
        return FAILURE

    adress, internal, _ = get_setup()
    url = '%s:%d' % (adress, internal)
    command = 'python setup.py sdist upload -r %s' % url
    completed = run_target(
        root,
        command,
        root,
        verbose=False,
        skip_error_message=[SDIST_UPLOAD_WARNING],
        virtual=True,
    )

    if completed.returncode == SUCCESS:
        logging('Publish completed')
    return completed.returncode


SEPARATOR_WIDTH = 80


def run(root: str, virtual=False):
    """Check project-environment for custom run sequences, execute them from
    first to end.

    Args:
        root(str): project root where .baw and git are located
        virtual(bool): run in virtual environment
    Returns:
        0 if all sequences run succesfull else not 0
    """
    check_root(root)
    logging('Run')

    cmds = commands(root)
    if not cmds:
        logging_error('No commands available')
        return FAILURE

    env = {} if virtual else dict(environ.items())
    ret = SUCCESS
    for command, executable in cmds.items():
        logging('\n' + command.upper().center(SEPARATOR_WIDTH, '*') + '\n')
        completed = run_target(root, executable, env=env, virtual=virtual)
        logging('\n' + command.upper().center(SEPARATOR_WIDTH, '='))

        ret += completed.returncode
    return ret
