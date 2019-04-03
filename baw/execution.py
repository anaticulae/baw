###############################################################################
#                                Kiwi Project                                 #
#                                    2019                                     #
#                          Helmut Konrad Fahrendholz                          #
#                             kiwi@derspanier.de                              #
###############################################################################
"""Run every function which is used by `baw`."""
import tempfile
from contextlib import contextmanager
from glob import glob
from os import environ
from os import remove
from os import unlink
from os.path import abspath
from os.path import exists
from os.path import isfile
from os.path import join
from os.path import split
from os.path import splitdrive
from shutil import rmtree

from baw.cmd import test
from baw.config import commands
from baw.config import shortcut
from baw.resources import SETUP_CFG
from baw.runtime import run_target
from baw.runtime import VIRTUAL_FOLDER
from baw.utils import BAW_EXT
from baw.utils import check_root
from baw.utils import get_setup
from baw.utils import GIT_EXT
from baw.utils import logging
from baw.utils import logging_error


def root(cwd: str):
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


def clean(root: str):
    check_root(root)
    logging('Start cleaning')
    patterns = [
        '.coverage',
        '.pytest_cache',
        '__pycache__',
        'build',
        'doctrees',
        'html',
        '.tmp',
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
                    rmtree(item)
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
        exit(1)
    logging('Finished')


def release(
        root: str,
        *,
        stash: bool = False,
        verbose: bool = False,
        virtual: bool = False,
        release_type: str = 'auto',
):
    """Running release. Running test, commit and tag.

    Args:
        root(str): generated project
        stash(bool): git stash to test on a clean git directory
        verbose(bool): log additional output
        virtual(bool): run in virtual environment
        release_type(str): major x.0.0
                           minor 0.x.0
                           patch 0.0.x
                           noop  0.0.0 do nothing
                           auto  let semantic release decide
    Return:
        0 if success else > 0
    """
    ret = test(
        root,
        longrun=True,
        stash=stash,
        verbose=verbose,
        virtual=virtual,
    )
    if ret:
        logging_error('\nTests failed, could not release.\n')
        return ret

    logging("Update version tag")
    with temp_semantic_config(root) as config:
        # only release with type if user select one
        release_type = '' if release_type == 'auto' else '--%s' % release_type
        cmd = 'semantic-release version %s --config="%s"'
        cmd = cmd % (release_type, config)
        completed = run_target(root, cmd, verbose=verbose)
        logging(completed.stdout)

    logging("Update Changelog")

    if completed.returncode:
        logging_error('while running semantic-release')
        return completed.returncode

    logging("Packing project")

    return 0


@contextmanager
def temp_semantic_config(root: str):
    short = shortcut(root)
    replaced = SETUP_CFG.replace('$_SHORT_$', short)
    if replaced == SETUP_CFG:
        logging_error('while replacing template')
        exit(1)
    with tempfile.TemporaryFile(mode='w', delete=False) as fp:
        fp.write(replaced)
        fp.seek(0)
    yield fp.name

    # remove file
    unlink(fp.name)


def head_tag(root: str, virtual: bool):
    command = 'git tag --points-at HEAD'

    completed = run_target(root, command, root, verbose=False, virtual=virtual)
    return completed.stdout.strip()


def publish(root: str, virtual: bool = False):
    tag = head_tag(root, virtual)
    if not tag:
        logging_error('Could not find release-git-tag. Aborting publishing.')
        return 1

    ret = release(root, virtual=virtual)
    if ret:
        exit(ret)

    adress, internal, _ = get_setup()
    url = '%s:%d' % (adress, internal)
    command = 'python setup.py sdist upload -r %s' % url
    completed = run_target(root, command, root, virtual=virtual)

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
        return 1

    env = {} if virtual else dict(environ.items())
    ret = 0
    for command, executable in cmds.items():
        logging('\n' + command.upper().center(SEPARATOR_WIDTH, '*') + '\n')
        completed = run_target(root, executable, env=env, virtual=virtual)
        logging('\n' + command.upper().center(SEPARATOR_WIDTH, '='))

        ret += completed.returncode
    return ret
