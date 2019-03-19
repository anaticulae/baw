###############################################################################
#                                Kiwi Project                                 #
#                                    2019                                     #
#                          Helmut Konrad Fahrendholz                          #
#                             kiwi@derspanier.de                              #
###############################################################################
""" Run every function which is used by `baw`"""

from functools import partial
from glob import glob
from os import environ
from os.path import abspath
from os.path import exists
from os.path import isfile
from os.path import join
from os.path import split
from os.path import splitdrive
from shutil import rmtree
from subprocess import PIPE
from subprocess import run
from sys import stdout

from . import logging
from . import logging_error
from . import THIS
from .utils import BAW_EXT
from .utils import get_setup
from .utils import GIT_EXT
from .virtual import run_virtual


def root(cwd: str):
    """Determine root path of project.

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
    is_file = isfile(cwd)
    if is_file:
        cwd = split(cwd)[0]  # remove filename out of path

    while not exists(join(cwd, GIT_EXT)) and not exists(join(cwd, BAW_EXT)):
        cwd = abspath(join(cwd, '..'))
        if splitdrive(cwd)[1] == '\\':
            msg = 'Could not determine project root. Current: %s' % cwd
            raise ValueError(msg)
    return cwd


def clean(root: str, virtual: bool = False):
    check_root(root)
    logging('Start cleaning')
    patterns = ['build', 'html', 'doctrees', 'virtual', '__pycache__']
    # if not virtual:
    #     patterns.append('virtual')

    # problems while deleting recursive
    for pattern in patterns:
        todo = glob(root + '/**/' + pattern, recursive=True)
        todo = sorted(todo, reverse=True)  # longtest path first, to avoid
        for item in todo:
            logging('Remove %s' % item)
            try:
                rmtree(item)
            except OSError as error:
                print(error, file=stdout)
    print()  # Newline


def test(root: str, virtual: bool = False):
    check_root(root)

    logging('Running tests')
    test_dir = join(root, 'tests')
    if not exists(test_dir):
        logging_error('No testdirectory %s available' % test_dir)
        exit(1)

    cmd = 'pytest --continue-on-collection-errors -vvv %s' % test_dir
    completed = run_target(root, cmd, virtual=True)
    return completed.returncode


def run_target(root: str, command: str, cwd: str = '', virtual: bool = False):
    if not cwd:
        cwd = root
    if virtual:
        completed = run_virtual(root, command, cwd=root, verbose=False)
    else:
        completed = run(
            command.split(),
            stdout=PIPE,
            stderr=PIPE,
            cwd=cwd,
            universal_newlines=True)
    if completed.stdout:
        logging(completed.stdout)
    if completed.returncode and completed.stderr:
        logging_error(completed.stderr)

    return completed


def doc(root: str, virtual: bool = False):
    """Run Sphinx doc generation

    The result is locatated in `doc/build` as html-report. The stderr and
    stdout are printed to console

    Exception:
        raises SystemExit if some error occurs"""
    doc = join(root, 'doc')
    doc_build = join(doc, 'build')
    # Create files out of source
    command = 'sphinx-apidoc -d 10 -M -f -e -o %s %s' % (doc_build, root)
    completed = run_target(root, command, virtual=virtual)
    # if virtual:
    #     result = run_virtual(root, command, cwd=root, verbose=False)
    # else:
    #     result = run(command.split(), cwd=root)

    if completed.returncode:
        return completed.returncode

    # Create html result
    logging('Running make html')

    build_options = [
        '-v ',
        # '-n',  # warn about all missing references
        # '-W',  # turn warning into error
        '-b coverage',
        '-j 8'
    ]
    build_options = ' '.join(build_options)

    command = 'sphinx-build -M html %s %s %s'
    command = command % (doc, doc, build_options)

    result = run_target(root, command, virtual=virtual)

    return result.returncode


def release(root: str, virtual: bool = False):
    ret = test(root, virtual=virtual)
    if ret:
        logging_error('\nTests failed, could not release.\n')
        return ret

    logging("Update version tag")

    logging("Update Changelog")

    logging("Packing project")

    return 0


def head_tag(root: str, virtual: bool):
    # command = 'git tag --points-at 7c4bd36557a010349ce784ddd466c16721d231f'
    command = 'git tag --points-at HEAD'

    completed = run_target(root, command, root, virtual=virtual)
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


def sync(root: str, virtual: bool = False):
    check_root(root)
    logging('Sync dependencies')

    requirements_dev = 'requirements-dev.txt'
    resources = ['requirements.txt', requirements_dev]
    resources = [join(root, item) for item in resources]
    resources = [item for item in resources if exists(item)]

    if not exists(join(root, requirements_dev)):
        resources.append(abspath(join(THIS, '..', requirements_dev)))

    ret = 0

    try:
        pip_index = environ['HELPY_INT_DIRECT']
        extra_url = environ['HELPY_EXT_DIRECT']
    except KeyError as error:
        logging_error('Global var %s does not exist' % error)
        exit(1)

    pip_source = '--index-url %s --extra-index-url %s' % (pip_index, extra_url)
    for item in resources:

        cmd = 'python -mpip install %s -U -r %s' % (pip_source, item)
        logging(cmd)
        if virtual:
            completed = run_virtual(root, cmd, cwd=root)
        else:
            completed = run(cmd.split(), cwd=root)

        if completed.stdout:
            logging(completed.stdout)
        if completed.returncode and completed.stderr:
            logging_error(completed.stderr)
        ret += completed.returncode
    return ret


def check_root(root: str):
    if not exists(root):
        raise ValueError('Project root does not exists' % root)
