#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019 by Helmut Konrad Fahrendholz. All rights reserved.
# Tis file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================
"""Run every function which is used by `baw`."""
from glob import glob
from os import chmod
from os import environ
from os import remove
from os.path import abspath
from os.path import exists
from os.path import isfile
from os.path import join
from os.path import split
from os.path import splitdrive
from shutil import rmtree
from stat import S_IWRITE

from baw.config import commands
from baw.config import shortcut
from baw.runtime import run_target
from baw.runtime import VIRTUAL_FOLDER
from baw.utils import BAW_EXT
from baw.utils import check_root
from baw.utils import FAILURE
from baw.utils import get_setup
from baw.utils import GIT_EXT
from baw.utils import logging
from baw.utils import logging_error
from baw.utils import SUCCESS


def find_root(cwd: str):
    """Determine root path of project.

    Iterate to the top directory while searching for GIT or BAW folder.

    Args:
        cwd(str): location where `baw` is executed
    Returns:
        path(str): of project-root(git)
    Raises:
        ValueError if no root is located or cwd does not exists
    """
    if not exists(cwd):
        raise ValueError('Current work directory does not exists %s' % cwd)

    cwd = abspath(cwd)  # ensure to work with absolut path
    if isfile(cwd):
        cwd = split(cwd)[0]  # remove filename out of path

    while True:
        if exists(join(cwd, GIT_EXT)):
            return cwd
        if exists(join(cwd, BAW_EXT)):
            return cwd
        cwd = abspath(join(cwd, '..'))
        if splitdrive(cwd)[1] == '\\':  #TODO: Windows only?
            msg = 'Could not determine project root. Current: %s' % cwd
            raise ValueError(msg)
    return cwd


def remove_readonly(func, path, _):
    "Clear the readonly bit and reattempt the removal"
    chmod(path, S_IWRITE)
    func(path)


def clean(root: str):
    check_root(root)
    logging('Start cleaning')
    patterns = [
        '*.egg',
        '*.egg-info',
        '.coverage',
        '.pytest_cache',
        '.tmp',
        '__pycache__',
        'build',
        'dist',
        'doctrees',
        'html',
    ]

    # problems while deleting recursive
    ret = 0
    for pattern in patterns:
        try:
            todo = glob(root + '/**/' + pattern, recursive=True)
        except NotADirectoryError:
            todo = glob(root + '**' + pattern, recursive=True)
        todo = sorted(todo, reverse=True)  # longtest path first, to avoid
        for item in todo:
            logging('Remove %s' % item)
            try:
                if isfile(item):
                    remove(item)
                else:
                    rmtree(item, onerror=remove_readonly)
            except OSError as error:
                ret += 1
                logging_error(error)
    if ret:
        exit(ret)
    logging()  # Newline


def clean_virtual(root: str):
    """Clean virtual environment of given project

    Args:
        root(str): generated project
    Hint:
        Try to remove .virtual folder
    Raises:
        SystemExit if cleaning not work
    """
    virtual_path = join(root, VIRTUAL_FOLDER)
    if not exists(virtual_path):
        logging('Virtual environment does not exist %s' % virtual_path)
        return
    logging('Try to clean virtual environment %s' % virtual_path)
    try:
        rmtree(virtual_path)
    except OSError as error:
        logging_error(error)
        exit(FAILURE)
    logging('Finished')


def install(root: str, virtual: bool):
    # -f always install newest one
    command = 'python setup.py install -f'

    completed = run_target(root, command, root, verbose=False, virtual=virtual)
    print(completed.stdout)
    return completed.returncode


def head_tag(root: str, virtual: bool):
    command = 'git tag --points-at HEAD'

    completed = run_target(root, command, root, verbose=False, virtual=virtual)
    return completed.stdout.strip()


# TODO: Use twine for uploading packages
SDIST_UPLOAD_WARNING = ('WARNING: Uploading via this command is deprecated, '
                        'use twine to upload instead '
                        '(https://pypi.org/p/twine/)')


def publish(root: str):
    """Push release to defined repository

    Hint:
        publish run's always in virtual environment
    """
    tag = head_tag(root, virtual=True)
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


def format_source(root: str, verbose: bool = False, virtual: bool = False):
    short = shortcut(root)
    for item in [short, 'tests']:
        source = join(root, item)
        command = 'yapf -r -i --style=google %s' % source
        logging('Format source %s' % source)

        completed = run_target(
            root,
            command,
            source,
            virtual=virtual,
            verbose=verbose,
        )

        if completed.returncode:
            logging_error('Error while fromating\n%s' % str(completed))
            return FAILURE
    logging('Format complete')
    return SUCCESS


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
